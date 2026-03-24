# How to Stop Data Retrieval

## Overview
The data retrieval system now supports **graceful cancellation** during processing. You can stop the retrieval at any time, and the system will:
- Complete the current batch being processed
- Save all retrieved data up to that point
- Update the checkpoint file for potential resume
- Mark the status as "cancelled"

---

## Methods to Stop Retrieval

### Method 1: Using the Web Interface (Recommended)

1. **Open the web interface** at http://localhost:3000
2. While retrieval is in progress, you'll see a **"Stop Retrieval"** button (red/danger button)
3. Click the **"Stop Retrieval"** button
4. The system will:
   - Display a notification: "Cancellation requested. Retrieval will stop after current batch."
   - Continue processing the current batch
   - Stop before starting new months
   - Update status to "Cancelled"

**Visual Indicators:**
- Status tag changes to **"Cancelled"** (magenta color with stop icon)
- A message appears: "Retrieval was cancelled by user"
- The "Reset" button becomes available to clear the status

---

### Method 2: Using API Directly

If you prefer to use the API directly:

```bash
curl -X POST http://localhost:5001/api/stop
```

**Response:**
```json
{
  "message": "Cancellation requested. Retrieval will stop after current batch.",
  "status": "cancelling"
}
```

---

### Method 3: Stopping the Backend Server

**Emergency Stop (Not Recommended):**
- Press `Ctrl+C` in the terminal running the backend
- This will immediately terminate the process
- Data may be incomplete for the current batch
- Checkpoint file will reflect the last completed batch

---

## What Happens When You Stop?

### 1. **Immediate Actions**
- Cancellation flag is set
- Current batch completes processing
- No new months are started

### 2. **Data Preservation**
- All completed months are saved in `output/` directory
- Checkpoint file (`retrieval_checkpoint.json`) is updated
- Partial data from the current batch is saved

### 3. **Status Updates**
- Backend status changes to `"cancelled"`
- Frontend displays cancelled state
- Error message: "Retrieval cancelled by user"

### 4. **Resume Capability**
- You can resume from where you stopped
- The system will skip completed months
- Only remaining months will be processed

---

## Resuming After Cancellation

### Option 1: Reset and Start Fresh
1. Click the **"Reset"** button in the web interface
2. Select new date range (or keep the same)
3. Click **"Start Retrieval"** again
4. System will skip already completed months automatically

### Option 2: Continue from Checkpoint
The system automatically resumes from the checkpoint:
- Completed months are skipped
- In-progress months are restarted
- New months are processed normally

---

## Current Retrieval Status

Based on your terminal output, here's what's happening:

```
Current Status: Processing
Progress: 0 / 2 months
Records Retrieved: 364,092
Retrieval Progress: 0.00% complete
```

**Analysis:**
- **2 months** are being processed (2020-02 and 2020-03)
- **364,092 records** have been retrieved so far
- Progress shows 0% because months aren't fully completed yet
- The system is actively fetching data (you can see page progress in logs)

**To Stop Now:**
1. Go to http://localhost:3000
2. Click the red **"Stop Retrieval"** button
3. Wait for current batch to complete (~2-5 seconds)
4. Status will change to "Cancelled"

---

## Technical Details

### Backend Implementation
- **Cancellation Flag:** Global `cancellation_flag` variable
- **Check Points:** Checked before starting each month and during batch processing
- **Graceful Shutdown:** Completes current batch before stopping

### Frontend Implementation
- **Stop Button:** Appears only when status is "processing"
- **API Call:** `POST /api/stop`
- **Status Polling:** Updates every 2 seconds to reflect cancellation

### Orchestrator Behavior
- **Month Processing:** Checks cancellation before each month
- **Batch Processing:** Checks cancellation during data fetching
- **Cleanup:** Saves checkpoint and closes file handles

---

## Troubleshooting

### Stop Button Not Appearing
- **Check:** Is the status "processing"?
- **Solution:** Refresh the page (F5)

### Cancellation Takes Too Long
- **Reason:** Waiting for current batch to complete
- **Normal:** Can take 2-10 seconds depending on batch size
- **Action:** Be patient, it will stop gracefully

### Status Stuck on "Processing"
- **Check:** Backend terminal for errors
- **Solution:** Restart backend server
- **Emergency:** Press Ctrl+C in backend terminal

### Data Loss Concerns
- **No Data Loss:** All completed batches are saved
- **Checkpoint:** System tracks progress automatically
- **Resume:** Can continue from where you stopped

---

## Best Practices

1. **Use Web Interface:** Most user-friendly method
2. **Wait for Confirmation:** Don't force-quit immediately
3. **Check Logs:** Monitor backend terminal for progress
4. **Resume Capability:** You can always continue later
5. **Reset When Done:** Clear status before starting new retrieval

---

## Example Workflow

### Scenario: Stop and Resume

1. **Start Retrieval:**
   - Date range: 2020-01-01 to 2020-12-31
   - 12 months to process

2. **Stop After 5 Months:**
   - Click "Stop Retrieval"
   - Wait for cancellation
   - Status: "Cancelled"
   - Data: 5 months saved in `output/`

3. **Resume Later:**
   - Click "Reset"
   - Same date range: 2020-01-01 to 2020-12-31
   - Click "Start Retrieval"
   - System processes remaining 7 months only

---

## Summary

✅ **Stop Retrieval:** Click the red "Stop Retrieval" button in the web interface
✅ **Graceful:** Completes current batch before stopping
✅ **Safe:** All data is preserved
✅ **Resumable:** Can continue from checkpoint
✅ **Fast:** Stops within seconds

**Current Action Required:**
If you want to stop the current retrieval (364,092 records, 2 months):
1. Open http://localhost:3000
2. Click "Stop Retrieval"
3. Wait for cancellation confirmation

---

Made with Bob 🤖