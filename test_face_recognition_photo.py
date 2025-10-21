#!/usr/bin/env python3
"""
Test script for face recognition with photo capture
"""

import os
import sys
import platform
import time
from face_recognition_system import FaceRecognitionSystem

def test_face_recognition_photo():
    """Test the face recognition system with photo capture"""
    
    print("="*60)
    print("FACE RECOGNITION PHOTO CAPTURE TEST")
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
    
    # Test photo capture for a test user
    test_user = "TestUser"
    print(f"[INFO] Testing photo capture for user: {test_user}")
    
    try:
        # Call save_skin_photo directly
        photo_saved = face_system.save_skin_photo(test_user)
        
        if photo_saved:
            print(f"✅ Photo capture test successful!")
            
            # Check if photo file was created
            current_date = time.strftime("%Y-%m-%d")
            photo_path = os.path.join(skin_base_dir, test_user, f"{current_date}.jpg")
            
            if os.path.exists(photo_path):
                file_size = os.path.getsize(photo_path)
                print(f"✅ Photo file created: {photo_path}")
                print(f"   File size: {file_size} bytes ({file_size/1024:.2f} KB)")
                return True
            else:
                print(f"❌ Photo file not found: {photo_path}")
                return False
        else:
            print(f"❌ Photo capture test failed!")
            return False
            
    except Exception as e:
        print(f"❌ Photo capture test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_face_recognition_photo()
    if success:
        print(f"\n✅ FACE RECOGNITION PHOTO CAPTURE TEST PASSED!")
    else:
        print(f"\n❌ FACE RECOGNITION PHOTO CAPTURE TEST FAILED!")
    
    sys.exit(0 if success else 1)
