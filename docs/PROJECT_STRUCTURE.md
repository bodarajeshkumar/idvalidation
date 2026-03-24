# Project Structure - Data Retrieval System

## 📁 Project Organization

This project has two main components:
1. **Standalone Data Retrieval Scripts** (original functionality)
2. **Full-Stack Web Application** (new web interface)

---

## 🔧 Core Data Retrieval Files (Required)

These files are **essential** for data retrieval functionality:

### Main Scripts
- **`api_client.py`** - Cloudant API client with authentication, pagination, rate limiting
- **`orchestrator.py`** - Manages concurrent month processing and data aggregation
- **`run.py`** - Simple runner script for standalone data retrieval
- **`requirements.txt`** - Python dependencies for data retrieval

### Monitoring & Testing
- **`test_connection.py`** - Tests API connection and estimates retrieval time
- **`monitor_progress.py`** - Real-time progress monitoring script
- **`check_status.sh`** - Quick status check script
- **`example_usage.py`** - Example usage patterns (7 different examples)
- **`monitoring.py`** - Advanced monitoring capabilities

### Configuration
- **`.env`** - API credentials (Cloudant URL, API key, password)

### Documentation
- **`HOW_TO_RUN.md`** - Original guide for standalone data retrieval
- **`RETRIEVAL_STATUS.md`** - Status report and monitoring guide
- **`large-dataset-retrieval-solution.md`** - Architecture and design details
- **`README.md`** - Original project README

---

## 🌐 Full-Stack Web Application Files

### Backend (Flask REST API)
```
backend/
├── app.py              # Flask REST API server
└── requirements.txt    # Backend-specific dependencies
```

**Purpose:** Provides REST APIs for the web frontend to trigger and monitor data retrieval

### Frontend (React + Carbon Design)
```
frontend/
├── public/
│   └── index.html      # HTML template
├── src/
│   ├── App.js          # Main React component
│   ├── App.scss        # Component styles
│   ├── index.js        # Entry point
│   └── index.scss      # Global styles
├── package.json        # Node dependencies
└── .env                # API URL configuration
```

**Purpose:** Web interface for users to start retrieval and monitor progress

### Setup & Deployment
- **`setup_fullstack.sh`** - Automated setup script
- **`start_servers.sh`** - Start both backend and frontend servers
- **`QUICKSTART.md`** - Quick start guide for web application
- **`FULL_STACK_SETUP.md`** - Detailed setup documentation

---

## 📊 Data & Output Files

### Generated During Retrieval
- **`output/`** - Directory containing retrieved data files
  - `data_2023_01.jsonl` - January 2023 data
  - `data_2023_02.jsonl` - February 2023 data
  - etc. (24 files total for 2023-2024)

### Progress Tracking
- **`retrieval_checkpoint.json`** - Progress checkpoint for resume capability
- **`retrieval_stats.json`** - Final statistics (created upon completion)
- **`backend.log`** - Backend server logs

---

## 🎯 Usage Scenarios

### Scenario 1: Standalone Data Retrieval (Command Line)

**Use these files:**
- `api_client.py`
- `orchestrator.py`
- `run.py`
- `requirements.txt`
- `.env`

**How to run:**
```bash
pip install -r requirements.txt
python run.py
```

**Monitoring:**
```bash
python monitor_progress.py
./check_status.sh
```

---

### Scenario 2: Web Application (Full Stack)

**Use these files:**
- All core data retrieval files (above)
- `backend/` directory
- `frontend/` directory
- Setup scripts

**How to run:**
```bash
# Terminal 1 - Backend
cd backend
python app.py

# Terminal 2 - Frontend
cd frontend
npm start
```

**Access:** http://localhost:3000

---

## 🔄 How They Work Together

```
┌─────────────────────────────────────────────────┐
│           Web Frontend (React)                  │
│  - Date range selection                         │
│  - Start/Stop buttons                           │
│  - Progress display                             │
└────────────────┬────────────────────────────────┘
                 │ HTTP Requests
                 ↓
┌─────────────────────────────────────────────────┐
│        Backend API (Flask)                      │
│  - /api/retrieve - Start retrieval              │
│  - /api/status - Get status                     │
└────────────────┬────────────────────────────────┘
                 │ Calls
                 ↓
┌─────────────────────────────────────────────────┐
│     Data Orchestrator (orchestrator.py)         │
│  - Manages concurrent month processing          │
│  - Coordinates API calls                        │
└────────────────┬────────────────────────────────┘
                 │ Uses
                 ↓
┌─────────────────────────────────────────────────┐
│       API Client (api_client.py)                │
│  - Handles authentication                       │
│  - Manages pagination                           │
│  - Rate limiting                                │
└────────────────┬────────────────────────────────┘
                 │ Connects to
                 ↓
┌─────────────────────────────────────────────────┐
│      Cloudant Database (IBM Cloud)              │
│  - 21,179,498 records                           │
│  - 2023-2024 data                               │
└─────────────────────────────────────────────────┘
```

---

## 📝 File Dependencies

### Core Dependencies
```
api_client.py
    ↓ imports
orchestrator.py
    ↓ uses
run.py (standalone)
    OR
backend/app.py (web application)
```

### All files depend on:
- `.env` - Configuration
- `requirements.txt` - Python packages

---

## 🗑️ Files You Can Safely Remove

**None of the current files should be removed** as they serve specific purposes:

- **Core files** - Required for data retrieval
- **Web app files** - Required for web interface
- **Documentation** - Helpful for understanding and using the system
- **Scripts** - Useful for setup and monitoring

---

## 💡 Recommendations

### For Standalone Use Only
If you only want command-line data retrieval:
- Keep: Core data retrieval files + monitoring scripts
- Optional: `backend/` and `frontend/` directories

### For Web Application Only
If you only want the web interface:
- Keep: All files (web app uses core retrieval files)
- Optional: `example_usage.py`, some documentation files

### For Both (Recommended)
- Keep: All files
- Benefit: Flexibility to use either interface

---

## 📚 Quick Reference

| Task | Files Needed | Command |
|------|--------------|---------|
| Test connection | `test_connection.py`, `.env` | `python test_connection.py` |
| Standalone retrieval | `run.py`, core files | `python run.py` |
| Monitor progress | `monitor_progress.py` | `python monitor_progress.py` |
| Check status | `check_status.sh` | `./check_status.sh` |
| Web application | All files | `./start_servers.sh` |

---

**Summary:** All current files serve a purpose. The project supports both standalone command-line usage and a modern web interface, giving you flexibility in how you interact with the data retrieval system.