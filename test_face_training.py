#!/usr/bin/env python3
"""
Test script for face training
Verifies that the training process works correctly
"""

import os
import cv2
import numpy as np
import json
from pathlib import Path

# Try different cascade paths for compatibility
def get_cascade_path():
    """Get the correct path to the face cascade file"""
    possible_paths = []
    
    # Try cv2.data.haarcascades if available
    try:
        if hasattr(cv2, 'data') and hasattr(cv2.data, 'haarcascades'):
            possible_paths.append(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    except:
        pass
    
    # Add common system paths
    possible_paths.extend([
        '/usr/share/opencv4/haarcascades/haarcascade_frontalface_default.xml',
        '/usr/share/opencv/haarcascades/haarcascade_frontalface_default.xml',
        '/usr/local/share/opencv4/haarcascades/haarcascade_frontalface_default.xml',
        '/usr/local/share/opencv/haarcascades/haarcascade_frontalface_default.xml',
        '/home/andii/haarcascades/haarcascade_frontalface_default.xml',
        'haarcascade_frontalface_default.xml'
    ])
    
    # Check each path
    for path in possible_paths:
        if os.path.exists(path):
            return path
    
    # If none found, try to find any haarcascade file
    import glob
    cascade_files = glob.glob('**/haarcascade_frontalface_default.xml', recursive=True)
    if cascade_files:
        return cascade_files[0]
    
    return None

def test_training_files():
    """Test if training files exist and are valid"""
    print("🧪 Testing Face Training Files")
    print("=" * 30)
    
    # Check if Images directory exists
    images_dir = Path("Images")
    if not images_dir.exists():
        print("❌ Images directory not found!")
        print("   Run: python3 setup_face_training.py")
        return False
    
    print("✅ Images directory exists")
    
    # Check for person directories
    person_dirs = [d for d in images_dir.iterdir() 
                   if d.is_dir() and not d.name.startswith('.')]
    
    if not person_dirs:
        print("❌ No person directories found!")
        print("   Create directories and add photos first")
        return False
    
    print(f"✅ Found {len(person_dirs)} person directories: {[d.name for d in person_dirs]}")
    
    # Check for images in each directory
    total_images = 0
    for person_dir in person_dirs:
        image_files = list(person_dir.glob("*.jpg")) + list(person_dir.glob("*.jpeg")) + list(person_dir.glob("*.png")) + list(person_dir.glob("*.bmp"))
        image_count = len(image_files)
        total_images += image_count
        
        if image_count > 0:
            print(f"   👤 {person_dir.name}: {image_count} images")
        else:
            print(f"   ⚠️  {person_dir.name}: No images")
    
    if total_images < 10:
        print("❌ Not enough images! Need at least 10 faces total.")
        print("   Recommended: 40+ faces per person for best accuracy")
        return False
    
    print(f"✅ Total images: {total_images}")
    
    # Check if trainer.yml exists
    if os.path.exists("trainer.yml"):
        print("✅ trainer.yml exists")
        
        # Test loading the trainer
        try:
            recognizer = cv2.face.LBPHFaceRecognizer_create()
            recognizer.read("trainer.yml")
            print("✅ trainer.yml is valid and can be loaded")
        except Exception as e:
            print(f"❌ trainer.yml is corrupted: {e}")
            return False
    else:
        print("⚠️  trainer.yml not found - need to run training")
    
    # Check if labels.json exists
    if os.path.exists("labels.json"):
        print("✅ labels.json exists")
        
        try:
            with open("labels.json", "r") as f:
                labels = json.load(f)
            print(f"✅ labels.json is valid - {len(labels.get('people', []))} people")
        except Exception as e:
            print(f"❌ labels.json is corrupted: {e}")
            return False
    else:
        print("⚠️  labels.json not found - need to run training")
    
    return True

def test_face_detection():
    """Test face detection on sample images"""
    print("\n🔍 Testing Face Detection")
    print("=" * 25)
    
    # Load face cascade
    cascade_path = get_cascade_path()
    if cascade_path is None:
        print("❌ Face cascade not found. Please install OpenCV properly.")
        print("   Try: sudo apt-get install python3-opencv")
        return False
    
    face_cascade = cv2.CascadeClassifier(cascade_path)
    if face_cascade.empty():
        print("❌ Could not load face cascade")
        return False
    
    if face_cascade.empty():
        print("❌ Could not load face cascade")
        return False
    
    print("✅ Face cascade loaded")
    
    # Test on a few images
    images_dir = Path("Images")
    test_count = 0
    success_count = 0
    
    for person_dir in images_dir.iterdir():
        if person_dir.is_dir() and not person_dir.name.startswith('.'):
            image_files = list(person_dir.glob("*.jpg")) + list(person_dir.glob("*.jpeg")) + list(person_dir.glob("*.png")) + list(person_dir.glob("*.bmp"))
            
            # Test first few images
            for image_file in image_files[:3]:  # Test up to 3 images per person
                test_count += 1
                
                try:
                    image = cv2.imread(str(image_file))
                    if image is None:
                        continue
                    
                    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                    faces = face_cascade.detectMultiScale(gray, 1.1, 5, minSize=(30, 30))
                    
                    if len(faces) > 0:
                        success_count += 1
                        print(f"   ✅ {person_dir.name}/{image_file.name}: {len(faces)} face(s) detected")
                    else:
                        print(f"   ⚠️  {person_dir.name}/{image_file.name}: No faces detected")
                
                except Exception as e:
                    print(f"   ❌ {person_dir.name}/{image_file.name}: Error - {e}")
    
    if test_count == 0:
        print("❌ No images found to test")
        return False
    
    success_rate = (success_count / test_count) * 100
    print(f"📊 Face detection success rate: {success_rate:.1f}% ({success_count}/{test_count})")
    
    if success_rate < 50:
        print("⚠️  Low success rate - check image quality")
        return False
    
    print("✅ Face detection working well")
    return True

def test_training_process():
    """Test the training process without saving"""
    print("\n🤖 Testing Training Process")
    print("=" * 25)
    
    try:
        # This is a simplified version of the training process
        images_dir = Path("Images")
        cascade_path = get_cascade_path()
    if cascade_path is None:
        print("❌ Face cascade not found. Please install OpenCV properly.")
        print("   Try: sudo apt-get install python3-opencv")
        return False
    
    face_cascade = cv2.CascadeClassifier(cascade_path)
    if face_cascade.empty():
        print("❌ Could not load face cascade")
        return False
        
        faces = []
        labels = []
        label_map = {}
        
        for person_id, person_dir in enumerate(images_dir.iterdir()):
            if person_dir.is_dir() and not person_dir.name.startswith('.'):
                label_map[person_id] = person_dir.name
                
                image_files = list(person_dir.glob("*.jpg")) + list(person_dir.glob("*.jpeg")) + list(person_dir.glob("*.png")) + list(person_dir.glob("*.bmp"))
                
                for image_file in image_files[:5]:  # Test with first 5 images
                    try:
                        image = cv2.imread(str(image_file))
                        if image is None:
                            continue
                        
                        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                        detected_faces = face_cascade.detectMultiScale(gray, 1.1, 5, minSize=(30, 30))
                        
                        if len(detected_faces) > 0:
                            largest_face = max(detected_faces, key=lambda x: x[2] * x[3])
                            x, y, w, h = largest_face
                            
                            face_roi = gray[y:y+h, x:x+w]
                            face_resized = cv2.resize(face_roi, (100, 100))
                            
                            faces.append(face_resized)
                            labels.append(person_id)
                    
                    except Exception as e:
                        continue
        
        if len(faces) < 10:
            print("❌ Not enough faces for training test")
            print("   Need at least 10 faces, recommended 40+ per person")
            return False
        
        print(f"✅ Found {len(faces)} faces for training")
        print(f"✅ Found {len(set(labels))} different people")
        
        # Test creating recognizer
        recognizer = cv2.face.LBPHFaceRecognizer_create()
        recognizer.train(faces, np.array(labels))
        
        print("✅ Training process works correctly")
        return True
        
    except Exception as e:
        print(f"❌ Training test failed: {e}")
        return False

def main():
    """Main test function"""
    print("🧪 Face Training Test Suite")
    print("=" * 30)
    
    # Test 1: Check files and directories
    if not test_training_files():
        print("\n❌ File structure test failed")
        return
    
    # Test 2: Test face detection
    if not test_face_detection():
        print("\n❌ Face detection test failed")
        return
    
    # Test 3: Test training process
    if not test_training_process():
        print("\n❌ Training process test failed")
        return
    
    print("\n🎉 All tests passed!")
    print("\n📋 Next steps:")
    print("   1. Run: python3 simple_train_faces.py")
    print("   2. Test: python3 face_recognition_system.py")
    print("   3. Start MagicMirror²: ./start.sh")

if __name__ == "__main__":
    main()
