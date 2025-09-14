#!/usr/bin/env python3
"""
Camera Test Script for Face Recognition
Tests camera functionality and provides troubleshooting
"""

import cv2
import os
import sys
import subprocess

def check_camera_devices():
    """Check for available camera devices"""
    print("🔍 Checking camera devices...")
    
    # Check /dev/video* devices
    try:
        result = subprocess.run(['ls', '/dev/video*'], capture_output=True, text=True)
        if result.returncode == 0:
            devices = result.stdout.strip().split('\n')
            print(f"✅ Found camera devices: {devices}")
            return devices
        else:
            print("❌ No camera devices found in /dev/video*")
            return []
    except Exception as e:
        print(f"❌ Error checking devices: {e}")
        return []

def test_camera_backends():
    """Test different camera backends"""
    print("\n🧪 Testing camera backends...")
    
    backends = [
        (cv2.CAP_V4L2, "V4L2"),
        (cv2.CAP_GSTREAMER, "GStreamer"),
        (cv2.CAP_ANY, "Any"),
    ]
    
    working_cameras = []
    
    for backend, name in backends:
        print(f"\n📹 Testing {name} backend...")
        for camera_index in range(3):  # Test cameras 0, 1, 2
            try:
                cap = cv2.VideoCapture(camera_index, backend)
                if cap.isOpened():
                    ret, frame = cap.read()
                    if ret and frame is not None:
                        print(f"   ✅ Camera {camera_index} working with {name}")
                        working_cameras.append((backend, camera_index, name))
                    else:
                        print(f"   ❌ Camera {camera_index} opened but can't read frames")
                    cap.release()
                else:
                    print(f"   ❌ Camera {camera_index} failed to open with {name}")
            except Exception as e:
                print(f"   ❌ Camera {camera_index} error with {name}: {e}")
    
    return working_cameras

def test_camera_live(backend, camera_index, name):
    """Test camera with live preview"""
    print(f"\n📺 Testing live camera {camera_index} with {name}...")
    
    cap = cv2.VideoCapture(camera_index, backend)
    if not cap.isOpened():
        print(f"❌ Could not open camera {camera_index}")
        return False
    
    # Configure camera
    try:
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        cap.set(cv2.CAP_PROP_FPS, 30)
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
    except:
        pass
    
    print("📋 Instructions:")
    print("   - Look at the camera")
    print("   - Press 'q' to quit")
    print("   - Press 's' to save a test image")
    print("")
    
    frame_count = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            print("❌ Failed to read frame")
            break
        
        frame_count += 1
        
        # Add frame counter
        cv2.putText(frame, f"Frame: {frame_count}", (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.putText(frame, f"Camera: {camera_index} ({name})", (10, 70), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.putText(frame, "Press 'q' to quit, 's' to save", (10, 110), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        # Show frame
        cv2.imshow(f'Camera Test - {name}', frame)
        
        # Handle key presses
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('s'):
            filename = f"test_camera_{camera_index}_{name.lower()}.jpg"
            cv2.imwrite(filename, frame)
            print(f"✅ Saved test image: {filename}")
    
    cap.release()
    cv2.destroyAllWindows()
    
    print(f"✅ Camera {camera_index} test completed")
    return True

def check_permissions():
    """Check camera permissions"""
    print("\n🔐 Checking camera permissions...")
    
    try:
        # Check if user is in video group
        result = subprocess.run(['groups'], capture_output=True, text=True)
        if 'video' in result.stdout:
            print("✅ User is in video group")
        else:
            print("❌ User is NOT in video group")
            print("   Fix: sudo usermod -a -G video $USER")
            print("   Then logout and login again")
    except Exception as e:
        print(f"❌ Error checking permissions: {e}")

def main():
    """Main function"""
    print("📹 Camera Test for Face Recognition")
    print("=" * 40)
    
    # Check camera devices
    devices = check_camera_devices()
    
    # Check permissions
    check_permissions()
    
    # Test camera backends
    working_cameras = test_camera_backends()
    
    if not working_cameras:
        print("\n❌ No working cameras found!")
        print("\n🔧 Troubleshooting:")
        print("   1. Check camera connection")
        print("   2. Try: sudo usermod -a -G video $USER")
        print("   3. Reboot and try again")
        print("   4. Check: ls /dev/video*")
        print("   5. Try different camera")
        return False
    
    print(f"\n✅ Found {len(working_cameras)} working cameras:")
    for i, (backend, camera_index, name) in enumerate(working_cameras):
        print(f"   {i+1}. Camera {camera_index} ({name})")
    
    # Test first working camera
    if working_cameras:
        backend, camera_index, name = working_cameras[0]
        print(f"\n🎥 Testing camera {camera_index} ({name})...")
        test_camera_live(backend, camera_index, name)
    
    print("\n🎉 Camera test completed!")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
