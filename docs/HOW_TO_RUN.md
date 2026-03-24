# How to Run the Large Dataset Retrieval System

## Prerequisites

✅ Python 3.7+ installed  
✅ Dependencies installed (see below)  
✅ API credentials configured  

## Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

## Step 2: Configure Your API

You have **3 options** to configure the API:

### Option A: Edit `run.py` (Simplest)

Open [`run.py`](run.py) and update line 20:

```python
config = APIConfig(
    base_url='https://YOUR-ACTUAL-API-URL.com/v1',  # ⚠️ UPDATE THIS
    api_key='apikey-b37e7fba3c244a2abb665cdf019d9814',
    password='a8329b6ab9a6d64c2ed31fdb85a4a5a41a5d81a8',
    page_size=2500,
    rate_limit_per_second=10,
    concurrent_months=3
)
```

### Option B: Use Environment Variables (Recommended for Production)

```bash
export API_BASE_URL='https://your-api-url.com/v1'
export API_KEY='apikey-b37e7fba3c244a2abb665cdf019d9814'
export API_PASSWORD='a8329b6ab9a6d64c2ed31fdb85a4a5a41a5d81a8'
```

Then modify `run.py` to use:
```python
config = APIConfig(
    base_url=os.getenv('API_BASE_URL'),
    api_key=os.getenv('API_KEY'),
    password=os.getenv('API_PASSWORD'),
    ...
)
```

### Option C: Edit `orchestrator.py` Directly

Modify the `main()` function in [`orchestrator.py`](orchestrator.py:432-465) at line 436.

## Step 3: Run the Application

### Method 1: Using the Simple Runner (Recommended)

```bash
python run.py
```

### Method 2: Using the Main Orchestrator

```bash
python orchestrator.py
```

### Method 3: Using Example Scripts

```bash
python example_usage.py
```

This will show an interactive menu with 7 different examples.

### Method 4: Test with a Single Month First

Create a test script:

```python
import asyncio
from api_client import APIClient, APIConfig

async def test():
    config = APIConfig(
        base_url='https://your-api-url.com/v1',
        api_key='your-key',
        password='your-password',
        page_size=1000,
        rate_limit_per_second=5
    )
    
    async with APIClient(config) as client:
        total = 0
        async for batch in client.fetch_month(2024, 1):
            total += len(batch)
            print(f"Fetched {len(batch)} records (total: {total})")
        
        print(f"✅ Test complete! Total: {total} records")

asyncio.run(test())
```

## Step 4: Monitor Progress

The system will create several files:

- **`output/`** - Directory containing retrieved data files
  - `data_2023_01.jsonl` - January 2023 data
  - `data_2023_02.jsonl` - February 2023 data
  - etc.

- **`retrieval_checkpoint.json`** - Progress checkpoint (for resume capability)
- **`retrieval_stats.json`** - Final statistics
- **`retrieval.log`** - Detailed logs (if monitoring enabled)

## Configuration Options

### Performance Tuning

**For Faster Retrieval:**
```python
config = APIConfig(
    page_size=5000,              # Larger pages
    concurrent_months=5,         # More parallelism
    rate_limit_per_second=20     # Higher rate limit
)
```

**For Stability:**
```python
config = APIConfig(
    page_size=1000,              # Smaller pages
    concurrent_months=2,         # Less parallelism
    rate_limit_per_second=5,     # Lower rate limit
    max_retries=10               # More retries
)
```

### Output Formats

Change the `output_format` parameter:

```python
orchestrator = DataOrchestrator(
    config=config,
    output_format='jsonl'  # Options: 'jsonl', 'json', 'csv'
)
```

## Resume Capability

If the process is interrupted, simply run again:

```bash
python run.py
```

The system will automatically resume from the last checkpoint.

To start fresh:
```python
stats = await orchestrator.run(
    start_date='2023-01-01',
    end_date='2024-12-31',
    resume=False  # Set to False to start over
)
```

## Troubleshooting

### Issue: "Connection refused" or "API not responding"

**Solution:** Check your `base_url` in the configuration. Make sure it's the correct API endpoint.

### Issue: "Authentication failed"

**Solution:** Verify your API credentials in [`.env`](.env) or your configuration.

### Issue: "Rate limit exceeded"

**Solution:** Reduce `rate_limit_per_second` in your configuration:
```python
config = APIConfig(
    rate_limit_per_second=5,  # Lower this value
    ...
)
```

### Issue: "Memory error"

**Solution:** Use JSONL format (most memory efficient):
```python
orchestrator = DataOrchestrator(
    output_format='jsonl'  # Streaming format
)
```

### Issue: Process is too slow

**Solution:** Increase parallelism:
```python
config = APIConfig(
    page_size=5000,
    concurrent_months=5,
    rate_limit_per_second=20
)
```

## Expected Performance

For **21 million records**:

- **Conservative:** 12-15 minutes (~23,000 records/sec)
- **Balanced:** 8-10 minutes (~35,000 records/sec)
- **Aggressive:** 6-8 minutes (~45,000 records/sec)

*Actual performance depends on API response time and network latency.*

## Quick Commands Reference

```bash
# Install dependencies
pip install -r requirements.txt

# Run the main script
python run.py

# Run with examples
python example_usage.py

# Check logs (if monitoring enabled)
tail -f retrieval.log

# View checkpoint status
cat retrieval_checkpoint.json

# View final statistics
cat retrieval_stats.json
```

## Next Steps

1. ✅ Update API URL in `run.py`
2. ✅ Test with a single month first
3. ✅ Run full retrieval
4. ✅ Monitor progress
5. ✅ Check output files

## Need Help?

- See [`README.md`](README.md) for detailed documentation
- See [`example_usage.py`](example_usage.py) for 7 different usage examples
- See [`large-dataset-retrieval-solution.md`](large-dataset-retrieval-solution.md) for architecture details

---

**Important:** Always start with a small date range (e.g., one month) to test your configuration before running the full retrieval!