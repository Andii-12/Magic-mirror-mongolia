#!/bin/bash

# Lightweight MagicMirror² Face Recognition Startup Script
# Optimized for Raspberry Pi 4 with 1GB RAM

echo "🚀 Starting Lightweight MagicMirror² Face Recognition System..."
echo "=============================================================="

# Kill any existing processes
echo "🧹 Cleaning up existing processes..."
pkill -f "python.*face_recognition" 2>/dev/null
pkill -f "node.*electron" 2>/dev/null
pkill -f "npm start" 2>/dev/null
sleep 3

# Clear GPIO pins
echo "🔧 Clearing GPIO pins..."
sudo gpio unexportall 2>/dev/null || true

# Start face recognition system in background
echo "🤖 Starting face recognition system..."
python3 face_recognition_system.py &
FACE_PID=$!
echo "Face recognition PID: $FACE_PID"

# Wait for face recognition to initialize
echo "⏳ Waiting for face recognition to initialize..."
sleep 5

# Start MagicMirror² with reduced memory usage
echo "🪞 Starting MagicMirror² (lightweight mode)..."
NODE_OPTIONS="--max-old-space-size=512" npm start > /dev/null 2>&1 &
MAGICMIRROR_PID=$!
echo "MagicMirror² PID: $MAGICMIRROR_PID"

# Wait for MagicMirror² to start
echo "⏳ Waiting for MagicMirror² to initialize..."
sleep 8

# Hide the MagicMirror window initially
echo "👻 Hiding MagicMirror² window..."
DISPLAY=:0 wmctrl -r "MagicMirror²" -b add,hidden 2>/dev/null || echo "wmctrl not available, using alternative method"

# Monitor the status file for proximity detection
echo "👀 Monitoring proximity detection..."
echo "Move within 20cm of the sensor to activate MagicMirror²"
echo "Press Ctrl+C to stop the system"

# Function to show MagicMirror window
show_magicmirror() {
    echo "👁️  Showing MagicMirror² window..."
    DISPLAY=:0 wmctrl -r "MagicMirror²" -b remove,hidden 2>/dev/null || echo "Window shown"
}

# Function to hide MagicMirror window
hide_magicmirror() {
    echo "👻 Hiding MagicMirror² window..."
    DISPLAY=:0 wmctrl -r "MagicMirror²" -b add,hidden 2>/dev/null || echo "Window hidden"
}

# Monitor status file
STATUS_FILE="/tmp/magicmirror_face_status.json"
LAST_ACTIVE=false

while true; do
    if [ -f "$STATUS_FILE" ]; then
        # Read the status file
        ACTIVE=$(python3 -c "
import json
try:
    with open('$STATUS_FILE', 'r') as f:
        data = json.load(f)
    print(data.get('active', False))
except:
    print('False')
" 2>/dev/null)
        
        if [ "$ACTIVE" = "True" ] && [ "$LAST_ACTIVE" = "false" ]; then
            echo "🎯 Proximity detected! Activating MagicMirror²..."
            show_magicmirror
            LAST_ACTIVE=true
        elif [ "$ACTIVE" = "False" ] && [ "$LAST_ACTIVE" = "true" ]; then
            echo "👋 Proximity lost. Hiding MagicMirror²..."
            hide_magicmirror
            LAST_ACTIVE=false
        fi
    fi
    
    sleep 2  # Check every 2 seconds to reduce CPU usage
done

# Cleanup function
cleanup() {
    echo ""
    echo "🛑 Shutting down system..."
    kill $FACE_PID 2>/dev/null
    kill $MAGICMIRROR_PID 2>/dev/null
    pkill -f "python.*face_recognition" 2>/dev/null
    pkill -f "node.*electron" 2>/dev/null
    sudo gpio unexportall 2>/dev/null || true
    echo "✅ System stopped"
    exit 0
}

# Trap Ctrl+C
trap cleanup SIGINT SIGTERM
