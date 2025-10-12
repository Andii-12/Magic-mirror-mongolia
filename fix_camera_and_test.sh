#!/bin/bash
# Fix camera and test skin photo feature

echo "============================================================"
echo "CAMERA FIX AND SKIN PHOTO TEST"
echo "============================================================"

# Step 1: Check camera status
echo -e "\nStep 1: Checking camera status..."
camera_status=$(vcgencmd get_camera)
echo "Camera status: $camera_status"

if [[ $camera_status == *"supported=0"* ]] || [[ $camera_status == *"detected=0"* ]]; then
    echo "❌ Camera is NOT properly enabled!"
    echo ""
    echo "Please run: sudo raspi-config"
    echo "Then:"
    echo "  1. Interface Options"
    echo "  2. Legacy Camera → Enable"
    echo "  3. Camera → Enable"
    echo "  4. Finish"
    echo "  5. sudo reboot"
    echo ""
    echo "After reboot, run this script again."
    exit 1
else
    echo "✅ Camera is enabled"
fi

# Step 2: Test camera
echo -e "\nStep 2: Testing camera capture..."
libcamera-still -o test_camera.jpg --timeout 2000
if [ -f "test_camera.jpg" ]; then
    echo "✅ Camera test successful!"
    ls -lh test_camera.jpg
    rm test_camera.jpg
else
    echo "❌ Camera test failed!"
    exit 1
fi

# Step 3: Check if trainer.yml exists
echo -e "\nStep 3: Checking for trainer.yml..."
if [ -f "trainer.yml" ]; then
    echo "✅ trainer.yml found"
elif [ -f "python_code/trainer.yml" ]; then
    echo "✅ trainer.yml found in python_code/"
else
    echo "⚠️  No trainer.yml found - will run in simulation mode"
    echo "   This is OK for testing the skin photo feature"
fi

# Step 4: Test skin photo directory
echo -e "\nStep 4: Testing skin photo directory..."
python3 test_skin_photo.py

# Step 5: Run face recognition for 30 seconds
echo -e "\nStep 5: Running face recognition test..."
echo "The system will run for 30 seconds."
echo "Stand close to the camera (<20cm) to trigger recognition."
echo ""
echo "Starting in 3 seconds..."
sleep 3

# Run face recognition in background with timeout
timeout 30 python3 face_recognition_system.py &
FR_PID=$!

# Wait for it to complete
wait $FR_PID

# Step 6: Check results
echo -e "\n============================================================"
echo "Step 6: Checking results..."
echo "============================================================"

if [ -d "Skin" ]; then
    echo "✅ Skin folder was created!"
    echo ""
    echo "Contents:"
    ls -laR Skin/
    echo ""
    
    # Check for photos
    photo_count=$(find Skin/ -name "*.jpg" 2>/dev/null | wc -l)
    if [ $photo_count -gt 0 ]; then
        echo "✅ SUCCESS! Found $photo_count photo(s)!"
        echo ""
        find Skin/ -name "*.jpg" -exec ls -lh {} \;
    else
        echo "❌ No photos found"
        echo "Check if face was recognized during the test"
    fi
else
    echo "❌ Skin folder was NOT created"
    echo "Face recognition may not have been triggered"
fi

echo ""
echo "============================================================"
echo "TEST COMPLETE"
echo "============================================================"

