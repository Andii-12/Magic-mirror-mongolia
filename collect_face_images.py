#!/usr/bin/env python3
"""
Face Image Collection Helper for MagicMirror²
Helps collect 40+ face images using webcam for training
"""

import cv2
import os
import numpy as np
from datetime import datetime
from pathlib import Path

# Configuration
IMAGES_DIR = "Images"
TARGET_IMAGES = 40
CASCADE_PATH = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'

def create_person_directory(person_name):
    """Create directory for a person and return the path"""
    person_dir = Path(IMAGES_DIR) / person_name
    person_dir.mkdir(parents=True, exist_ok=True)
    return person_dir

def collect_images_for_person(person_name):
    """Collect face images for a specific person using webcam"""
    print(f"📸 Collecting images for {person_name}")
    print("=" * 40)
    
    # Create directory
    person_dir = create_person_directory(person_name)
    
    # Load face cascade
    face_cascade = cv2.CascadeClassifier(CASCADE_PATH)
    if face_cascade.empty():
        print("❌ Could not load face cascade")
        return False
    
    # Check if we're on Windows (simulation mode)
    import platform
    if platform.system() == "Windows":
        print("⚠️  Windows detected - simulation mode")
        print(f"   Please manually add 40+ photos to: {person_dir}")
        print("   Supported formats: .jpg, .jpeg, .png, .bmp")
        return True
    
    # Initialize camera
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("❌ Could not open camera")
        return False
    
    print(f"🎯 Target: {TARGET_IMAGES} images")
    print("📋 Instructions:")
    print("   - Look at the camera")
    print("   - Press SPACE to capture a photo")
    print("   - Press 'q' to quit")
    print("   - Make sure your face is clearly visible")
    print("")
    
    image_count = 0
    last_capture_time = 0
    min_capture_interval = 1.0  # Minimum 1 second between captures
    
    while image_count < TARGET_IMAGES:
        ret, frame = cap.read()
        if not ret:
            break
        
        # Get current time
        current_time = datetime.now().timestamp()
        
        # Convert to grayscale for face detection
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Detect faces
        faces = face_cascade.detectMultiScale(gray, 1.1, 5, minSize=(30, 30))
        
        # Draw rectangle around detected face
        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
            
            # Add text overlay
            cv2.putText(frame, f"Face detected! Press SPACE to capture", 
                       (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        # Add status text
        status_text = f"Images collected: {image_count}/{TARGET_IMAGES}"
        cv2.putText(frame, status_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        
        # Add instructions
        cv2.putText(frame, "SPACE: Capture | Q: Quit", (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        # Show frame
        cv2.imshow(f'Collecting images for {person_name}', frame)
        
        # Handle key presses
        key = cv2.waitKey(1) & 0xFF
        
        if key == ord(' '):  # Space bar to capture
            if len(faces) > 0 and (current_time - last_capture_time) >= min_capture_interval:
                # Use the largest face
                largest_face = max(faces, key=lambda x: x[2] * x[3])
                x, y, w, h = largest_face
                
                # Extract face region
                face_roi = frame[y:y+h, x:x+w]
                
                # Save image
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"{person_name.lower()}_{image_count+1:03d}_{timestamp}.jpg"
                filepath = person_dir / filename
                
                cv2.imwrite(str(filepath), face_roi)
                image_count += 1
                last_capture_time = current_time
                
                print(f"✅ Captured image {image_count}/{TARGET_IMAGES}: {filename}")
                
                # Show success message briefly
                cv2.putText(frame, "CAPTURED!", (x, y-30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 3)
                cv2.imshow(f'Collecting images for {person_name}', frame)
                cv2.waitKey(500)  # Show success message for 500ms
                
            elif len(faces) == 0:
                print("⚠️  No face detected - position yourself in front of the camera")
            else:
                print("⚠️  Please wait before capturing another image")
        
        elif key == ord('q'):  # Quit
            break
    
    # Cleanup
    cap.release()
    cv2.destroyAllWindows()
    
    print(f"")
    print(f"📊 Collection complete!")
    print(f"   Images collected: {image_count}/{TARGET_IMAGES}")
    print(f"   Saved to: {person_dir}")
    
    if image_count < TARGET_IMAGES:
        print(f"   ⚠️  You can add more images manually to reach {TARGET_IMAGES}")
    
    return image_count > 0

def list_existing_people():
    """List existing people in the Images directory"""
    images_dir = Path(IMAGES_DIR)
    
    if not images_dir.exists():
        return []
    
    people = []
    for person_dir in images_dir.iterdir():
        if person_dir.is_dir() and not person_dir.name.startswith('.'):
            # Count images in directory
            image_files = list(person_dir.glob("*.jpg")) + list(person_dir.glob("*.jpeg")) + list(person_dir.glob("*.png")) + list(person_dir.glob("*.bmp"))
            image_count = len(image_files)
            people.append((person_dir.name, image_count))
    
    return people

def main():
    """Main collection function"""
    print("📸 Face Image Collection Helper")
    print("=" * 35)
    
    # List existing people
    existing_people = list_existing_people()
    
    if existing_people:
        print("👥 Existing people:")
        for person_name, image_count in existing_people:
            status = "✅" if image_count >= TARGET_IMAGES else "⚠️"
            print(f"   {status} {person_name}: {image_count} images")
        print("")
    
    # Get person name
    person_name = input("Enter person's name (or 'q' to quit): ").strip()
    
    if person_name.lower() == 'q':
        print("👋 Goodbye!")
        return
    
    if not person_name:
        print("❌ Please enter a valid name")
        return
    
    # Check if person already exists
    person_dir = Path(IMAGES_DIR) / person_name
    if person_dir.exists():
        existing_images = list(person_dir.glob("*.jpg")) + list(person_dir.glob("*.jpeg")) + list(person_dir.glob("*.png")) + list(person_dir.glob("*.bmp"))
        existing_count = len(existing_images)
        
        if existing_count >= TARGET_IMAGES:
            print(f"✅ {person_name} already has {existing_count} images")
            choice = input("Do you want to collect more? (y/n): ").strip().lower()
            if choice != 'y':
                return
        else:
            print(f"📊 {person_name} has {existing_count} images, need {TARGET_IMAGES - existing_count} more")
    
    # Collect images
    success = collect_images_for_person(person_name)
    
    if success:
        print("")
        print("🎉 Image collection completed!")
        print("")
        print("📋 Next steps:")
        print("   1. Run: python3 simple_train_faces.py")
        print("   2. Test: python3 test_face_training.py")
        print("   3. Start MagicMirror²: ./start.sh")
    else:
        print("❌ Image collection failed")

if __name__ == "__main__":
    main()
