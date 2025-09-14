#!/usr/bin/env python3
"""
Comprehensive Face Training Script for MagicMirror²
All-in-one solution for face recognition training
"""

import cv2
import os
import numpy as np
import json
import shutil
from datetime import datetime
from pathlib import Path
import platform

# Configuration
IMAGES_DIR = "Images"
TARGET_IMAGES = 40

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

class FaceTrainer:
    def __init__(self):
        self.face_cascade = None
        self.recognizer = None
        self.labels = []
        self.label_ids = {}
        self.next_id = 0
        
    def load_face_cascade(self):
        """Load face cascade classifier"""
        cascade_path = get_cascade_path()
        
        if cascade_path is None:
            print("❌ Face cascade not found. Please install OpenCV properly.")
            print("   Try: sudo apt-get install python3-opencv")
            print("   Or: pip3 install opencv-python")
            return False
        
        print(f"📁 Using cascade: {cascade_path}")
        self.face_cascade = cv2.CascadeClassifier(cascade_path)
        
        if self.face_cascade.empty():
            print("❌ Could not load face cascade")
            return False
        
        print("✅ Face detector loaded")
        return True
    
    def setup_directories(self):
        """Setup directory structure for face training"""
        print("📁 Setting up directories...")
        
        # Create Images directory
        if not os.path.exists(IMAGES_DIR):
            os.makedirs(IMAGES_DIR)
            print(f"📁 Created {IMAGES_DIR}/ directory")
        
        # Create example directories
        example_people = ["Andii", "Jane", "Default"]
        for person in example_people:
            person_dir = Path(IMAGES_DIR) / person
            person_dir.mkdir(exist_ok=True)
            
            # Create README file
            readme_content = f"""# {person} Face Images

## Instructions:
1. Add 40+ clear face photos of {person} to this directory
2. Use good lighting and clear, front-facing photos
3. Supported formats: .jpg, .jpeg, .png, .bmp
4. Avoid blurry or side-profile photos

## Tips for best results:
- Use photos taken in good lighting
- Face should be clearly visible and centered
- Avoid sunglasses or hats that obscure the face
- Mix of different expressions works well
- Photos should be recent and representative
- More photos = better accuracy (40+ recommended)

## Example filenames:
- {person.lower()}_1.jpg
- {person.lower()}_2.jpg
- {person.lower()}_3.jpg
- etc.

After adding photos, run: python3 train_faces.py
"""
            
            readme_file = person_dir / "README.md"
            readme_file.write_text(readme_content)
            
            print(f"📁 Created directory: {person_dir}")
        
        print("✅ Directory structure created successfully!")
        return True
    
    def collect_images_webcam(self, person_name):
        """Collect face images using webcam"""
        print(f"📸 Collecting images for {person_name}")
        print("=" * 40)
        
        # Create directory
        person_dir = Path(IMAGES_DIR) / person_name
        person_dir.mkdir(parents=True, exist_ok=True)
        
        # Check if we're on Windows (simulation mode)
        if platform.system() == "Windows":
            print("⚠️  Windows detected - simulation mode")
            print(f"   Please manually add 40+ photos to: {person_dir}")
            print("   Supported formats: .jpg, .jpeg, .png, .bmp")
            return True
        
        # Try different camera backends and indices
        camera_backends = [
            (cv2.CAP_V4L2, 0),      # V4L2 backend (Linux)
            (cv2.CAP_V4L2, 1),      # V4L2 backend, camera 1
            (cv2.CAP_ANY, 0),       # Any backend, camera 0
            (cv2.CAP_ANY, 1),       # Any backend, camera 1
            (cv2.CAP_GSTREAMER, 0), # GStreamer backend
        ]
        
        cap = None
        for backend, camera_index in camera_backends:
            try:
                print(f"🔍 Trying camera {camera_index} with backend {backend}...")
                cap = cv2.VideoCapture(camera_index, backend)
                
                if cap.isOpened():
                    # Test if we can read a frame
                    ret, frame = cap.read()
                    if ret and frame is not None:
                        print(f"✅ Camera {camera_index} working with backend {backend}")
                        break
                    else:
                        cap.release()
                        cap = None
                else:
                    cap.release()
                    cap = None
            except Exception as e:
                print(f"   ❌ Failed: {e}")
                if cap:
                    cap.release()
                    cap = None
        
        if cap is None or not cap.isOpened():
            print("❌ Could not open any camera")
            print("\n🔧 Troubleshooting:")
            print("   1. Check if camera is connected")
            print("   2. Try: ls /dev/video*")
            print("   3. Check camera permissions")
            print("   4. Try: sudo usermod -a -G video $USER")
            print("   5. Reboot and try again")
            print(f"\n💡 Alternative: Manually add photos to {person_dir}")
            return False
        
        # Configure camera settings
        try:
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            cap.set(cv2.CAP_PROP_FPS, 30)
            cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # Reduce buffer size
        except:
            pass  # Ignore if settings can't be applied
        
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
        frame_skip_count = 0
        max_frame_skips = 10  # Maximum consecutive frame skips
        
        while image_count < TARGET_IMAGES:
            ret, frame = cap.read()
            if not ret:
                frame_skip_count += 1
                if frame_skip_count >= max_frame_skips:
                    print("❌ Too many failed frame reads. Camera may have disconnected.")
                    break
                continue
            
            frame_skip_count = 0  # Reset skip count on successful read
            
            # Get current time
            current_time = datetime.now().timestamp()
            
            # Convert to grayscale for face detection
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Detect faces
            faces = self.face_cascade.detectMultiScale(gray, 1.1, 5, minSize=(30, 30))
            
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
    
    def process_images(self, person_name):
        """Process and enhance images for better training"""
        print(f"🔧 Processing images for {person_name}...")
        
        person_dir = Path(IMAGES_DIR) / person_name
        if not person_dir.exists():
            print(f"   ❌ Directory not found: {person_dir}")
            return 0
        
        # Get all image files
        image_files = []
        for ext in ['*.jpg', '*.jpeg', '*.png', '*.bmp']:
            image_files.extend(person_dir.glob(ext))
        
        if not image_files:
            print(f"   ⚠️  No images found in {person_name}")
            return 0
        
        print(f"   📸 Found {len(image_files)} images")
        
        processed_count = 0
        for image_file in image_files:
            try:
                # Load image
                image = cv2.imread(str(image_file))
                if image is None:
                    continue
                
                # Convert to different color spaces for variety
                variations = [
                    image,  # Original
                    cv2.cvtColor(image, cv2.COLOR_BGR2GRAY),  # Grayscale
                    cv2.cvtColor(image, cv2.COLOR_BGR2HSV),   # HSV
                ]
                
                # Apply different enhancements
                for i, variation in enumerate(variations):
                    if len(variation.shape) == 2:  # Grayscale
                        # Convert back to BGR for consistency
                        variation = cv2.cvtColor(variation, cv2.COLOR_GRAY2BGR)
                    
                    # Apply histogram equalization
                    enhanced = cv2.cvtColor(variation, cv2.COLOR_BGR2YUV)
                    enhanced[:,:,0] = cv2.equalizeHist(enhanced[:,:,0])
                    enhanced = cv2.cvtColor(enhanced, cv2.COLOR_YUV2BGR)
                    
                    # Save enhanced version
                    base_name = image_file.stem
                    filename = f"{person_name.lower()}_{base_name}_enhanced_{i+1}.jpg"
                    output_path = person_dir / filename
                    cv2.imwrite(str(output_path), enhanced)
                    processed_count += 1
                    
            except Exception as e:
                print(f"   ⚠️  Error processing {image_file.name}: {e}")
        
        print(f"   ✅ Created {processed_count} enhanced variations")
        return processed_count
    
    def load_training_data(self):
        """Load and prepare training data from Images directory"""
        print("📚 Loading training data...")
        
        faces = []
        labels = []
        
        if not os.path.exists(IMAGES_DIR):
            print(f"❌ {IMAGES_DIR} directory not found!")
            return None, None
        
        # Get all person directories
        person_dirs = [d for d in os.listdir(IMAGES_DIR) 
                      if os.path.isdir(os.path.join(IMAGES_DIR, d)) and not d.startswith('.')]
        
        if not person_dirs:
            print("❌ No person directories found!")
            return None, None
        
        print(f"👥 Found {len(person_dirs)} people: {', '.join(person_dirs)}")
        
        # Process each person
        for person_dir in person_dirs:
            person_path = os.path.join(IMAGES_DIR, person_dir)
            person_id = self.next_id
            self.label_ids[person_dir] = person_id
            self.next_id += 1
            
            print(f"   👤 Processing {person_dir}...")
            
            # Get all image files
            image_files = []
            for ext in ['*.jpg', '*.jpeg', '*.png', '*.bmp']:
                image_files.extend(Path(person_path).glob(ext))
            
            faces_found = 0
            for image_file in image_files:
                try:
                    # Load image
                    image = cv2.imread(str(image_file))
                    if image is None:
                        continue
                    
                    # Convert to grayscale
                    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                    
                    # Detect faces
                    detected_faces = self.face_cascade.detectMultiScale(gray, 1.1, 5, minSize=(50, 50))
                    
                    # Add each detected face
                    for (x, y, w, h) in detected_faces:
                        face_roi = gray[y:y+h, x:x+w]
                        face_resized = cv2.resize(face_roi, (200, 200))
                        faces.append(face_resized)
                        labels.append(person_id)
                        faces_found += 1
                        
                except Exception as e:
                    print(f"   ⚠️  Error with {image_file.name}: {e}")
                    continue
            
            print(f"   ✅ Found {faces_found} faces")
        
        if len(faces) < 10:
            print("❌ Not enough faces found! Need at least 10 faces total.")
            print("   Recommended: 40+ faces per person for best accuracy")
            return None, None
        
        print(f"✅ Total faces loaded: {len(faces)}")
        print(f"✅ Total people: {len(set(labels))}")
        
        return faces, labels
    
    def train_recognizer(self, faces, labels):
        """Train the face recognizer"""
        print("🤖 Training recognizer...")
        
        try:
            # Create recognizer
            recognizer = cv2.face.LBPHFaceRecognizer_create()
            
            # Train the recognizer
            recognizer.train(faces, np.array(labels))
            
            print("✅ Training completed successfully!")
            return recognizer
            
        except Exception as e:
            print(f"❌ Training failed: {e}")
            return None
    
    def save_model(self, recognizer):
        """Save the trained model and labels"""
        print("💾 Saving model...")
        
        try:
            # Save recognizer
            recognizer.save("trainer.yml")
            print("✅ Saved trainer.yml")
            
            # Save labels
            labels_data = {
                "people": {person: id for person, id in self.label_ids.items()},
                "created_at": datetime.now().isoformat(),
                "total_people": len(self.label_ids)
            }
            
            with open("labels.json", "w") as f:
                json.dump(labels_data, f, indent=2)
            
            print("✅ Saved labels.json")
            
            # Create summary
            summary = {
                "model_file": "trainer.yml",
                "labels_file": "labels.json",
                "people": list(self.label_ids.keys()),
                "total_people": len(self.label_ids),
                "created_at": datetime.now().isoformat()
            }
            
            with open("training_summary.json", "w") as f:
                json.dump(summary, f, indent=2)
            
            print("✅ Saved training_summary.json")
            return True
            
        except Exception as e:
            print(f"❌ Failed to save model: {e}")
            return False
    
    def test_model(self, recognizer):
        """Test the trained model with camera"""
        print("🧪 Testing model with camera...")
        
        if platform.system() == "Windows":
            print("⚠️  Windows detected - skipping camera test")
            return True
        
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("❌ Could not open camera for testing")
            return False
        
        print("📋 Instructions:")
        print("   - Look at the camera to test recognition")
        print("   - Press 'q' to quit testing")
        print("")
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            # Convert to grayscale
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Detect faces
            faces = self.face_cascade.detectMultiScale(gray, 1.1, 5, minSize=(50, 50))
            
            # Recognize each face
            for (x, y, w, h) in faces:
                face_roi = gray[y:y+h, x:x+w]
                face_resized = cv2.resize(face_roi, (200, 200))
                
                # Predict
                label, confidence = recognizer.predict(face_resized)
                
                # Get person name
                person_name = "Unknown"
                for person, person_id in self.label_ids.items():
                    if person_id == label:
                        person_name = person
                        break
                
                # Draw rectangle and label
                color = (0, 255, 0) if confidence < 100 else (0, 0, 255)
                cv2.rectangle(frame, (x, y), (x+w, y+h), color, 2)
                
                # Add text
                text = f"{person_name} ({confidence:.1f})"
                cv2.putText(frame, text, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
            
            # Show frame
            cv2.imshow('Face Recognition Test', frame)
            
            # Check for quit
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        # Cleanup
        cap.release()
        cv2.destroyAllWindows()
        
        print("✅ Camera test completed")
        return True
    
    def show_menu(self):
        """Display main menu"""
        print("\n" + "="*50)
        print("🎭 FACE TRAINING SYSTEM FOR MAGICMIRROR²")
        print("="*50)
        print("1. 📁 Setup directories")
        print("2. 📸 Collect images with webcam")
        print("3. 🔧 Process existing images")
        print("4. 🤖 Train face recognition model")
        print("5. 🧪 Test trained model")
        print("6. 📊 Show training status")
        print("7. 🚀 Complete training workflow")
        print("8. ❌ Exit")
        print("="*50)
    
    def show_status(self):
        """Show current training status"""
        print("\n📊 TRAINING STATUS")
        print("="*30)
        
        # Check Images directory
        if os.path.exists(IMAGES_DIR):
            person_dirs = [d for d in os.listdir(IMAGES_DIR) 
                          if os.path.isdir(os.path.join(IMAGES_DIR, d)) and not d.startswith('.')]
            
            if person_dirs:
                print("👥 People found:")
                total_images = 0
                for person_dir in person_dirs:
                    person_path = os.path.join(IMAGES_DIR, person_dir)
                    image_files = []
                    for ext in ['*.jpg', '*.jpeg', '*.png', '*.bmp']:
                        image_files.extend(Path(person_path).glob(ext))
                    
                    image_count = len(image_files)
                    total_images += image_count
                    status = "✅" if image_count >= TARGET_IMAGES else "⚠️"
                    print(f"   {status} {person_dir}: {image_count} images")
                
                print(f"\n📸 Total images: {total_images}")
                print(f"🎯 Target per person: {TARGET_IMAGES}+")
            else:
                print("❌ No people directories found")
        else:
            print("❌ Images directory not found")
        
        # Check model files
        print("\n🤖 Model files:")
        if os.path.exists("trainer.yml"):
            print("   ✅ trainer.yml (trained model)")
        else:
            print("   ❌ trainer.yml (not found)")
        
        if os.path.exists("labels.json"):
            print("   ✅ labels.json (person labels)")
        else:
            print("   ❌ labels.json (not found)")
        
        if os.path.exists("training_summary.json"):
            print("   ✅ training_summary.json (summary)")
        else:
            print("   ❌ training_summary.json (not found)")
    
    def complete_workflow(self):
        """Run complete training workflow"""
        print("\n🚀 COMPLETE TRAINING WORKFLOW")
        print("="*40)
        
        # Step 1: Setup
        print("\n1️⃣ Setting up directories...")
        if not self.setup_directories():
            return False
        
        # Step 2: Collect images
        print("\n2️⃣ Collecting images...")
        people = [d for d in os.listdir(IMAGES_DIR) 
                 if os.path.isdir(os.path.join(IMAGES_DIR, d)) and not d.startswith('.')]
        
        for person in people:
            print(f"\n📸 Collecting images for {person}...")
            if not self.collect_images_webcam(person):
                print(f"⚠️  Skipping {person} - no images collected")
                continue
            
            # Process images
            print(f"🔧 Processing images for {person}...")
            self.process_images(person)
        
        # Step 3: Train model
        print("\n3️⃣ Training model...")
        faces, labels = self.load_training_data()
        if faces is None:
            print("❌ No training data found")
            return False
        
        recognizer = self.train_recognizer(faces, labels)
        if recognizer is None:
            print("❌ Training failed")
            return False
        
        # Step 4: Save model
        print("\n4️⃣ Saving model...")
        if not self.save_model(recognizer):
            print("❌ Failed to save model")
            return False
        
        # Step 5: Test model
        print("\n5️⃣ Testing model...")
        self.test_model(recognizer)
        
        print("\n🎉 Training workflow completed successfully!")
        print("\n📋 Next steps:")
        print("   1. Copy trainer.yml to your MagicMirror² directory")
        print("   2. Copy labels.json to your MagicMirror² directory")
        print("   3. Start MagicMirror²: ./start.sh")
        
        return True
    
    def run(self):
        """Main run function"""
        print("🎭 Welcome to Face Training System!")
        
        # Load face cascade
        if not self.load_face_cascade():
            return
        
        while True:
            self.show_menu()
            choice = input("\nSelect an option (1-8): ").strip()
            
            if choice == "1":
                self.setup_directories()
            
            elif choice == "2":
                person_name = input("Enter person's name: ").strip()
                if person_name:
                    self.collect_images_webcam(person_name)
            
            elif choice == "3":
                person_name = input("Enter person's name: ").strip()
                if person_name:
                    self.process_images(person_name)
            
            elif choice == "4":
                faces, labels = self.load_training_data()
                if faces is not None:
                    recognizer = self.train_recognizer(faces, labels)
                    if recognizer is not None:
                        self.save_model(recognizer)
                        self.recognizer = recognizer
            
            elif choice == "5":
                if self.recognizer is not None:
                    self.test_model(self.recognizer)
                else:
                    print("❌ No trained model found. Train first!")
            
            elif choice == "6":
                self.show_status()
            
            elif choice == "7":
                self.complete_workflow()
            
            elif choice == "8":
                print("👋 Goodbye!")
                break
            
            else:
                print("❌ Invalid choice. Please select 1-8.")
            
            input("\nPress Enter to continue...")

def main():
    """Main function"""
    trainer = FaceTrainer()
    trainer.run()

if __name__ == "__main__":
    main()
