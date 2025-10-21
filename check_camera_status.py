#!/usr/bin/env python3
"""
Check camera status and permissions
"""

import subprocess
import os

def check_camera_status():
    """Check camera status and permissions"""
    
    print("="*60)
    print("CAMERA STATUS CHECK")
    print("="*60)
    
    # Check if user is in video group
    try:
        result = subprocess.run(["groups"], capture_output=True, text=True)
        if result.returncode == 0:
            groups = result.stdout.strip()
            print(f"User groups: {groups}")
            if "video" in groups:
                print("✅ User is in video group")
            else:
                print("❌ User is NOT in video group - this may cause camera issues")
                print("   Run: sudo usermod -a -G video $USER")
                print("   Then logout and login again")
        else:
            print("❌ Failed to check user groups")
    except Exception as e:
        print(f"❌ Error checking groups: {e}")
    
    # Check camera permissions
    print(f"\n[INFO] Checking camera permissions...")
    try:
        result = subprocess.run(["ls", "-la", "/dev/video*"], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"Video devices: {result.stdout}")
        else:
            print("No video devices found or permission denied")
    except Exception as e:
        print(f"❌ Error checking video devices: {e}")
    
    # Check if camera is in use
    print(f"\n[INFO] Checking if camera is in use...")
    try:
        result = subprocess.run(["lsof", "/dev/video0"], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"Camera in use by: {result.stdout}")
        else:
            print("Camera not in use")
    except Exception as e:
        print(f"❌ Error checking camera usage: {e}")
    
    # Check rpicam-still version and help
    print(f"\n[INFO] Checking rpicam-still version...")
    try:
        result = subprocess.run(["rpicam-still", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"rpicam-still version: {result.stdout}")
        else:
            print("❌ Failed to get rpicam-still version")
    except Exception as e:
        print(f"❌ Error checking rpicam-still version: {e}")
    
    # Check rpicam-still help
    print(f"\n[INFO] Checking rpicam-still help...")
    try:
        result = subprocess.run(["rpicam-still", "--help"], capture_output=True, text=True)
        if result.returncode == 0:
            print("rpicam-still help available")
            # Look for specific parameters
            help_text = result.stdout
            if "--gain" in help_text:
                print("✅ --gain parameter is supported")
            else:
                print("❌ --gain parameter is NOT supported")
            
            if "--quality" in help_text:
                print("✅ --quality parameter is supported")
            else:
                print("❌ --quality parameter is NOT supported")
        else:
            print("❌ Failed to get rpicam-still help")
    except Exception as e:
        print(f"❌ Error checking rpicam-still help: {e}")
    
    # Test basic camera access
    print(f"\n[INFO] Testing basic camera access...")
    try:
        result = subprocess.run(["rpicam-still", "--list-cameras"], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"Available cameras: {result.stdout}")
        else:
            print(f"❌ Failed to list cameras: {result.stderr}")
    except Exception as e:
        print(f"❌ Error listing cameras: {e}")

if __name__ == "__main__":
    check_camera_status()
