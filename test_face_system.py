#!/usr/bin/env python3
"""
Test script for face recognition system
This script simulates the face recognition system for testing
"""

import json
import time
import os
from datetime import datetime

# Test the face recognition system
def test_face_system():
    print("Testing Face Recognition System...")
    
    # Test status file creation
    status_file = "/tmp/magicmirror_face_status.json"
    
    # Test 1: No detection
    print("\n1. Testing no detection state...")
    status = {
        "distance": 999,
        "person": None,
        "active": False,
        "status": "waiting",
        "timestamp": datetime.now().isoformat()
    }
    with open(status_file, 'w') as f:
        json.dump(status, f, indent=2)
    print("Status: No detection - should show 'Please stand closer'")
    
    time.sleep(2)
    
    # Test 2: Object detected, scanning face
    print("\n2. Testing object detection...")
    status = {
        "distance": 15,
        "person": None,
        "active": True,
        "status": "detecting",
        "timestamp": datetime.now().isoformat()
    }
    with open(status_file, 'w') as f:
        json.dump(status, f, indent=2)
    print("Status: Object detected - should show 'Scanning face'")
    
    time.sleep(2)
    
    # Test 3: Face recognized
    print("\n3. Testing face recognition...")
    status = {
        "distance": 15,
        "person": "Andii",
        "active": True,
        "status": "recognized",
        "timestamp": datetime.now().isoformat()
    }
    with open(status_file, 'w') as f:
        json.dump(status, f, indent=2)
    print("Status: Face recognized - should show 'Hello, Andii' and personal data")
    
    time.sleep(2)
    
    # Test 4: User moved away, timeout started
    print("\n4. Testing user moved away...")
    status = {
        "distance": 50,
        "person": "Andii",
        "active": True,
        "status": "timeout",
        "timestamp": datetime.now().isoformat()
    }
    with open(status_file, 'w') as f:
        json.dump(status, f, indent=2)
    print("Status: User moved away - should show timeout countdown")
    
    time.sleep(2)
    
    # Test 5: Timeout completed, user logged out
    print("\n5. Testing timeout completed...")
    status = {
        "distance": 50,
        "person": None,
        "active": False,
        "status": "waiting",
        "timestamp": datetime.now().isoformat()
    }
    with open(status_file, 'w') as f:
        json.dump(status, f, indent=2)
    print("Status: Timeout completed - should hide personal data and show 'Please stand closer'")
    
    print("\nTest completed! Check your MagicMirror display for the status changes.")

if __name__ == "__main__":
    test_face_system()
