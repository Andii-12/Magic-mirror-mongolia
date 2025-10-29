#!/bin/bash

# MagicMirror² Complete Startup Script for Raspberry Pi 4
# Starts face recognition + ultrasonic + relay lights + MagicMirror² + personal data

echo "🚀 Starting MagicMirror² Complete System"
echo "======================================="

# Check if running on Raspberry Pi
if [ -f /proc/device-tree/model ]; then
    echo "✅ Raspberry Pi detected: $(cat /proc/device-tree/model)"
else
    echo "❌ This script is designed for Raspberry Pi 4 only"
    exit 1
fi

# Check if we're in the right directory
if [ ! -f "package.json" ]; then
    echo "❌ Error: Please run this from the MagicMirror directory"
    exit 1
fi

# Set display for X11
export DISPLAY=:0

# Create status file if it doesn't exist
if [ ! -f "/tmp/magicmirror_face_status.json" ]; then
    echo "📝 Creating face status file..."
    mkdir -p /tmp
    echo '{"person": null, "active": false, "distance": 999, "status": "waiting", "timestamp": "2024-01-01T00:00:00"}' > /tmp/magicmirror_face_status.json
    echo "✅ Status file created"
else
    echo "✅ Face status file already exists"
fi

# Create initial status file (no user recognized)
echo "📝 Creating initial status file (no user recognized)..."
echo '{"person": null, "active": false, "distance": 999, "status": "waiting", "timestamp": "'$(date -Iseconds)'"}' > /tmp/magicmirror_face_status.json
echo "✅ Initial status created - waiting for face recognition"

# Kill any existing processes
echo "🧹 Cleaning up existing processes..."
pkill -f "face_recognition_system.py" 2>/dev/null
pkill -f "node.*electron" 2>/dev/null
pkill -f "npm start" 2>/dev/null
sleep 2

# Check for test mode
if [ "$1" = "test" ]; then
    echo "🧪 Starting face recognition system in TEST MODE..."
    FACE_RECOGNITION_TEST=true python3 face_recognition_system.py &
    FACE_PID=$!
else
    echo "🎯 Starting face recognition system with neutral white balance (natural skin tones)..."
    # Balanced white balance for natural skin colors (not too yellow, not too blue)
    SKIN_COLOR_MODE=natural \
    SKIN_AWB=auto \
    SKIN_AWB_GAINS=1.0,1.2 \
    python3 face_recognition_system.py &
    FACE_PID=$!
fi

# Wait a moment for face recognition to initialize
sleep 3

# Check if face recognition started successfully
if ps -p $FACE_PID > /dev/null; then
    echo "✅ Face recognition system started (PID: $FACE_PID)"
else
    echo "❌ Failed to start face recognition system"
    exit 1
fi

# Start MagicMirror²
echo "🎯 Starting MagicMirror²..."
echo "   Address: 0.0.0.0:8080"
echo "   Mode: Standalone (Kiosk)"
echo "   Language: Mongolian"
echo "   Face Recognition: Running"
echo "   Relay Lights: GPIO 18"
echo ""
echo "Press Ctrl+C to stop everything"
echo ""

# Start MagicMirror² (this will block)
npm start

# Cleanup when MagicMirror² stops
echo ""
echo "🛑 MagicMirror² stopped - cleaning up..."

# Stop face recognition
if ps -p $FACE_PID > /dev/null; then
    echo "🛑 Stopping face recognition system..."
    kill $FACE_PID
fi

echo "✅ Cleanup complete"
