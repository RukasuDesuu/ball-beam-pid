#!/bin/bash

# Define log file paths
BACKEND_LOG="./logs/backend.log"
FRONTEND_LOG="./logs/frontend.log"

# Check if backend is running, if not, start it
if ! pgrep -f "telemetrix_backend.py" > /dev/null; then
    echo "Backend is not running. Starting backend..."
    uv run telemetrix_backend.py >> "$BACKEND_LOG" 2>&1 &
    BACKEND_PID=$!
else
    echo 'Backend is already running.'
fi

# Check if frontend is running, if not, start it
if ! pgrep -f "streamlit_frontend.py" > /dev/null; then
    echo "Frontend is not running. Starting frontend..."
    uv run streamlit run streamlit_frontend.py &
    FRONTEND_PID=$!
else
    echo 'Frontend is already running.'
fi

# Handle interrupt and terminate background processes
trap "kill $BACKEND_PID $FRONTEND_PID" SIGINT SIGTERM EXIT

# Wait for all background processes to finish
wait $BACKEND_PID $FRONTEND_PID
