#!/usr/bin/env python3
"""
OpenCV Test Script
Tests OpenCV installation and finds cascade files
"""

import cv2
import os
import sys
import glob

def test_opencv():
    """Test OpenCV installation and find cascade files"""
    print("🧪 Testing OpenCV Installation")
    print("=" * 35)
    
    # Test basic OpenCV import
    try:
        print(f"✅ OpenCV version: {cv2.__version__}")
    except Exception as e:
        print(f"❌ OpenCV import failed: {e}")
        return False
    
    # Test cv2.data attribute
    print("\n📁 Testing cv2.data attribute...")
    try:
        if hasattr(cv2, 'data'):
            print("✅ cv2.data attribute exists")
            if hasattr(cv2.data, 'haarcascades'):
                print("✅ cv2.data.haarcascades exists")
                cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
                print(f"   Path: {cascade_path}")
                if os.path.exists(cascade_path):
                    print("✅ Cascade file found at cv2.data path")
                    return True
                else:
                    print("❌ Cascade file not found at cv2.data path")
            else:
                print("❌ cv2.data.haarcascades does not exist")
        else:
            print("❌ cv2.data attribute does not exist")
    except Exception as e:
        print(f"❌ Error accessing cv2.data: {e}")
    
    # Search for cascade files
    print("\n🔍 Searching for cascade files...")
    possible_paths = [
        '/usr/share/opencv4/haarcascades/haarcascade_frontalface_default.xml',
        '/usr/share/opencv/haarcascades/haarcascade_frontalface_default.xml',
        '/usr/local/share/opencv4/haarcascades/haarcascade_frontalface_default.xml',
        '/usr/local/share/opencv/haarcascades/haarcascade_frontalface_default.xml',
        '/home/andii/haarcascades/haarcascade_frontalface_default.xml',
        'haarcascade_frontalface_default.xml'
    ]
    
    found_paths = []
    for path in possible_paths:
        if os.path.exists(path):
            found_paths.append(path)
            print(f"✅ Found: {path}")
        else:
            print(f"❌ Not found: {path}")
    
    # Search recursively
    print("\n🔍 Searching recursively...")
    cascade_files = glob.glob('**/haarcascade_frontalface_default.xml', recursive=True)
    if cascade_files:
        print("✅ Found cascade files:")
        for file in cascade_files:
            print(f"   {file}")
    else:
        print("❌ No cascade files found recursively")
    
    # Test cascade loading
    print("\n🧪 Testing cascade loading...")
    test_paths = found_paths + cascade_files
    if not test_paths:
        print("❌ No cascade files to test")
        return False
    
    for path in test_paths:
        try:
            cascade = cv2.CascadeClassifier(path)
            if not cascade.empty():
                print(f"✅ Successfully loaded: {path}")
                return True
            else:
                print(f"❌ Failed to load: {path}")
        except Exception as e:
            print(f"❌ Error loading {path}: {e}")
    
    return False

def main():
    """Main function"""
    success = test_opencv()
    
    print("\n" + "=" * 35)
    if success:
        print("🎉 OpenCV test passed!")
        print("   You can now run: python3 train_faces.py")
    else:
        print("❌ OpenCV test failed!")
        print("\n🔧 Troubleshooting:")
        print("   1. Install OpenCV: sudo apt-get install python3-opencv")
        print("   2. Or try: pip3 install opencv-python")
        print("   3. Check Python version: python3 --version")
        print("   4. Try: python3 -c 'import cv2; print(cv2.__version__)'")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
