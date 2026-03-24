# ⚠️ IMPORTANT - How to Access the Application

## 🚫 Common Mistake

**DON'T** open http://localhost:5001 in your browser!

That's the **backend API server** - it only responds to API calls, not web pages.
That's why you see "Not Found" error.

## ✅ Correct Way to Use

### You Need TWO Servers Running:

```
┌─────────────────────────────────────┐
│  Terminal 1: Backend (Port 5001)   │  ← API Server (already running)
│  cd backend && python app.py       │
└─────────────────────────────────────┘
                 ↑
                 │ API Calls
                 │
┌─────────────────────────────────────┐
│  Terminal 2: Frontend (Port 3000)  │  ← Web Interface (YOU NEED TO START THIS)
│  cd frontend && npm start          │
└─────────────────────────────────────┘
                 ↓
         Open in Browser:
      http://localhost:3000
```

## 📋 Step-by-Step Instructions

### Step 1: Backend is Already Running ✅

Your Terminal 2 shows backend is running on port 5001.
**Keep this terminal open!**

### Step 2: Start Frontend (NEW Terminal)

Open a **NEW terminal window** and run:

```bash
cd /Users/kesojusaipriya/Dormant-ID/frontend
npm install  # First time only
npm start
```

### Step 3: Browser Will Auto-Open

The browser will automatically open to: **http://localhost:3000**

If it doesn't, manually open: **http://localhost:3000**

## 🎯 What You'll See

At **http://localhost:3000** you'll see:

```
┌────────────────────────────────────────────┐
│  Data Retrieval System                     │
│                                            │
│  Current Status: [Not Started]             │
│                                            │
│  Date Range Selection:                     │
│  Start Date: [2023-01-01]                  │
│  End Date:   [2024-12-31]                  │
│                                            │
│  [Start Retrieval Button]                  │
└────────────────────────────────────────────┘
```

## 🔍 Understanding the Ports

| Port | Purpose | Access Method |
|------|---------|---------------|
| **5001** | Backend API | **DON'T** open in browser - API only |
| **3000** | Frontend Web | **DO** open in browser - User interface |

## 🧪 Test Backend API (Optional)

If you want to test the backend API directly, use curl:

```bash
# Health check
curl http://localhost:5001/api/health

# Get status
curl http://localhost:5001/api/status
```

**But for normal use, just access the frontend at port 3000!**

## ⚡ Quick Commands

```bash
# In NEW terminal - Start Frontend
cd frontend
npm install  # First time only
npm start

# Browser will open automatically to:
# http://localhost:3000
```

## 🐛 Troubleshooting

### "Port 5001 already in use"

The backend is already running! That's good.
Just start the frontend in a NEW terminal.

### "Port 3000 already in use"

```bash
lsof -ti:3000 | xargs kill -9
cd frontend
npm start
```

### Still seeing "Not Found"?

You're probably still trying to access port 5001.
**Use port 3000 instead:** http://localhost:3000

---

## 📝 Summary

1. ✅ Backend running on port 5001 (API server - already done)
2. ⏳ Frontend needs to run on port 3000 (Web interface - YOU NEED TO DO THIS)
3. 🌐 Open browser to **http://localhost:3000** (NOT 5001!)

**Next Step:** Open a new terminal and run:
```bash
cd frontend && npm start