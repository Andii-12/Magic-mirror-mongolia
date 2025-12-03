#!/usr/bin/env python3
"""
Interactive Face Training Script for MagicMirror²
This script takes photos and trains the face recognition system
"""

import cv2
import os
import numpy as np
import time
import platform

# Check platform
IS_WINDOWS = platform.system() == "Windows"

if not IS_WINDOWS:
    try:
        from picamera2 import Picamera2
    except ImportError:
        print("⚠️  Warning: picamera2 not available - camera features will be limited")
        Picamera2 = None
else:
    print("⚠️  Running on Windows - camera features will be simulated")
    Picamera2 = None

# Paths
IMAGE_BASE = "Images"
TRAINER_FILE = "trainer.yml"
CASCADE_PATH = "/home/andii/haarcascades/haarcascade_frontalface_default.xml"

def load_face_cascade():
    """Load face cascade with fallback to OpenCV default"""
    cascade_paths = []
    if CASCADE_PATH:
        cascade_paths.append(CASCADE_PATH)
    # Add relative path option
    cascade_paths.append("haarcascades/haarcascade_frontalface_default.xml")
    # Add OpenCV default as final fallback
    cascade_paths.append(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    
    for cascade_path in cascade_paths:
        if os.path.exists(cascade_path) or cascade_path == cascade_paths[-1]:  # Always try OpenCV default
            try:
                face_cascade = cv2.CascadeClassifier(cascade_path)
                if not face_cascade.empty():
                    print(f"✅ Loaded face cascade from: {cascade_path}")
                    return face_cascade
            except Exception as e:
                print(f"⚠️  Failed to load cascade from {cascade_path}: {e}")
                if cascade_path != cascade_paths[-1]:
                    continue
                else:
                    raise SystemError("Cannot load face cascade classifier")
    
    raise SystemError("Cannot load face cascade classifier - no valid cascade found")

def capture_photos(person_name, num_photos=40):
    """Capture photos for a person using camera"""
    print(f"📸 Capturing {num_photos} photos for {person_name}...")
    
    # Create person directory
    person_path = os.path.join(IMAGE_BASE, person_name)
    os.makedirs(person_path, exist_ok=True)
    
    # Initialize camera
    try:
        if IS_WINDOWS or Picamera2 is None:
            print("❌ Camera not available on this platform")
            return False
        
        picam2 = Picamera2()
        config = picam2.create_preview_configuration(main={"size": (640, 480)})
        picam2.configure(config)
        picam2.start()
        time.sleep(2)  # Let camera initialize
        
        # Load face cascade
        try:
            face_cascade = load_face_cascade()
        except SystemError as e:
            print(f"❌ Error: {e}")
            picam2.close()
            return False
        
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
            # Capture frame (Picamera2 returns RGB)
            frame_rgb = picam2.capture_array()
            
            # Convert RGB to BGR for OpenCV processing
            frame_bgr = cv2.cvtColor(frame_rgb, cv2.COLOR_RGB2BGR)
            
            # Detect faces and draw rectangle
            gray = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, 1.3, 5)
            
            # Draw face rectangles (use BGR frame for drawing, then convert to RGB for display)
            display_frame = frame_bgr.copy()
            for (x, y, w, h) in faces:
                cv2.rectangle(display_frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                cv2.putText(display_frame, "Face Detected", (x, y-10), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            # Add instructions on frame
            cv2.putText(display_frame, "Press ENTER to start capturing", (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            cv2.putText(display_frame, "Press 'q' to quit", (10, 60), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            
            # Show frame (OpenCV expects BGR for display)
            cv2.imshow(preview_window, display_frame)
            
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
            
            # Capture frame (Picamera2 returns RGB)
            frame_rgb = picam2.capture_array()
            # Convert RGB to BGR for OpenCV processing
            frame_bgr = cv2.cvtColor(frame_rgb, cv2.COLOR_RGB2BGR)
            gray = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2GRAY)
            
            # Detect faces with optimized parameters (same as recognition)
            faces = face_cascade.detectMultiScale(
                gray, 
                scaleFactor=1.05,  # Same as recognition
                minNeighbors=3,    # Same as recognition
                minSize=(60, 60),  # Same as recognition
                flags=cv2.CASCADE_SCALE_IMAGE
            )
            
            if len(faces) > 0:
                # Use the largest face found (same as recognition)
                largest_face = max(faces, key=lambda face: face[2] * face[3])
                (x, y, w, h) = largest_face
                face_img = gray[y:y+h, x:x+w]
                
                # Resize face to standard size
                face_img = cv2.resize(face_img, (100, 100))
                
                # Apply histogram equalization for better recognition (same as recognition)
                face_img = cv2.equalizeHist(face_img)
                
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
    try:
        face_cascade = load_face_cascade()
    except SystemError as e:
        print(f"❌ Error: {e}")
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