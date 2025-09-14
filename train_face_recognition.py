#!/usr/bin/env python3
"""
Face Recognition Training Script for MagicMirror²
Trains the LBPHFaceRecognizer with face images from the Images directory
"""

import cv2
import os
import numpy as np
from PIL import Image
import json
import sys
from datetime import datetime

# Configuration
IMAGES_DIR = "Images"
TRAINER_FILE = "trainer.yml"
LABELS_FILE = "labels.json"
CASCADE_PATH = "/home/andii/haarcascades/haarcascade_frontalface_default.xml"

# Check if we're running on Windows (for development)
import platform
if platform.system() == "Windows":
    print("⚠️  Running on Windows - using default cascade")
    CASCADE_PATH = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'

def create_directories():
    """Create necessary directories if they don't exist"""
    if not os.path.exists(IMAGES_DIR):
        os.makedirs(IMAGES_DIR)
        print(f"📁 Created directory: {IMAGES_DIR}")
    
    # Create subdirectories for each person
    print("📁 Directory structure:")
    print(f"   {IMAGES_DIR}/")
    print("   ├── Person1/     # Put 40+ face images here")
    print("   ├── Person2/     # Put 40+ face images here")
    print("   └── Person3/     # Put 40+ face images here")
    print("")
    print("💡 Instructions:")
    print("   1. Create subdirectories for each person")
    print("   2. Add 40+ clear face photos per person")
    print("   3. Run this script to train the recognizer")
    print("")

def get_face_cascade():
    """Load face cascade classifier"""
    if os.path.exists(CASCADE_PATH):
        face_cascade = cv2.CascadeClassifier(CASCADE_PATH)
        print(f"✅ Loaded face cascade from: {CASCADE_PATH}")
    else:
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        print(f"⚠️  Using default face cascade")
    
    return face_cascade

