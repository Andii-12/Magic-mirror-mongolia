#!/usr/bin/env python3
"""
Test script for continuous face recognition with photo capture
"""

import os
import sys
import time
from face_recognition_system import FaceRecognitionSystem

def test_continuous_face_recognition():
    """Test continuous face recognition with photo capture"""
    
    print("="*60)
    print("CONTINUOUS FACE RECOGNITION TEST")
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
    
    # Test multiple recognitions to see if photos are saved
    test_user = "Andii"
    print(f"[INFO] Testing multiple recognitions for user: {test_user}")
    
    for i in range(3):
        print(f"\n--- Test {i+1} ---")
        
        try:
            # Simulate face recognition
            print(f"[INFO] Simulating face recognition {i+1}...")
            person = face_system.recognize_face_with_camera()
            
            print(f"[INFO] Recognized person: {person}")
            
            # Check if photo was saved
            if person:
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
            
            # Wait a bit between tests
            time.sleep(2)
            
        except Exception as e:
            print(f"❌ Error in test {i+1}: {e}")
            import traceback
            traceback.print_exc()
    
    return True

if __name__ == "__main__":
    success = test_continuous_face_recognition()
    if success:
        print(f"\n✅ CONTINUOUS FACE RECOGNITION TEST COMPLETED!")
    else:
        print(f"\n❌ CONTINUOUS FACE RECOGNITION TEST FAILED!")
    
    sys.exit(0 if success else 1)
