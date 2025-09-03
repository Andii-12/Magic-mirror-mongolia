@echo off
REM Lightweight MagicMirror² Face Recognition Startup Script for Windows
REM Optimized for Raspberry Pi 4 with 1GB RAM

echo 🚀 Starting Lightweight MagicMirror² Face Recognition System...
echo ==============================================================

REM Kill any existing processes
echo 🧹 Cleaning up existing processes...
taskkill /f /im python.exe 2>nul
taskkill /f /im node.exe 2>nul
taskkill /f /im electron.exe 2>nul
timeout /t 3 /nobreak >nul

REM Clear GPIO pins and processes
echo 🔧 Clearing GPIO pins and processes...
python cleanup_gpio.py 2>nul

REM Start face recognition system in background
echo 🤖 Starting face recognition system...
start /b python face_recognition_system.py
echo Face recognition started

REM Wait for face recognition to initialize
echo ⏳ Waiting for face recognition to initialize...
timeout /t 5 /nobreak >nul

REM Start MagicMirror² with reduced memory usage
echo 🪞 Starting MagicMirror² (lightweight mode)...
set NODE_OPTIONS=--max-old-space-size=512
start /b npm start
echo MagicMirror² started

REM Wait for MagicMirror² to start
echo ⏳ Waiting for MagicMirror² to initialize...
timeout /t 8 /nobreak >nul

echo 👀 System is now running!
echo Move within 20cm of the sensor to activate MagicMirror²
echo Press Ctrl+C to stop the system

REM Monitor the status file for proximity detection
:monitor_loop
if exist "/tmp/magicmirror_face_status.json" (
    REM Check if active (simplified check)
    python -c "
import json
try:
    with open('/tmp/magicmirror_face_status.json', 'r') as f:
        data = json.load(f)
    if data.get('active', False):
        print('🎯 Proximity detected!')
    else:
        print('👋 Proximity lost.')
except:
    pass
" 2>nul
)

timeout /t 2 /nobreak >nul
goto monitor_loop
