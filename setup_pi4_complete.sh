#!/bin/bash

# Complete Raspberry Pi 4 Setup Script for MagicMirror² with Personal API
# This script sets up everything needed to run the complete system

echo "🍓 Raspberry Pi 4 Complete MagicMirror² Setup"
echo "=============================================="
echo ""

# Check if running on Raspberry Pi
if ! grep -q "Raspberry Pi" /proc/cpuinfo; then
    echo "⚠️  Warning: This script is optimized for Raspberry Pi 4"
    echo "   Some features may not work on other systems"
    echo ""
fi

# Check available memory
MEMORY=$(free -m | awk 'NR==2{printf "%.0f", $2}')
echo "📊 Available RAM: ${MEMORY}MB"
if [ "$MEMORY" -lt 900 ]; then
    echo "⚠️  Warning: Low memory detected. Consider optimizing your setup."
fi
echo ""

# Update system
echo "🔄 Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install essential packages
echo "📦 Installing essential packages..."
sudo apt install -y git curl wget build-essential python3-pip python3-venv python3-dev

# Install Node.js 22.x
echo "📦 Installing Node.js 22.x..."
curl -fsSL https://deb.nodesource.com/setup_22.x | sudo -E bash -
sudo apt-get install -y nodejs

# Verify Node.js installation
NODE_VERSION=$(node -v | cut -d'v' -f2 | cut -d'.' -f1)
if [ "$NODE_VERSION" -lt 22 ]; then
    echo "❌ Error: Node.js version $NODE_VERSION detected. Required: 22.x+"
    exit 1
fi
echo "✅ Node.js $(node -v) installed successfully"

# Install Python dependencies
echo "🐍 Installing Python dependencies..."
sudo apt install -y python3-opencv python3-picamera2 python3-numpy

# Install additional Python packages
echo "📦 Installing additional Python packages..."
pip3 install opencv-python RPi.GPIO numpy face-recognition

# Enable camera
echo "📷 Enabling camera module..."
sudo raspi-config nonint do_camera 0

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p Images
mkdir -p /home/pi/haarcascades
mkdir -p /tmp

# Download Haar cascade
echo "📥 Downloading face detection model..."
wget -O /home/pi/haarcascades/haarcascade_frontalface_default.xml \
  https://raw.githubusercontent.com/opencv/opencv/master/data/haarcascades/haarcascade_frontalface_default.xml

# Set permissions
chmod 644 /home/pi/haarcascades/haarcascade_frontalface_default.xml

# Test camera
echo "📷 Testing camera..."
if libcamera-hello --list-cameras > /dev/null 2>&1; then
    echo "✅ Camera is working"
else
    echo "⚠️  Camera test failed. Please check camera connection."
fi

# Install MagicMirror dependencies
echo "📦 Installing MagicMirror² dependencies..."
if [ -f "package.json" ]; then
    npm install --only=prod --omit=dev
    echo "✅ MagicMirror² dependencies installed"
else
    echo "❌ package.json not found. Please run this script from MagicMirror directory."
    exit 1
fi

# Run Mongolian setup
echo "🇲🇳 Setting up Mongolian language support..."
if [ -f "setup-mongolian.sh" ]; then
    chmod +x setup-mongolian.sh
    ./setup-mongolian.sh
else
    echo "⚠️  Mongolian setup script not found. Skipping..."
fi

# Create systemd services
echo "⚙️  Creating systemd services..."

# Face recognition service
sudo tee /etc/systemd/system/magicmirror-face.service > /dev/null <<EOF
[Unit]
Description=MagicMirror Face Recognition
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=$(pwd)
ExecStart=/usr/bin/python3 face_recognition_system.py
Restart=always
RestartSec=10
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target
EOF

# MagicMirror service
sudo tee /etc/systemd/system/magicmirror.service > /dev/null <<EOF
[Unit]
Description=MagicMirror
After=network.target magicmirror-face.service

[Service]
Type=simple
User=pi
WorkingDirectory=$(pwd)
ExecStart=/usr/bin/npm start
Restart=always
RestartSec=10
Environment=NODE_ENV=production

[Install]
WantedBy=multi-user.target
EOF

# Enable services
echo "🔧 Enabling services..."
sudo systemctl daemon-reload
sudo systemctl enable magicmirror-face.service
sudo systemctl enable magicmirror.service

# Optimize for Pi 4
echo "⚡ Applying Pi 4 optimizations..."

# Disable unnecessary services
sudo systemctl disable bluetooth
sudo systemctl disable hciuart

# Optimize GPU memory split
if ! grep -q "gpu_mem=64" /boot/config.txt; then
    echo "gpu_mem=64" | sudo tee -a /boot/config.txt
fi

# Set up zram for swap
if ! dpkg -l | grep -q zram-tools; then
    sudo apt install -y zram-tools
