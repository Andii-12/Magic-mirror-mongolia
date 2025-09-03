#!/usr/bin/env python3
"""
Test script for face recognition system
This script tests the face recognition without the full MagicMirror² integration
"""

import json
import time
import os
from face_recognition_system import FaceRecognitionSystem

def test_face_recognition():
    """Test the face recognition system"""
    print("🧪 Testing Face Recognition System")
    print("==================================")
    
    # Check if trainer.yml exists (try both locations)
    trainer_paths = ["trainer.yml", "python_code/trainer.yml"]
    trainer_found = False
    
    for trainer_path in trainer_paths:
        if os.path.exists(trainer_path):
            print(f"✅ Found trainer.yml at: {trainer_path}")
            trainer_found = True
            break
    
    if not trainer_found:
        print("❌ trainer.yml not found!")
        print("📋 You need to train the face recognition system first:")
        print("   1. Run: python3 train_faces.py")
        print("   2. Choose option 1 to add a person")
        print("   3. Choose option 2 to train the system")
        return False
    
    try:
        # Initialize the system
        system = FaceRecognitionSystem()
        
        print("✅ System initialized successfully")
        print(f"📁 Known faces: {system.label_names}")
        print(f"📄 Status file: {system.status_file}")
        
        # Test distance reading
        print("\n📏 Testing ultrasonic sensor...")
        for i in range(3):
            distance = system.get_distance()
            print(f"   Distance reading {i+1}: {distance}cm")
            time.sleep(1)
        
        # Test status file creation
        print("\n📄 Testing status file creation...")
        system.current_distance = 15
        system.is_active = True
        system.current_person = "TestPerson"
        system.update_status_file()
        
        if os.path.exists(system.status_file):
            with open(system.status_file, 'r') as f:
                status = json.load(f)
            print(f"   ✅ Status file created: {status}")
        else:
            print("   ❌ Status file not created")
        
        print("\n🎯 Test completed successfully!")
        print("   You can now run the full system with:")
        print("   ./start_magicmirror_proximity.sh (Linux)")
        print("   start_magicmirror_proximity.bat (Windows)")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False
    
    return True

if __name__ == "__main__":
    test_face_recognition()
