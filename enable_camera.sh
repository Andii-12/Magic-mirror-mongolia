#!/bin/bash
# Auto-enable camera on Raspberry Pi

echo "============================================================"
echo "RASPBERRY PI CAMERA ENABLER"
echo "============================================================"

# Check current status
echo -e "\nStep 1: Checking current camera status..."
camera_status=$(vcgencmd get_camera)
echo "Current status: $camera_status"

if [[ $camera_status == *"supported=1"* ]] && [[ $camera_status == *"detected=1"* ]]; then
    echo "✅ Camera is already enabled!"
    echo ""
    echo "Testing camera..."
    libcamera-hello --list-cameras
    exit 0
fi

echo "❌ Camera needs to be enabled"
echo ""

# Backup config
echo "Step 2: Creating backup of /boot/config.txt..."
sudo cp /boot/config.txt /boot/config.txt.backup.$(date +%Y%m%d_%H%M%S)
echo "✅ Backup created"

# Check if lines exist
echo ""
echo "Step 3: Checking /boot/config.txt..."

if grep -q "^camera_auto_detect=1" /boot/config.txt; then
    echo "✅ camera_auto_detect=1 already set"
else
    echo "Adding camera_auto_detect=1..."
    echo "camera_auto_detect=1" | sudo tee -a /boot/config.txt
fi

if grep -q "^start_x=1" /boot/config.txt; then
    echo "✅ start_x=1 already set"
else
    echo "Adding start_x=1..."
    echo "start_x=1" | sudo tee -a /boot/config.txt
fi

if grep -q "^gpu_mem=" /boot/config.txt; then
    echo "✅ gpu_mem already set"
else
    echo "Adding gpu_mem=128..."
    echo "gpu_mem=128" | sudo tee -a /boot/config.txt
fi

echo ""
echo "============================================================"
echo "CAMERA CONFIGURATION UPDATED"
echo "============================================================"
echo ""
echo "Changes made to /boot/config.txt:"
echo "  - camera_auto_detect=1"
echo "  - start_x=1"
echo "  - gpu_mem=128"
echo ""
echo "Backup saved to: /boot/config.txt.backup.*"
echo ""
echo "⚠️  REBOOT REQUIRED!"
echo ""
echo "Run: sudo reboot"
echo ""
echo "After reboot, verify with: vcgencmd get_camera"
echo "============================================================"

