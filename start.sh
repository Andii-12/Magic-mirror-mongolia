#!/bin/bash

# MagicMirror² Complete System Startup
# ONE command to start everything

echo "🚀 Starting MagicMirror² Complete System"
echo "========================================"

# Check if we're in the right directory
if [ ! -f "package.json" ]; then
    echo "❌ Error: Please run this from the MagicMirror directory"
    exit 1
fi

# Kill any existing processes
echo "🧹 Cleaning up existing processes..."
pkill -f "face_recognition_system.py" 2>/dev/null
pkill -f "node.*electron" 2>/dev/null
pkill -f "npm start" 2>/dev/null
sleep 2

# Start face recognition system
echo "🤖 Starting face recognition system..."
python3 face_recognition_system.py &
FACE_PID=$!
echo "Face recognition PID: $FACE_PID"

# Wait for face recognition to initialize
sleep 3

# Start MagicMirror²
echo "🪞 Starting MagicMirror²..."
echo "🌐 Will be available at: http://localhost:8080"
echo ""
echo "Press Ctrl+C to stop everything"
echo ""

# Start MagicMirror² in foreground
npm start

# Cleanup function
cleanup() {
    echo ""
    echo "🛑 Shutting down system..."
    kill $FACE_PID 2>/dev/null
    pkill -f "node.*electron" 2>/dev/null
    pkill -f "npm start" 2>/dev/null
    echo "✅ System stopped"
    exit 0
}

# Trap Ctrl+C
trap cleanup SIGINT SIGTERM
