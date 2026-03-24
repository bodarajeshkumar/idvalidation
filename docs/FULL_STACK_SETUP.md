# Full Stack Data Retrieval System Setup Guide

## 🏗️ Architecture Overview

This is a complete full-stack application with:
- **Backend**: Flask REST API (Python)
- **Frontend**: React with Carbon Design System
- **Database**: Cloudant (IBM Cloud)

## 📋 Prerequisites

- Python 3.7+
- Node.js 16+ and npm
- Git

## 🚀 Quick Start

### Option 1: Automated Setup (Recommended)

```bash
# Make setup script executable
chmod +x setup_fullstack.sh

# Run setup
./setup_fullstack.sh
```

### Option 2: Manual Setup

#### Step 1: Backend Setup

```bash
# Install backend dependencies
cd backend
pip install -r requirements.txt

# Start backend server
python app.py
```

Backend will run on: `http://localhost:5000`

#### Step 2: Frontend Setup

```bash
# Install frontend dependencies
cd frontend
npm install

# Start frontend development server
npm start
```

Frontend will run on: `http://localhost:3000`

## 🔌 API Endpoints

### Backend REST API

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/health` | Health check |
| GET | `/api/status` | Get current retrieval status |
| POST | `/api/retrieve` | Start data retrieval |
| POST | `/api/reset` | Reset status (for testing) |

### API Request Examples

#### Start Retrieval
```bash
curl -X POST http://localhost:5000/api/retrieve \
  -H "Content-Type: application/json" \
  -d '{
    "start_date": "2023-01-01",
    "end_date": "2024-12-31"
  }'
```

#### Check Status
```bash
curl http://localhost:5000/api/status
```

#### Reset Status
```bash
curl -X POST http://localhost:5000/api/reset
```

## 🎨 Frontend Features

### Components Used from Carbon Design System

1. **DatePicker** - For start and end date selection
2. **Button** - Primary action button (disabled during processing)
3. **ProgressBar** - Shows retrieval progress
4. **Tag** - Status indicators (Not Started, Processing, Finished, Error)
5. **Tile** - Content containers
6. **InlineNotification** - Success/error messages
7. **Grid/Column** - Responsive layout
8. **Theme** - Dark theme (g100)

### Key Features

✅ **Date Range Selection** - Pick start and end dates
✅ **Status Monitoring** - Real-time status updates every 2 seconds
✅ **Progress Tracking** - Visual progress bar with percentage
✅ **Button State Management** - Disabled during processing
✅ **Error Handling** - Clear error messages
✅ **Responsive Design** - Works on all screen sizes
✅ **Dark Theme** - Carbon g100 theme

## 🔒 Security & Validation

### Backend Validations

1. ✅ Cannot start retrieval if already processing (409 Conflict)
2. ✅ Date format validation (YYYY-MM-DD)
3. ✅ Required field validation
4. ✅ CORS enabled for frontend communication

### Frontend Validations

1. ✅ Button disabled during processing
2. ✅ Date picker disabled during processing
3. ✅ Real-time status polling
4. ✅ Error notification display

## 📊 Status States

| Status | Description | Button State |
|--------|-------------|--------------|
| `not_started` | No retrieval in progress | Enabled |
| `processing` | Retrieval in progress | **Disabled** |
| `finished` | Retrieval completed | Enabled (with Reset) |
| `error` | Retrieval failed | Enabled (with Reset) |

## 🗂️ Project Structure

```
Dormant-ID/
├── backend/
│   ├── app.py                 # Flask REST API
│   └── requirements.txt       # Backend dependencies
├── frontend/
│   ├── public/
│   │   └── index.html
│   ├── src/
│   │   ├── App.js            # Main React component
│   │   ├── App.scss          # Styles
│   │   ├── index.js          # Entry point
│   │   └── index.scss        # Global styles
│   └── package.json          # Frontend dependencies
├── api_client.py             # Cloudant API client
├── orchestrator.py           # Data orchestration
├── .env                      # API credentials
└── output/                   # Retrieved data files
```

## 🔧 Configuration

### Backend Configuration

Edit `.env` file:
```env
API_BASE_URL=https://your-cloudant-url.com/...
API_KEY=your-api-key
API_PASSWORD=your-password
```

### Frontend Configuration

Create `frontend/.env`:
```env
REACT_APP_API_URL=http://localhost:5000
```

## 🧪 Testing

### Test Backend API

```bash
# Health check
curl http://localhost:5000/api/health

