#!/usr/bin/env python3
"""
Simple photo capture test
"""

import subprocess
import os
from datetime import datetime

def simple_photo_test():
    """Simple photo capture test"""
    
    print("="*60)
    print("SIMPLE PHOTO CAPTURE TEST")
    print("="*60)
    
    # Create Skin directory structure
    person_name = "TestUser"
    skin_base_dir = os.path.join(os.getcwd(), "Skin")
    person_dir = os.path.join(skin_base_dir, person_name)
    
    try:
        os.makedirs(person_dir, exist_ok=True)
        print(f"✅ Created directory: {person_dir}")
    except Exception as e:
        print(f"❌ Failed to create directory: {e}")
        return False
    
    # Get photo path
    current_date = datetime.now().strftime("%Y-%m-%d")
    photo_filename = f"{current_date}.jpg"
    photo_path = os.path.join(person_dir, photo_filename)
    
    print(f"[INFO] Target photo path: {photo_path}")
    
    # Try the simplest possible rpicam-still command
    print(f"\n[TEST 1] Simplest rpicam-still command")
    cmd1 = ["rpicam-still", "-o", photo_path, "-t", "1000"]
    print(f"Command: {' '.join(cmd1)}")
    
    try:
        result = subprocess.run(cmd1, capture_output=True, text=True, timeout=15)
        print(f"Return code: {result.returncode}")
        if result.stdout:
            print(f"Stdout: {result.stdout}")
        if result.stderr:
            print(f"Stderr: {result.stderr}")
        
        if os.path.exists(photo_path):
            file_size = os.path.getsize(photo_path)
            print(f"✅ Photo created: {photo_path} ({file_size} bytes)")
            return True
        else:
            print(f"❌ Photo not created")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Try with resolution
    print(f"\n[TEST 2] With resolution")
    cmd2 = ["rpicam-still", "-o", photo_path, "--width", "1080", "--height", "1080", "-t", "1000"]
    print(f"Command: {' '.join(cmd2)}")
    
    try:
        result = subprocess.run(cmd2, capture_output=True, text=True, timeout=15)
        print(f"Return code: {result.returncode}")
        if result.stdout:
            print(f"Stdout: {result.stdout}")
        if result.stderr:
            print(f"Stderr: {result.stderr}")
        
        if os.path.exists(photo_path):
            file_size = os.path.getsize(photo_path)
            print(f"✅ Photo created: {photo_path} ({file_size} bytes)")
            return True
        else:
            print(f"❌ Photo not created")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Try with different timeout
    print(f"\n[TEST 3] With longer timeout")
    cmd3 = ["rpicam-still", "-o", photo_path, "--width", "1080", "--height", "1080", "-t", "3000"]
    print(f"Command: {' '.join(cmd3)}")
    
    try:
        result = subprocess.run(cmd3, capture_output=True, text=True, timeout=20)
        print(f"Return code: {result.returncode}")
        if result.stdout:
            print(f"Stdout: {result.stdout}")
        if result.stderr:
            print(f"Stderr: {result.stderr}")
        
        if os.path.exists(photo_path):
            file_size = os.path.getsize(photo_path)
            print(f"✅ Photo created: {photo_path} ({file_size} bytes)")
            return True
        else:
            print(f"❌ Photo not created")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    return False

if __name__ == "__main__":
    success = simple_photo_test()
    if success:
        print(f"\n✅ SIMPLE PHOTO TEST PASSED!")
    else:
        print(f"\n❌ SIMPLE PHOTO TEST FAILED!")
