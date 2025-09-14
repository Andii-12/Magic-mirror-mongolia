#!/bin/bash
"""
OpenCV Installation Script for Face Recognition
Installs OpenCV with face detection support on Raspberry Pi
"""

echo "🔧 Installing OpenCV for Face Recognition"
echo "=========================================="

# Update package list
echo "📦 Updating package list..."
sudo apt-get update

# Install OpenCV and dependencies
echo "📦 Installing OpenCV and dependencies..."
sudo apt-get install -y python3-opencv python3-pip

# Install additional Python packages
echo "📦 Installing Python packages..."
pip3 install numpy pillow

# Check if OpenCV is working
echo "🧪 Testing OpenCV installation..."
python3 -c "
import cv2
import sys

try:
    # Try to access haarcascades
    if hasattr(cv2, 'data') and hasattr(cv2.data, 'haarcascades'):
        cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        print(f'✅ OpenCV data path: {cascade_path}')
    else:
        print('⚠️  OpenCV data path not available')
    
    # Try to load face cascade
    face_cascade = cv2.CascadeClassifier(cascade_path)
    if not face_cascade.empty():
        print('✅ Face cascade loaded successfully')
    else:
        print('❌ Could not load face cascade')
    
    print('✅ OpenCV installation successful!')
    
except Exception as e:
    print(f'❌ OpenCV test failed: {e}')
    sys.exit(1)
"

if [ $? -eq 0 ]; then
    echo ""
    echo "🎉 OpenCV installation completed successfully!"
    echo ""
    echo "📋 Next steps:"
    echo "   1. Run: python3 train_faces.py"
    echo "   2. Follow the training menu"
    echo "   3. Add 40+ photos per person"
    echo "   4. Train the face recognition model"
else
    echo ""
    echo "❌ OpenCV installation failed!"
    echo ""
    echo "🔧 Troubleshooting:"
    echo "   1. Check internet connection"
    echo "   2. Try: sudo apt-get update && sudo apt-get upgrade"
    echo "   3. Try: pip3 install opencv-python"
    echo "   4. Check Python version: python3 --version"
fi
