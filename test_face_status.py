#!/usr/bin/env python3
"""
Test script to verify face recognition status file communication
"""

import json
import time
import os

def test_status_file():
    """Test the status file creation and reading"""
    status_file = "/tmp/magicmirror_face_status.json"
    
    print("🧪 Testing Face Recognition Status File Communication")
    print("=" * 60)
    
    # Test 1: Check if file exists
    print(f"1. Checking if status file exists: {status_file}")
    if os.path.exists(status_file):
        print("   ✅ Status file exists")
    else:
        print("   ❌ Status file does not exist")
        return False
    
    # Test 2: Read and parse the file
    print("2. Reading and parsing status file...")
    try:
        with open(status_file, 'r') as f:
            data = json.load(f)
        print("   ✅ Status file is valid JSON")
        print(f"   📄 Content: {data}")
    except Exception as e:
        print(f"   ❌ Error reading status file: {e}")
        return False
    
    # Test 3: Check required fields
    print("3. Checking required fields...")
    required_fields = ['distance', 'person', 'active', 'timestamp']
    for field in required_fields:
        if field in data:
            print(f"   ✅ {field}: {data[field]}")
        else:
            print(f"   ❌ Missing field: {field}")
            return False
    
    # Test 4: Simulate face recognition
    print("4. Simulating face recognition...")
    test_data = {
        "distance": 15.5,
        "person": "Andii",
        "active": True,
        "status": "recognized",
        "timestamp": time.time()
    }
    
    try:
        with open(status_file, 'w') as f:
            json.dump(test_data, f, indent=2)
        print("   ✅ Successfully wrote test data")
    except Exception as e:
        print(f"   ❌ Error writing test data: {e}")
        return False
    
    # Test 5: Verify the write
    print("5. Verifying the write...")
    try:
        with open(status_file, 'r') as f:
            read_data = json.load(f)
        if read_data['person'] == 'Andii':
            print("   ✅ Test data verified successfully")
        else:
            print("   ❌ Test data verification failed")
            return False
    except Exception as e:
        print(f"   ❌ Error verifying test data: {e}")
        return False
    
    print("\n🎉 All tests passed! Face recognition status file is working correctly.")
    print("   The personal modules should now be able to read face recognition data.")
    return True

if __name__ == "__main__":
    test_status_file()
