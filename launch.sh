#!/bin/bash

# PrintJoy - PrintBot Launch Script
# Starts Backend (FastAPI) and Kiosk (KivyMD)

echo "🤖 Starting PrintJoy System..."

# 1. Activate Virtual Env if exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# 2. Check for .env
if [ ! -f .env ]; then
    echo "❌ Error: .env file missing. Please copy .env.example to .env and configure it."
    exit 1
fi

# 3. Start Backend in Background
echo "📡 Starting Backend Service..."
uvicorn web.main:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

# Wait for backend to be ready
echo "⏳ Waiting for backend to initialize..."
sleep 5

# 4. Start Kiosk Interface
echo "🖥️ Starting Kiosk Interface..."
python3 kiosk/main.py

# 5. Cleanup on Exit
echo "🛑 Shutting down backend..."
kill $BACKEND_PID
echo "✅ System Stopped."
