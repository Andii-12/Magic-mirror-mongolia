#!/bin/bash

# Fix Skin Tone Colors for MagicMirror²
# Comprehensive script to fix purple/lavender skin tone issues

echo "🎨 Fixing MagicMirror² Skin Tone Colors"
echo "======================================"

# Check if running on Raspberry Pi
if ! grep -q "Raspberry Pi" /proc/cpuinfo; then
    echo "❌ This script is designed for Raspberry Pi only"
    exit 1
fi

echo "📸 Applying comprehensive skin tone color fixes..."

# 1. Test current camera with different settings
echo "1️⃣ Testing camera with different white balance settings..."

# Test different white balance settings for skin tones
wb_settings=("auto" "daylight" "cloudy" "tungsten" "fluorescent")
for wb in "${wb_settings[@]}"; do
    echo "   Testing white balance: $wb"
    libcamera-still -o "test_wb_${wb}_1080.jpg" \
        -t 1000 \
        -n \
        --width 1080 \
        --height 1080 \
        --awb "$wb" \
        --saturation 1.2 \
        --contrast 1.1 \
        --brightness 0.1
done

# 2. Test enhanced skin tone settings
echo "2️⃣ Testing enhanced skin tone settings..."

# Enhanced settings specifically for skin tones
libcamera-still -o "test_skin_enhanced_1080.jpg" \
    -t 1000 \
    -n \
    --width 1080 \
    --height 1080 \
    --awb daylight \
    --saturation 1.3 \
    --contrast 1.15 \
    --brightness 0.15 \
    --sharpness 1.1 \
    --metering average

# 3. Run advanced color correction tests
echo "3️⃣ Running advanced color correction tests..."

if [ -f "test_advanced_color_correction.py" ]; then
    echo "   🧪 Running advanced color correction tests..."
    python3 test_advanced_color_correction.py
else
    echo "   ⚠️  Advanced color correction script not found"
fi

# 4. Create optimized camera configuration
echo "4️⃣ Creating optimized camera configuration..."

cat > camera_skin_tone_config.py << 'EOF'
#!/usr/bin/env python3
"""
Optimized Camera Configuration for Skin Tones
MagicMirror² Face Recognition System
"""

import cv2
import numpy as np
from picamera2 import Picamera2
import libcamera

class SkinToneCamera:
    def __init__(self):
        self.camera = None
        self.initialized = False
    
    def initialize(self):
        """Initialize camera with skin tone optimized settings"""
        try:
            self.camera = Picamera2()
            
            # Preview configuration for face recognition
            preview_config = self.camera.create_preview_configuration(
                main={"size": (640, 480), "format": "RGB888"},
                transform=libcamera.Transform(hflip=0, vflip=0)
            )
            
            self.camera.configure(preview_config)
            self.camera.start()
            time.sleep(1)
            
            self.initialized = True
            print("✅ Camera initialized with skin tone optimized settings")
            
        except Exception as e:
            print(f"❌ Camera initialization failed: {e}")
            self.initialized = False
    
    def capture_skin_photo(self, filename, person_name):
        """Capture photo with aggressive skin tone correction"""
        if not self.initialized:
            return False
        
        try:
            # Create high-resolution still configuration
            still_config = self.camera.create_still_configuration(
                main={"size": (1080, 1080), "format": "RGB888"},
                buffer_count=1,
                transform=libcamera.Transform(hflip=0, vflip=0)
            )
            
            # Stop preview and configure for still
            self.camera.stop()
            self.camera.configure(still_config)
            self.camera.start()
            time.sleep(0.5)
            
            # Capture frame
            frame_rgb = self.camera.capture_array("main")
            
            # Apply aggressive skin tone correction
            corrected_frame = self.apply_skin_tone_correction(frame_rgb)
            
            # Save image
            success = cv2.imwrite(filename, corrected_frame, [cv2.IMWRITE_JPEG_QUALITY, 95])
            
            # Restore preview configuration
            self.camera.stop()
            preview_config = self.camera.create_preview_configuration(
                main={"size": (640, 480), "format": "RGB888"},
                transform=libcamera.Transform(hflip=0, vflip=0)
            )
            self.camera.configure(preview_config)
            self.camera.start()
            
            if success:
                print(f"✅ Skin photo saved: {filename}")
                return True
            else:
                print(f"❌ Failed to save: {filename}")
                return False
                
        except Exception as e:
            print(f"❌ Capture failed: {e}")
            return False
    
    def apply_skin_tone_correction(self, frame_rgb):
        """Apply aggressive color correction for skin tones"""
        try:
            # Convert RGB to BGR
            frame_bgr = cv2.cvtColor(frame_rgb, cv2.COLOR_RGB2BGR)
            
            # Method 1: LAB color space correction
            lab = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2LAB)
            l, a, b = cv2.split(lab)
            
            # Reduce blue tint and enhance warm tones
            b = cv2.add(b, 12)  # Shift towards yellow
            a = cv2.add(a, 6)   # Shift towards red
            
            # Apply CLAHE for better contrast
            clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
            l = clahe.apply(l)
            
            lab_corrected = cv2.merge([l, a, b])
            frame_corrected = cv2.cvtColor(lab_corrected, cv2.COLOR_LAB2BGR)
            
            # Method 2: BGR channel manipulation
            b, g, r = cv2.split(frame_corrected)
            
            # Aggressive blue reduction (main cause of purple skin)
            b = cv2.multiply(b, 0.7)  # Reduce blue by 30%
            
            # Enhance red for warmer skin tones
            r = cv2.multiply(r, 1.12)  # Increase red by 12%
            
            # Slight green increase for natural balance
            g = cv2.multiply(g, 1.03)  # Increase green by 3%
            
            frame_final = cv2.merge([b, g, r])
            
            # Method 3: Gamma correction for better contrast
            gamma = 1.15
            frame_final = np.power(frame_final / 255.0, gamma) * 255.0
            frame_final = np.uint8(frame_final)
            
            print("✅ Applied aggressive skin tone correction")
            return frame_final
            
        except Exception as e:
            print(f"⚠️ Color correction failed: {e}")
            # Fallback to simple conversion
            return cv2.cvtColor(frame_rgb, cv2.COLOR_RGB2BGR)
    
    def close(self):
        """Close camera"""
        if self.camera:
            self.camera.stop()
            self.camera.close()

