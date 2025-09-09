#!/usr/bin/env python3
"""
Test script to verify the face recognition logic works correctly
This simulates the behavior without requiring actual hardware
"""

import json
import time
import os

# Simulate the face recognition system behavior
class TestFaceRecognition:
    def __init__(self):
        self.current_person = None
        self.current_distance = 999
        self.is_active = False
        self.proximity_threshold = 20
        self.status_file = "/tmp/magicmirror_face_status_test.json"
        
    def simulate_distance(self, distance):
        """Simulate ultrasonic sensor reading"""
        self.current_distance = distance
        print(f"📏 Distance: {distance}cm")
        
    def simulate_face_recognition(self, person):
        """Simulate face recognition result"""
        if person and person != "Unknown":
            print(f"👤 Face recognized: {person}")
            self.current_person = person
        else:
            print("🔍 Face not recognized")
            # Don't reset current_person to None if already recognized
            
    def update_status_file(self):
        """Update status file (same logic as the real system)"""
        if not self.is_active:
            status_type = "waiting"
        elif self.current_person and self.current_person != "Unknown":
            status_type = "recognized"
        elif self.is_active and self.current_person is None:
            status_type = "detecting"
        else:
            status_type = "waiting"
            
        status = {
            "distance": self.current_distance,
            "person": self.current_person,
            "active": self.is_active,
            "status": status_type,
            "timestamp": time.time()
        }
        
        with open(self.status_file, 'w') as f:
            json.dump(status, f, indent=2)
            
        print(f"📄 Status: {status_type} | Person: {self.current_person} | Active: {self.is_active}")
        
    def run_test_scenario(self):
        """Run the test scenario"""
        print("🧪 Testing Face Recognition Logic")
        print("=" * 50)
        
        # Test scenario steps
        steps = [
            ("1. No proximity", 50, None),
            ("2. Object detected", 15, None),
            ("3. Face not recognized", 15, None),
            ("4. Face recognized", 15, "Andii"),
            ("5. Face moves away (still < 20cm)", 18, None),  # This should maintain recognition
            ("6. Face moves back (still < 20cm)", 16, "Andii"),  # This should maintain recognition
            ("7. Object moves away", 25, None),
        ]
        
        for step_name, distance, person in steps:
            print(f"\n{step_name}")
            print("-" * 30)
            
            # Simulate distance reading
            self.simulate_distance(distance)
            
            # Check proximity
            if distance <= self.proximity_threshold:
                if not self.is_active:
                    print("🚀 Starting face recognition")
                    self.is_active = True
                    self.current_person = None
                    
                # Only try recognition if no person is currently recognized
                if self.current_person is None:
                    self.simulate_face_recognition(person)
                else:
                    print(f"✅ Maintaining recognized state for {self.current_person}")
            else:
                if self.is_active:
                    print("⏰ Object moved away - resetting")
                    self.is_active = False
                    self.current_person = None
                    
            # Update status
            self.update_status_file()
            time.sleep(1)
            
        print("\n" + "=" * 50)
        print("✅ Test completed!")
        print(f"📄 Check status file: {self.status_file}")

if __name__ == "__main__":
    test = TestFaceRecognition()
    test.run_test_scenario()
