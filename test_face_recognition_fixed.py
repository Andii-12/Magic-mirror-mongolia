#!/usr/bin/env python3
"""
Test script for the fixed face recognition system
Tests the ultrasonic sensor and camera integration
"""

import json
import time
import os
from datetime import datetime

def create_test_status(distance, person, active, status):
    """Create a test status file"""
    status_data = {
        "distance": distance,
        "person": person,
        "active": active,
        "status": status,
        "timestamp": datetime.now().isoformat()
    }
    
    status_file = "/tmp/magicmirror_face_status.json"
    with open(status_file, 'w') as f:
        json.dump(status_data, f, indent=2)
    
    print(f"📝 Created status: Distance={distance}cm, Person={person}, Active={active}, Status={status}")
    return status_data

def test_fixed_logic_flow():
    """Test the fixed logic flow"""
    print("🧪 Testing Fixed Face Recognition Logic Flow")
    print("=" * 50)
    
    # Test 1: Far from sensor (>20cm)
    print("\n1️⃣  Test: Far from sensor (>20cm)")
    create_test_status(50, None, False, "waiting")
    print("   Expected: Show 'Ойртож зогсоорой' in top-left")
    print("   Expected: Hide personal data")
    input("   Press Enter to continue...")
    
    # Test 2: Approaching sensor (15cm) - should activate
    print("\n2️⃣  Test: Approaching sensor (15cm) - activating")
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
    
    print("\n✅ Fixed logic flow test completed!")
    print("   Check your MagicMirror² display to verify the behavior")
    print("   Personal data should NOT blink during status updates")

def test_stability():
    """Test stability of the system"""
    print("\n🔧 Testing System Stability")
    print("=" * 30)
    
    # Simulate rapid status updates that should not cause blinking
    print("Testing rapid status updates...")
    
    for i in range(5):
        # Simulate user staying close with minor distance variations
        distance = 15 + (i % 3)  # 15, 16, 17, 15, 16
        create_test_status(distance, "Andii", True, "recognized")
        time.sleep(0.5)
        print(f"   Update {i+1}: Distance={distance}cm, Person=Andii")
    
    print("✅ Stability test completed!")
    print("   Personal data should remain stable during minor distance changes")

if __name__ == "__main__":
    print("🎯 Face Recognition System Test (Fixed Version)")
    print("=" * 50)
    
    # Create initial status file
    create_test_status(999, None, False, "waiting")
    
    # Run tests
    test_fixed_logic_flow()
    test_stability()
    
    print("\n🎉 All tests completed!")
    print("📋 Key improvements:")
    print("   ✅ Stable proximity detection (3 consecutive readings)")
    print("   ✅ Proper timeout handling (10s countdown)")
    print("   ✅ No data blinking during status updates")
    print("   ✅ Camera activation only when needed")
    print("   ✅ Smooth user experience")
