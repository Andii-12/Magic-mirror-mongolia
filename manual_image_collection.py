#!/usr/bin/env python3
"""
Manual Image Collection Script
Alternative to webcam collection - helps organize manual photos
"""

import os
import shutil
from pathlib import Path
from datetime import datetime

def setup_manual_collection():
    """Setup manual image collection"""
    print("📸 Manual Image Collection Setup")
    print("=" * 40)
    
    # Get person name
    person_name = input("Enter person's name: ").strip()
    if not person_name:
        print("❌ Please enter a valid name")
        return
    
    # Create directory
    person_dir = Path("Images") / person_name
    person_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"\n📁 Directory created: {person_dir}")
    print(f"🎯 Target: 40+ images")
    
    # Instructions
    print("\n📋 Instructions:")
    print("1. Take 40+ clear photos of the person")
    print("2. Use good lighting and front-facing angles")
    print("3. Copy photos to this directory:")
    print(f"   {person_dir}")
    print("4. Supported formats: .jpg, .jpeg, .png, .bmp")
    print("5. Run this script again to check progress")
    
    # Check existing images
    check_existing_images(person_dir, person_name)

def check_existing_images(person_dir, person_name):
    """Check existing images in directory"""
    print(f"\n📊 Checking existing images for {person_name}...")
    
    # Count images
    image_files = []
    for ext in ['.jpg', '.jpeg', '.png', '.bmp']:
        image_files.extend(person_dir.glob(f"*{ext}"))
        image_files.extend(person_dir.glob(f"*{ext.upper()}"))
    
    image_count = len(image_files)
    
    print(f"📸 Found {image_count} images")
    
    if image_count >= 40:
        print("✅ Enough images for training!")
        print("   You can now run: python3 train_faces.py")
    elif image_count > 0:
        print(f"⚠️  Need {40 - image_count} more images")
        print("   Add more photos and run this script again")
    else:
        print("❌ No images found")
        print("   Add photos to the directory and run again")
    
    # Show file list
    if image_files:
        print(f"\n📁 Files in {person_dir}:")
        for i, file in enumerate(image_files[:10]):  # Show first 10
            print(f"   {i+1}. {file.name}")
        if len(image_files) > 10:
            print(f"   ... and {len(image_files) - 10} more files")

def organize_images():
    """Organize images by renaming them"""
    print("\n🔧 Image Organization")
    print("=" * 25)
    
    # Get person name
    person_name = input("Enter person's name: ").strip()
    if not person_name:
        print("❌ Please enter a valid name")
        return
    
    person_dir = Path("Images") / person_name
    if not person_dir.exists():
        print(f"❌ Directory not found: {person_dir}")
        return
    
    # Get all image files
    image_files = []
    for ext in ['.jpg', '.jpeg', '.png', '.bmp']:
        image_files.extend(person_dir.glob(f"*{ext}"))
        image_files.extend(person_dir.glob(f"*{ext.upper()}"))
    
    if not image_files:
        print("❌ No images found")
        return
    
    print(f"📸 Found {len(image_files)} images")
    print("🔄 Renaming images for better organization...")
    
    # Rename images
    for i, file in enumerate(image_files):
        try:
            # Get file extension
            ext = file.suffix.lower()
            if not ext:
                ext = '.jpg'
            
            # Create new name
            new_name = f"{person_name.lower()}_{i+1:03d}{ext}"
            new_path = person_dir / new_name
            
            # Rename file
            if file != new_path:
                file.rename(new_path)
                print(f"   ✅ {file.name} -> {new_name}")
        except Exception as e:
            print(f"   ❌ Error renaming {file.name}: {e}")
    
    print("✅ Image organization completed!")

def main():
    """Main function"""
    print("📸 Manual Image Collection for Face Training")
    print("=" * 50)
    print("1. Setup manual collection")
    print("2. Check existing images")
    print("3. Organize images")
    print("4. Exit")
    
    while True:
        choice = input("\nSelect an option (1-4): ").strip()
        
        if choice == "1":
            setup_manual_collection()
        elif choice == "2":
            person_name = input("Enter person's name: ").strip()
            if person_name:
                person_dir = Path("Images") / person_name
                check_existing_images(person_dir, person_name)
        elif choice == "3":
            organize_images()
        elif choice == "4":
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid choice. Please select 1-4.")
        
        input("\nPress Enter to continue...")

if __name__ == "__main__":
    main()
