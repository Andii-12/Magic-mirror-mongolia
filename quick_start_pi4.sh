#!/bin/bash

# Quick Start Script for Raspberry Pi 4
# Run this after the complete setup

echo "🚀 Quick Start - MagicMirror² with Personal API"
echo "=============================================="
echo ""

# Check if we're in the right directory
if [ ! -f "package.json" ]; then
    echo "❌ Error: Please run this from the MagicMirror directory"
    exit 1
fi

# Check if face recognition is running
if pgrep -f "face_recognition_system.py" > /dev/null; then
    echo "✅ Face recognition is already running"
else
    echo "👤 Starting face recognition system..."
    python3 face_recognition_system.py &
    sleep 3
fi

# Check if MagicMirror is running
if pgrep -f "npm start" > /dev/null; then
    echo "✅ MagicMirror is already running"
    echo "🌐 Access at: http://localhost:8080"
else
    echo "🪞 Starting MagicMirror²..."
    echo "🌐 Will be available at: http://localhost:8080"
    echo ""
    echo "Press Ctrl+C to stop"
    echo ""
    npm start
fi
