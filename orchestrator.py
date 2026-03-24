"""
Orchestrator for Month-wise Data Retrieval
Manages concurrent month processing and data aggregation
"""

import asyncio
import logging
from typing import List, Dict, Optional, Callable
from datetime import datetime, timedelta
from pathlib import Path
import json
import os
from dataclasses import dataclass, asdict
from collections import defaultdict

from api_client import APIClient, APIConfig, CheckpointManager

logger = logging.getLogger(__name__)


@dataclass
class MonthRange:
    """Represents a month to process"""
    year: int
    month: int
    
    def __str__(self):
        return f"{self.year}-{self.month:02d}"
    
    def to_dict(self):
        return {'year': self.year, 'month': self.month}


@dataclass
class RetrievalStats:
    """Statistics for the entire retrieval process"""
    total_months: int = 0
    completed_months: int = 0
    failed_months: int = 0
    total_records: int = 0
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    duration_seconds: float = 0.0
    months_per_minute: float = 0.0
    records_per_second: float = 0.0


class DataWriter:
    """Handles writing retrieved data to storage"""
    
    def __init__(self, output_dir: str = 'output', format: str = 'jsonl'):
        """
        Initialize data writer
        
        Args:
            output_dir: Directory to write output files
            format: Output format ('jsonl', 'json', 'csv')
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.format = format
        self.file_handles = {}
    
    def get_file_path(self, year: int, month: int) -> Path:
        """Get output file path for a month"""
        filename = f"data_{year}_{month:02d}.{self.format}"
        return self.output_dir / filename
    
    async def write_batch(self, year: int, month: int, records: List[Dict]):
        """
        Write a batch of records to file
        
        Args:
            year: Year
            month: Month
            records: List of records to write
        """
        file_path = self.get_file_path(year, month)
        
        if self.format == 'jsonl':
            # JSON Lines format - one record per line
            with open(file_path, 'a') as f:
                for record in records:
                    f.write(json.dumps(record) + '\n')
        
        elif self.format == 'json':
            # Standard JSON array format
            existing_data = []
            if file_path.exists():
                with open(file_path, 'r') as f:
                    existing_data = json.load(f)
            
            existing_data.extend(records)
            
            with open(file_path, 'w') as f:
                json.dump(existing_data, f, indent=2)
        
        elif self.format == 'csv':
            # CSV format (requires pandas or csv module)
            import csv
            
            if not records:
                return
            
            # Get all unique keys from records
            fieldnames = set()
            for record in records:
                fieldnames.update(record.keys())
            fieldnames = sorted(fieldnames)
            
            file_exists = file_path.exists()
            
            with open(file_path, 'a', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                
                if not file_exists:
                    writer.writeheader()
                
                writer.writerows(records)
    
    def close_all(self):
        """Close all open file handles"""
        for handle in self.file_handles.values():
            handle.close()
        self.file_handles.clear()


class ProgressTracker:
    """Tracks and displays progress of data retrieval"""
    
    def __init__(self, total_months: int):
        """
        Initialize progress tracker
        
        Args:
            total_months: Total number of months to process
        """
        self.total_months = total_months
        self.completed_months = 0
        self.month_progress = defaultdict(dict)
        self.start_time = datetime.now()
        self.lock = asyncio.Lock()
    
    async def update_month_progress(
        self,
        year: int,
        month: int,
        page: int,
        total_pages: int,
        records: int
    ):
        """Update progress for a specific month"""
        async with self.lock:
            key = f"{year}-{month:02d}"
            self.month_progress[key] = {
                'page': page,
                'total_pages': total_pages,
                'records': records,
                'progress_pct': (page / total_pages * 100) if total_pages > 0 else 0
            }
            self._display_progress()
    
    async def mark_month_completed(self, year: int, month: int):
        """Mark a month as completed"""
        async with self.lock:
            self.completed_months += 1
            key = f"{year}-{month:02d}"
            if key in self.month_progress:
                del self.month_progress[key]
            self._display_progress()
    
    def _display_progress(self):
        """Display current progress"""
        elapsed = (datetime.now() - self.start_time).total_seconds()
        elapsed_min = elapsed / 60
        
        # Overall progress
        overall_pct = (self.completed_months / self.total_months * 100) if self.total_months > 0 else 0
        
        logger.info(
            f"Overall Progress: {self.completed_months}/{self.total_months} months "
            f"({overall_pct:.1f}%) | Elapsed: {elapsed_min:.1f}m"
        )
        
        # Active months progress
        if self.month_progress:
            for month_key, progress in sorted(self.month_progress.items()):
                logger.info(
                    f"  {month_key}: Page {progress['page']}/{progress['total_pages']} "
                    f"({progress['progress_pct']:.1f}%) - {progress['records']} records"
                )
    
    def get_eta(self) -> Optional[str]:
        """Calculate estimated time to completion"""
        if self.completed_months == 0:
            return None
        
        elapsed = (datetime.now() - self.start_time).total_seconds()
        rate = self.completed_months / elapsed  # months per second
        remaining = self.total_months - self.completed_months
        eta_seconds = remaining / rate if rate > 0 else 0
        
        eta_time = datetime.now() + timedelta(seconds=eta_seconds)
        return eta_time.strftime('%Y-%m-%d %H:%M:%S')


class DataOrchestrator:
    """Orchestrates the entire data retrieval process"""
    
    def __init__(
        self,
        config: APIConfig,
        output_dir: str = 'output',
        output_format: str = 'jsonl',
        checkpoint_file: str = 'retrieval_checkpoint.json'
    ):
        """
        Initialize orchestrator
        
        Args:
            config: API configuration
            output_dir: Directory for output files
            output_format: Output file format
            checkpoint_file: Checkpoint file path
        """
        self.config = config
        self.writer = DataWriter(output_dir, output_format)
        self.checkpoint = CheckpointManager(checkpoint_file)
        self.stats = RetrievalStats()
        self.cancellation_callback = None
    
    def set_cancellation_callback(self, callback: Callable[[], bool]):
        """
        Set a callback function to check for cancellation
        
        Args:
            callback: Function that returns True if cancellation is requested
        """
        self.cancellation_callback = callback
    
    def is_cancelled(self) -> bool:
        """Check if cancellation has been requested"""
        if self.cancellation_callback:
            return self.cancellation_callback()
        return False
    
    def generate_month_ranges(
        self,
        start_date: str,
        end_date: str
    ) -> List[MonthRange]:
        """
        Generate list of months to process
        
        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            
        Returns:
            List of MonthRange objects
        """
        start = datetime.strptime(start_date, '%Y-%m-%d')
        end = datetime.strptime(end_date, '%Y-%m-%d')
        
        months = []
        current = start.replace(day=1)
        
        while current <= end:
            # Skip if already completed
            if not self.checkpoint.is_month_completed(current.year, current.month):
                months.append(MonthRange(current.year, current.month))
            else:
                logger.info(f"Skipping {current.year}-{current.month:02d} (already completed)")
            
            # Move to next month
            if current.month == 12:
                current = current.replace(year=current.year + 1, month=1)
            else:
                current = current.replace(month=current.month + 1)
        
        return months
    
    async def process_month(
        self,
        client: APIClient,
        month: MonthRange,
        progress_tracker: ProgressTracker
    ) -> Dict:
        """
        Process a single month
        
        Args:
            client: API client
            month: Month to process
            progress_tracker: Progress tracker
            
        Returns:
            Dictionary with processing results
        """
        month_key = str(month)
        logger.info(f"Starting month: {month_key}")
        
        # Check for cancellation before starting
        if self.is_cancelled():
            logger.info(f"Cancellation detected, skipping month: {month_key}")
            return {
                'month': month_key,
                'status': 'cancelled',
                'record_count': 0
            }
        
        self.checkpoint.mark_month_started(month.year, month.month)
        
        record_count = 0
        
        try:
            # Progress callback
            async def progress_callback(year, m, page, total_pages, records):
                await progress_tracker.update_month_progress(
                    year, m, page, total_pages, records
                )
            
            # Fetch and write data
            async for batch in client.fetch_month(
                month.year,
                month.month,
                progress_callback
            ):
                # Check for cancellation during processing
                if self.is_cancelled():
                    logger.info(f"Cancellation detected during processing of {month_key}")
                    return {
                        'month': month_key,
                        'status': 'cancelled',
                        'record_count': record_count
                    }
                
                await self.writer.write_batch(month.year, month.month, batch)
                record_count += len(batch)
            
            # Mark as completed
            self.checkpoint.mark_month_completed(month.year, month.month, record_count)
            await progress_tracker.mark_month_completed(month.year, month.month)
            
            logger.info(f"Completed month: {month_key} ({record_count} records)")
            
            return {
                'month': month_key,
                'status': 'success',
                'record_count': record_count
            }
            
        except Exception as e:
            logger.error(f"Failed to process month {month_key}: {str(e)}")
            return {
                'month': month_key,
                'status': 'failed',
                'error': str(e),
                'record_count': record_count
            }
    
    async def run(
        self,
        start_date: str,
        end_date: str,
        resume: bool = True
    ) -> RetrievalStats:
        """
        Run the complete data retrieval process
        
        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            resume: Whether to resume from checkpoint
            
        Returns:
            RetrievalStats object with results
        """
        if not resume:
            self.checkpoint.reset()
        
        # Generate month ranges
        months = self.generate_month_ranges(start_date, end_date)
        
        if not months:
            logger.info("No months to process (all completed)")
            return self.stats
        
        self.stats.total_months = len(months)
        self.stats.start_time = datetime.now().isoformat()
        
        logger.info(f"Starting retrieval: {len(months)} months to process")
        logger.info(f"Concurrent months: {self.config.concurrent_months}")
        logger.info(f"Page size: {self.config.page_size}")
        
        # Initialize progress tracker
        progress_tracker = ProgressTracker(len(months))
        
        # Process months with controlled concurrency
        async with APIClient(self.config) as client:
            # Create semaphore to limit concurrent months
            semaphore = asyncio.Semaphore(self.config.concurrent_months)
            
            async def process_with_semaphore(month: MonthRange):
                async with semaphore:
                    return await self.process_month(client, month, progress_tracker)
            
            # Process all months
            results = await asyncio.gather(
                *[process_with_semaphore(month) for month in months],
                return_exceptions=True
            )
            
            # Aggregate results
            for result in results:
                if isinstance(result, Exception):
                    self.stats.failed_months += 1
                    logger.error(f"Month processing exception: {str(result)}")
                elif result['status'] == 'success':
                    self.stats.completed_months += 1
                    self.stats.total_records += result['record_count']
                else:
                    self.stats.failed_months += 1
            
            # Get API client stats
            api_stats = client.get_stats()
            logger.info(f"API Statistics: {api_stats}")
        
        # Finalize stats
        self.stats.end_time = datetime.now().isoformat()
        start_dt = datetime.fromisoformat(self.stats.start_time)
        end_dt = datetime.fromisoformat(self.stats.end_time)
        self.stats.duration_seconds = (end_dt - start_dt).total_seconds()
        
        if self.stats.duration_seconds > 0:
            self.stats.months_per_minute = (
                self.stats.completed_months / (self.stats.duration_seconds / 60)
            )
            self.stats.records_per_second = (
                self.stats.total_records / self.stats.duration_seconds
            )
        
        # Log final summary
        self._log_summary()
        
        # Close writer
        self.writer.close_all()
        
        return self.stats
    
    def _log_summary(self):
        """Log final summary"""
        logger.info("=" * 80)
        logger.info("RETRIEVAL COMPLETE")
        logger.info("=" * 80)
        logger.info(f"Total months: {self.stats.total_months}")
        logger.info(f"Completed: {self.stats.completed_months}")
        logger.info(f"Failed: {self.stats.failed_months}")
        logger.info(f"Total records: {self.stats.total_records:,}")
        logger.info(f"Duration: {self.stats.duration_seconds:.1f} seconds")
        logger.info(f"Rate: {self.stats.records_per_second:.1f} records/second")
        logger.info(f"Rate: {self.stats.months_per_minute:.2f} months/minute")
        logger.info("=" * 80)


# Example usage
async def main():
    """Main execution function"""
    
    # Configure API
    # Load from .env file
    env_vars = {}
    try:
        with open('.env', 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    env_vars[key] = value
    except FileNotFoundError:
        print("Error: .env file not found!")
        return
    
    config = APIConfig(
        base_url=env_vars.get('API_BASE_URL', ''),
        api_key=env_vars.get('API_KEY', ''),
        password=env_vars.get('API_PASSWORD', ''),
        page_size=2500,
        rate_limit_per_second=10,
        concurrent_months=3,
        max_retries=5
    )
    
    # Create orchestrator
    orchestrator = DataOrchestrator(
        config=config,
        output_dir='output',
        output_format='jsonl',
        checkpoint_file='retrieval_checkpoint.json'
    )
    
    # Run retrieval
    stats = await orchestrator.run(
        start_date='2023-01-01',
        end_date='2024-12-31',
        resume=True  # Resume from checkpoint if available
    )
    
    # Save stats
    with open('retrieval_stats.json', 'w') as f:
        json.dump(asdict(stats), f, indent=2)
    
    logger.info("Retrieval process completed!")


if __name__ == '__main__':
    asyncio.run(main())

# Made with Bob
