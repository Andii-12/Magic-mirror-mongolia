#!/usr/bin/env python3
"""
Face Training Script for MagicMirror²
This script trains the face recognition system using photos in the Images directory
"""

import cv2
import os
import numpy as np
from PIL import Image

# Paths
IMAGE_BASE = "Images"
TRAINER_FILE = "trainer.yml"
CASCADE_PATH = "/home/andii/haarcascades/haarcascade_frontalface_default.xml"

def get_images_and_labels():
    """Get images and labels from the Images directory"""
    image_paths = []
    labels = []
    label_names = []
    
    # Get all subdirectories in Images folder
    if not os.path.exists(IMAGE_BASE):
        print(f"❌ Error: {IMAGE_BASE} directory not found!")
        print(f"   Please create the {IMAGE_BASE} directory and add person folders")
        print(f"   Example: {IMAGE_BASE}/John/photo1.jpg, {IMAGE_BASE}/Jane/photo1.jpg")
        return [], [], []
    
    # Get list of person directories
    person_dirs = [d for d in os.listdir(IMAGE_BASE) 
                   if os.path.isdir(os.path.join(IMAGE_BASE, d))]
    
    if not person_dirs:
        print(f"❌ Error: No person directories found in {IMAGE_BASE}")
        print(f"   Please create folders for each person:")
        print(f"   mkdir -p {IMAGE_BASE}/John")
        print(f"   mkdir -p {IMAGE_BASE}/Jane")
        print(f"   Then add photos to each folder")
        return [], [], []
    
    print(f"📁 Found {len(person_dirs)} person directories: {person_dirs}")
    
    # Load face cascade
    face_cascade = cv2.CascadeClassifier(CASCADE_PATH)
    if face_cascade.empty():
        print(f"❌ Error: Could not load face cascade from {CASCADE_PATH}")
        print(f"   Please check if the file exists")
        return [], [], []
    
    # Process each person directory
    for person_name in person_dirs:
        person_path = os.path.join(IMAGE_BASE, person_name)
        print(f"👤 Processing {person_name}...")
        
        # Get all image files in the person's directory
        image_files = [f for f in os.listdir(person_path) 
                      if f.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp'))]
        
        if not image_files:
            print(f"   ⚠️  No images found in {person_name} folder")
            continue
        
        print(f"   📸 Found {len(image_files)} images")
        
        # Process each image
        for image_file in image_files:
            image_path = os.path.join(person_path, image_file)
            
            try:
                # Read image
                image = cv2.imread(image_path)
                if image is None:
                    print(f"   ⚠️  Could not read {image_file}")
                    continue
                
                # Convert to grayscale
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                
                # Detect faces
                faces = face_cascade.detectMultiScale(gray, 1.3, 5)
                
                if len(faces) == 0:
                    print(f"   ⚠️  No face detected in {image_file}")
                    continue
                
                # Use the first face found
                (x, y, w, h) = faces[0]
                face_img = gray[y:y+h, x:x+w]
                
                # Resize face to standard size
                face_img = cv2.resize(face_img, (100, 100))
                
                # Add to training data
                image_paths.append(face_img)
                labels.append(len(label_names))  # Use index as label
                
                print(f"   ✅ Added face from {image_file}")
                
            except Exception as e:
                print(f"   ❌ Error processing {image_file}: {e}")
                continue
        
        # Add person name to label names
        if any(label == len(label_names) for label in labels):
            label_names.append(person_name)
    
    return image_paths, labels, label_names

def train_recognizer():
    """Train the face recognizer"""
    print("🎓 Training Face Recognition System")
    print("===================================")
    
    # Get training data
    images, labels, label_names = get_images_and_labels()
    
    if not images:
        print("❌ No training data found!")
        return False
    
    print(f"📊 Training data: {len(images)} faces from {len(label_names)} people")
    print(f"👥 People: {label_names}")
    
    # Create recognizer
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    
    try:
        # Train the recognizer
        print("🔄 Training recognizer...")
        recognizer.train(images, np.array(labels))
        
        # Save the trained model
        recognizer.write(TRAINER_FILE)
        print(f"✅ Training completed! Model saved to {TRAINER_FILE}")
        
        # Save label mapping
        with open("label_names.txt", "w") as f:
            for i, name in enumerate(label_names):
                f.write(f"{i}:{name}\n")
        print("✅ Label mapping saved to label_names.txt")
        
        return True
        
    except Exception as e:
        print(f"❌ Training failed: {e}")
        return False

def test_training():
    """Test the trained model"""
    print("\n🧪 Testing Trained Model")
    print("========================")
    
    if not os.path.exists(TRAINER_FILE):
        print(f"❌ {TRAINER_FILE} not found!")
        return False
    
    try:
        # Load recognizer
        recognizer = cv2.face.LBPHFaceRecognizer_create()
        recognizer.read(TRAINER_FILE)
        
        # Load label names
        label_names = []
        if os.path.exists("label_names.txt"):
            with open("label_names.txt", "r") as f:
                for line in f:
                    parts = line.strip().split(":")
                    if len(parts) == 2:
                        label_names.append(parts[1])
        
        print(f"✅ Model loaded successfully!")
        print(f"👥 Recognized people: {label_names}")
        
        return True
        
    except Exception as e:
        print(f"❌ Model test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Face Recognition Training System")
    print("===================================")
    
    # Check if Images directory exists
    if not os.path.exists(IMAGE_BASE):
        print(f"📁 Creating {IMAGE_BASE} directory...")
        os.makedirs(IMAGE_BASE)
        print(f"✅ Created {IMAGE_BASE} directory")
        print(f"📋 Next steps:")
        print(f"   1. Create folders for each person: mkdir -p {IMAGE_BASE}/YourName")
        print(f"   2. Add photos to each folder")
        print(f"   3. Run this script again: python3 train_faces.py")
        exit(0)
    
    # Train the recognizer
    if train_recognizer():
        # Test the training
        test_training()
        print("\n🎉 Training completed successfully!")
        print("   You can now run: python3 test_face_recognition.py")
    else:
        print("\n❌ Training failed!")
        print("   Please check your Images directory and try again")