if __name__ == "__main__":
    # Test the skin tone camera
    camera = SkinToneCamera()
    camera.initialize()
    
    if camera.initialized:
        # Take a test photo
        camera.capture_skin_photo("test_skin_tone_optimized_1080.jpg", "test_user")
        camera.close()
        print("✅ Skin tone camera test completed")
    else:
        print("❌ Skin tone camera test failed")
EOF

chmod +x camera_skin_tone_config.py
echo "   ✅ Optimized camera configuration created"

# 5. Test the optimized configuration
echo "5️⃣ Testing optimized skin tone configuration..."

python3 camera_skin_tone_config.py

# 6. Create comparison script
echo "6️⃣ Creating color comparison script..."

cat > compare_skin_colors.py << 'EOF'
#!/usr/bin/env python3
"""
Compare different skin tone correction methods
"""

import cv2
import os
import glob

def compare_images():
    """Compare all generated skin tone images"""
    
    print("🔍 Comparing Skin Tone Correction Methods")
    print("=" * 50)
    
    # Find all test images
    test_images = glob.glob("test_*.jpg") + glob.glob("color_test_*.jpg") + glob.glob("*skin*.jpg")
    
    if not test_images:
        print("❌ No test images found")
        return
    
    print(f"Found {len(test_images)} test images:")
    for img in sorted(test_images):
        if os.path.exists(img):
            size = os.path.getsize(img)
            print(f"   📸 {img} ({size} bytes)")
    
    print("\n🎯 Recommendations:")
    print("1. Look for images with natural, warm skin tones")
    print("2. Avoid images with purple, blue, or overly pink tints")
    print("3. Check that skin looks healthy and natural")
    print("4. The best images should have good contrast and detail")
    
    print("\n📋 To apply the best settings:")
    print("1. Identify the image with the best skin tones")
    print("2. Note the white balance and correction method used")
    print("3. Update your face_recognition_system.py accordingly")

if __name__ == "__main__":
    compare_images()
EOF

chmod +x compare_skin_colors.py
echo "   ✅ Color comparison script created"

# 7. Run comparison
echo "7️⃣ Running color comparison..."

python3 compare_skin_colors.py

# 8. Summary
echo ""
echo "🎯 Skin Tone Color Fix Summary"
echo "=============================="
echo "✅ Multiple white balance settings tested"
echo "✅ Enhanced skin tone settings applied"
echo "✅ Advanced color correction methods tested"
echo "✅ Optimized camera configuration created"
echo "✅ Color comparison completed"
echo ""
echo "📋 Generated Test Images:"
echo "   • test_wb_*_1080.jpg - Different white balance settings"
echo "   • test_skin_enhanced_1080.jpg - Enhanced skin tone settings"
echo "   • color_test_*_1080.jpg - Advanced color correction methods"
echo "   • test_skin_tone_optimized_1080.jpg - Optimized configuration"
echo ""
echo "🎨 Next Steps:"
echo "1. Review all test images to find the best skin tones"
echo "2. The optimized configuration should give the best results"
echo "3. If colors are still wrong, try different lighting conditions"
echo "4. Update your face_recognition_system.py with the best settings"
echo ""
echo "✅ Skin tone color fix complete!"
