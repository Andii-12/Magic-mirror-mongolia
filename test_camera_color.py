#!/usr/bin/env python3
"""
Test Camera Color Correction
Quick test to check if rpicam-still color correction is working
"""

import subprocess
import os
import time

def test_rpicam_color():
    """Test different rpicam-still color settings"""
    print("🎯 Testing rpicam-still Color Correction")
    print("=" * 40)
    
    # Create test directory
    test_dir = "camera_test"
    os.makedirs(test_dir, exist_ok=True)
    
    # Test different color settings
    tests = [
        {
            "name": "Default Settings",
            "cmd": ["rpicam-still", "-o", f"{test_dir}/test_default.jpg", "-t", "1000"]
        },
        {
            "name": "Daylight White Balance",
            "cmd": ["rpicam-still", "-o", f"{test_dir}/test_daylight.jpg", "-t", "2000", 
                   "--awb", "daylight", "--denoise", "cdn_off", "--gain", "1.0", 
                   "--exposure", "normal", "--brightness", "0.0", "--contrast", "1.0", 
                   "--saturation", "1.2", "--shutter", "10000", "--analoggain", "1.0", 
                   "--digitalgain", "1.0", "--colormatrix", "1"]
        },
        {
            "name": "Incandescent White Balance",
            "cmd": ["rpicam-still", "-o", f"{test_dir}/test_incandescent.jpg", "-t", "2000", 
                   "--awb", "incandescent", "--denoise", "cdn_off", "--gain", "1.0", 
                   "--exposure", "normal", "--brightness", "0.1", "--contrast", "1.1", 
                   "--saturation", "1.3", "--shutter", "15000", "--analoggain", "1.0", 
                   "--digitalgain", "1.0", "--colormatrix", "0", "--awbgains", "1.5,1.0"]
        },
        {
            "name": "Auto White Balance + Fixed Gains",
            "cmd": ["rpicam-still", "-o", f"{test_dir}/test_auto_fixed.jpg", "-t", "2000", 
                   "--awb", "auto", "--denoise", "cdn_off", "--gain", "1.0", 
                   "--exposure", "normal", "--brightness", "0.0", "--contrast", "1.0", 
                   "--saturation", "1.0", "--shutter", "10000"]
        },
        {
            "name": "Greyworld White Balance",
            "cmd": ["rpicam-still", "-o", f"{test_dir}/test_greyworld.jpg", "-t", "2000", 
                   "--awb", "greyworld", "--denoise", "cdn_off", "--gain", "1.0", 
                   "--exposure", "normal", "--brightness", "0.0", "--contrast", "1.0", 
                   "--saturation", "1.0"]
        }
    ]
    
    print("📸 Taking test photos with different color settings...")
    print("   Look at the camera and stay still for each test!")
    print("")
    
    for i, test in enumerate(tests, 1):
        print(f"Test {i}/5: {test['name']}")
        print(f"   Command: {' '.join(test['cmd'])}")
        
        try:
            result = subprocess.run(test['cmd'], capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                file_size = os.path.getsize(test['cmd'][2])
                print(f"   ✅ Success! File size: {file_size} bytes")
            else:
                print(f"   ❌ Failed: {result.stderr}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        print("")
        time.sleep(2)  # Wait between tests
    
    print("🎉 Test complete!")
    print(f"📁 Check the photos in the '{test_dir}/' directory")
    print("   Compare the colors and choose the best settings!")
    print("")
    print("💡 If you see blue/purple tint, try:")
    print("   - Different lighting conditions")
    print("   - Different --awb settings (auto, greyworld, daylight)")
    print("   - Adjust --gain and --exposure values")

if __name__ == "__main__":
    test_rpicam_color()
