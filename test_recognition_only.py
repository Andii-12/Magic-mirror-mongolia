#!/usr/bin/env python3
"""
Simple Face Recognition Test
This script tests face recognition using the existing trainer.yml
"""

import cv2
import os
import numpy as np
from picamera2 import Picamera2

# Paths
CASCADE_PATH = "/home/andii/haarcascades/haarcascade_frontalface_default.xml"
TRAINER_PATHS = ["trainer.yml", "python_code/trainer.yml"]
IMAGE_BASE = "Images"

def test_face_recognition():
    """Test face recognition with camera"""
    print("🧪 Testing Face Recognition")
    print("===========================")
    
    # Find trainer.yml
    trainer_path = None
    for path in TRAINER_PATHS:
        if os.path.exists(path):
            trainer_path = path
            print(f"✅ Found trainer.yml at: {path}")
            break
    
    if not trainer_path:
        print("❌ trainer.yml not found!")
        print("📋 Please run: python3 train_faces.py")
        return False
    
    # Load face cascade
    face_cascade = cv2.CascadeClassifier(CASCADE_PATH)
    if face_cascade.empty():
        print(f"❌ Could not load face cascade from {CASCADE_PATH}")
        return False
    
    # Load recognizer
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    try:
        recognizer.read(trainer_path)
        print("✅ Face recognizer loaded successfully")
    except Exception as e:
        print(f"❌ Could not load recognizer: {e}")
        return False
    
    # Load label names
    label_names = []
    if os.path.exists(IMAGE_BASE):
        label_names = os.listdir(IMAGE_BASE)
        print(f"👥 Known people: {label_names}")
    else:
        print("⚠️  Images directory not found")
    
    # Initialize camera
    try:
        picam2 = Picamera2()
        config = picam2.create_preview_configuration(main={"size": (640, 480)})
        picam2.configure(config)
        picam2.start()
        time.sleep(2)
        
        print("📷 Camera ready! Look at the camera...")
        print("Press Ctrl+C to stop")
        
        while True:
            # Capture frame
            frame = picam2.capture_array()
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Detect faces
            faces = face_cascade.detectMultiScale(gray, 1.3, 5)
            
            if len(faces) > 0:
                # Use the first face found
                (x, y, w, h) = faces[0]
                face_img = gray[y:y+h, x:x+w]
                face_img = cv2.resize(face_img, (100, 100))
                
                # Recognize face
                label, confidence = recognizer.predict(face_img)
                
                if confidence < 100:  # Lower confidence = better match
                    name = label_names[label] if label < len(label_names) else "Unknown"
                    print(f"👤 Recognized: {name} (Confidence: {confidence:.2f})")
                else:
                    print("❓ Unknown person (Confidence too low)")
            else:
                print("👤 No face detected")
            
            time.sleep(1)  # Check every second
            
    except KeyboardInterrupt:
        print("\n👋 Stopping recognition test...")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        try:
            picam2.close()
        except:
            pass
    
    return True

if __name__ == "__main__":
    test_face_recognition()
