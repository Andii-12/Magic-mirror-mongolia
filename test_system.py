#!/usr/bin/env python3
"""
Simple system test for MagicMirror² Face Recognition
Tests GPIO, camera, and face recognition without full system
"""

import os
import time
import json

def test_gpio():
    """Test GPIO functionality"""
    print("🔧 Testing GPIO...")
    try:
        import RPi.GPIO as GPIO
        
        # Clean up any existing GPIO setup first
        try:
            GPIO.cleanup()
        except:
            pass
        
        # Set mode and test pins
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(23, GPIO.OUT)
        GPIO.setup(24, GPIO.IN)
        
        # Test basic functionality
        GPIO.output(23, GPIO.LOW)
        time.sleep(0.1)
        GPIO.output(23, GPIO.HIGH)
        time.sleep(0.1)
        GPIO.output(23, GPIO.LOW)
        
        # Clean up
        GPIO.cleanup()
        print("   ✅ GPIO test passed")
        return True
    except Exception as e:
        print(f"   ❌ GPIO test failed: {e}")
        # Try to clean up even if test failed
        try:
            import RPi.GPIO as GPIO
            GPIO.cleanup()
        except:
            pass
        return False

def test_camera():
    """Test camera functionality"""
    print("📷 Testing camera...")
    try:
        from picamera2 import Picamera2
        picam2 = Picamera2()
        config = picam2.create_preview_configuration(main={"size": (320, 240)})
        picam2.configure(config)
        picam2.start()
        time.sleep(1)
        frame = picam2.capture_array()
        picam2.close()
        print("   ✅ Camera test passed")
        return True
    except Exception as e:
        print(f"   ❌ Camera test failed: {e}")
        return False

def test_face_recognition():
    """Test face recognition files"""
    print("🧠 Testing face recognition...")
    
    # Check trainer.yml
    trainer_paths = ["trainer.yml", "python_code/trainer.yml"]
    trainer_found = False
    
    for path in trainer_paths:
        if os.path.exists(path):
            print(f"   ✅ Found trainer.yml at: {path}")
            trainer_found = True
            break
    
    if not trainer_found:
        print("   ❌ trainer.yml not found")
        return False
    
    # Check cascade file
    cascade_path = "/home/andii/haarcascades/haarcascade_frontalface_default.xml"
    if os.path.exists(cascade_path):
        print(f"   ✅ Found cascade file at: {cascade_path}")
    else:
        print(f"   ❌ Cascade file not found at: {cascade_path}")
        return False
    
    # Check Images directory
    if os.path.exists("Images"):
        images = os.listdir("Images")
        print(f"   ✅ Found Images directory with {len(images)} people")
    else:
        print("   ❌ Images directory not found")
        return False
    
    return True

def test_status_file():
    """Test status file creation"""
    print("📄 Testing status file...")
    try:
        status = {
            "distance": 999,
            "person": None,
            "active": False,
            "timestamp": time.time()
        }
        
        with open("/tmp/magicmirror_face_status.json", "w") as f:
            json.dump(status, f)
        
        print("   ✅ Status file test passed")
        return True
    except Exception as e:
        print(f"   ❌ Status file test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 MagicMirror² Face Recognition System Test")
    print("=============================================")
    
    tests = [
        ("GPIO", test_gpio),
        ("Camera", test_camera),
        ("Face Recognition", test_face_recognition),
        ("Status File", test_status_file)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{test_name} Test:")
        result = test_func()
        results.append((test_name, result))
    
    print("\n📊 Test Results:")
    print("================")
    
    all_passed = True
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
        if not result:
            all_passed = False
    
    print("\n" + "="*50)
    if all_passed:
        print("🎉 All tests passed! System is ready.")
        print("   You can now run: ./start_lightweight.sh")
    else:
        print("⚠️  Some tests failed. Please fix the issues above.")
        print("   Common fixes:")
        print("   - GPIO: Check connections and permissions")
        print("   - Camera: Enable in raspi-config")
        print("   - Face Recognition: Run python3 train_faces.py")
        print("   - Status File: Check /tmp directory permissions")

if __name__ == "__main__":
    main()
