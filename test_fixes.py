#!/usr/bin/env python3
"""
Test script to verify the fixes for events and status display
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

def test_fixes():
    """Test the fixes"""
    print("🧪 Testing Fixes for Events and Status Display")
    print("=" * 50)
    
    # Test 1: Start - Far from sensor
    print("\n1️⃣  START: Far from sensor")
    create_test_status(50, None, False, "waiting")
    print("   Expected: Show 'Please stand closer' in top-left")
    print("   Expected: Hide personal data (tasks AND events)")
    input("   Press Enter to continue...")
    
    # Test 2: Move close to sensor
    print("\n2️⃣  APPROACH: Move close to sensor (<20cm)")
    create_test_status(15, None, True, "detecting")
    print("   Expected: Show 'Scanning face' in top-left")
    print("   Expected: Hide personal data during scanning")
    input("   Press Enter to continue...")
    
    # Test 3: Face recognized
    print("\n3️⃣  RECOGNIZED: Face recognized as 'Andii'")
    create_test_status(12, "Andii", True, "recognized")
    print("   Expected: Show 'Hello, Andii' greeting")
    print("   Expected: Show personal data from API:")
    print("     - Tasks: Today's tasks (max 5)")
    print("     - Events: Upcoming events")
    print("   Expected: Both tasks AND events should be visible")
    input("   Press Enter to continue...")
    
    # Test 4: Stay close - maintain recognition
    print("\n4️⃣  MAINTAIN: Stay close to sensor")
    create_test_status(10, "Andii", True, "recognized")
    print("   Expected: Keep showing 'Hello, Andii'")
    print("   Expected: Keep showing personal data")
    print("   Expected: Both tasks AND events visible")
    input("   Press Enter to continue...")
    
    # Test 5: Move away - immediate logout
    print("\n5️⃣  LOGOUT: Move away from sensor")
    create_test_status(45, None, False, "waiting")
    print("   Expected: Show 'Please stand closer' in top-left")
    print("   Expected: Hide ALL personal data immediately:")
    print("     - Tasks: Hidden")
    print("     - Events: Hidden")
    print("   Expected: Reset all states")
    input("   Press Enter to continue...")
    
    print("\n✅ Fixes test completed!")
    print("\n🔑 Key fixes applied:")
    print("   - Fixed data structure: 'todo' → 'lists'")
    print("   - Added inline CSS positioning for status messages")
    print("   - Ensured both tasks AND events hide when user moves away")
    print("   - Fixed personalcalendar module to use API data only")
    print("   - Added proper data broadcasting between modules")

if __name__ == "__main__":
    test_fixes()
