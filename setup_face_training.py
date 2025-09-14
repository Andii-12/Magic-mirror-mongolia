#!/usr/bin/env python3
"""
Face Training Setup Script for MagicMirror²
Helps organize and prepare face images for training
"""

import os
import shutil
from pathlib import Path

def create_training_structure():
    """Create the proper directory structure for face training"""
    print("🎯 Setting up Face Training Structure")
    print("=" * 40)
    
    # Create main directories
    images_dir = Path("Images")
    images_dir.mkdir(exist_ok=True)
    
    # Create example person directories
    example_people = ["Andii", "Jane", "Guest"]
    
    for person in example_people:
        person_dir = images_dir / person
        person_dir.mkdir(exist_ok=True)
        
        # Create README file for each person
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

After adding photos, run: python3 simple_train_faces.py
"""
        
        readme_file = person_dir / "README.md"
        readme_file.write_text(readme_content)
        
        print(f"📁 Created directory: {person_dir}")
    
    # Create main README
    main_readme = images_dir / "README.md"
    main_readme.write_text("""# Face Training Images

This directory contains face images for training the MagicMirror² face recognition system.

## Directory Structure:
```
Images/
├── Andii/          # Photos of Andii
├── Jane/           # Photos of Jane  
├── Guest/          # Photos of Guest
└── README.md       # This file
```

## Quick Start:
1. Add 10-20 clear face photos to each person's directory
2. Run: `python3 simple_train_faces.py`
3. Copy the generated `trainer.yml` to your MagicMirror² directory

## Training Scripts:
- `simple_train_faces.py` - Quick and easy training
- `train_face_recognition.py` - Advanced training with testing

## Tips:
- Use photos with good lighting
- Face should be clearly visible and centered
- Avoid sunglasses, hats, or side profiles
- Mix of expressions works best
- Recent photos are recommended
""")
    
    print(f"📁 Created main README: {main_readme}")
    
    # Create sample images directory
    sample_dir = images_dir / "sample_images"
    sample_dir.mkdir(exist_ok=True)
    
    sample_readme = sample_dir / "README.md"
    sample_readme.write_text("""# Sample Images

This directory is for sample images that demonstrate the proper format and quality.

## Image Requirements:
- Format: JPG, PNG, BMP
- Size: Any (will be resized automatically)
- Quality: Clear, well-lit, front-facing
- Content: Single face per image

## What to avoid:
- Blurry photos
- Side profiles
- Sunglasses or hats
- Multiple faces in one image
- Very old photos (if appearance has changed)

## Example good photos:
- Selfie with good lighting
- Clear portrait photos
- Photos taken in natural light
- Recent photos that look like you now
""")
    
    print(f"📁 Created sample directory: {sample_dir}")
    
    print("")
    print("✅ Directory structure created successfully!")
    print("")
    print("📋 Next steps:")
    print("   1. Add face photos to each person's directory")
    print("   2. Run: python3 simple_train_faces.py")
    print("   3. Copy trainer.yml to your MagicMirror² directory")
    print("")
    print("💡 Tips:")
    print("   - Use 40+ photos per person for best accuracy")
    print("   - Good lighting is important")
    print("   - Clear, front-facing photos work best")
    print("   - Mix of expressions is helpful")
    print("   - More photos = better recognition")

def check_existing_images():
    """Check if there are already images in the directories"""
    images_dir = Path("Images")
    
    if not images_dir.exists():
        return
    
    print("🔍 Checking existing images...")
    
    total_images = 0
    for person_dir in images_dir.iterdir():
        if person_dir.is_dir() and not person_dir.name.startswith('.'):
            image_files = list(person_dir.glob("*.jpg")) + list(person_dir.glob("*.jpeg")) + list(person_dir.glob("*.png")) + list(person_dir.glob("*.bmp"))
            image_count = len(image_files)
            total_images += image_count
            
            if image_count > 0:
                print(f"   👤 {person_dir.name}: {image_count} images")
            else:
                print(f"   👤 {person_dir.name}: No images")
    
    if total_images > 0:
        print(f"   📊 Total images found: {total_images}")
        print("   ✅ Ready for training!")
    else:
        print("   ⚠️  No images found. Please add face photos first.")

def main():
    """Main setup function"""
    print("🎯 MagicMirror² Face Training Setup")
    print("=" * 40)
    
    # Create directory structure
    create_training_structure()
    
    # Check for existing images
    check_existing_images()
    
    print("")
    print("🚀 Setup complete!")
    print("")
    print("📖 For detailed instructions, see the README files in each directory.")

if __name__ == "__main__":
    main()