fi

# Create startup script
echo "📝 Creating startup script..."
cat > start_magicmirror.sh << 'EOF'
#!/bin/bash
echo "🚀 Starting MagicMirror² with Personal API Integration"
echo "====================================================="

# Start face recognition in background
echo "👤 Starting face recognition system..."
python3 face_recognition_system.py &
FACE_PID=$!

# Wait a moment for face recognition to initialize
sleep 3

# Start MagicMirror
echo "🪞 Starting MagicMirror²..."
npm start

# Cleanup on exit
trap "kill $FACE_PID 2>/dev/null" EXIT
EOF

chmod +x start_magicmirror.sh

# Create test script
echo "🧪 Creating test script..."
cat > test_system.py << 'EOF'
#!/usr/bin/env python3
"""
Test script for the complete MagicMirror² system
"""

import cv2
import json
import time
import os
import subprocess
import requests

def test_camera():
    """Test camera functionality"""
    print("📷 Testing camera...")
    try:
        from picamera2 import Picamera2
        picam2 = Picamera2()
        config = picam2.create_preview_configuration(main={"size": (320, 240)})
        picam2.configure(config)
        picam2.start()
        time.sleep(1)
        frame = picam2.capture_array()
        picam2.close()
        print("✅ Camera test passed")
        return True
    except Exception as e:
        print(f"❌ Camera test failed: {e}")
        return False

def test_face_detection():
    """Test face detection"""
    print("👤 Testing face detection...")
    try:
        cascade_path = "/home/pi/haarcascades/haarcascade_frontalface_default.xml"
        face_cascade = cv2.CascadeClassifier(cascade_path)
        if face_cascade.empty():
            print("❌ Face cascade not loaded")
            return False
        
        from picamera2 import Picamera2
        picam2 = Picamera2()
        config = picam2.create_preview_configuration(main={"size": (320, 240)})
        picam2.configure(config)
        picam2.start()
        time.sleep(1)
        
        frame = picam2.capture_array()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)
        
        picam2.close()
        print(f"✅ Face detection test passed - Found {len(faces)} faces")
        return True
    except Exception as e:
        print(f"❌ Face detection test failed: {e}")
        return False

def test_api():
    """Test Personal API"""
    print("🌐 Testing Personal API...")
    try:
        response = requests.get("https://calendar-app-production-6d2d.up.railway.app/api/magic-mirror/future-data", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ API test passed - {data['summary']['totalUsers']} users, {data['summary']['totalEvents']} events")
            return True
        else:
            print(f"❌ API test failed - HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ API test failed: {e}")
        return False

def test_magicmirror_config():
    """Test MagicMirror configuration"""
    print("⚙️  Testing MagicMirror configuration...")
    try:
        result = subprocess.run(["node", "js/check_config.js"], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ MagicMirror configuration test passed")
            return True
        else:
            print(f"❌ MagicMirror configuration test failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ MagicMirror configuration test failed: {e}")
        return False

def main():
    print("🧪 MagicMirror² System Test")
    print("===========================")
    print("")
    
    tests = [
        test_camera,
        test_face_detection,
        test_api,
        test_magicmirror_config
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print("")
    
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! System is ready to run.")
        print("")
        print("🚀 To start the system:")
        print("   ./start_magicmirror.sh")
        print("")
        print("🔧 To start services:")
        print("   sudo systemctl start magicmirror-face.service")
        print("   sudo systemctl start magicmirror.service")
    else:
        print("❌ Some tests failed. Please check the errors above.")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
EOF

chmod +x test_system.py

# Install requests for API testing
pip3 install requests

# Run system test
echo "🧪 Running system tests..."
python3 test_system.py

echo ""
echo "🎉 Setup Complete!"
echo "=================="
echo ""
echo "📋 What's been set up:"
echo "   ✅ System packages and dependencies"
echo "   ✅ Node.js 22.x and npm"
echo "   ✅ Python OpenCV and camera libraries"
echo "   ✅ Face recognition system"
echo "   ✅ MagicMirror² with Mongolian language"
echo "   ✅ Personal API integration"
echo "   ✅ Systemd services for auto-start"
echo "   ✅ Pi 4 optimizations"
echo ""
echo "🚀 To start the complete system:"
echo "   ./start_magicmirror.sh"
echo ""
echo "🔧 To start services individually:"
echo "   sudo systemctl start magicmirror-face.service"
echo "   sudo systemctl start magicmirror.service"
echo ""
echo "🧪 To test the system:"
echo "   python3 test_system.py"
echo ""
echo "📱 Access MagicMirror:"
echo "   http://localhost:8080"
echo "   http://[PI_IP]:8080 (from other devices)"
echo ""
echo "🇲🇳 Your Mongolian MagicMirror² with Personal API is ready!"
echo ""
