#!/usr/bin/env python3
"""
Force photo test by manually resetting flags
"""

import os
import sys
import time
from face_recognition_system import FaceRecognitionSystem

def force_photo_test():
    """Force photo test by manually resetting flags"""
    
    print("="*60)
    print("FORCE PHOTO TEST")
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
    
    # Force reset all flags
    test_user = "Andii"
    print(f"\n[INFO] Force resetting all photo flags...")
    print(f"[DEBUG] Before reset - photo_saved_this_session: {face_system.photo_saved_this_session}")
    print(f"[DEBUG] Before reset - last_photo_time: {face_system.last_photo_time}")
    
    # Force reset
    face_system.photo_saved_this_session = False
    face_system.last_photo_time = 0
    
    print(f"[DEBUG] After reset - photo_saved_this_session: {face_system.photo_saved_this_session}")
    print(f"[DEBUG] After reset - last_photo_time: {face_system.last_photo_time}")
    
    try:
        # Call save_skin_photo directly
        print(f"\n[INFO] Calling save_skin_photo with reset flags...")
        photo_saved = face_system.save_skin_photo(test_user)
        
        print(f"[INFO] save_skin_photo returned: {photo_saved}")
        
        # Check if photo file was created
        current_date = time.strftime("%Y-%m-%d")
        photo_path = os.path.join(skin_base_dir, test_user, f"{current_date}.jpg")
        
        print(f"\n[INFO] Checking for photo: {photo_path}")
        if os.path.exists(photo_path):
            file_size = os.path.getsize(photo_path)
            print(f"✅ Photo file created: {photo_path}")
            print(f"   File size: {file_size} bytes ({file_size/1024:.2f} KB)")
            return True
        else:
            print(f"❌ Photo file not found: {photo_path}")
            
            # Check if directory exists
            person_dir = os.path.join(skin_base_dir, test_user)
            if os.path.exists(person_dir):
                print(f"✅ Person directory exists: {person_dir}")
                files = os.listdir(person_dir)
                print(f"   Files in directory: {files}")
            else:
                print(f"❌ Person directory does not exist: {person_dir}")
                print(f"   Skin directory contents: {os.listdir(skin_base_dir)}")
            
            return False
            
    except Exception as e:
        print(f"❌ Error in photo saving: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = force_photo_test()
    if success:
        print(f"\n✅ FORCE PHOTO TEST PASSED!")
    else:
        print(f"\n❌ FORCE PHOTO TEST FAILED!")
    
    sys.exit(0 if success else 1)
