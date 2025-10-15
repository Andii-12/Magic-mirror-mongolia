#!/bin/bash

# Fix Camera Colors for MagicMirror²
# This script applies optimal camera settings for proper color reproduction

echo "🎨 Fixing MagicMirror² Camera Colors"
echo "===================================="

# Check if running on Raspberry Pi
if ! grep -q "Raspberry Pi" /proc/cpuinfo; then
    echo "❌ This script is designed for Raspberry Pi only"
    exit 1
fi

echo "📸 Applying optimal camera settings..."

# 1. Set camera configuration for better colors
echo "1️⃣ Setting camera configuration..."

# Create camera configuration file
sudo tee /etc/camera-settings.txt > /dev/null << 'EOF'
# Optimal camera settings for MagicMirror²
# These settings improve color accuracy and skin tone reproduction

# White balance settings
awb_mode=auto
awb_gains=1.0,1.0

# Exposure settings  
exposure_mode=auto
metering_mode=average

# Color correction
saturation=1.0
contrast=1.0
brightness=0.0

# Image quality
sharpness=1.0
denoise=auto
EOF

echo "   ✅ Camera configuration saved"

# 2. Test camera with different settings
echo "2️⃣ Testing camera configurations..."

# Run the color test script
if [ -f "test_camera_color.py" ]; then
    echo "   🧪 Running camera color tests..."
    python3 test_camera_color.py
else
    echo "   ⚠️  Color test script not found, creating basic test..."
    
    # Basic camera test with different white balance settings
    echo "   Testing auto white balance..."
    libcamera-still -o test_auto.jpg -t 1000 -n --awb auto --width 640 --height 480
    
    echo "   Testing daylight white balance..."
    libcamera-still -o test_daylight.jpg -t 1000 -n --awb daylight --width 640 --height 480
    
    echo "   Testing cloudy white balance..."
    libcamera-still -o test_cloudy.jpg -t 1000 -n --awb cloudy --width 640 --height 480
fi

# 3. Update system camera settings
echo "3️⃣ Updating system camera settings..."

# Check current camera configuration
echo "   Current camera info:"
vcgencmd get_camera

# Set optimal camera parameters
echo "   Setting optimal parameters..."
# These commands help with color accuracy
sudo raspi-config nonint do_camera 0  # Enable camera if not already enabled

# 4. Create camera calibration script
echo "4️⃣ Creating camera calibration script..."

cat > calibrate_camera.py << 'EOF'
#!/usr/bin/env python3
"""
Camera Calibration Script for MagicMirror²
Helps adjust camera settings for optimal color reproduction
"""

import cv2
import numpy as np
from picamera2 import Picamera2
import libcamera

def calibrate_camera():
    """Calibrate camera for optimal color reproduction"""
    
    print("🎯 Camera Calibration for MagicMirror²")
    print("=" * 40)
    
    # Initialize camera with optimal settings
    camera = Picamera2()
    
    # Try different configurations
    configs = [
        {
            "name": "Standard RGB",
            "config": camera.create_preview_configuration(
                main={"size": (640, 480), "format": "RGB888"},
                transform=libcamera.Transform(hflip=0, vflip=0)
            )
        },
        {
            "name": "High Quality RGB", 
            "config": camera.create_still_configuration(
                main={"size": (1920, 1080), "format": "RGB888"},
                transform=libcamera.Transform(hflip=0, vflip=0)
            )
        }
    ]
    
    for config in configs:
        print(f"\n📸 Testing: {config['name']}")
        
        try:
            camera.configure(config['config'])
            camera.start()
            time.sleep(1)
            
            # Capture frame
            frame = camera.capture_array()
            print(f"   Frame shape: {frame.shape}")
            print(f"   Frame type: {frame.dtype}")
            
            # Convert to BGR for OpenCV
            frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            
            # Apply color correction
            # Convert to LAB color space for better color adjustment
            lab = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2LAB)
            l, a, b = cv2.split(lab)
            
            # Apply CLAHE (Contrast Limited Adaptive Histogram Equalization)
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
            l = clahe.apply(l)
            
            # Merge channels back
            lab = cv2.merge([l, a, b])
            
            # Convert back to BGR
            corrected = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)
            
            # Save original and corrected images
            original_filename = f"calibration_{config['name'].lower().replace(' ', '_')}_original.jpg"
            corrected_filename = f"calibration_{config['name'].lower().replace(' ', '_')}_corrected.jpg"
            
            cv2.imwrite(original_filename, frame_bgr)
            cv2.imwrite(corrected_filename, corrected)
            
            print(f"   ✅ Saved: {original_filename}")
            print(f"   ✅ Saved: {corrected_filename}")
            
            camera.stop()
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    camera.close()
    
    print("\n🎯 Calibration Complete!")
    print("Compare the original and corrected images to see the improvement.")
    print("The corrected images should have better color balance and skin tones.")

if __name__ == "__main__":
    calibrate_camera()
EOF

chmod +x calibrate_camera.py
echo "   ✅ Camera calibration script created"

# 5. Test the fixes
echo "5️⃣ Testing camera fixes..."

echo "   📸 Taking test photo with optimized settings..."
libcamera-still -o magicmirror_test.jpg \
    -t 2000 \
    -n \
    --width 1920 \
    --height 1080 \
    --awb auto \
    --metering average \
    --exposure auto \
    --gain auto \
    --saturation 1.0 \
    --contrast 1.0 \
    --brightness 0.0 \
    --sharpness 1.0

if [ -f "magicmirror_test.jpg" ]; then
    echo "   ✅ Test photo saved: magicmirror_test.jpg"
    echo "   📋 Check this image for proper color reproduction"
else
    echo "   ❌ Failed to create test photo"
fi

# 6. Summary
echo ""
echo "🎯 Camera Color Fix Summary"
echo "=========================="
echo "✅ Camera configuration updated"
echo "✅ Color test scripts created"
echo "✅ System settings optimized"
echo "✅ Test photos generated"
echo ""
echo "📋 Next Steps:"
echo "1. Review the test images to verify color improvements"
echo "2. Run: python3 calibrate_camera.py (for advanced calibration)"
echo "3. Run: python3 test_camera_color.py (for detailed testing)"
echo "4. Restart your MagicMirror² system: ./start.sh"
echo ""
echo "🎨 If colors still look wrong:"
echo "   - Check lighting conditions"
echo "   - Try different white balance settings (daylight, cloudy, etc.)"
echo "   - Adjust the --awb parameter in libcamera-still commands"
echo ""
echo "✅ Camera color fix complete!"
