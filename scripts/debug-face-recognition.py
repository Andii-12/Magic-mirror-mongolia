#!/usr/bin/env python3

"""
Debug script for face recognition system
Helps diagnose issues with ultrasonic sensor and face recognition
"""

import os
import sys
import json
import time
from datetime import datetime

def check_system_requirements():
    """Check if all system requirements are met"""
    print("🔍 Checking System Requirements")
    print("==============================")
    
    issues = []
    
    # Check Python version
    if sys.version_info < (3, 6):
        issues.append("Python 3.6+ required")
    else:
        print(f"✅ Python {sys.version.split()[0]}")
    
    # Check required modules
    required_modules = ['cv2', 'numpy', 'RPi.GPIO', 'picamera2']
    for module in required_modules:
        try:
            __import__(module)
            print(f"✅ {module} available")
        except ImportError:
            issues.append(f"Missing module: {module}")
            print(f"❌ {module} missing")
    
    # Check GPIO access
    try:
        import RPi.GPIO as GPIO
        GPIO.setmode(GPIO.BCM)
        GPIO.cleanup()
        print("✅ GPIO access available")
    except Exception as e:
        issues.append(f"GPIO access issue: {e}")
        print(f"❌ GPIO access failed: {e}")
    
    # Check camera access
    try:
        from picamera2 import Picamera2
        picam2 = Picamera2()
        picam2.close()
        print("✅ Camera access available")
    except Exception as e:
        issues.append(f"Camera access issue: {e}")
        print(f"❌ Camera access failed: {e}")
    
    # Check file permissions
    status_file = "/tmp/magicmirror_face_status.json"
    try:
        with open(status_file, 'w') as f:
            json.dump({"test": True}, f)
        os.remove(status_file)
        print("✅ Status file writable")
    except Exception as e:
        issues.append(f"Status file write issue: {e}")
        print(f"❌ Status file write failed: {e}")
    
    print("")
    if issues:
        print("❌ Issues found:")
        for issue in issues:
            print(f"   - {issue}")
        return False
    else:
        print("✅ All system requirements met")
        return True

def test_ultrasonic_sensor():
    """Test ultrasonic sensor functionality"""
    print("🔧 Testing Ultrasonic Sensor")
    print("============================")
    
    try:
        import RPi.GPIO as GPIO
        
        TRIG_PIN = 5
        ECHO_PIN = 6
        
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(TRIG_PIN, GPIO.OUT)
        GPIO.setup(ECHO_PIN, GPIO.IN)
        
        print(f"Testing GPIO pins: TRIG={TRIG_PIN}, ECHO={ECHO_PIN}")
        
        # Take 5 readings
        readings = []
        for i in range(5):
            try:
                GPIO.output(TRIG_PIN, False)
                time.sleep(0.01)
                
                GPIO.output(TRIG_PIN, True)
                time.sleep(0.00001)
                GPIO.output(TRIG_PIN, False)
                
                # Wait for echo start
                timeout_start = time.time()
                while GPIO.input(ECHO_PIN) == 0:
                    if time.time() - timeout_start > 0.1:
                        break
                    pulse_start = time.time()
                
                # Wait for echo end
                timeout_start = time.time()
                while GPIO.input(ECHO_PIN) == 1:
                    if time.time() - timeout_start > 0.1:
                        break
                    pulse_end = time.time()
                
                pulse_duration = pulse_end - pulse_start
                distance = (pulse_duration * 34300) / 2
                
                if 2 <= distance <= 400:
                    readings.append(distance)
                    print(f"  Reading {i+1}: {distance:.2f}cm")
                else:
                    print(f"  Reading {i+1}: Invalid ({distance:.2f}cm)")
                
                time.sleep(0.1)
                
            except Exception as e:
                print(f"  Reading {i+1}: Error - {e}")
        
        GPIO.cleanup()
        
        if readings:
            avg_distance = sum(readings) / len(readings)
            print(f"Average distance: {avg_distance:.2f}cm")
            print("✅ Ultrasonic sensor working")
            return True
        else:
            print("❌ No valid readings from ultrasonic sensor")
            return False
            
    except Exception as e:
        print(f"❌ Ultrasonic sensor test failed: {e}")
        return False

def test_face_recognition():
    """Test face recognition functionality"""
    print("📷 Testing Face Recognition")
    print("===========================")
    
    try:
        import cv2
        from picamera2 import Picamera2
        
        # Test camera
        picam2 = Picamera2()
        config = picam2.create_preview_configuration(main={"size": (320, 240)})
        picam2.configure(config)
        picam2.start()
        time.sleep(1)
        
        frame = picam2.capture_array()
        print(f"✅ Camera working - captured {frame.shape} image")
        
        # Test face detection
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)
        
        print(f"✅ Face detection working - found {len(faces)} faces")
        
        picam2.close()
        return True
        
    except Exception as e:
        print(f"❌ Face recognition test failed: {e}")
        return False

def test_status_file():
    """Test status file communication"""
    print("📄 Testing Status File Communication")
    print("====================================")
    
    status_file = "/tmp/magicmirror_face_status.json"
    
    try:
        # Test writing
        test_status = {
            "distance": 15.5,
            "person": "TestUser",
            "active": True,
            "status": "recognized",
            "timestamp": datetime.now().isoformat()
        }
        
        with open(status_file, 'w') as f:
            json.dump(test_status, f, indent=2)
        print("✅ Status file write successful")
        
        # Test reading
        with open(status_file, 'r') as f:
            read_status = json.load(f)
        
        if read_status == test_status:
            print("✅ Status file read successful")
            print("✅ Status file communication working")
            return True
        else:
            print("❌ Status file read mismatch")
            return False
            
    except Exception as e:
        print(f"❌ Status file test failed: {e}")
        return False

def run_full_diagnostic():
    """Run complete diagnostic"""
    print("🚀 Face Recognition System Diagnostic")
    print("=====================================")
    print("")
    
    results = {
        "system_requirements": check_system_requirements(),
        "ultrasonic_sensor": test_ultrasonic_sensor(),
        "face_recognition": test_face_recognition(),
        "status_file": test_status_file()
    }
    
    print("")
    print("📊 Diagnostic Summary")
    print("====================")
    
    all_passed = True
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{test_name.replace('_', ' ').title()}: {status}")
        if not passed:
            all_passed = False
    
    print("")
    if all_passed:
        print("🎉 All tests passed! Face recognition system should work correctly.")
        print("")
        print("💡 Usage:")
        print("   - Normal mode: ./start.sh")
        print("   - Test mode: ./start.sh test")
        print("   - Ultrasonic test only: npm run test-ultrasonic")
    else:
        print("⚠️  Some tests failed. Please fix the issues above before running the system.")
        print("")
        print("🔧 Common fixes:")
        print("   - Install missing modules: pip3 install opencv-python numpy RPi.GPIO picamera2")
        print("   - Check wiring connections for ultrasonic sensor")
        print("   - Run with sudo if GPIO access is denied")
        print("   - Check camera permissions")
    
    return all_passed

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "quick":
        # Quick test mode
        print("⚡ Quick Diagnostic Mode")
        print("=======================")
        check_system_requirements()
    else:
        # Full diagnostic
        success = run_full_diagnostic()
        sys.exit(0 if success else 1)
