#!/usr/bin/env python3
"""
Test script to check rpicam-still parameters
"""

import subprocess
import os

def test_rpicam_parameters():
    """Test different rpicam-still parameter combinations"""
    
    print("="*60)
    print("RPICAM-STILL PARAMETER TEST")
    print("="*60)
    
    # Create test directory
    test_dir = "test_photos"
    if not os.path.exists(test_dir):
        os.makedirs(test_dir)
    
    # Test different parameter combinations
    test_cases = [
        {
            "name": "Basic command",
            "cmd": ["rpicam-still", "-o", f"{test_dir}/test1.jpg", "-t", "1000"]
        },
        {
            "name": "With resolution",
            "cmd": ["rpicam-still", "-o", f"{test_dir}/test2.jpg", "--width", "1080", "--height", "1080", "-t", "1000"]
        },
        {
            "name": "With auto white balance",
            "cmd": ["rpicam-still", "-o", f"{test_dir}/test3.jpg", "--width", "1080", "--height", "1080", "--awb", "auto", "-t", "1000"]
        },
        {
            "name": "With auto exposure",
            "cmd": ["rpicam-still", "-o", f"{test_dir}/test4.jpg", "--width", "1080", "--height", "1080", "--exposure", "auto", "-t", "1000"]
        },
        {
            "name": "With quality",
            "cmd": ["rpicam-still", "-o", f"{test_dir}/test5.jpg", "--width", "1080", "--height", "1080", "--quality", "95", "-t", "1000"]
        },
        {
            "name": "With immediate capture",
            "cmd": ["rpicam-still", "-o", f"{test_dir}/test6.jpg", "--width", "1080", "--height", "1080", "--immediate", "-t", "1000"]
        },
        {
            "name": "Full command without gain",
            "cmd": ["rpicam-still", "-o", f"{test_dir}/test7.jpg", "--width", "1080", "--height", "1080", "--awb", "auto", "--exposure", "auto", "--quality", "95", "--immediate", "-t", "1000"]
        }
    ]
    
    for i, test_case in enumerate(test_cases):
        print(f"\n[TEST {i+1}] {test_case['name']}")
        print(f"Command: {' '.join(test_case['cmd'])}")
        
        try:
            result = subprocess.run(test_case['cmd'], capture_output=True, text=True, timeout=10)
            
            print(f"Return code: {result.returncode}")
            if result.stdout:
                print(f"Stdout: {result.stdout}")
            if result.stderr:
                print(f"Stderr: {result.stderr}")
            
            # Check if photo was created
            photo_path = test_case['cmd'][2]  # -o parameter
            if os.path.exists(photo_path):
                file_size = os.path.getsize(photo_path)
                print(f"✅ Photo created: {photo_path} ({file_size} bytes)")
            else:
                print(f"❌ Photo not created: {photo_path}")
                
        except subprocess.TimeoutExpired:
            print("❌ Command timed out")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    # Clean up test photos
    print(f"\n[INFO] Cleaning up test photos...")
    for i in range(1, 8):
        photo_path = f"{test_dir}/test{i}.jpg"
        if os.path.exists(photo_path):
            os.remove(photo_path)
    
    if os.path.exists(test_dir):
        os.rmdir(test_dir)
    
    print("✅ Test completed")

if __name__ == "__main__":
    test_rpicam_parameters()
