#!/usr/bin/env python3
"""
Color Correction Test Script for MagicMirror²
Tests different color correction methods to fix blue-purple skin tone issues
"""

import cv2
import numpy as np
import os
import sys
from datetime import datetime

def test_color_correction_methods():
    """Test different color correction methods on a sample image"""
    
    print("🎨 Color Correction Test Script")
    print("=" * 40)
    
    # Check if we have a test image
    test_image_path = "test_skin_photo.jpg"
    if not os.path.exists(test_image_path):
        print(f"❌ Test image not found: {test_image_path}")
        print("   Please take a photo first using the face recognition system")
        return
    
    # Load the test image
    print(f"📸 Loading test image: {test_image_path}")
    image = cv2.imread(test_image_path)
    if image is None:
        print("❌ Could not load test image")
        return
    
    print(f"✅ Image loaded: {image.shape}")
    
    # Create output directory
    output_dir = "color_correction_tests"
    os.makedirs(output_dir, exist_ok=True)
    
    # Method 1: rpicam-still with different color correction settings
    print("\n🔧 Method 1: rpicam-still color correction (PRIMARY METHOD)")
    try:
        import subprocess
        
        # Test different rpicam-still settings for blue-purple fix
        test_settings = [
            {
                "name": "blue_fix_primary",
                "cmd": [
                    "rpicam-still", "-o", f"{output_dir}/blue_fix_primary.jpg",
                    "--width", "1080", "--height", "1080", "-t", "2000",
                    "--immediate", "--awb", "auto", "--awbgains", "1.8,1.0",
                    "--saturation", "1.3", "--brightness", "0.1", "--contrast", "1.1",
                    "--shutter", "15000", "--colormatrix", "0", "--ev", "0.2"
                ]
            },
            {
                "name": "daylight_wb_boost_red", 
                "cmd": [
                    "rpicam-still", "-o", f"{output_dir}/daylight_wb_boost_red.jpg",
                    "--width", "1080", "--height", "1080", "-t", "2000",
                    "--immediate", "--awb", "daylight", "--awbgains", "2.0,1.0",
                    "--saturation", "1.4", "--brightness", "0.2"
                ]
            },
            {
                "name": "incandescent_wb_aggressive",
                "cmd": [
                    "rpicam-still", "-o", f"{output_dir}/incandescent_wb_aggressive.jpg",
                    "--width", "1080", "--height", "1080", "-t", "2000",
                    "--immediate", "--awb", "incandescent", "--awbgains", "2.2,1.0",
                    "--saturation", "1.5", "--brightness", "0.3", "--contrast", "1.2"
                ]
            },
            {
                "name": "manual_gains_high_red",
                "cmd": [
                    "rpicam-still", "-o", f"{output_dir}/manual_gains_high_red.jpg",
                    "--width", "1080", "--height", "1080", "-t", "2000",
                    "--immediate", "--awb", "off", "--awbgains", "2.5,1.0",
                    "--saturation", "1.6", "--brightness", "0.4"
                ]
            }
        ]
        
        for setting in test_settings:
            print(f"   Testing: {setting['name']}")
            result = subprocess.run(setting['cmd'], capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                print(f"   ✅ {setting['name']} - Success")
            else:
                print(f"   ❌ {setting['name']} - Failed: {result.stderr}")
                
    except Exception as e:
        print(f"   ❌ rpicam-still test failed: {e}")
    
    # Method 2: ImageMagick color correction
    print("\n🔧 Method 2: ImageMagick color correction")
    try:
        import subprocess
        
        # Test different ImageMagick corrections
        magick_tests = [
            {
                "name": "basic_correction",
                "cmd": [
                    "convert", test_image_path,
                    "-colorspace", "RGB",
                    "-channel", "R", "-evaluate", "multiply", "1.3",
                    "-channel", "B", "-evaluate", "multiply", "0.8",
                    "+channel", "-gamma", "1.2", "-saturation", "120%",
                    f"{output_dir}/magick_basic.jpg"
                ]
            },
            {
                "name": "aggressive_correction",
                "cmd": [
                    "convert", test_image_path,
                    "-colorspace", "RGB",
                    "-channel", "R", "-evaluate", "multiply", "1.5",
                    "-channel", "G", "-evaluate", "multiply", "1.1", 
                    "-channel", "B", "-evaluate", "multiply", "0.7",
                    "+channel", "-gamma", "1.3", "-saturation", "130%",
                    "-brightness-contrast", "8x8",
                    f"{output_dir}/magick_aggressive.jpg"
                ]
            },
            {
                "name": "color_matrix_correction",
                "cmd": [
                    "convert", test_image_path,
                    "-colorspace", "RGB",
                    "-color-matrix", "1.3,0,0,0,1.1,0,0,0,0.8",
                    "-gamma", "1.2", "-saturation", "125%",
                    f"{output_dir}/magick_matrix.jpg"
                ]
            }
        ]
        
        for test in magick_tests:
            print(f"   Testing: {test['name']}")
            result = subprocess.run(test['cmd'], capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                print(f"   ✅ {test['name']} - Success")
            else:
                print(f"   ❌ {test['name']} - Failed: {result.stderr}")
                
    except Exception as e:
        print(f"   ❌ ImageMagick test failed: {e}")
    
    # Method 3: OpenCV color correction
    print("\n🔧 Method 3: OpenCV color correction")
    try:
        # Load original image
        img = cv2.imread(test_image_path)
        
        # Method 3a: LAB color space correction
        lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        b = cv2.subtract(b, 15)  # Reduce blue
        a = cv2.add(a, 8)        # Increase red-green
        lab_corrected = cv2.merge([l, a, b])
        lab_result = cv2.cvtColor(lab_corrected, cv2.COLOR_LAB2BGR)
        cv2.imwrite(f"{output_dir}/opencv_lab.jpg", lab_result)
        print("   ✅ LAB correction - Success")
        
        # Method 3b: RGB channel adjustment
        b, g, r = cv2.split(img)
        r = cv2.multiply(r, 1.3)  # Boost red
        g = cv2.multiply(g, 1.1)  # Slight green boost
        b = cv2.multiply(b, 0.7)  # Reduce blue
        rgb_result = cv2.merge([b, g, r])
        rgb_result = np.clip(rgb_result, 0, 255).astype(np.uint8)
        cv2.imwrite(f"{output_dir}/opencv_rgb.jpg", rgb_result)
        print("   ✅ RGB correction - Success")
        
        # Method 3c: Combined approach
        combined = cv2.addWeighted(lab_result, 0.7, rgb_result, 0.3, 0)
        cv2.imwrite(f"{output_dir}/opencv_combined.jpg", combined)
        print("   ✅ Combined correction - Success")
        
    except Exception as e:
        print(f"   ❌ OpenCV test failed: {e}")
    
    print(f"\n📁 Results saved in: {output_dir}/")
    print("   Compare the different methods to see which works best for your setup")
    print("\n💡 Recommendations:")
    print("   1. Check the rpicam-still results first (ONLY method used now)")
    print("   2. Look for 'blue_fix_primary' - this matches your system settings")
    print("   3. If still blue-purple, try 'manual_gains_high_red' or 'incandescent_wb_aggressive'")
    print("   4. ImageMagick correction is applied automatically if rpicam-still succeeds")
    print("\n🎯 Your system now uses ONLY rpicam-still for photo capture!")
    print("   No more Picamera2/OpenCV mixing that caused color issues")

if __name__ == "__main__":
    test_color_correction_methods()
