#!/usr/bin/env python3
"""
Bypass proximity detection and test face recognition directly
"""

import os
import sys
import time
from face_recognition_system import FaceRecognitionSystem

def bypass_proximity_test():
    """Bypass proximity detection and test face recognition directly"""
    
    print("="*60)
    print("BYPASS PROXIMITY TEST")
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
    
    # Bypass proximity detection by directly calling face recognition
    print(f"\n[INFO] Bypassing proximity detection...")
    
    # Set up the system as if proximity was detected
    face_system.is_active = True
    face_system.current_distance = 50  # Simulate close distance
    face_system.face_recognition_attempted = False
    face_system.current_person = None
    face_system.photo_saved_this_session = False
    face_system.last_photo_time = 0
    
    print(f"[INFO] System state set up for face recognition")
    print(f"[DEBUG] is_active: {face_system.is_active}")
    print(f"[DEBUG] current_distance: {face_system.current_distance}")
    print(f"[DEBUG] face_recognition_attempted: {face_system.face_recognition_attempted}")
    print(f"[DEBUG] current_person: {face_system.current_person}")
    print(f"[DEBUG] photo_saved_this_session: {face_system.photo_saved_this_session}")
    
    try:
        # Directly call face recognition
        print(f"\n[INFO] Calling face recognition directly...")
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
                print(f"❌ Photo not found: {photo_path}")
                
                # Check if directory exists
                person_dir = os.path.join(skin_base_dir, person)
                if os.path.exists(person_dir):
                    print(f"✅ Person directory exists: {person_dir}")
                    files = os.listdir(person_dir)
                    print(f"   Files in directory: {files}")
                else:
                    print(f"❌ Person directory does not exist: {person_dir}")
                    print(f"   Skin directory contents: {os.listdir(skin_base_dir)}")
        else:
            print(f"❌ Face recognition returned None or Unknown")
            
    except Exception as e:
        print(f"❌ Error in face recognition: {e}")
        import traceback
        traceback.print_exc()
    
    return False

if __name__ == "__main__":
    success = bypass_proximity_test()
    if success:
        print(f"\n✅ BYPASS PROXIMITY TEST PASSED!")
    else:
        print(f"\n❌ BYPASS PROXIMITY TEST FAILED!")
    
    sys.exit(0 if success else 1)
