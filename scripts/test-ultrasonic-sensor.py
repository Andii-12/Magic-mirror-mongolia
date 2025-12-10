#!/usr/bin/env python3

"""
Test script for ultrasonic sensor
Tests the HC-SR04 ultrasonic sensor independently
"""

import RPi.GPIO as GPIO
import time
import sys

# GPIO pins for ultrasonic sensor
TRIG_PIN = 5   # GPIO pin for TRIG
ECHO_PIN = 6   # GPIO pin for ECHO

def test_ultrasonic_sensor():
    """Test ultrasonic sensor with detailed diagnostics"""
    print("🔧 Testing Ultrasonic Sensor (HC-SR04)")
    print("=====================================")
    print(f"TRIG Pin: GPIO {TRIG_PIN}")
    print(f"ECHO Pin: GPIO {ECHO_PIN}")
    print("")
    
    try:
        # Initialize GPIO
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(TRIG_PIN, GPIO.OUT)
        GPIO.setup(ECHO_PIN, GPIO.IN)
        
        print("✅ GPIO initialized successfully")
        print("")
        
        # Test multiple readings
        readings = []
        print("📏 Taking 10 distance readings...")
        
        for i in range(10):
            try:
                # Ensure trigger is low initially
                GPIO.output(TRIG_PIN, False)
                time.sleep(0.01)

                # Send trigger pulse
                GPIO.output(TRIG_PIN, True)
                time.sleep(0.00001)  # 10 microseconds
                GPIO.output(TRIG_PIN, False)

                # Wait for echo to start (with timeout)
                timeout_start = time.time()
                while GPIO.input(ECHO_PIN) == 0:
                    if time.time() - timeout_start > 0.1:  # 100ms timeout
                        print(f"  Reading {i+1}: Echo start timeout")
                        readings.append(999)
                        continue
                    pulse_start = time.time()

                # Wait for echo to end (with timeout)
                timeout_start = time.time()
                while GPIO.input(ECHO_PIN) == 1:
                    if time.time() - timeout_start > 0.1:  # 100ms timeout
                        print(f"  Reading {i+1}: Echo end timeout")
                        readings.append(999)
                        continue
                    pulse_end = time.time()

                # Calculate distance
                pulse_duration = pulse_end - pulse_start
                
                # Validate pulse duration
                if pulse_duration < 0.0001 or pulse_duration > 0.1:
                    print(f"  Reading {i+1}: Invalid pulse duration: {pulse_duration}")
                    readings.append(999)
                    continue
                
                # Convert to distance
                distance = (pulse_duration * 34300) / 2
                distance = round(distance, 2)
                
                # Validate distance range
                if distance < 2 or distance > 400:
                    print(f"  Reading {i+1}: Distance out of range: {distance}cm")
                    readings.append(999)
                else:
                    print(f"  Reading {i+1}: {distance}cm")
                    readings.append(distance)
                
                time.sleep(0.1)  # Small delay between readings
                
            except Exception as e:
                print(f"  Reading {i+1}: Error - {e}")
                readings.append(999)
        
        # Analyze results
        print("")
        print("📊 Analysis:")
        print("============")
        
        valid_readings = [r for r in readings if r != 999]
        
        if valid_readings:
            avg_distance = sum(valid_readings) / len(valid_readings)
            min_distance = min(valid_readings)
            max_distance = max(valid_readings)
            
            print(f"Valid readings: {len(valid_readings)}/10")
            print(f"Average distance: {avg_distance:.2f}cm")
            print(f"Min distance: {min_distance:.2f}cm")
            print(f"Max distance: {max_distance:.2f}cm")
            
            # Check for stability
            if max_distance - min_distance < 10:
                print("✅ Sensor readings are stable")
            else:
                print("⚠️  Sensor readings are unstable (variance > 10cm)")
            
            # Check if sensor is working in expected range
            if 5 <= avg_distance <= 200:
                print("✅ Sensor appears to be working correctly")
            else:
                print("⚠️  Sensor readings seem unusual")
        else:
            print("❌ No valid readings obtained")
            print("🔧 Troubleshooting:")
            print("   - Check wiring connections")
            print("   - Verify GPIO pins are correct")
            print("   - Check if sensor is powered")
            print("   - Try different GPIO pins")
        
        print("")
        print("🎯 Proximity Test:")
        print("=================")
        print("Move your hand in front of the sensor and watch the readings change.")
        print("Press Ctrl+C to stop the proximity test.")
        
        # Continuous monitoring
        try:
            while True:
                distance = get_single_reading()
                if distance != 999:
                    status = "CLOSE" if distance <= 20 else "FAR"
                    print(f"\rDistance: {distance:6.2f}cm ({status})", end="", flush=True)
                else:
                    print(f"\rDistance: ERROR", end="", flush=True)
                time.sleep(0.1)
        except KeyboardInterrupt:
            print("\n\n✅ Proximity test completed")
        
    except Exception as e:
        print(f"❌ Error initializing GPIO: {e}")
        print("🔧 Make sure you're running as root or with sudo")
        return False
    finally:
        GPIO.cleanup()
        print("🧹 GPIO cleanup completed")
    
    return len(valid_readings) > 0

def get_single_reading():
    """Get a single distance reading"""
    try:
        # Ensure trigger is low initially
        GPIO.output(TRIG_PIN, False)
        time.sleep(0.01)

        # Send trigger pulse
        GPIO.output(TRIG_PIN, True)
        time.sleep(0.00001)
        GPIO.output(TRIG_PIN, False)

        # Wait for echo to start
        timeout_start = time.time()
        while GPIO.input(ECHO_PIN) == 0:
            if time.time() - timeout_start > 0.1:
                return 999
            pulse_start = time.time()

        # Wait for echo to end
        timeout_start = time.time()
        while GPIO.input(ECHO_PIN) == 1:
            if time.time() - timeout_start > 0.1:
                return 999
            pulse_end = time.time()

        # Calculate distance
        pulse_duration = pulse_end - pulse_start
        distance = (pulse_duration * 34300) / 2
        
        if 2 <= distance <= 400:
            return round(distance, 2)
        else:
            return 999
            
    except Exception:
        return 999

if __name__ == "__main__":
    print("🚀 Starting ultrasonic sensor test...")
    print("")
    
    if test_ultrasonic_sensor():
        print("✅ Ultrasonic sensor test completed successfully!")
        sys.exit(0)
    else:
        print("❌ Ultrasonic sensor test failed!")
        sys.exit(1)
