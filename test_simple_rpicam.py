#!/usr/bin/env python3
"""
Simple rpicam-still Test
Tests basic rpicam-still functionality without complex options
"""

import subprocess
import time
import os

def test_simple_rpicam():
    """Test simple rpicam-still commands"""
    
    print("📸 Simple rpicam-still Test")
    print("=" * 40)
    
    # Test 1: Most basic command
    print("\n🔧 Test 1: Most basic rpicam-still")
    try:
        cmd = ["rpicam-still", "-o", "test_basic.jpg", "-t", "2000", "--immediate"]
        print(f"Running: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0 and os.path.exists("test_basic.jpg"):
            file_size = os.path.getsize("test_basic.jpg")
            print(f"✅ SUCCESS - {file_size} bytes")
            os.remove("test_basic.jpg")
        else:
            print(f"❌ FAILED - {result.stderr}")
            
    except Exception as e:
        print(f"❌ FAILED - {e}")
    
    # Test 2: With size
    print("\n🔧 Test 2: With size")
    try:
        cmd = ["rpicam-still", "-o", "test_size.jpg", "--width", "640", "--height", "480", "-t", "2000", "--immediate"]
        print(f"Running: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0 and os.path.exists("test_size.jpg"):
            file_size = os.path.getsize("test_size.jpg")
            print(f"✅ SUCCESS - {file_size} bytes")
            os.remove("test_size.jpg")
        else:
            print(f"❌ FAILED - {result.stderr}")
            
    except Exception as e:
        print(f"❌ FAILED - {e}")
    
    # Test 3: With AWB
    print("\n🔧 Test 3: With AWB")
    try:
        cmd = ["rpicam-still", "-o", "test_awb.jpg", "--width", "640", "--height", "480", "-t", "2000", "--immediate", "--awb", "auto"]
        print(f"Running: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0 and os.path.exists("test_awb.jpg"):
            file_size = os.path.getsize("test_awb.jpg")
            print(f"✅ SUCCESS - {file_size} bytes")
            os.remove("test_awb.jpg")
        else:
            print(f"❌ FAILED - {result.stderr}")
            
    except Exception as e:
        print(f"❌ FAILED - {e}")
    
    # Test 4: With AWB gains
    print("\n🔧 Test 4: With AWB gains")
    try:
        cmd = ["rpicam-still", "-o", "test_gains.jpg", "--width", "640", "--height", "480", "-t", "2000", "--immediate", "--awb", "auto", "--awbgains", "1.8,1.0"]
        print(f"Running: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0 and os.path.exists("test_gains.jpg"):
            file_size = os.path.getsize("test_gains.jpg")
            print(f"✅ SUCCESS - {file_size} bytes")
            os.remove("test_gains.jpg")
        else:
            print(f"❌ FAILED - {result.stderr}")
            
    except Exception as e:
        print(f"❌ FAILED - {e}")
    
    print("\n" + "=" * 40)
    print("🎯 SUMMARY")
    print("If Test 1 passes, rpicam-still is working!")
    print("If all tests pass, your camera is fully functional!")

if __name__ == "__main__":
    test_simple_rpicam()
