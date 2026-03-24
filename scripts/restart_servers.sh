#!/bin/bash

# Restart Servers Script
# This script helps you restart both backend and frontend servers

echo "=========================================="
echo "  Data Retrieval System - Server Restart"
echo "=========================================="
echo ""

# Function to kill processes on specific ports
kill_port() {
    local port=$1
    echo "Checking for processes on port $port..."
    
    # Find and kill process on the port
    lsof -ti:$port | xargs kill -9 2>/dev/null
    
    if [ $? -eq 0 ]; then
        echo "✓ Killed process on port $port"
    else
        echo "✓ No process found on port $port"
    fi
}

# Kill existing processes
echo "Step 1: Stopping existing servers..."
kill_port 5001  # Backend
kill_port 3000  # Frontend
echo ""

# Wait a moment for ports to be released
sleep 2

echo "Step 2: Starting servers..."
echo ""

# Start backend in background
echo "Starting Backend Server (port 5001)..."
cd backend
python app.py > ../backend.log 2>&1 &
BACKEND_PID=$!
cd ..
echo "✓ Backend started (PID: $BACKEND_PID)"
echo "  Log file: backend.log"
echo ""

# Wait for backend to initialize
sleep 3

# Start frontend in background
echo "Starting Frontend Server (port 3000)..."
cd frontend
npm start > ../frontend.log 2>&1 &
FRONTEND_PID=$!
cd ..
echo "✓ Frontend started (PID: $FRONTEND_PID)"
echo "  Log file: frontend.log"
echo ""

echo "=========================================="
echo "  Servers Started Successfully!"
echo "=========================================="
echo ""
echo "Backend:  http://localhost:5001"
echo "Frontend: http://localhost:3000"
echo ""
echo "Backend PID:  $BACKEND_PID"
echo "Frontend PID: $FRONTEND_PID"
echo ""
echo "To view logs:"
echo "  Backend:  tail -f backend.log"
echo "  Frontend: tail -f frontend.log"
echo ""
echo "To stop servers:"
echo "  kill $BACKEND_PID $FRONTEND_PID"
echo ""
echo "Opening browser in 5 seconds..."
sleep 5

# Open browser (works on macOS)
open http://localhost:3000 2>/dev/null || echo "Please open http://localhost:3000 in your browser"

# Made with Bob
