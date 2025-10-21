#!/usr/bin/env python3
"""
Debug script for face recognition system
"""

import os
import sys
import platform
import time
import json
from datetime import datetime

def debug_face_recognition():
    """Debug the face recognition system"""
    
    print("="*60)
    print("FACE RECOGNITION DEBUG")
    print("="*60)
    
    # Check platform
    current_platform = platform.system()
    print(f"[INFO] Platform: {current_platform}")
    
    # Check if we're on Windows
    if current_platform == "Windows":
        print("[INFO] Windows detected - will simulate face recognition")
        
        # Test the face recognition system
        try:
            from face_recognition_system import FaceRecognitionSystem
            face_system = FaceRecognitionSystem()
            
            # Simulate face recognition
            print("[INFO] Simulating face recognition...")
            person = face_system.recognize_face_with_camera()
            
            print(f"[INFO] Recognized person: {person}")
            
            # Check if photo was saved
            if person:
                skin_base_dir = os.path.join(os.getcwd(), "Skin")
                person_dir = os.path.join(skin_base_dir, person)
                current_date = datetime.now().strftime("%Y-%m-%d")
                photo_path = os.path.join(person_dir, f"{current_date}.jpg")
                
                print(f"[INFO] Checking for photo: {photo_path}")
                if os.path.exists(photo_path):
                    file_size = os.path.getsize(photo_path)
                    print(f"✅ Photo found: {photo_path}")
                    print(f"   File size: {file_size} bytes")
                else:
                    print(f"❌ Photo not found: {photo_path}")
                    
                    # Check if directory exists
                    if os.path.exists(person_dir):
                        print(f"✅ Person directory exists: {person_dir}")
                        files = os.listdir(person_dir)
                        print(f"   Files in directory: {files}")
                    else:
                        print(f"❌ Person directory does not exist: {person_dir}")
                        
                        # Check if Skin directory exists
                        if os.path.exists(skin_base_dir):
                            print(f"✅ Skin directory exists: {skin_base_dir}")
                            dirs = os.listdir(skin_base_dir)
                            print(f"   Directories in Skin: {dirs}")
                        else:
                            print(f"❌ Skin directory does not exist: {skin_base_dir}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error testing face recognition: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    else:
        print("[INFO] Linux/Raspberry Pi detected - checking camera commands")
        
        # Check if camera commands are available
        import subprocess
        
        # Check rpicam-still
        try:
            result = subprocess.run(["which", "rpicam-still"], capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✅ rpicam-still found: {result.stdout.strip()}")
            else:
                print(f"❌ rpicam-still not found")
        except Exception as e:
            print(f"❌ Error checking rpicam-still: {e}")
        
        # Check libcamera-still
        try:
            result = subprocess.run(["which", "libcamera-still"], capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✅ libcamera-still found: {result.stdout.strip()}")
            else:
                print(f"❌ libcamera-still not found")
        except Exception as e:
            print(f"❌ Error checking libcamera-still: {e}")
        
        return True

if __name__ == "__main__":
    success = debug_face_recognition()
    if success:
        print(f"\n✅ FACE RECOGNITION DEBUG COMPLETED!")
    else:
        print(f"\n❌ FACE RECOGNITION DEBUG FAILED!")
    
    sys.exit(0 if success else 1)
