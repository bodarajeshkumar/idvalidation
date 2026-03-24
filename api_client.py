"""
API Client for Large Dataset Retrieval
Handles authentication, pagination, rate limiting, and error handling
"""

import asyncio
import aiohttp
import time
import logging
from typing import Dict, List, Optional, AsyncGenerator
from dataclasses import dataclass
from datetime import datetime, timedelta
import json
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


@dataclass
class APIConfig:
    """Configuration for API client"""
    base_url: str
    api_key: str
    password: str
    page_size: int = 2500
    max_retries: int = 5
    initial_backoff: float = 1.0
    max_backoff: float = 60.0
    rate_limit_per_second: int = 10
    timeout: int = 30
    concurrent_months: int = 3


@dataclass
class PageResponse:
    """Response from a single page request"""
    data: List[Dict]
    page: int
    total_pages: int
    total_records: int
    has_next: bool


class RateLimiter:
    """Token bucket rate limiter"""
    
    def __init__(self, rate: int):
        """
        Initialize rate limiter
        
        Args:
            rate: Maximum requests per second
        """
        self.rate = rate
        self.tokens = rate
        self.last_update = time.time()
        self.lock = asyncio.Lock()
    
    async def acquire(self):
        """Acquire a token, waiting if necessary"""
        async with self.lock:
            now = time.time()
            elapsed = now - self.last_update
            
            # Refill tokens based on elapsed time
            self.tokens = min(self.rate, self.tokens + elapsed * self.rate)
            self.last_update = now
            
            # Wait if no tokens available
            if self.tokens < 1:
                wait_time = (1 - self.tokens) / self.rate
                await asyncio.sleep(wait_time)
                self.tokens = 0
            else:
                self.tokens -= 1


