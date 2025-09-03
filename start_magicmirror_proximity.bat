@echo off
REM MagicMirror² Proximity-Controlled Startup Script for Windows
REM This script starts MagicMirror² and waits for proximity detection

echo 🚀 Starting MagicMirror² Proximity System...
echo =============================================

REM Kill any existing MagicMirror processes
echo 🧹 Cleaning up existing processes...
taskkill /f /im electron.exe 2>nul
taskkill /f /im node.exe 2>nul
timeout /t 2 /nobreak >nul

REM Start face recognition system in background
echo 🤖 Starting face recognition system...
start /b python face_recognition_system.py

REM Wait a moment for face recognition to initialize
timeout /t 3 /nobreak >nul

REM Start MagicMirror²
echo 🪞 Starting MagicMirror²...
start /b npm start

REM Wait for MagicMirror² to start
timeout /t 5 /nobreak >nul

echo 👀 Monitoring proximity detection...
echo Move within 20cm of the sensor to activate MagicMirror²
echo Press Ctrl+C to stop the system

REM Monitor the status file for proximity detection
:monitor_loop
if exist "C:\temp\magicmirror_face_status.json" (
    REM Check if file has been modified recently
    forfiles /p "C:\temp" /m "magicmirror_face_status.json" /c "cmd /c echo File found" >nul 2>&1
    if !errorlevel! equ 0 (
        REM File exists and is accessible
        REM You could add more sophisticated monitoring here
    )
)

timeout /t 1 /nobreak >nul
goto monitor_loop
