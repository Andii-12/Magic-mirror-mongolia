#!/usr/bin/env python3
"""
Simulate the start.sh workflow to test photo saving
"""

import os
import sys
import time
import subprocess
from face_recognition_system import FaceRecognitionSystem

def simulate_start_sh():
    """Simulate the start.sh workflow"""
    
    print("="*60)
    print("SIMULATE START.SH WORKFLOW")
    print("="*60)
    
    # Create Skin directory if it doesn't exist
    skin_base_dir = os.path.join(os.getcwd(), "Skin")
    if not os.path.exists(skin_base_dir):
        os.makedirs(skin_base_dir, exist_ok=True)
        print(f"✅ Created Skin directory: {skin_base_dir}")
    
    # Initialize face recognition system
    print("[INFO] Initializing face recognition system...")
    try:
        face_system = FaceRecognitionSystem()
        print("✅ Face recognition system initialized")
    except Exception as e:
        print(f"❌ Failed to initialize face recognition system: {e}")
        return False
    
    # Simulate the workflow from start.sh
    print(f"\n[INFO] Simulating face recognition workflow...")
    
    # Test 1: Direct face recognition call
    print(f"\n--- Test 1: Direct face recognition call ---")
    try:
        person = face_system.recognize_face_with_camera()
        print(f"[INFO] Face recognition returned: {person}")
        
        if person:
            # Check if photo was saved
            current_date = time.strftime("%Y-%m-%d")
            photo_path = os.path.join(skin_base_dir, person, f"{current_date}.jpg")
            
            print(f"[INFO] Checking for photo: {photo_path}")
            if os.path.exists(photo_path):
                file_size = os.path.getsize(photo_path)
                print(f"✅ Photo found: {photo_path}")
                print(f"   File size: {file_size} bytes")
            else:
                print(f"❌ Photo not found: {photo_path}")
                
                # Check if directory exists
                person_dir = os.path.join(skin_base_dir, person)
                if os.path.exists(person_dir):
                    print(f"✅ Person directory exists: {person_dir}")
                    files = os.listdir(person_dir)
                    print(f"   Files in directory: {files}")
                else:
                    print(f"❌ Person directory does not exist: {person_dir}")
    except Exception as e:
        print(f"❌ Error in face recognition: {e}")
        import traceback
        traceback.print_exc()
    
    # Test 2: Force reset and try again
    print(f"\n--- Test 2: Force reset and try again ---")
    try:
        # Force reset flags
        face_system.photo_saved_this_session = False
        face_system.last_photo_time = 0
        face_system.current_person = None
        
        print(f"[INFO] Flags reset, trying face recognition again...")
        person = face_system.recognize_face_with_camera()
        print(f"[INFO] Face recognition returned: {person}")
        
        if person:
            # Check if photo was saved
            current_date = time.strftime("%Y-%m-%d")
            photo_path = os.path.join(skin_base_dir, person, f"{current_date}.jpg")
            
            print(f"[INFO] Checking for photo: {photo_path}")
            if os.path.exists(photo_path):
                file_size = os.path.getsize(photo_path)
                print(f"✅ Photo found: {photo_path}")
                print(f"   File size: {file_size} bytes")
                return True
            else:
                print(f"❌ Photo still not found: {photo_path}")
    except Exception as e:
        print(f"❌ Error in second test: {e}")
        import traceback
        traceback.print_exc()
    
    return False

if __name__ == "__main__":
    success = simulate_start_sh()
    if success:
        print(f"\n✅ SIMULATE START.SH WORKFLOW PASSED!")
    else:
        print(f"\n❌ SIMULATE START.SH WORKFLOW FAILED!")
    
    sys.exit(0 if success else 1)
