#!/usr/bin/env python3
"""
Interactive Face Training Script for MagicMirror²
This script takes photos and trains the face recognition system
"""

import cv2
import os
import numpy as np
import time
from picamera2 import Picamera2

# Paths
IMAGE_BASE = "Images"
TRAINER_FILE = "trainer.yml"
CASCADE_PATH = "/home/andii/haarcascades/haarcascade_frontalface_default.xml"

def capture_photos(person_name, num_photos=40):
    """Capture photos for a person using camera"""
    print(f"📸 Capturing {num_photos} photos for {person_name}...")
    
    # Create person directory
    person_path = os.path.join(IMAGE_BASE, person_name)
    os.makedirs(person_path, exist_ok=True)
    
    # Initialize camera
    try:
        picam2 = Picamera2()
        config = picam2.create_preview_configuration(main={"size": (640, 480)})
        picam2.configure(config)
        picam2.start()
        time.sleep(2)  # Let camera initialize
        
        print("📷 Camera ready! You can see yourself in the preview window.")
        print("📋 Instructions:")
        print("   - Look directly at the camera")
        print("   - Make sure your face is clearly visible")
        print("   - Good lighting helps with recognition")
        print("   - Press Enter when you're ready to start capturing photos")
        print("   - Press 'q' to quit without capturing")
        
        # Show camera preview
        preview_window = "Face Recognition Preview"
        cv2.namedWindow(preview_window, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(preview_window, 640, 480)
        
        print("\n👀 Camera preview is now showing...")
        print("   Press Enter to start capturing photos")
        print("   Press 'q' to quit")
        
        # Show preview until user presses Enter
        while True:
            # Capture frame
            frame = picam2.capture_array()
            
            # Convert to RGB for display
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Detect faces and draw rectangle
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, 1.3, 5)
            
            # Draw face rectangles
            for (x, y, w, h) in faces:
                cv2.rectangle(rgb_frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                cv2.putText(rgb_frame, "Face Detected", (x, y-10), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            # Add instructions on frame
            cv2.putText(rgb_frame, "Press ENTER to start capturing", (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            cv2.putText(rgb_frame, "Press 'q' to quit", (10, 60), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            
            # Show frame
            cv2.imshow(preview_window, rgb_frame)
            
            # Check for key press
            key = cv2.waitKey(1) & 0xFF
            if key == ord('\r') or key == ord('\n'):  # Enter key
                break
            elif key == ord('q'):
                cv2.destroyAllWindows()
                picam2.close()
                print("❌ Photo capture cancelled")
                return False
        
        # Close preview window
        cv2.destroyAllWindows()
        print("✅ Starting photo capture...")
        
        captured_count = 0
        attempt = 0
        max_attempts = num_photos * 3  # Allow more attempts in case no face detected
        
        while captured_count < num_photos and attempt < max_attempts:
            attempt += 1
            
            # Capture frame
            frame = picam2.capture_array()
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Detect faces
            faces = face_cascade.detectMultiScale(gray, 1.3, 5)
            
            if len(faces) > 0:
                # Use the first face found
                (x, y, w, h) = faces[0]
                face_img = gray[y:y+h, x:x+w]
                
                # Resize face to standard size
                face_img = cv2.resize(face_img, (100, 100))
                
                # Save the face image
                photo_path = os.path.join(person_path, f"photo_{captured_count + 1:03d}.jpg")
                cv2.imwrite(photo_path, face_img)
                
                captured_count += 1
                progress = (captured_count / num_photos) * 100
                print(f"   ✅ Captured photo {captured_count}/{num_photos} ({progress:.1f}%)")
                
                # Small delay between captures
                time.sleep(0.5)
            else:
                print(f"   ⚠️  No face detected (attempt {attempt})")
                time.sleep(0.2)
        
        picam2.close()
        
        if captured_count >= num_photos:
            print(f"✅ Successfully captured {captured_count} photos for {person_name}")
            return True
        else:
            print(f"⚠️  Only captured {captured_count} photos (target was {num_photos})")
            return captured_count > 0
            
    except Exception as e:
        print(f"❌ Error capturing photos: {e}")
        return False

def get_images_and_labels():
    """Get images and labels from the Images directory"""
    image_paths = []
    labels = []
    label_names = []
    
    # Get all subdirectories in Images folder
    if not os.path.exists(IMAGE_BASE):
        print(f"❌ Error: {IMAGE_BASE} directory not found!")
        return [], [], []
    
    # Get list of person directories
    person_dirs = [d for d in os.listdir(IMAGE_BASE) 
                   if os.path.isdir(os.path.join(IMAGE_BASE, d))]
    
    if not person_dirs:
        print(f"❌ Error: No person directories found in {IMAGE_BASE}")
        return [], [], []
    
    print(f"📁 Found {len(person_dirs)} person directories: {person_dirs}")
    
    # Load face cascade
    face_cascade = cv2.CascadeClassifier(CASCADE_PATH)
    if face_cascade.empty():
        print(f"❌ Error: Could not load face cascade from {CASCADE_PATH}")
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
                    continue
                
                # Convert to grayscale
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                
                # Detect faces
                faces = face_cascade.detectMultiScale(gray, 1.3, 5)
                
                if len(faces) == 0:
                    continue
                
                # Use the first face found
                (x, y, w, h) = faces[0]
                face_img = gray[y:y+h, x:x+w]
                
                # Resize face to standard size
                face_img = cv2.resize(face_img, (100, 100))
                
                # Add to training data
                image_paths.append(face_img)
                labels.append(len(label_names))  # Use index as label
                
            except Exception as e:
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
    print("🚀 Interactive Face Recognition Training System")
    print("===============================================")
    
    # Create Images directory if it doesn't exist
    if not os.path.exists(IMAGE_BASE):
        print(f"📁 Creating {IMAGE_BASE} directory...")
        os.makedirs(IMAGE_BASE)
        print(f"✅ Created {IMAGE_BASE} directory")
    
    while True:
        print("\n📋 What would you like to do?")
        print("1. Add a new person (capture photos)")
        print("2. Train the system with existing photos")
        print("3. Test the trained system")
        print("4. Exit")
        
        choice = input("\nEnter your choice (1-4): ").strip()
        
        if choice == "1":
            # Add new person
            person_name = input("Enter the person's name: ").strip()
            if person_name:
                print(f"\n👤 Adding {person_name} to the system...")
                if capture_photos(person_name, 40):
                    print(f"✅ Successfully captured photos for {person_name}")
                else:
                    print(f"❌ Failed to capture photos for {person_name}")
            else:
                print("❌ Please enter a valid name")
        
        elif choice == "2":
            # Train the system
            print("\n🎓 Training the face recognition system...")
            if train_recognizer():
                test_training()
                print("\n🎉 Training completed successfully!")
                print("   You can now run: python3 test_face_recognition.py")
            else:
                print("\n❌ Training failed!")
                print("   Please add some people first (option 1)")
        
        elif choice == "3":
            # Test the system
            print("\n🧪 Testing the trained system...")
            test_training()
        
        elif choice == "4":
            print("👋 Goodbye!")
            break
        
        else:
            print("❌ Invalid choice. Please enter 1, 2, 3, or 4.")
