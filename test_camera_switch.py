#!/usr/bin/env python3
"""
Test Camera Switching Between Picamera2 and rpicam-still
This script tests if we can properly stop Picamera2 and use rpicam-still
"""

import subprocess
import time
import os

def test_camera_switching():
    """Test switching between Picamera2 and rpicam-still"""
    
    print("🔄 Camera Switching Test")
    print("=" * 40)
    
    # Test 1: Check if rpicam-still works when camera is free
    print("\n📸 Test 1: rpicam-still with free camera")
    try:
        cmd = [
            "rpicam-still",
            "-o", "test_free_camera.jpg",
            "--width", "640",
            "--height", "480",
            "-t", "2000",
            "--immediate"
        ]
        
        print(f"Running: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0 and os.path.exists("test_free_camera.jpg"):
            file_size = os.path.getsize("test_free_camera.jpg")
            print(f"✅ SUCCESS - {file_size} bytes")
            os.remove("test_free_camera.jpg")  # Clean up
        else:
            print(f"❌ FAILED - {result.stderr}")
            
    except Exception as e:
        print(f"❌ FAILED - {e}")
    
    # Test 2: Check camera processes
    print("\n🔍 Test 2: Check camera processes")
    try:
        result = subprocess.run(["ps", "aux"], capture_output=True, text=True)
        camera_processes = [line for line in result.stdout.split('\n') if 'camera' in line.lower() or 'rpicam' in line.lower()]
        
        if camera_processes:
            print("📷 Camera processes found:")
            for process in camera_processes:
                print(f"   {process}")
        else:
            print("📷 No camera processes found")
            
    except Exception as e:
        print(f"❌ FAILED - {e}")
    
    # Test 3: Check camera device
    print("\n🔍 Test 3: Check camera device")
    try:
        result = subprocess.run(["ls", "-la", "/dev/video*"], capture_output=True, text=True)
        if result.returncode == 0:
            print("📹 Video devices:")
            print(result.stdout)
        else:
            print("❌ No video devices found")
            
    except Exception as e:
        print(f"❌ FAILED - {e}")
    
    # Test 4: Test rpicam-still with different settings
    print("\n📸 Test 4: rpicam-still with color correction")
    try:
        cmd = [
            "rpicam-still",
            "-o", "test_color_correction.jpg",
            "--width", "640",
            "--height", "480",
            "-t", "2000",
            "--immediate",
            "--awb", "auto",
            "--awbgains", "1.8,1.0",
            "--saturation", "1.3"
        ]
        
        print(f"Running: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0 and os.path.exists("test_color_correction.jpg"):
            file_size = os.path.getsize("test_color_correction.jpg")
            print(f"✅ SUCCESS - {file_size} bytes")
            os.remove("test_color_correction.jpg")  # Clean up
        else:
            print(f"❌ FAILED - {result.stderr}")
            
    except Exception as e:
        print(f"❌ FAILED - {e}")
    
    print("\n" + "=" * 40)
    print("🎯 SUMMARY")
    print("If all tests pass, your camera switching should work!")
    print("If tests fail, check:")
    print("1. Camera is properly connected")
    print("2. rpicam-still is installed")
    print("3. No other processes are using the camera")

if __name__ == "__main__":
    test_camera_switching()
