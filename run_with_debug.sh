#!/bin/bash
# Run face recognition system with full debug logging

echo "============================================================"
echo "STARTING FACE RECOGNITION WITH DEBUG LOGGING"
echo "============================================================"
echo "Logs will be saved to: face_recognition_debug.log"
echo ""
echo "Press Ctrl+C to stop"
echo ""

# Create timestamp
timestamp=$(date +%Y-%m-%d_%H-%M-%S)
log_file="face_recognition_debug_${timestamp}.log"

# Run with full output capture
python3 face_recognition_system.py 2>&1 | tee "$log_file"

echo ""
echo "============================================================"
echo "FACE RECOGNITION STOPPED"
echo "============================================================"
echo "Log saved to: $log_file"
echo ""
echo "Checking for SKIN PHOTO activity..."
grep -A 5 "SKIN PHOTO" "$log_file" || echo "No SKIN PHOTO messages found in log"
echo ""
echo "Checking for errors..."
grep "ERROR" "$log_file" || echo "No ERROR messages found"
echo ""
echo "Checking if Skin folder was created..."
if [ -d "Skin" ]; then
    echo "✅ Skin folder exists"
    echo "Contents:"
    ls -laR Skin/
else
    echo "❌ Skin folder was NOT created"
fi
echo ""

