#!/bin/bash
# Diagnostic script for Skin Photo feature on Raspberry Pi

echo "============================================================"
echo "SKIN PHOTO DIAGNOSTIC TOOL"
echo "============================================================"

# 1. Check platform
echo -e "\n1. PLATFORM CHECK"
echo "-----------------------------------------------------------"
python3 -c "import platform; print(f'Platform: {platform.system()}')"

# 2. Check camera
echo -e "\n2. CAMERA CHECK"
echo "-----------------------------------------------------------"
vcgencmd get_camera || echo "Not a Raspberry Pi or camera command failed"

# 3. Check current directory
echo -e "\n3. DIRECTORY CHECK"
echo "-----------------------------------------------------------"
echo "Current directory: $(pwd)"
echo "Files in current directory:"
ls -la | head -20

# 4. Check if Skin folder exists
echo -e "\n4. SKIN FOLDER CHECK"
echo "-----------------------------------------------------------"
if [ -d "Skin" ]; then
    echo "✅ Skin folder exists"
    echo "Contents:"
    ls -la Skin/
else
    echo "❌ Skin folder does NOT exist"
    echo "Attempting to create..."
    mkdir -p Skin/TestUser
    if [ -d "Skin/TestUser" ]; then
        echo "✅ Successfully created Skin/TestUser"
    else
        echo "❌ Failed to create directory"
    fi
fi

# 5. Check permissions
echo -e "\n5. PERMISSIONS CHECK"
echo "-----------------------------------------------------------"
ls -ld . | awk '{print "Current directory permissions: " $1}'
if [ -d "Skin" ]; then
    ls -ld Skin/ | awk '{print "Skin directory permissions: " $1}'
fi

# 6. Check disk space
echo -e "\n6. DISK SPACE CHECK"
echo "-----------------------------------------------------------"
df -h . | tail -n 1

# 7. Test file creation
echo -e "\n7. FILE CREATION TEST"
echo "-----------------------------------------------------------"
test_file="Skin/TestUser/test_$(date +%Y-%m-%d_%H-%M-%S).txt"
echo "Creating test file: $test_file"
mkdir -p Skin/TestUser
echo "Test file created at $(date)" > "$test_file"
if [ -f "$test_file" ]; then
    echo "✅ Test file created successfully"
    echo "   File: $test_file"
    echo "   Size: $(ls -lh "$test_file" | awk '{print $5}')"
else
    echo "❌ Failed to create test file"
fi

# 8. Check Python packages
echo -e "\n8. PYTHON PACKAGES CHECK"
echo "-----------------------------------------------------------"
echo "Checking required packages..."
python3 -c "import cv2; print(f'OpenCV: {cv2.__version__}')" || echo "❌ OpenCV not found"
python3 -c "import numpy; print(f'NumPy: {numpy.__version__}')" || echo "❌ NumPy not found"
python3 -c "from picamera2 import Picamera2; print('Picamera2: OK')" || echo "❌ Picamera2 not found"

# 9. Run Python test
echo -e "\n9. PYTHON FILE SYSTEM TEST"
echo "-----------------------------------------------------------"
if [ -f "test_skin_photo.py" ]; then
    echo "Running test_skin_photo.py..."
    python3 test_skin_photo.py
else
    echo "⚠️  test_skin_photo.py not found"
fi

echo -e "\n============================================================"
echo "DIAGNOSTIC COMPLETE"
echo "============================================================"
echo ""
echo "Next steps:"
echo "1. If all checks pass, run: python3 face_recognition_system.py"
echo "2. Watch for [SKIN PHOTO] messages in the output"
echo "3. After recognition, check: ls -la Skin/*/"
echo ""

