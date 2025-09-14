#!/usr/bin/env python3
"""
Image Preparation Script for Face Training
Helps prepare and organize images for better training results
"""

import cv2
import os
import numpy as np
from pathlib import Path
import shutil
from datetime import datetime

# Configuration
IMAGES_DIR = "Images"
PROCESSED_DIR = "Images_Processed"
CASCADE_PATH = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'

def create_processed_directory():
    """Create processed images directory"""
    processed_path = Path(PROCESSED_DIR)
    processed_path.mkdir(exist_ok=True)
    return processed_path

def detect_and_crop_faces(image_path, face_cascade):
    """Detect faces in an image and return cropped face regions"""
    try:
        # Load image
        image = cv2.imread(str(image_path))
        if image is None:
            return []
        
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Detect faces
        faces = face_cascade.detectMultiScale(
            gray, 
            scaleFactor=1.1, 
            minNeighbors=5, 
            minSize=(50, 50)  # Minimum face size
        )
        
        cropped_faces = []
        for (x, y, w, h) in faces:
            # Add some padding around the face
            padding = 20
            x1 = max(0, x - padding)
            y1 = max(0, y - padding)
            x2 = min(image.shape[1], x + w + padding)
            y2 = min(image.shape[0], y + h + padding)
            
            # Crop face region
            face_crop = image[y1:y2, x1:x2]
            
            # Resize to standard size
            face_resized = cv2.resize(face_crop, (200, 200))
            
            cropped_faces.append(face_resized)
        
        return cropped_faces
        
    except Exception as e:
        print(f"   ❌ Error processing {image_path.name}: {e}")
        return []

def process_person_images(person_name, face_cascade):
    """Process all images for a specific person"""
    print(f"👤 Processing {person_name}...")
    
    person_dir = Path(IMAGES_DIR) / person_name
    if not person_dir.exists():
        print(f"   ❌ Directory not found: {person_dir}")
        return 0
    
    # Create processed directory for this person
    processed_person_dir = Path(PROCESSED_DIR) / person_name
    processed_person_dir.mkdir(exist_ok=True)
    
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
        # Detect and crop faces
        cropped_faces = detect_and_crop_faces(image_file, face_cascade)
        
        if cropped_faces:
            # Save each detected face
            for i, face in enumerate(cropped_faces):
                # Generate filename
                base_name = image_file.stem
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"{person_name.lower()}_{base_name}_{i+1}_{timestamp}.jpg"
                output_path = processed_person_dir / filename
                
                # Save processed face
                cv2.imwrite(str(output_path), face)
                processed_count += 1
        else:
            print(f"   ⚠️  No faces detected in {image_file.name}")
    
    print(f"   ✅ Processed {processed_count} faces")
    return processed_count

def enhance_images(person_name):
    """Enhance images for better training"""
    print(f"🔧 Enhancing images for {person_name}...")
    
    person_dir = Path(IMAGES_DIR) / person_name
    if not person_dir.exists():
        return 0
    
    enhanced_count = 0
    for image_file in person_dir.glob("*.jpg"):
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
                enhanced_count += 1
                
        except Exception as e:
            print(f"   ⚠️  Error enhancing {image_file.name}: {e}")
    
    print(f"   ✅ Created {enhanced_count} enhanced variations")
    return enhanced_count

def create_training_summary():
    """Create a summary of the training data"""
    print("📊 Creating training summary...")
    
    summary = {
        "created_at": datetime.now().isoformat(),
        "people": {},
        "total_images": 0,
        "total_faces": 0
    }
    
    # Count images in original directory
    images_dir = Path(IMAGES_DIR)
    if images_dir.exists():
        for person_dir in images_dir.iterdir():
            if person_dir.is_dir() and not person_dir.name.startswith('.'):
                image_files = []
                for ext in ['*.jpg', '*.jpeg', '*.png', '*.bmp']:
                    image_files.extend(person_dir.glob(ext))
                
                summary["people"][person_dir.name] = {
                    "original_images": len(image_files),
                    "processed_faces": 0
                }
                summary["total_images"] += len(image_files)
    
    # Count processed faces
    processed_dir = Path(PROCESSED_DIR)
    if processed_dir.exists():
        for person_dir in processed_dir.iterdir():
            if person_dir.is_dir() and not person_dir.name.startswith('.'):
                face_files = list(person_dir.glob("*.jpg"))
                if person_dir.name in summary["people"]:
                    summary["people"][person_dir.name]["processed_faces"] = len(face_files)
                summary["total_faces"] += len(face_files)
    
    # Save summary
    import json
    with open("training_summary.json", "w") as f:
        json.dump(summary, f, indent=2)
    
    print("✅ Training summary saved to training_summary.json")
    
    # Print summary
    print("\n📊 Training Data Summary:")
    print("=" * 30)
    for person_name, data in summary["people"].items():
        print(f"👤 {person_name}:")
        print(f"   📸 Original images: {data['original_images']}")
        print(f"   🎯 Processed faces: {data['processed_faces']}")
    
    print(f"\n📈 Total:")
    print(f"   📸 Images: {summary['total_images']}")
    print(f"   🎯 Faces: {summary['total_faces']}")
    
    return summary

def main():
    """Main processing function"""
    print("🔧 Image Preparation for Face Training")
    print("=" * 40)
    
    # Check if Images directory exists
    images_dir = Path(IMAGES_DIR)
    if not images_dir.exists():
        print(f"❌ {IMAGES_DIR} directory not found!")
        print("   Run: python3 setup_face_training.py")
        return
    
    # Load face cascade
    face_cascade = cv2.CascadeClassifier(CASCADE_PATH)
    if face_cascade.empty():
        print("❌ Could not load face cascade")
        return
    
    print("✅ Face detector loaded")
    
    # Create processed directory
    create_processed_directory()
    
    # Get list of people
    people = [d.name for d in images_dir.iterdir() 
              if d.is_dir() and not d.name.startswith('.')]
    
    if not people:
        print("❌ No people directories found!")
        return
    
    print(f"👥 Found {len(people)} people: {', '.join(people)}")
    print("")
    
    # Process each person
    total_faces = 0
    for person_name in people:
        # Process images
        faces_count = process_person_images(person_name, face_cascade)
        total_faces += faces_count
        
        # Enhance images (optional)
        enhance_choice = input(f"Enhance images for {person_name}? (y/n): ").strip().lower()
        if enhance_choice == 'y':
            enhance_images(person_name)
    
    print("")
    print("🎉 Image processing completed!")
    print(f"   📊 Total faces processed: {total_faces}")
    
    # Create summary
    create_training_summary()
    
    print("")
    print("📋 Next steps:")
    print("   1. Review processed images in Images_Processed/")
    print("   2. Run: python3 simple_train_faces.py")
    print("   3. Test: python3 test_face_training.py")

if __name__ == "__main__":
    main()
