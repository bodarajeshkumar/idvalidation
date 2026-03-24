# 🚀 Quick Start Guide - Data Retrieval System

## Overview

A full-stack web application for retrieving 21+ million records from Cloudant database with real-time progress monitoring.

**Tech Stack:**
- Backend: Flask (Python) REST API
- Frontend: React + Carbon Design System
- Database: Cloudant (IBM Cloud)

---

## ⚡ Quick Start (2 Steps)

### Step 1: Install Dependencies

```bash
# Backend
cd backend
pip install -r requirements.txt
cd ..

# Frontend
cd frontend
npm install
cd ..
```

### Step 2: Start Servers

**Terminal 1 - Backend:**
```bash
cd backend
python app.py
```
Backend runs on: **http://localhost:5001**

**Terminal 2 - Frontend:**
```bash
cd frontend
npm start
```
Frontend runs on: **http://localhost:3000**

**Open browser:** http://localhost:3000

---

## 🎯 How to Use

1. **Select Date Range**
   - Start Date: e.g., 2023-01-01
   - End Date: e.g., 2024-12-31

2. **Click "Start Retrieval"**
   - Button will be disabled during processing
   - Status updates every 2 seconds

3. **Monitor Progress**
   - Real-time progress bar
   - Records retrieved count
   - Completion percentage

4. **Wait for Completion**
   - Status changes to "Finished"
   - View final statistics
   - Button re-enables

---

## 📋 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/health` | Health check |
| GET | `/api/status` | Get current status |
| POST | `/api/retrieve` | Start retrieval |
| POST | `/api/reset` | Reset status |

### Test API

```bash
# Health check
curl http://localhost:5001/api/health

# Get status
curl http://localhost:5001/api/status

# Start retrieval
curl -X POST http://localhost:5001/api/retrieve \
  -H "Content-Type: application/json" \
  -d '{"start_date": "2023-01-01", "end_date": "2023-01-31"}'
```

---

## ✅ Key Features

### Backend Features
✅ **Retrieval API** - Start data retrieval with date range
✅ **Status API** - Real-time status monitoring
✅ **State Management** - not_started → processing → finished
✅ **Validation** - Cannot start if already processing
✅ **Error Handling** - Comprehensive error messages
✅ **CORS Enabled** - Frontend communication

### Frontend Features
✅ **Carbon Design System** - Professional IBM design
✅ **Date Pickers** - Easy date range selection
✅ **Status Display** - Real-time updates (2s polling)
✅ **Progress Bar** - Visual progress tracking
✅ **Button States** - Disabled during processing
✅ **Notifications** - Success/error messages
✅ **Responsive** - Works on all screen sizes
✅ **Dark Theme** - Carbon g100 theme

---

## 🔒 Status States

| Status | Description | Button |
|--------|-------------|--------|
| `not_started` | Ready to start | ✅ Enabled |
| `processing` | Retrieval in progress | ❌ Disabled |
| `finished` | Completed successfully | ✅ Enabled |
| `error` | Failed with error | ✅ Enabled |

**Important:** The "Start Retrieval" button is automatically disabled when status is `processing` and cannot be clicked until the process finishes.

---

## 📊 Expected Performance

- **Total Records:** 21,179,498
- **Estimated Time:** 1.5-2 hours
- **Speed:** ~3,000-3,500 records/second
- **Concurrent Processing:** 3 months in parallel
- **Output:** JSONL files in `output/` directory

---

## 🗂️ Project Structure

```
Dormant-ID/
├── backend/
│   ├── app.py              # Flask REST API
│   └── requirements.txt    # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── App.js         # Main React component
│   │   ├── App.scss       # Styles
│   │   └── index.js       # Entry point
│   ├── package.json       # Node dependencies
│   └── .env               # API URL config
├── api_client.py          # Cloudant client
├── orchestrator.py        # Data orchestration
├── .env                   # API credentials
└── output/                # Retrieved data
```

---

## 🐛 Troubleshooting

### Backend won't start
```bash
# Check if port 5001 is in use
lsof -ti:5001 | xargs kill -9

# Reinstall dependencies
cd backend
pip install -r requirements.txt
```

### Frontend won't start
```bash
# Check if port 3000 is in use
lsof -ti:3000 | xargs kill -9

# Reinstall dependencies
cd frontend
rm -rf node_modules package-lock.json
npm install
```

### CORS errors
- Ensure backend is running on port 5001
- Check `frontend/.env` has correct API URL
- Restart both servers

### Button not working
- Check browser console for errors
- Verify backend is running: `curl http://localhost:5001/api/health`
- Check status: `curl http://localhost:5001/api/status`

---

## 📸 Screenshots

### Main Interface
- Date range pickers (Carbon DatePicker)
- Status display with tags
- Progress bar with percentage
- Start Retrieval button

### Status States
- **Not Started:** Gray tag, button enabled
- **Processing:** Blue tag with spinner, button disabled
- **Finished:** Green tag with checkmark, button enabled
- **Error:** Red tag with error icon, button enabled

---

## 🔧 Configuration

### Backend (.env in root)
```env
API_BASE_URL=https://your-cloudant-url.com/...
API_KEY=your-api-key
API_PASSWORD=your-password
```

### Frontend (frontend/.env)
```env
REACT_APP_API_URL=http://localhost:5001
```

---

## 📝 Example Usage Flow

1. User opens http://localhost:3000
2. Sees "Not Started" status
3. Selects dates: 2023-01-01 to 2024-12-31
4. Clicks "Start Retrieval"
5. Button becomes disabled
6. Status changes to "Processing"
7. Progress bar shows 0% → 100%
8. Records count increases in real-time
9. After ~2 hours, status changes to "Finished"
10. Button re-enables
11. User can view final statistics

---

## 🎨 Carbon Components Used

- `DatePicker` & `DatePickerInput` - Date selection
- `Button` - Primary actions
- `ProgressBar` - Progress visualization
- `Tag` - Status indicators
- `Tile` - Content containers
- `InlineNotification` - Messages
- `Grid` & `Column` - Layout
- `Theme` - Dark theme (g100)

---

## 📚 Additional Documentation

- [`FULL_STACK_SETUP.md`](FULL_STACK_SETUP.md) - Detailed setup guide
- [`HOW_TO_RUN.md`](HOW_TO_RUN.md) - Original data retrieval guide
- [`RETRIEVAL_STATUS.md`](RETRIEVAL_STATUS.md) - Status report

---

## ✨ Key Requirements Met

✅ **Task 1: Backend APIs**
- ✅ Retrieval API with start_date and end_date
- ✅ Status API with states (not_started, processing, finished)
- ✅ Cannot invoke during processing (409 Conflict)
- ✅ Optimal retrieval time (~2 hours for 21M records)

✅ **Task 2: Frontend**
- ✅ Simple UI with Carbon Design System
- ✅ Date range pickers for start and end dates
- ✅ Send button to trigger Retrieval API
- ✅ Status display from Status API
- ✅ Button disabled until status is Finished

---

**Built with ❤️ using Flask, React, and Carbon Design System**