class APIClient:
    """Async API client with pagination, rate limiting, and error handling"""
    
    def __init__(self, config: APIConfig):
        """
        Initialize API client
        
        Args:
            config: API configuration
        """
        self.config = config
        self.rate_limiter = RateLimiter(config.rate_limit_per_second)
        self.session: Optional[aiohttp.ClientSession] = None
        self.stats = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'retries': 0,
            'records_retrieved': 0
        }
    
    async def __aenter__(self):
        """Async context manager entry"""
        # Use Basic Authentication for Cloudant
        import base64
        credentials = f"{self.config.api_key}:{self.config.password}"
        encoded_credentials = base64.b64encode(credentials.encode()).decode()
        
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=self.config.timeout),
            headers={
                'Authorization': f'Basic {encoded_credentials}',
                'Content-Type': 'application/json'
            }
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    async def _make_request(
        self,
        endpoint: str,
        params: Dict,
        retry_count: int = 0
    ) -> Dict:
        """
        Make HTTP request with retry logic
        
        Args:
            endpoint: API endpoint (ignored for Cloudant views, base_url is used directly)
            params: Query parameters
            retry_count: Current retry attempt
            
        Returns:
            Response JSON
            
        Raises:
            Exception: If all retries exhausted
        """
        await self.rate_limiter.acquire()
        
        # For Cloudant views, base_url already contains the full path
        url = self.config.base_url
        self.stats['total_requests'] += 1
        
        try:
            async with self.session.get(url, params=params) as response:
                # Handle rate limiting
                if response.status == 429:
                    retry_after = int(response.headers.get('Retry-After', 60))
                    logger.warning(f"Rate limited. Waiting {retry_after} seconds")
                    await asyncio.sleep(retry_after)
                    return await self._make_request(endpoint, params, retry_count)
                
                # Handle server errors with retry
                if response.status >= 500:
                    if retry_count < self.config.max_retries:
                        backoff = min(
                            self.config.initial_backoff * (2 ** retry_count),
                            self.config.max_backoff
                        )
                        logger.warning(
                            f"Server error {response.status}. "
                            f"Retry {retry_count + 1}/{self.config.max_retries} "
                            f"after {backoff}s"
                        )
                        self.stats['retries'] += 1
                        await asyncio.sleep(backoff)
                        return await self._make_request(endpoint, params, retry_count + 1)
                    else:
                        raise Exception(f"Max retries exceeded. Status: {response.status}")
                
                # Handle client errors (except 429)
                if response.status >= 400:
                    error_text = await response.text()
                    raise Exception(f"Client error {response.status}: {error_text}")
                
                # Success
                response.raise_for_status()
                self.stats['successful_requests'] += 1
                return await response.json()
                
        except asyncio.TimeoutError:
            if retry_count < self.config.max_retries:
                backoff = min(
                    self.config.initial_backoff * (2 ** retry_count),
                    self.config.max_backoff
                )
                logger.warning(
                    f"Request timeout. "
                    f"Retry {retry_count + 1}/{self.config.max_retries} "
                    f"after {backoff}s"
                )
                self.stats['retries'] += 1
                await asyncio.sleep(backoff)
                return await self._make_request(endpoint, params, retry_count + 1)
            else:
                self.stats['failed_requests'] += 1
                raise Exception("Request timeout after max retries")
        
        except Exception as e:
            self.stats['failed_requests'] += 1
            logger.error(f"Request failed: {str(e)}")
            raise
    
    async def fetch_page(
        self,
        page: int,
        start_date: str,
        end_date: str
    ) -> PageResponse:
        """
        Fetch a single page of data
        
        Args:
            page: Page number (1-indexed)
            start_date: Start date filter (YYYY-MM-DD)
            end_date: End date filter (YYYY-MM-DD)
            
        Returns:
            PageResponse object
        """
        # Cloudant view parameters
        # The view uses complex keys: [active, year, month, day, hour, minute, second]
        from datetime import datetime as dt
        import json as json_lib
        
        start_dt = dt.strptime(start_date, '%Y-%m-%d')
        end_dt = dt.strptime(end_date, '%Y-%m-%d')
        
        # Create complex keys for date range
        # Start key: [true, year, month, day, 0, 0, 0]
        start_key = [True, start_dt.year, start_dt.month, start_dt.day, 0, 0, 0]
        # End key: [true, year, month, day, 23, 59, 59]
        end_key = [True, end_dt.year, end_dt.month, end_dt.day, 23, 59, 59]
        
        # Calculate skip for pagination
        skip = (page - 1) * self.config.page_size
        
        params = {
            'startkey': json_lib.dumps(start_key),
            'endkey': json_lib.dumps(end_key),
            'limit': self.config.page_size,
            'skip': skip,
            'reduce': 'false',
            'include_docs': 'false'
        }
        
        response = await self._make_request('', params)
        
        # Parse Cloudant view response
        rows = response.get('rows', [])
        # Get key/value pairs instead of full documents (faster)
        data = [{'id': row.get('id'), 'key': row.get('key'), 'value': row.get('value')}
                for row in rows]
        total_records = response.get('total_rows', len(rows))
        total_pages = (total_records + self.config.page_size - 1) // self.config.page_size
        
        self.stats['records_retrieved'] += len(data)
        
        return PageResponse(
            data=data,
            page=page,
            total_pages=total_pages,
            total_records=total_records,
            has_next=page < total_pages
        )
    
    async def fetch_month(
        self,
        year: int,
        month: int,
        progress_callback: Optional[callable] = None
    ) -> AsyncGenerator[List[Dict], None]:
        """
        Fetch all data for a specific month
        
        Args:
            year: Year
            month: Month (1-12)
            progress_callback: Optional callback for progress updates
            
        Yields:
            Batches of records
        """
        # Calculate date range
        start_date = datetime(year, month, 1)
        if month == 12:
            end_date = datetime(year + 1, 1, 1) - timedelta(days=1)
        else:
            end_date = datetime(year, month + 1, 1) - timedelta(days=1)
        
        start_str = start_date.strftime('%Y-%m-%d')
        end_str = end_date.strftime('%Y-%m-%d')
        
        logger.info(f"Fetching data for {year}-{month:02d} ({start_str} to {end_str})")
        
        page = 1
        total_pages = None
        month_records = 0
        
        while True:
            try:
                response = await self.fetch_page(page, start_str, end_str)
                
                if total_pages is None:
                    total_pages = response.total_pages
                    logger.info(
                        f"Month {year}-{month:02d}: "
                        f"{response.total_records} records, "
                        f"{total_pages} pages"
                    )
                
                month_records += len(response.data)
                
                if progress_callback:
                    await progress_callback(year, month, page, total_pages, month_records)
                
                yield response.data
                
                if not response.has_next:
                    break
                
                page += 1
                
            except Exception as e:
                logger.error(f"Error fetching page {page} for {year}-{month:02d}: {str(e)}")
                raise
        
        logger.info(f"Completed {year}-{month:02d}: {month_records} records retrieved")
    
    def get_stats(self) -> Dict:
        """Get client statistics"""
        return self.stats.copy()


