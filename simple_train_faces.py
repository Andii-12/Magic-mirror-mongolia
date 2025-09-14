#!/usr/bin/env python3
"""
Simple Face Training Script for MagicMirror²
Quick and easy face training for the Mongolian MagicMirror project
"""

import cv2
import os
import numpy as np
import json
from datetime import datetime

# Configuration
IMAGES_DIR = "Images"
TRAINER_FILE = "trainer.yml"

# Try different cascade paths for compatibility
def get_cascade_path():
    """Get the correct path to the face cascade file"""
    possible_paths = [
        cv2.data.haarcascades + 'haarcascade_frontalface_default.xml',
        '/usr/share/opencv4/haarcascades/haarcascade_frontalface_default.xml',
        '/usr/share/opencv/haarcascades/haarcascade_frontalface_default.xml',
        '/usr/local/share/opencv4/haarcascades/haarcascade_frontalface_default.xml',
        '/usr/local/share/opencv/haarcascades/haarcascade_frontalface_default.xml',
        'haarcascade_frontalface_default.xml'
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            return path
    
    # If none found, try to find any haarcascade file
    import glob
    cascade_files = glob.glob('**/haarcascade_frontalface_default.xml', recursive=True)
    if cascade_files:
        return cascade_files[0]
    
    return None

def main():
    print("🎯 Simple Face Training for MagicMirror²")
    print("=" * 40)
    
    # Create Images directory if it doesn't exist
    if not os.path.exists(IMAGES_DIR):
        os.makedirs(IMAGES_DIR)
        print(f"📁 Created {IMAGES_DIR}/ directory")
    
    print(f"📁 Please organize your images like this:")
    print(f"   {IMAGES_DIR}/")
    print(f"   ├── Andii/          # Put 40+ photos of Andii here")
    print(f"   ├── Jane/           # Put 40+ photos of Jane here")
    print(f"   └── OtherPerson/    # Add more people as needed")
    print("")
    
    # Check if we have any person directories
    person_dirs = [d for d in os.listdir(IMAGES_DIR) 
                   if os.path.isdir(os.path.join(IMAGES_DIR, d)) and not d.startswith('.')]
    
    if not person_dirs:
        print("❌ No person directories found!")
        print("   Please create subdirectories and add face photos first.")
        return
    
    print(f"👥 Found {len(person_dirs)} people: {', '.join(person_dirs)}")
    print("")
    
    # Load face cascade
    cascade_path = get_cascade_path()
    if cascade_path is None:
        print("❌ Face cascade not found. Please install OpenCV properly.")
        print("   Try: sudo apt-get install python3-opencv")
        print("   Or: pip3 install opencv-python")
        return
    
    print(f"📁 Using cascade: {cascade_path}")
    face_cascade = cv2.CascadeClassifier(cascade_path)
    if face_cascade.empty():
        print("❌ Could not load face cascade")
        return
    
    print("✅ Face detector loaded")
    
    # Prepare training data
    faces = []
    labels = []
    label_map = {}
    
    for person_id, person_name in enumerate(person_dirs):
        person_dir = os.path.join(IMAGES_DIR, person_name)
        label_map[person_id] = person_name
        
        print(f"👤 Training {person_name}...")
        
        # Get all images for this person
        image_files = [f for f in os.listdir(person_dir) 
                      if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp'))]
        
        faces_found = 0
        for image_file in image_files:
            image_path = os.path.join(person_dir, image_file)
            
            try:
                # Load and process image
                image = cv2.imread(image_path)
                if image is None:
                    continue
                
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                
                # Detect faces
                detected_faces = face_cascade.detectMultiScale(gray, 1.1, 5, minSize=(30, 30))
                
                if len(detected_faces) > 0:
                    # Use the largest face
                    largest_face = max(detected_faces, key=lambda x: x[2] * x[3])
                    x, y, w, h = largest_face
                    
                    # Extract and resize face
                    face_roi = gray[y:y+h, x:x+w]
                    face_resized = cv2.resize(face_roi, (100, 100))
                    
                    faces.append(face_resized)
                    labels.append(person_id)
                    faces_found += 1
                    
            except Exception as e:
                print(f"   ⚠️  Error with {image_file}: {e}")
                continue
        
        print(f"   ✅ Found {faces_found} faces")
    
    if len(faces) < 10:
        print("❌ Not enough faces found! Need at least 10 faces total.")
        print("   Recommended: 40+ faces per person for best accuracy")
        return
    
    print(f"")
    print(f"🤖 Training recognizer with {len(faces)} faces...")
    
    # Train the recognizer
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    recognizer.train(faces, np.array(labels))
    
    # Save the trainer
    recognizer.save(TRAINER_FILE)
    print(f"✅ Saved trainer to: {TRAINER_FILE}")
    
    # Save label mapping
    with open("labels.json", "w") as f:
        json.dump({
            "label_map": label_map,
            "trained_at": datetime.now().isoformat(),
            "total_faces": len(faces),
            "people": list(label_map.values())
        }, f, indent=2)
    
    print(f"✅ Saved labels to: labels.json")
    print("")
    print("🎉 Training completed!")
    print("")
    print("📋 Next steps:")
    print("   1. Copy trainer.yml to your MagicMirror² directory")
    print("   2. Make sure face_recognition_system.py can find it")
    print("   3. Start MagicMirror²: ./start.sh")
    print("")
    print("🧪 Test your setup:")
    print("   python3 face_recognition_system.py")

if __name__ == "__main__":
    main()
