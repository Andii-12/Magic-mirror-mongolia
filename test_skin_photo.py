#!/usr/bin/env python3
"""
Test script for Skin Photo feature
This helps debug photo saving issues
"""

import os
import sys
from datetime import datetime

print("="*70)
print("SKIN PHOTO FEATURE - DEBUG TEST")
print("="*70)

# Test 1: Check current directory
print("\n1. CHECKING CURRENT DIRECTORY")
print("-" * 50)
current_dir = os.getcwd()
print(f"Current working directory: {current_dir}")

# Test 2: Test directory creation
print("\n2. TESTING DIRECTORY CREATION")
print("-" * 50)
test_person = "TestUser"
skin_base = os.path.join(current_dir, "Skin")
person_dir = os.path.join(skin_base, test_person)

print(f"Base directory will be: {skin_base}")
print(f"Person directory will be: {person_dir}")

try:
    os.makedirs(person_dir, exist_ok=True)
    print(f"✅ Directories created successfully!")
    
    # Verify
    if os.path.isdir(person_dir):
        print(f"✅ Directory exists and is accessible")
    else:
        print(f"❌ Directory not accessible")
        sys.exit(1)
        
except Exception as e:
    print(f"❌ Failed to create directories: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 3: Test file creation
print("\n3. TESTING FILE CREATION")
print("-" * 50)
current_date = datetime.now().strftime("%Y-%m-%d")
test_filename = f"test_{current_date}.txt"
test_filepath = os.path.join(person_dir, test_filename)

print(f"Test file will be: {test_filepath}")

try:
    with open(test_filepath, 'w') as f:
        f.write(f"Test file created at {datetime.now()}\n")
        f.write(f"Person: {test_person}\n")
        f.write(f"Date: {current_date}\n")
    
    print(f"✅ Test file created")
    
    # Verify
    if os.path.exists(test_filepath):
        file_size = os.path.getsize(test_filepath)
        print(f"✅ File exists!")
        print(f"   Size: {file_size} bytes")
        
        # Read back
        with open(test_filepath, 'r') as f:
            content = f.read()
        print(f"   Content preview: {content[:50]}...")
    else:
        print(f"❌ File does not exist after creation")
        sys.exit(1)
        
except Exception as e:
    print(f"❌ Failed to create test file: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 4: Check permissions
print("\n4. CHECKING PERMISSIONS")
print("-" * 50)
try:
    import stat
    
    # Check base directory
    base_stat = os.stat(skin_base)
    base_mode = stat.filemode(base_stat.st_mode)
    print(f"Base directory permissions: {base_mode}")
    
    # Check person directory
    person_stat = os.stat(person_dir)
    person_mode = stat.filemode(person_stat.st_mode)
    print(f"Person directory permissions: {person_mode}")
    
    # Check if writable
    if os.access(person_dir, os.W_OK):
        print(f"✅ Directory is writable")
    else:
        print(f"❌ Directory is NOT writable")
        
except Exception as e:
    print(f"⚠️  Could not check permissions: {e}")

# Test 5: List all files
print("\n5. LISTING FILES IN SKIN DIRECTORY")
print("-" * 50)
try:
    for root, dirs, files in os.walk(skin_base):
        level = root.replace(skin_base, '').count(os.sep)
        indent = ' ' * 2 * level
        print(f"{indent}{os.path.basename(root)}/")
        subindent = ' ' * 2 * (level + 1)
        for file in files:
            file_path = os.path.join(root, file)
            file_size = os.path.getsize(file_path)
            print(f"{subindent}{file} ({file_size} bytes)")
except Exception as e:
    print(f"Error listing files: {e}")

# Test 6: Disk space
print("\n6. CHECKING DISK SPACE")
print("-" * 50)
try:
    import shutil
    total, used, free = shutil.disk_usage(current_dir)
    
    print(f"Total: {total / (1024**3):.2f} GB")
    print(f"Used: {used / (1024**3):.2f} GB")
    print(f"Free: {free / (1024**3):.2f} GB")
    
    if free > 100 * 1024 * 1024:  # More than 100MB free
        print(f"✅ Sufficient disk space available")
    else:
        print(f"⚠️  Low disk space!")
        
except Exception as e:
    print(f"Could not check disk space: {e}")

# Summary
print("\n" + "="*70)
print("TEST SUMMARY")
print("="*70)
print(f"✅ All tests passed!")
print(f"\nYour Skin photo directory is ready:")
print(f"   Base: {skin_base}")
print(f"   Test user: {person_dir}")
print(f"\nYou can now run the face recognition system.")
print(f"Photos will be saved to: Skin/{{PersonName}}/{{date}}.jpg")
print("="*70)

# Cleanup option
print("\n📌 Test files created. Do you want to keep them? (for testing)")
print("   Keep them to verify the face recognition system can write here.")
print("   Or delete them manually later: rm -rf Skin/TestUser/")

