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
            "name": "Auto White Balance",
            "cmd": ["rpicam-still", "-o", f"{test_dir}/test_awb_auto.jpg", "-t", "1000", "--awb", "auto"]
        },
        {
            "name": "Greyworld White Balance",
            "cmd": ["rpicam-still", "-o", f"{test_dir}/test_awb_greyworld.jpg", "-t", "1000", "--awb", "greyworld"]
        },
        {
            "name": "Fixed Gain + AWB",
            "cmd": ["rpicam-still", "-o", f"{test_dir}/test_fixed_gain.jpg", "-t", "1000", "--awb", "auto", "--gain", "1.0"]
        },
        {
            "name": "Full Color Correction",
            "cmd": ["rpicam-still", "-o", f"{test_dir}/test_full_correction.jpg", "-t", "1000", 
                   "--awb", "auto", "--denoise", "off", "--gain", "1.0", 
                   "--exposure", "normal", "--brightness", "0.0", "--contrast", "1.0", "--saturation", "1.0"]
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
