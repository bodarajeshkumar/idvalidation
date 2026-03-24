# 🚀 START HERE - Data Retrieval System

## Quick Start Guide

### Step 1: Start Backend Server

Open **Terminal 1** and run:
```bash
cd backend
python app.py
```

You should see:
```
================================================================================
Data Retrieval Backend API Server
================================================================================
Server starting on http://localhost:5001
 * Running on http://127.0.0.1:5001
```

✅ Backend is now running!

---

### Step 2: Start Frontend Server

Open **Terminal 2** (new terminal) and run:
```bash
cd frontend
npm install  # Only needed first time
npm start
```

The browser will automatically open to: **http://localhost:3000**

✅ Frontend is now running!

---

### Step 3: Use the Application

1. **Open Browser**: http://localhost:3000

2. **Select Date Range**:
   - Start Date: `2023-01-01`
   - End Date: `2024-12-31`

3. **Click "Start Retrieval"**:
   - Button will become disabled
   - Status changes to "Processing"
   - Progress bar shows real-time progress

4. **Monitor Progress**:
   - Updates every 2 seconds
   - Shows records retrieved
   - Shows completion percentage

5. **Wait for Completion**:
   - Takes approximately 1.5-2 hours
   - Status changes to "Finished"
   - Button re-enables
   - View final statistics

---

## 🔧 Troubleshooting

### Problem: Port 5001 already in use

**Solution:**
```bash
lsof -ti:5001 | xargs kill -9
```
Then restart the backend server.

### Problem: Port 3000 already in use

**Solution:**
```bash
lsof -ti:3000 | xargs kill -9
```
Then restart the frontend server.

### Problem: "Not Found" error

**Solution:**
- Make sure backend is running on port 5001
- Check: `curl http://localhost:5001/api/health`
- Should return: `{"status": "healthy", ...}`

### Problem: Frontend can't connect to backend

**Solution:**
1. Verify backend is running: `curl http://localhost:5001/api/status`
2. Check `frontend/.env` has: `REACT_APP_API_URL=http://localhost:5001`
3. Restart both servers

---

## 📊 What Happens During Retrieval

1. **Backend receives request** from frontend
2. **Validates date range** and checks if already processing
3. **Starts background thread** to run data retrieval
4. **Orchestrator processes 3 months** concurrently
5. **API client fetches data** from Cloudant (2,500 records/page)
6. **Data is written** to `output/` directory as JSONL files
7. **Progress updates** every 2 seconds via Status API
8. **Frontend polls** Status API and updates UI
9. **Completion** - Status changes to "Finished"

---

## 📁 Output Files

Data is saved in: `output/` directory

```
output/
├── data_2023_01.jsonl  (January 2023)
├── data_2023_02.jsonl  (February 2023)
├── data_2023_03.jsonl  (March 2023)
├── ...
└── data_2024_12.jsonl  (December 2024)
```

Total: 24 files, ~21.18 million records, ~15-20 GB

---

## 🧪 Test the APIs

### Health Check
```bash
curl http://localhost:5001/api/health
```

### Get Status
```bash
curl http://localhost:5001/api/status
```

### Start Retrieval (via API)
```bash
curl -X POST http://localhost:5001/api/retrieve \
  -H "Content-Type: application/json" \
  -d '{"start_date": "2023-01-01", "end_date": "2023-01-31"}'
```

### Reset Status
```bash
curl -X POST http://localhost:5001/api/reset
```

---

## 🎯 Key Features

### Backend (Flask REST API)
- ✅ `/api/retrieve` - Start data retrieval
- ✅ `/api/status` - Get current status
- ✅ `/api/health` - Health check
- ✅ `/api/reset` - Reset status

### Frontend (React + Carbon Design)
- ✅ Date range pickers
- ✅ Start retrieval button
- ✅ Real-time status updates
- ✅ Progress bar
- ✅ **Button disabled during processing**
- ✅ Error notifications
- ✅ Professional IBM Carbon design

---

## 📝 Status States

| Status | Description | Button State |
|--------|-------------|--------------|
| `not_started` | Ready to start | ✅ Enabled |
| `processing` | Retrieval in progress | ❌ **Disabled** |
| `finished` | Completed successfully | ✅ Enabled |
| `error` | Failed with error | ✅ Enabled |

**Important:** You cannot start a new retrieval while one is already processing!

---

## 📚 Additional Documentation

- [`QUICKSTART.md`](QUICKSTART.md) - Detailed quick start
- [`FULL_STACK_SETUP.md`](FULL_STACK_SETUP.md) - Complete setup guide
- [`PROJECT_STRUCTURE.md`](PROJECT_STRUCTURE.md) - File organization
- [`RETRIEVAL_STATUS.md`](RETRIEVAL_STATUS.md) - Monitoring guide

---

## 💡 Tips

1. **First Time Setup**: Run `npm install` in frontend directory
2. **Keep Terminals Open**: Don't close the terminal windows
3. **Monitor Progress**: Watch the progress bar in the browser
4. **Check Logs**: Backend logs show detailed information
5. **Resume Capability**: If interrupted, restart and it will resume

---

## ⚡ Quick Commands

```bash
# Start backend
cd backend && python app.py

# Start frontend (new terminal)
cd frontend && npm start

# Kill backend
lsof -ti:5001 | xargs kill -9

# Kill frontend
lsof -ti:3000 | xargs kill -9

# Test API
curl http://localhost:5001/api/health
```

---

## 🎉 You're Ready!

1. ✅ Backend running on port 5001
2. ✅ Frontend running on port 3000
3. ✅ Open http://localhost:3000
4. ✅ Start retrieving data!

**Need help?** Check the troubleshooting section above or refer to the detailed documentation.