def detect_and_prepare_faces(images_dir, face_cascade):
    """Detect faces in images and prepare training data"""
    faces = []
    labels = []
    label_names = []
    label_map = {}
    
    print("🔍 Scanning for face images...")
    
    # Get all subdirectories (person names)
    person_dirs = [d for d in os.listdir(images_dir) 
                   if os.path.isdir(os.path.join(images_dir, d)) and not d.startswith('.')]
    
    if not person_dirs:
        print("❌ No person directories found!")
        print(f"   Please create subdirectories in {IMAGES_DIR}/ for each person")
        return None, None, None, None
    
    person_dirs.sort()  # Sort for consistent labeling
    
    for person_id, person_name in enumerate(person_dirs):
        person_dir = os.path.join(images_dir, person_name)
        label_map[person_id] = person_name
        label_names.append(person_name)
        
        print(f"👤 Processing {person_name}...")
        
        # Get all image files in person directory
        image_files = [f for f in os.listdir(person_dir) 
                      if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tiff'))]
        
        if not image_files:
            print(f"   ⚠️  No images found in {person_name}/")
            continue
        
        print(f"   📸 Found {len(image_files)} images")
        
        faces_found = 0
        for image_file in image_files:
            image_path = os.path.join(person_dir, image_file)
            
            try:
                # Load image
                image = cv2.imread(image_path)
                if image is None:
                    print(f"   ⚠️  Could not load: {image_file}")
                    continue
                
                # Convert to grayscale
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                
                # Detect faces
                detected_faces = face_cascade.detectMultiScale(
                    gray, 
                    scaleFactor=1.1, 
                    minNeighbors=5, 
                    minSize=(30, 30)
                )
                
                if len(detected_faces) == 0:
                    print(f"   ⚠️  No face detected in: {image_file}")
                    continue
                
                # Use the largest face if multiple faces detected
                largest_face = max(detected_faces, key=lambda x: x[2] * x[3])
                x, y, w, h = largest_face
                
                # Extract face region
                face_roi = gray[y:y+h, x:x+w]
                
                # Resize to standard size (100x100)
                face_resized = cv2.resize(face_roi, (100, 100))
                
                # Add to training data
                faces.append(face_resized)
                labels.append(person_id)
                faces_found += 1
                
                print(f"   ✅ Face detected in: {image_file}")
                
            except Exception as e:
                print(f"   ❌ Error processing {image_file}: {e}")
                continue
        
        print(f"   📊 {faces_found} faces extracted for {person_name}")
        print("")
    
    return faces, labels, label_names, label_map

def train_recognizer(faces, labels):
    """Train the LBPHFaceRecognizer"""
    if not faces or not labels:
        print("❌ No training data available!")
        return None
    
    print("🤖 Training LBPHFaceRecognizer...")
    print(f"   📊 Training with {len(faces)} face samples")
    print(f"   👥 {len(set(labels))} different people")
    
    # Create and train recognizer
    recognizer = cv2.face.LBPHFaceRecognizer_create(
        radius=1,
        neighbors=8,
        grid_x=8,
        grid_y=8,
        threshold=80.0
    )
    
    try:
        recognizer.train(faces, np.array(labels))
        print("✅ Training completed successfully!")
        return recognizer
    except Exception as e:
        print(f"❌ Training failed: {e}")
        return None

def save_training_data(recognizer, label_map, label_names):
    """Save the trained model and label mappings"""
    if recognizer is None:
        return False
    
    try:
        # Save recognizer
        recognizer.save(TRAINER_FILE)
        print(f"💾 Saved recognizer to: {TRAINER_FILE}")
        
        # Save label mappings
        training_data = {
            "label_map": label_map,
            "label_names": label_names,
            "trained_at": datetime.now().isoformat(),
            "total_people": len(label_names),
            "total_faces": sum(1 for _ in label_map.values())
        }
        
        with open(LABELS_FILE, 'w') as f:
            json.dump(training_data, f, indent=2)
        print(f"💾 Saved label mappings to: {LABELS_FILE}")
        
        return True
    except Exception as e:
        print(f"❌ Failed to save training data: {e}")
        return False

def test_recognizer(recognizer, label_names, face_cascade):
    """Test the trained recognizer with webcam"""
    if recognizer is None:
        return
    
    print("🧪 Testing recognizer...")
    print("   Press 'q' to quit, 's' to save test image")
    
    # Check if we're on Windows (simulation mode)
    if platform.system() == "Windows":
        print("⚠️  Windows detected - skipping camera test")
        print("   The recognizer is ready for use with MagicMirror²")
        return
    
    try:
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("❌ Could not open camera")
            return
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            # Convert to grayscale
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Detect faces
            faces = face_cascade.detectMultiScale(gray, 1.1, 5, minSize=(30, 30))
            
            for (x, y, w, h) in faces:
                # Draw rectangle around face
                cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                
                # Extract face and predict
                face_roi = gray[y:y+h, x:x+w]
                face_resized = cv2.resize(face_roi, (100, 100))
                
                label, confidence = recognizer.predict(face_resized)
                
                # Get person name
                if label < len(label_names):
                    person_name = label_names[label]
                    confidence_percent = 100 - confidence
                    
                    # Draw prediction
                    text = f"{person_name} ({confidence_percent:.1f}%)"
                    color = (0, 255, 0) if confidence_percent > 50 else (0, 0, 255)
                    cv2.putText(frame, text, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
                else:
                    cv2.putText(frame, "Unknown", (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            
            # Show frame
            cv2.imshow('Face Recognition Test', frame)
            
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('s'):
                # Save test image
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"test_image_{timestamp}.jpg"
                cv2.imwrite(filename, frame)
                print(f"📸 Saved test image: {filename}")
        
        cap.release()
        cv2.destroyAllWindows()
        print("✅ Test completed")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")

def main():
    """Main training function"""
    print("🎯 Face Recognition Training for MagicMirror²")
    print("=" * 50)
    
    # Create directories
    create_directories()
    
    # Load face cascade
    face_cascade = get_face_cascade()
    
    # Detect and prepare faces
    faces, labels, label_names, label_map = detect_and_prepare_faces(IMAGES_DIR, face_cascade)
    
    if faces is None:
        print("❌ No training data found. Please add face images and try again.")
        return
    
    if len(faces) < 20:
        print("⚠️  Warning: Few faces detected. Consider adding more images.")
        print("   Recommended: 40+ clear face photos per person for best accuracy")
    
    # Train recognizer
    recognizer = train_recognizer(faces, labels)
    
    if recognizer is None:
        print("❌ Training failed. Please check your images and try again.")
        return
    
    # Save training data
    if save_training_data(recognizer, label_map, label_names):
        print("")
        print("🎉 Training completed successfully!")
        print("")
        print("📋 Next steps:")
        print("   1. Copy trainer.yml to your MagicMirror² directory")
        print("   2. Update face_recognition_system.py to use the correct paths")
        print("   3. Start MagicMirror² with: ./start.sh")
        print("")
        print("🔧 Files created:")
        print(f"   - {TRAINER_FILE} (trained model)")
        print(f"   - {LABELS_FILE} (label mappings)")
        print("")
        
        # Test recognizer
        test_recognizer(recognizer, label_names, face_cascade)
    else:
        print("❌ Failed to save training data")

if __name__ == "__main__":
    main()
