#!/usr/bin/env python3
"""
Test script to verify the face recognition logic flow
"""

import json
import time
import os

def create_test_status(distance, person, active, status):
    """Create a test status file"""
    status_data = {
        "distance": distance,
        "person": person,
        "active": active,
        "status": status,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S")
    }
    
    status_file = "/tmp/magicmirror_face_status.json"
    with open(status_file, 'w') as f:
        json.dump(status_data, f, indent=2)
    
    print(f"📝 Created status: Distance={distance}cm, Person={person}, Active={active}, Status={status}")
    return status_data

def test_logic_flow():
    """Test the complete logic flow"""
    print("🧪 Testing Face Recognition Logic Flow")
    print("=" * 50)
    
    # Test 1: Far from sensor (>20cm)
    print("\n1️⃣  Test: Far from sensor (>20cm)")
    create_test_status(50, None, False, "waiting")
    print("   Expected: Show 'Ойртож зогсоорой' in top-left")
    print("   Expected: Hide personal data")
    input("   Press Enter to continue...")
    
    # Test 2: Close to sensor (<20cm) but no face recognized yet
    print("\n2️⃣  Test: Close to sensor (<20cm) - detecting")
    create_test_status(15, None, True, "detecting")
    print("   Expected: Show 'Царай уншиж байна...' in top-left")
    print("   Expected: Hide personal data")
    input("   Press Enter to continue...")
    
    # Test 3: Face recognized
    print("\n3️⃣  Test: Face recognized")
    create_test_status(12, "Andii", True, "recognized")
    print("   Expected: Show personalized greeting")
    print("   Expected: Show personal data for Andii")
    input("   Press Enter to continue...")
    
    # Test 4: Move away but still within timeout
    print("\n4️⃣  Test: Move away (timeout countdown)")
    create_test_status(35, "Andii", True, "recognized")
    print("   Expected: Still show personal data (10s countdown)")
    print("   Expected: Show greeting")
    input("   Press Enter to continue...")
    
    # Test 5: Timeout reached - logout
    print("\n5️⃣  Test: Timeout reached - logout")
    create_test_status(45, None, False, "waiting")
    print("   Expected: Show 'Ойртож зогсоорой' in top-left")
    print("   Expected: Hide personal data")
    input("   Press Enter to continue...")
    
    print("\n✅ Logic flow test completed!")
    print("   Check your MagicMirror² display to verify the behavior")

if __name__ == "__main__":
    test_logic_flow()
