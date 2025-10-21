#!/usr/bin/env python3
"""
Quick rpicam-still Color Test
Tests different rpicam-still settings to fix blue-purple skin tone issues
"""

import subprocess
import os
import time

def test_rpicam_color_settings():
    """Test different rpicam-still color settings"""
    
    print("🎨 rpicam-still Color Correction Test")
    print("=" * 50)
    
    # Create output directory
    output_dir = "rpicam_color_tests"
    os.makedirs(output_dir, exist_ok=True)
    
    # Test settings specifically for blue-purple fix
    test_settings = [
        {
            "name": "current_system",
            "description": "Your current system settings",
            "cmd": [
                "rpicam-still", "-o", f"{output_dir}/current_system.jpg",
                "--width", "1080", "--height", "1080", "-t", "2000",
                "--immediate", "--awb", "auto", "--awbgains", "1.8,1.0",
                "--saturation", "1.3", "--brightness", "0.1", "--contrast", "1.1",
                "--shutter", "15000", "--colormatrix", "0", "--ev", "0.2"
            ]
        },
        {
            "name": "aggressive_red_boost",
            "description": "Aggressive red boost to counter blue",
            "cmd": [
                "rpicam-still", "-o", f"{output_dir}/aggressive_red_boost.jpg",
                "--width", "1080", "--height", "1080", "-t", "2000",
                "--immediate", "--awb", "off", "--awbgains", "2.5,1.0",
                "--saturation", "1.6", "--brightness", "0.4", "--contrast", "1.3"
            ]
        },
        {
            "name": "incandescent_warm",
            "description": "Incandescent white balance for warm tones",
            "cmd": [
                "rpicam-still", "-o", f"{output_dir}/incandescent_warm.jpg",
                "--width", "1080", "--height", "1080", "-t", "2000",
                "--immediate", "--awb", "incandescent", "--awbgains", "2.2,1.0",
                "--saturation", "1.5", "--brightness", "0.3"
            ]
        },
        {
            "name": "daylight_boost",
            "description": "Daylight with red boost",
            "cmd": [
                "rpicam-still", "-o", f"{output_dir}/daylight_boost.jpg",
                "--width", "1080", "--height", "1080", "-t", "2000",
                "--immediate", "--awb", "daylight", "--awbgains", "2.0,1.0",
                "--saturation", "1.4", "--brightness", "0.2"
            ]
        },
        {
            "name": "manual_high_red",
            "description": "Manual settings with very high red gain",
            "cmd": [
                "rpicam-still", "-o", f"{output_dir}/manual_high_red.jpg",
                "--width", "1080", "--height", "1080", "-t", "2000",
                "--immediate", "--awb", "off", "--awbgains", "3.0,1.0",
                "--saturation", "1.8", "--brightness", "0.5", "--contrast", "1.4"
            ]
        }
    ]
    
    print(f"📸 Testing {len(test_settings)} different rpicam-still settings...")
    print(f"📁 Results will be saved in: {output_dir}/")
    print()
    
    successful_tests = []
    
    for i, setting in enumerate(test_settings, 1):
        print(f"[{i}/{len(test_settings)}] Testing: {setting['name']}")
        print(f"   Description: {setting['description']}")
        
        try:
            result = subprocess.run(setting['cmd'], capture_output=True, text=True, timeout=15)
            
            if result.returncode == 0:
                file_path = f"{output_dir}/{setting['name']}.jpg"
                if os.path.exists(file_path):
                    file_size = os.path.getsize(file_path)
                    print(f"   ✅ SUCCESS - {file_size} bytes")
                    successful_tests.append(setting['name'])
                else:
                    print(f"   ❌ FAILED - File not created")
            else:
                print(f"   ❌ FAILED - {result.stderr.strip()}")
                
        except subprocess.TimeoutExpired:
            print(f"   ❌ FAILED - Timeout")
        except Exception as e:
            print(f"   ❌ FAILED - {e}")
        
        print()
        time.sleep(1)  # Small delay between tests
    
    print("=" * 50)
    print(f"📊 RESULTS SUMMARY")
    print(f"   Successful tests: {len(successful_tests)}/{len(test_settings)}")
    
    if successful_tests:
        print(f"   ✅ Working settings: {', '.join(successful_tests)}")
        print(f"\n💡 Next steps:")
        print(f"   1. Check the images in {output_dir}/")
        print(f"   2. Find the one with the best skin tone")
        print(f"   3. Update your face_recognition_system.py with those settings")
    else:
        print(f"   ❌ No successful captures")
        print(f"   Check camera connection and rpicam-still installation")
    
    print(f"\n🎯 Remember: Your system now uses ONLY rpicam-still!")
    print(f"   No more Picamera2 mixing that caused color issues")

if __name__ == "__main__":
    test_rpicam_color_settings()
