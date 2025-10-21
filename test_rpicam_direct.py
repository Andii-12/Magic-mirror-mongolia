#!/usr/bin/env python3
"""
Test rpicam command directly
"""

import os
import sys
import subprocess
from datetime import datetime

def test_rpicam_direct():
    """Test rpicam command directly"""
    
    print("="*60)
    print("DIRECT RPICAM TEST")
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
    
    # Test the exact command that the face recognition system uses
    print(f"\n[INFO] Testing rpicam command...")
    cmd = [
        "rpicam-still",
        "-o", photo_path,
        "--width", "1080",
        "--height", "1080",
        "-t", "1000",
        "--immediate"
    ]
    
    print(f"Command: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
        
        print(f"Return code: {result.returncode}")
        if result.stdout:
            print(f"Stdout: {result.stdout}")
        if result.stderr:
            print(f"Stderr: {result.stderr}")
        
        # Check if photo was created
        if os.path.exists(photo_path):
            file_size = os.path.getsize(photo_path)
            print(f"✅ Photo created: {photo_path}")
            print(f"   File size: {file_size} bytes ({file_size/1024:.2f} KB)")
            return True
        else:
            print(f"❌ Photo not created")
            
            # Try to create a test file to see if it's a permission issue
            try:
                test_file = os.path.join(person_dir, "test.txt")
                with open(test_file, 'w') as f:
                    f.write("test")
                print(f"✅ Test file created successfully - permissions OK")
                os.remove(test_file)
            except Exception as e:
                print(f"❌ Failed to create test file - permission issue: {e}")
            
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ Command timed out")
        return False
    except Exception as e:
        print(f"❌ Error running command: {e}")
        return False

if __name__ == "__main__":
    success = test_rpicam_direct()
    if success:
        print(f"\n✅ DIRECT RPICAM TEST PASSED!")
    else:
        print(f"\n❌ DIRECT RPICAM TEST FAILED!")
    
    sys.exit(0 if success else 1)
