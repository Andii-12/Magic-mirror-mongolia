#!/usr/bin/env python3
"""
Test script to verify the new face recognition logic flow
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
    
    print(f"📝 Status: Distance={distance}cm, Person={person}, Active={active}, Status={status}")
    return status_data

def test_new_logic_flow():
    """Test the new logic flow"""
    print("🧪 Testing NEW Face Recognition Logic Flow")
    print("=" * 50)
    
    # Test 1: Start - Far from sensor
    print("\n1️⃣  START: Far from sensor")
    create_test_status(50, None, False, "waiting")
    print("   Expected: Show 'Please stand closer' in top-left")
    print("   Expected: Hide personal data")
    input("   Press Enter to continue...")
    
    # Test 2: Move close to sensor
    print("\n2️⃣  APPROACH: Move close to sensor (<20cm)")
    create_test_status(15, None, True, "detecting")
    print("   Expected: Show 'Scanning face' in top-left")
    print("   Expected: Camera opens ONCE for recognition")
    print("   Expected: Hide personal data during scanning")
    input("   Press Enter to continue...")
    
    # Test 3: Face recognized
    print("\n3️⃣  RECOGNIZED: Face recognized as 'Andii'")
    create_test_status(12, "Andii", True, "recognized")
    print("   Expected: Show 'Hello, Andii' greeting")
    print("   Expected: Show personal data from API")
    print("   Expected: Camera closed")
    input("   Press Enter to continue...")
    
    # Test 4: Stay close - maintain recognition
    print("\n4️⃣  MAINTAIN: Stay close to sensor")
    create_test_status(10, "Andii", True, "recognized")
    print("   Expected: Keep showing 'Hello, Andii'")
    print("   Expected: Keep showing personal data")
    print("   Expected: No camera activity")
    input("   Press Enter to continue...")
    
    # Test 5: Move away - immediate logout
    print("\n5️⃣  LOGOUT: Move away from sensor")
    create_test_status(45, None, False, "waiting")
    print("   Expected: Show 'Please stand closer' in top-left")
    print("   Expected: Hide personal data immediately")
    print("   Expected: Reset all states")
    input("   Press Enter to continue...")
    
    print("\n✅ New logic flow test completed!")
    print("\n🔑 Key differences from old logic:")
    print("   - Camera opens ONLY ONCE when first detected")
    print("   - No continuous camera looping")
    print("   - Immediate logout when moving away (no 10s timeout)")
    print("   - Personal data fetched from API when user recognized")
    print("   - No user_profiles.json dependency")

if __name__ == "__main__":
    test_new_logic_flow()
