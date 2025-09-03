#!/bin/bash

# Face Recognition System Setup Script for MagicMirror²
# This script sets up the face recognition system with ultrasonic sensor

echo "🤖 Setting up Face Recognition System for MagicMirror²"
echo "======================================================"

# Check if running on Raspberry Pi
if ! grep -q "Raspberry Pi" /proc/cpuinfo; then
    echo "⚠️  Warning: This script is designed for Raspberry Pi"
fi

# Install required Python packages (matching your working code)
echo "📦 Installing Python packages..."
pip3 install opencv-python RPi.GPIO picamera2 numpy

# Create Images directory (matching your working code structure)
echo "📁 Creating Images directory..."
mkdir -p Images
echo "   Place photos of people you want to recognize in the 'Images' directory"
echo "   Each person should have their own folder with their name"
echo "   Example: Images/John/photo1.jpg, Images/Jane/photo1.jpg"

# Make Python script executable
echo "🔧 Making face recognition script executable..."
chmod +x face_recognition_system.py

# Create systemd service for auto-start (optional)
echo "⚙️  Creating systemd service..."
sudo tee /etc/systemd/system/magicmirror-face-recognition.service > /dev/null <<EOF
[Unit]
Description=MagicMirror² Face Recognition System
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/Magic-mirror-mongolia-master
ExecStart=/usr/bin/python3 /home/pi/Magic-mirror-mongolia-master/face_recognition_system.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Enable the service (optional)
read -p "Do you want to enable auto-start of face recognition? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    sudo systemctl daemon-reload
    sudo systemctl enable magicmirror-face-recognition.service
    echo "✅ Face recognition service enabled for auto-start"
fi

# Create startup script
echo "📝 Creating startup script..."
cat > start_face_recognition.sh << 'EOF'
#!/bin/bash
echo "Starting Face Recognition System..."
cd /home/pi/Magic-mirror-mongolia-master
python3 face_recognition_system.py
EOF

chmod +x start_face_recognition.sh

# Create shutdown script for MagicMirror
echo "📝 Creating MagicMirror shutdown script..."
cat > shutdown_magicmirror.sh << 'EOF'
#!/bin/bash
echo "Shutting down MagicMirror²..."
pkill -f "node.*electron"
pkill -f "npm start"
EOF

chmod +x shutdown_magicmirror.sh

# Hardware setup instructions
echo ""
echo "🔌 Hardware Setup Instructions:"
echo "==============================="
echo "1. Connect ultrasonic sensor (matching your working code):"
echo "   - VCC to 5V (Pin 2)"
echo "   - GND to Ground (Pin 6)"
echo "   - TRIG to GPIO 23 (Pin 16)"
echo "   - ECHO to GPIO 24 (Pin 18)"
echo ""
echo "2. Connect camera:"
echo "   - Use Raspberry Pi Camera Module or USB webcam"
echo "   - For Pi Camera: Enable in raspi-config"
echo ""
echo "3. Test the setup:"
echo "   - Run: python3 face_recognition_system.py"
echo "   - Check: /tmp/magicmirror_face_status.json"

# Usage instructions
echo ""
echo "📋 Usage Instructions:"
echo "====================="
echo "1. Add photos to 'Images' directory:"
echo "   - Create folders for each person: Images/PersonName/"
echo "   - Add multiple photos per person for better recognition"
echo "   - Example: Images/John/photo1.jpg, Images/Jane/photo1.jpg"
echo ""
echo "2. Train the face recognizer:"
echo "   - Run your face training script to create trainer.yml"
echo "   - Make sure trainer.yml is in the same directory as face_recognition_system.py"
echo ""
echo "3. Start the face recognition system:"
echo "   - Manual: ./start_face_recognition.sh"
echo "   - Service: sudo systemctl start magicmirror-face-recognition"
echo ""
echo "4. Start MagicMirror²:"
echo "   - npm start"
echo ""
echo "5. Test the system:"
echo "   - Move within 20cm of the sensor"
echo "   - Look at the camera"
echo "   - MagicMirror should show: 'Сайн байна уу [name]!'"
echo ""
echo "6. Move away for 10+ seconds to auto-shutdown"

# Troubleshooting
echo ""
echo "🔧 Troubleshooting:"
echo "=================="
echo "- Check camera: ls /dev/video*"
echo "- Test ultrasonic: python3 -c 'import RPi.GPIO as GPIO; print(\"GPIO OK\")'"
echo "- Check status file: cat /tmp/magicmirror_face_status.json"
echo "- View logs: journalctl -u magicmirror-face-recognition -f"

echo ""
echo "🎉 Face Recognition System setup complete!"
echo "   Ready to recognize faces and control MagicMirror²!"
