#!/usr/bin/env python3
"""
Test script for skin photo capture functionality
"""

import os
import sys
import platform
import subprocess
from datetime import datetime

def test_skin_photo_capture():
    """Test the skin photo capture functionality"""
    
    print("="*60)
    print("SKIN PHOTO CAPTURE TEST")
    print("="*60)
    
    # Test person name
    person_name = "TestUser"
    
    # Create Skin directory if it doesn't exist
    skin_base_dir = os.path.join(os.getcwd(), "Skin")
    person_dir = os.path.join(skin_base_dir, person_name)
    
    print(f"[INFO] Base directory: {skin_base_dir}")
    print(f"[INFO] Person directory: {person_dir}")
    
    # Create directories if they don't exist
    try:
        os.makedirs(person_dir, exist_ok=True)
        print(f"✅ Directories created/verified: {person_dir}")
        
        # Verify directory was actually created
        if os.path.isdir(person_dir):
            print(f"✅ Directory exists and is accessible")
        else:
            print(f"[ERROR] Directory not accessible: {person_dir}")
            return False
            
    except Exception as e:
        print(f"[ERROR] Failed to create directory: {e}")
        return False
    
    # Get current date for filename
    current_date = datetime.now().strftime("%Y-%m-%d")
    photo_filename = f"{current_date}.jpg"
    photo_path = os.path.join(person_dir, photo_filename)
    
    print(f"[INFO] Photo filename: {photo_filename}")
    print(f"[INFO] Full path: {photo_path}")
    
    # Check platform
    current_platform = platform.system()
    print(f"[INFO] Platform detected: {current_platform}")
    
    # Windows test mode
    if current_platform == "Windows":
        print(f"[TEST MODE] Creating test file...")
        try:
            # Create a simple test file
            with open(photo_path, 'w') as f:
                f.write(f"Test photo for {person_name} on {current_date}\n")
            
            # Verify file was created
            if os.path.exists(photo_path):
                file_size = os.path.getsize(photo_path)
                print(f"✅ Test file created: {photo_path}")
                print(f"   File size: {file_size} bytes")
                return True
            else:
                print(f"[ERROR] Test file not created")
                return False
        except Exception as e:
            print(f"[ERROR] Failed to create test file: {e}")
            return False
    
    # Linux/Raspberry Pi - test camera commands
    print(f"[INFO] Testing camera commands...")
    
    # Test rpicam-still
    print(f"[INFO] Testing rpicam-still...")
    try:
        result_check = subprocess.run(["which", "rpicam-still"], capture_output=True, text=True)
        if result_check.returncode == 0:
            print(f"✅ rpicam-still found: {result_check.stdout.strip()}")
            
            # Try to capture a photo - minimal working command
            cmd = [
                "rpicam-still",
                "-o", photo_path,
                "--width", "1080",
                "--height", "1080",
                "-t", "1000",
                "--immediate"
            ]
            
            print(f"[INFO] Running rpicam command: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
            
            print(f"[DEBUG] rpicam return code: {result.returncode}")
            print(f"[DEBUG] rpicam stdout: {result.stdout}")
            print(f"[DEBUG] rpicam stderr: {result.stderr}")
            print(f"[DEBUG] Photo file exists after capture: {os.path.exists(photo_path)}")
            
            if result.returncode == 0 and os.path.exists(photo_path):
                file_size = os.path.getsize(photo_path)
                print(f"✅ Photo captured with rpicam-still!")
                print(f"   Path: {photo_path}")
                print(f"   Size: {file_size} bytes ({file_size/1024:.2f} KB)")
                return True
            else:
                print(f"[WARNING] rpicam-still failed: {result.stderr}")
        else:
            print(f"[WARNING] rpicam-still not found")
    except Exception as e:
        print(f"[WARNING] rpicam-still test failed: {e}")
    
    # Test libcamera-still
    print(f"[INFO] Testing libcamera-still...")
    try:
        result_check = subprocess.run(["which", "libcamera-still"], capture_output=True, text=True)
        if result_check.returncode == 0:
            print(f"✅ libcamera-still found: {result_check.stdout.strip()}")
            
            # Try to capture a photo
            cmd = [
                "libcamera-still",
                "-o", photo_path,
                "--width", "1080",
                "--height", "1080",
                "-t", "1000",
                "-n",
                "--awb", "auto",
                "--metering", "average",
                "--exposure", "auto",
                "--gain", "auto",
                "--denoise", "auto"
            ]
            
            print(f"[INFO] Running libcamera command: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            
            print(f"[DEBUG] libcamera return code: {result.returncode}")
            print(f"[DEBUG] libcamera stdout: {result.stdout}")
            print(f"[DEBUG] libcamera stderr: {result.stderr}")
            print(f"[DEBUG] Photo file exists after capture: {os.path.exists(photo_path)}")
            
            if result.returncode == 0 and os.path.exists(photo_path):
                file_size = os.path.getsize(photo_path)
                print(f"✅ Photo captured with libcamera-still!")
                print(f"   Path: {photo_path}")
                print(f"   Size: {file_size} bytes ({file_size/1024:.2f} KB)")
                return True
            else:
                print(f"[WARNING] libcamera-still failed: {result.stderr}")
        else:
            print(f"[WARNING] libcamera-still not found")
    except Exception as e:
        print(f"[WARNING] libcamera-still test failed: {e}")
    
    print(f"\n[ERROR] All camera capture methods failed!")
    return False

if __name__ == "__main__":
    success = test_skin_photo_capture()
    if success:
        print(f"\n✅ SKIN PHOTO CAPTURE TEST PASSED!")
    else:
        print(f"\n❌ SKIN PHOTO CAPTURE TEST FAILED!")
    
    sys.exit(0 if success else 1)