# Check status
curl http://localhost:5000/api/status

# Start retrieval (test)
curl -X POST http://localhost:5000/api/retrieve \
  -H "Content-Type: application/json" \
  -d '{"start_date": "2023-01-01", "end_date": "2023-01-31"}'
```

### Test Frontend

1. Open browser: `http://localhost:3000`
2. Select date range
3. Click "Start Retrieval"
4. Observe status updates
5. Verify button is disabled during processing

## 📈 Performance

### Expected Performance

- **Records**: 21,179,498 total
- **Time**: ~1.5-2 hours (balanced config)
- **Speed**: ~3,000-3,500 records/second
- **Concurrent**: 3 months processed in parallel

### Monitoring

The frontend automatically polls status every 2 seconds and displays:
- Current status
- Progress percentage
- Records retrieved
- Completed months
- Estimated completion

## 🐛 Troubleshooting

### Backend Issues

**Port already in use:**
```bash
# Kill process on port 5000
lsof -ti:5000 | xargs kill -9
```

**Module not found:**
```bash
cd backend
pip install -r requirements.txt
```

### Frontend Issues

**Port 3000 in use:**
```bash
# Kill process on port 3000
lsof -ti:3000 | xargs kill -9
```

**Dependencies not installed:**
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

### CORS Issues

If you see CORS errors:
1. Ensure backend is running on port 5000
2. Check `frontend/package.json` has `"proxy": "http://localhost:5000"`
3. Restart both servers

## 🚢 Production Deployment

### Backend (Flask)

```bash
# Use production WSGI server
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 backend.app:app
```

### Frontend (React)

```bash
cd frontend
npm run build
# Serve build/ directory with nginx or similar
```

## 📝 API Response Examples

### Status Response (Processing)
```json
{
  "status": "processing",
  "start_date": "2023-01-01",
  "end_date": "2024-12-31",
  "progress": {
    "total_records": 150000,
    "completed_months": 2,
    "total_months": 24,
    "percentage": 8.33
  },
  "start_time": "2026-03-23T12:00:00"
}
```

### Status Response (Finished)
```json
{
  "status": "finished",
  "start_date": "2023-01-01",
  "end_date": "2024-12-31",
  "stats": {
    "total_records": 21179498,
    "completed_months": 24,
    "total_months": 24,
    "duration_seconds": 5400,
    "records_per_second": 3922
  },
  "start_time": "2026-03-23T12:00:00",
  "end_time": "2026-03-23T13:30:00"
}
```

## 🎯 Key Requirements Met

✅ **Retrieval API** - POST `/api/retrieve` with start_date and end_date
✅ **Status API** - GET `/api/status` returns current status
✅ **Status States** - not_started, processing, finished, error
✅ **Button Disable** - Cannot invoke during processing
✅ **Date Range UI** - Carbon DatePicker components
✅ **Send Button** - Triggers retrieval API
✅ **Status Display** - Real-time status updates
✅ **Optimal Performance** - 3 concurrent months, 2500 records/page
✅ **Carbon Design** - Full Carbon Design System integration

## 📚 Additional Resources

- [Flask Documentation](https://flask.palletsprojects.com/)
- [React Documentation](https://react.dev/)
- [Carbon Design System](https://carbondesignsystem.com/)
- [Cloudant Documentation](https://cloud.ibm.com/docs/Cloudant)

---

**Built with ❤️ using Flask, React, and Carbon Design System**