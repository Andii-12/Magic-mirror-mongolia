#!/usr/bin/env python3
"""
Test script to verify rpicam-still fix
Tests the exact same command that the face recognition system uses
"""

import subprocess
import os
import time

def test_rpicam_fix():
    """Test the exact rpicam-still command used in face_recognition_system.py"""
    
    print("🔧 Testing rpicam-still fix")
    print("=" * 40)
    
    # Create test directory
    test_dir = "test_skin_photos"
    os.makedirs(test_dir, exist_ok=True)
    
    # Test the exact command from face_recognition_system.py
    photo_path = os.path.join(test_dir, "test_fix.jpg")
    
    cmd = [
        "rpicam-still",
        "-o", photo_path,
        "--width", "1080",
        "--height", "1080",
        "-t", "3000",  # 3 second timeout
        "--immediate",  # Capture immediately
        "--awb", "auto",  # Auto white balance
        "--awbgains", "1.8,1.0"  # Boost red channel
    ]
    
    print(f"📸 Running command: {' '.join(cmd)}")
    print(f"📁 Target file: {photo_path}")
    print(f"📁 Working directory: {os.getcwd()}")
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
        
        print(f"\n📊 Results:")
        print(f"   Return code: {result.returncode}")
        print(f"   stdout: {result.stdout}")
        print(f"   stderr: {result.stderr}")
        print(f"   File exists: {os.path.exists(photo_path)}")
        
        if os.path.exists(photo_path):
            file_size = os.path.getsize(photo_path)
            print(f"   File size: {file_size} bytes ({file_size/1024:.2f} KB)")
            
            if file_size > 0:
                print(f"\n✅ SUCCESS! Photo captured successfully")
                print(f"   This means the fix should work in face_recognition_system.py")
                return True
            else:
                print(f"\n❌ FAILED! Photo file is empty")
                return False
        else:
            print(f"\n❌ FAILED! Photo file was not created")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"\n❌ FAILED! Command timed out")
        return False
    except Exception as e:
        print(f"\n❌ FAILED! Error: {e}")
        return False

if __name__ == "__main__":
    success = test_rpicam_fix()
    
    if success:
        print(f"\n🎯 The fix should work! Try running ./start.sh now")
    else:
        print(f"\n⚠️  There may still be issues. Check the error messages above")