class CheckpointManager:
    """Manages progress checkpoints for resume capability"""
    
    def __init__(self, checkpoint_file: str = 'retrieval_checkpoint.json'):
        """
        Initialize checkpoint manager
        
        Args:
            checkpoint_file: Path to checkpoint file
        """
        self.checkpoint_file = Path(checkpoint_file)
        self.checkpoint = self._load_checkpoint()
    
    def _load_checkpoint(self) -> Dict:
        """Load checkpoint from file"""
        if self.checkpoint_file.exists():
            with open(self.checkpoint_file, 'r') as f:
                return json.load(f)
        return {'completed_months': [], 'in_progress': {}}
    
    def save_checkpoint(self):
        """Save checkpoint to file"""
        with open(self.checkpoint_file, 'w') as f:
            json.dump(self.checkpoint, f, indent=2)
    
    def mark_month_started(self, year: int, month: int):
        """Mark a month as started"""
        key = f"{year}-{month:02d}"
        self.checkpoint['in_progress'][key] = {
            'year': year,
            'month': month,
            'started_at': datetime.now().isoformat()
        }
        self.save_checkpoint()
    
    def mark_month_completed(self, year: int, month: int, record_count: int):
        """Mark a month as completed"""
        key = f"{year}-{month:02d}"
        self.checkpoint['completed_months'].append({
            'year': year,
            'month': month,
            'record_count': record_count,
            'completed_at': datetime.now().isoformat()
        })
        if key in self.checkpoint['in_progress']:
            del self.checkpoint['in_progress'][key]
        self.save_checkpoint()
    
    def is_month_completed(self, year: int, month: int) -> bool:
        """Check if a month is already completed"""
        return any(
            m['year'] == year and m['month'] == month
            for m in self.checkpoint['completed_months']
        )
    
    def get_completed_count(self) -> int:
        """Get total records from completed months"""
        return sum(m['record_count'] for m in self.checkpoint['completed_months'])
    
    def reset(self):
        """Reset checkpoint"""
        self.checkpoint = {'completed_months': [], 'in_progress': {}}
        self.save_checkpoint()


# Example usage
async def example_usage():
    """Example of how to use the API client"""
    
    # Configure API client
    config = APIConfig(
        base_url='https://api.example.com/v1',
        api_key='your-api-key-here',
        password='your-password-here',
        page_size=2500,
        rate_limit_per_second=10,
        concurrent_months=3
    )
    
    # Initialize checkpoint manager
    checkpoint = CheckpointManager()
    
    # Progress callback
    def progress_callback(year, month, page, total_pages, records):
        logger.info(
            f"Progress {year}-{month:02d}: "
            f"Page {page}/{total_pages}, "
            f"{records} records"
        )
    
    # Fetch data for a single month
    async with APIClient(config) as client:
        async for batch in client.fetch_month(2024, 1, progress_callback):
            # Process batch (write to file, database, etc.)
            logger.info(f"Processing batch of {len(batch)} records")
            # Your processing logic here
        
        # Get statistics
        stats = client.get_stats()
        logger.info(f"Statistics: {stats}")


if __name__ == '__main__':
    asyncio.run(example_usage())

# Made with Bob
