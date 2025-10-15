#!/usr/bin/env python3
"""
Camera Color Test Script for MagicMirror²
Tests different camera configurations to fix color issues
"""

import cv2
import time
from picamera2 import Picamera2
import libcamera

def test_camera_configs():
    """Test different camera configurations to find the best color settings"""
    
    print("🎨 Testing Camera Color Configurations")
    print("=" * 50)
    
    configs = [
        {
            "name": "RGB888 Format",
            "config": {
                "main": {"size": (640, 480), "format": "RGB888"},
                "transform": libcamera.Transform(hflip=0, vflip=0)
            }
        },
        {
            "name": "BGR888 Format", 
            "config": {
                "main": {"size": (640, 480), "format": "BGR888"},
                "transform": libcamera.Transform(hflip=0, vflip=0)
            }
        },
        {
            "name": "XRGB8888 Format",
            "config": {
                "main": {"size": (640, 480), "format": "XRGB8888"},
                "transform": libcamera.Transform(hflip=0, vflip=0)
            }
        }
    ]
    
    for i, test_config in enumerate(configs):
        print(f"\n📸 Testing Configuration {i+1}: {test_config['name']}")
        
        try:
            # Initialize camera
            camera = Picamera2()
            camera.configure(test_config['config'])
            camera.start()
            time.sleep(1)  # Let camera stabilize
            
            # Capture frame
            frame = camera.capture_array()
            print(f"   Frame shape: {frame.shape}")
            print(f"   Frame dtype: {frame.dtype}")
            
            # Save test image
            filename = f"test_color_{i+1}_{test_config['name'].lower().replace(' ', '_')}.jpg"
            
            if test_config['name'] == "RGB888 Format":
                # Convert RGB to BGR for OpenCV
                frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
                cv2.imwrite(filename, frame_bgr)
            elif test_config['name'] == "BGR888 Format":
                # Already in BGR format
                cv2.imwrite(filename, frame)
            else:
                # XRGB8888 - convert to BGR
                frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGBA2BGR)
                cv2.imwrite(filename, frame_bgr)
            
            print(f"   ✅ Saved: {filename}")
            
            # Stop camera
            camera.stop()
            camera.close()
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print("\n🎯 Color Test Complete!")
    print("Check the saved images to see which configuration gives the best colors.")
    print("Look for natural skin tones and proper color balance.")

def test_libcamera_still():
    """Test libcamera-still with different color settings"""
    
    print("\n📷 Testing libcamera-still Color Settings")
    print("=" * 50)
    
    import subprocess
    
    settings = [
        {
            "name": "Auto White Balance",
            "cmd": ["libcamera-still", "-o", "test_awb_auto.jpg", "-t", "1000", "-n", "--awb", "auto"]
        },
        {
            "name": "Daylight White Balance", 
            "cmd": ["libcamera-still", "-o", "test_awb_daylight.jpg", "-t", "1000", "-n", "--awb", "daylight"]
        },
        {
            "name": "Cloudy White Balance",
            "cmd": ["libcamera-still", "-o", "test_awb_cloudy.jpg", "-t", "1000", "-n", "--awb", "cloudy"]
        },
        {
            "name": "Tungsten White Balance",
            "cmd": ["libcamera-still", "-o", "test_awb_tungsten.jpg", "-t", "1000", "-n", "--awb", "tungsten"]
        },
        {
            "name": "Fluorescent White Balance",
            "cmd": ["libcamera-still", "-o", "test_awb_fluorescent.jpg", "-t", "1000", "-n", "--awb", "fluorescent"]
        }
    ]
    
    for setting in settings:
        print(f"\n📸 Testing: {setting['name']}")
        
        try:
            result = subprocess.run(setting['cmd'], capture_output=True, text=True, timeout=5)
            
            if result.returncode == 0:
                print(f"   ✅ Success: {setting['cmd'][-2]}")
            else:
                print(f"   ❌ Failed: {result.stderr}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print("\n🎯 libcamera-still Test Complete!")
    print("Check the saved images to see which white balance setting works best.")

if __name__ == "__main__":
    print("🔧 MagicMirror² Camera Color Test")
    print("This script will help identify the best camera settings for proper colors.")
    print("\nMake sure you're in good lighting conditions for accurate testing.")
    print("Press Enter to continue...")
    input()
    
    test_camera_configs()
    test_libcamera_still()
    
    print("\n✅ All tests completed!")
    print("Review the generated test images to determine the best color configuration.")
    print("Update your face_recognition_system.py with the settings that produce the best results.")