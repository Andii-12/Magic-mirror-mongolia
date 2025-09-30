#!/usr/bin/env python3
"""
Test script for optimized face recognition
"""

import cv2
import os
import time
from picamera2 import Picamera2

def test_face_recognition():
    """Test the optimized face recognition parameters"""
    print("Testing optimized face recognition...")
    
    # Load cascade
    cascade_path = "/home/andii/haarcascades/haarcascade_frontalface_default.xml"
    if not os.path.exists(cascade_path):
        cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
    
    face_cascade = cv2.CascadeClassifier(cascade_path)
    
    # Load recognizer
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    if os.path.exists("trainer.yml"):
        recognizer.read("trainer.yml")
        print("✅ Loaded trainer.yml")
    else:
        print("❌ No trainer.yml found - run train_faces.py first")
        return
    
    # Load labels
    image_base = "Images"
    if os.path.exists(image_base):
        label_names = os.listdir(image_base)
        label_map = {i: name for i, name in enumerate(label_names)}
        print(f"✅ Loaded {len(label_names)} labels: {label_names}")
    else:
        print("❌ No Images directory found")
        return
    
    # Initialize camera
    try:
        picam2 = Picamera2()
        config = picam2.create_preview_configuration(main={"size": (640, 480)})
        picam2.configure(config)
        picam2.start()
        time.sleep(1)
        print("✅ Camera initialized")
        
        print("\n📷 Starting face recognition test...")
        print("Look at the camera and press 'q' to quit")
        
        while True:
            start_time = time.time()
            
            # Capture frame
            frame = picam2.capture_array()
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Optimized face detection
            faces = face_cascade.detectMultiScale(
                gray, 
                scaleFactor=1.05,
                minNeighbors=3,
                minSize=(60, 60),
                flags=cv2.CASCADE_SCALE_IMAGE
            )
            
            if len(faces) > 0:
                # Process largest face
                largest_face = max(faces, key=lambda face: face[2] * face[3])
                x, y, w, h = largest_face
                
                face_img = gray[y:y+h, x:x+w]
                face_img = cv2.resize(face_img, (100, 100))
                face_img = cv2.equalizeHist(face_img)
                
                # Recognize
                label, confidence = recognizer.predict(face_img)
                name = label_map.get(label, "Unknown")
                
                # Draw rectangle and text
                cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                cv2.putText(frame, f"{name} ({confidence:.1f})", (x, y-10), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                
                print(f"Recognized: {name} (Confidence: {confidence:.2f})")
            else:
                print("No face detected")
            
            # Show frame
            cv2.imshow("Face Recognition Test", frame)
            
            # Check for quit
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
                
            # Show timing
            elapsed = time.time() - start_time
            print(f"Processing time: {elapsed:.3f}s")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        picam2.close()
        cv2.destroyAllWindows()
        print("Test completed")

if __name__ == "__main__":
    test_face_recognition()
