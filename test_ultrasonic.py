#!/usr/bin/env python3
"""
Simple Ultrasonic Sensor Test with Relay Control
Tests HC-SR04 ultrasonic sensor and relay (lights) together
"""

import time
import platform

# Check platform
IS_WINDOWS = platform.system() == "Windows"

# GPIO pins (same as face_recognition_system.py)
TRIG_PIN = 23  # GPIO pin for TRIG
ECHO_PIN = 24  # GPIO pin for ECHO
RELAY_PIN = 18  # GPIO pin for relay control

# Proximity threshold (same as main system)
PROXIMITY_THRESHOLD = 20  # cm

# Initialize GPIO
relay_available = False
gpio_available = False

if not IS_WINDOWS:
    try:
        import RPi.GPIO as GPIO
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(TRIG_PIN, GPIO.OUT)
        GPIO.setup(ECHO_PIN, GPIO.IN)
        GPIO.setup(RELAY_PIN, GPIO.OUT)
        GPIO.output(RELAY_PIN, GPIO.HIGH)  # Initialize relay to OFF
        gpio_available = True
        relay_available = True
        print("✅ GPIO initialized successfully")
    except Exception as e:
        print(f"⚠️  GPIO initialization error: {e}")
        print("   Continuing without GPIO...")
        gpio_available = False
        relay_available = False
else:
    print("⚠️  Running on Windows - GPIO features disabled")
    gpio_available = False
    relay_available = False

def get_distance():
    """Get distance from ultrasonic sensor in cm"""
    if not gpio_available:
        return 999
    
    try:
        # Ensure trigger is low initially
        GPIO.output(TRIG_PIN, False)
        time.sleep(0.001)
        
        # Send trigger pulse
        GPIO.output(TRIG_PIN, True)
        time.sleep(0.00001)  # 10 microseconds
        GPIO.output(TRIG_PIN, False)
        
        # Wait for echo start
        start_time = time.time()
        timeout = start_time + 0.05
        while GPIO.input(ECHO_PIN) == 0:
            if time.time() > timeout:
                return 999
            start_time = time.time()
        
        # Wait for echo end
        stop_time = time.time()
        timeout = stop_time + 0.05
        while GPIO.input(ECHO_PIN) == 1:
            if time.time() > timeout:
                return 999
            stop_time = time.time()
        
        # Calculate distance
        elapsed = stop_time - start_time
        distance = (elapsed * 34300) / 2
        
        # Validate distance range
        if 2 <= distance <= 400:
            return round(distance, 2)
        return 999
        
    except Exception as e:
        print(f"Error reading distance: {e}")
        return 999

def turn_on_lights():
    """Turn on the relay-controlled lights"""
    if not relay_available:
        return False
    try:
        GPIO.output(RELAY_PIN, GPIO.LOW)  # LOW = relay ON
        return True
    except Exception as e:
        print(f"Error turning on lights: {e}")
        return False

def turn_off_lights():
    """Turn off the relay-controlled lights"""
    if not relay_available:
        return False
    try:
        GPIO.output(RELAY_PIN, GPIO.HIGH)  # HIGH = relay OFF
        return True
    except Exception as e:
        print(f"Error turning off lights: {e}")
        return False

def test_ultrasonic_sensor():
    """Test ultrasonic sensor with multiple readings"""
    print("\n" + "="*60)
    print("🔧 ULTRASONIC SENSOR TEST")
    print("="*60)
    print(f"TRIG Pin: GPIO {TRIG_PIN}")
    print(f"ECHO Pin: GPIO {ECHO_PIN}")
    print(f"Proximity Threshold: {PROXIMITY_THRESHOLD}cm")
    print("")
    
    if not gpio_available:
        print("❌ GPIO not available - cannot test sensor")
        return False
    
    print("📏 Taking 10 test readings...")
    print("-" * 60)
    
    readings = []
    for i in range(10):
        distance = get_distance()
        readings.append(distance)
        if distance != 999:
            status = "✅ CLOSE" if distance <= PROXIMITY_THRESHOLD else "   FAR"
            print(f"  Reading {i+1:2d}: {distance:6.2f}cm {status}")
        else:
            print(f"  Reading {i+1:2d}: ERROR (no valid reading)")
        time.sleep(0.2)
    
    # Analyze results
    print("-" * 60)
    valid_readings = [r for r in readings if r != 999]
    
    if valid_readings:
        avg = sum(valid_readings) / len(valid_readings)
        min_dist = min(valid_readings)
        max_dist = max(valid_readings)
        
        print(f"📊 Results:")
        print(f"   Valid readings: {len(valid_readings)}/10")
        print(f"   Average: {avg:.2f}cm")
        print(f"   Min: {min_dist:.2f}cm")
        print(f"   Max: {max_dist:.2f}cm")
        
        if max_dist - min_dist < 10:
            print("   ✅ Sensor is stable")
        else:
            print("   ⚠️  Sensor readings vary significantly")
        
        return True
    else:
        print("❌ No valid readings obtained!")
        print("")
        print("🔧 Troubleshooting:")
        print("   1. Check wiring: TRIG->GPIO23, ECHO->GPIO24")
        print("   2. Verify sensor is powered (5V and GND)")
        print("   3. Check if sensor is connected properly")
        print("   4. Try running with: sudo python3 test_ultrasonic.py")
        return False

def test_relay_control():
    """Test relay (lights) control"""
    print("\n" + "="*60)
    print("💡 RELAY (LIGHTS) TEST")
    print("="*60)
    print(f"RELAY Pin: GPIO {RELAY_PIN}")
    print("")
    
    if not relay_available:
        print("❌ Relay control not available")
        return False
    
    print("Testing relay control...")
    print("")
    
    try:
        # Test turning on
        print("  💡 Turning ON lights...")
        if turn_on_lights():
            print("     ✅ Lights should be ON now")
        else:
            print("     ❌ Failed to turn on lights")
            return False
        
        time.sleep(2)
        
        # Test turning off
        print("  🌙 Turning OFF lights...")
        if turn_off_lights():
            print("     ✅ Lights should be OFF now")
        else:
            print("     ❌ Failed to turn off lights")
            return False
        
        time.sleep(1)
        
        print("")
        print("✅ Relay control test completed")
        return True
        
    except Exception as e:
        print(f"❌ Error testing relay: {e}")
        return False

def test_proximity_with_lights():
    """Test proximity detection with automatic light control"""
    print("\n" + "="*60)
    print("🎯 PROXIMITY + LIGHTS INTEGRATION TEST")
    print("="*60)
    print("This test simulates the face recognition system behavior:")
    print(f"  - Lights turn ON when distance < {PROXIMITY_THRESHOLD}cm")
    print(f"  - Lights turn OFF when distance > {PROXIMITY_THRESHOLD + 10}cm")
    print("")
    print("Move your hand in front of the sensor to test.")
    print("Press Ctrl+C to stop.")
    print("")
    
    if not gpio_available or not relay_available:
        print("❌ GPIO or relay not available - cannot run integration test")
        return False
    
    lights_on = False
    stable_count = 0
    STABLE_THRESHOLD = 3  # Require 3 stable readings
    
    try:
        print("Starting continuous monitoring...")
        print("-" * 60)
        
        while True:
            distance = get_distance()
            
            if distance != 999:
                # Determine status
                if distance <= PROXIMITY_THRESHOLD:
                    stable_count += 1
                    if stable_count >= STABLE_THRESHOLD and not lights_on:
                        turn_on_lights()
                        lights_on = True
                        print(f"\n💡 Lights ON  - Distance: {distance:.1f}cm (CLOSE)")
                    elif lights_on:
                        print(f"\rDistance: {distance:6.2f}cm (CLOSE) - Lights: ON ", end="", flush=True)
                    else:
                        print(f"\rDistance: {distance:6.2f}cm (CLOSE) - Approaching...", end="", flush=True)
                else:
                    stable_count = 0
                    if lights_on and distance > PROXIMITY_THRESHOLD + 10:
                        turn_off_lights()
                        lights_on = False
                        print(f"\n🌙 Lights OFF - Distance: {distance:.1f}cm (FAR)")
                    else:
                        status = "ON " if lights_on else "OFF"
                        print(f"\rDistance: {distance:6.2f}cm (FAR)  - Lights: {status}", end="", flush=True)
            else:
                print(f"\rDistance: ERROR", end="", flush=True)
            
            time.sleep(0.2)
            
    except KeyboardInterrupt:
        print("\n\n✅ Integration test stopped")
        if lights_on:
            turn_off_lights()
            print("🌙 Lights turned OFF")
        return True

def main():
    """Main test function"""
    print("\n" + "="*60)
    print("🚀 ULTRASONIC SENSOR & RELAY TEST SUITE")
    print("="*60)
    print("")
    
    # Test 1: Ultrasonic sensor
    sensor_ok = test_ultrasonic_sensor()
    
    # Test 2: Relay control
    relay_ok = test_relay_control()
    
    # Test 3: Integration test (if both work)
    if sensor_ok and relay_ok:
        print("\n" + "="*60)
        print("Would you like to run the integration test?")
        print("(This will continuously monitor distance and control lights)")
        response = input("Enter 'y' to continue, or any other key to exit: ").strip().lower()
        
        if response == 'y':
            test_proximity_with_lights()
    
    # Summary
    print("\n" + "="*60)
    print("📋 TEST SUMMARY")
    print("="*60)
    print(f"Ultrasonic Sensor: {'✅ PASS' if sensor_ok else '❌ FAIL'}")
    print(f"Relay Control:     {'✅ PASS' if relay_ok else '❌ FAIL'}")
    print("")
    
    # Cleanup
    if gpio_available:
        try:
            turn_off_lights()
            GPIO.cleanup()
            print("🧹 GPIO cleanup completed")
        except:
            pass
    
    if sensor_ok and relay_ok:
        print("✅ All tests passed! System is ready.")
        return 0
    else:
        print("❌ Some tests failed. Please check your wiring.")
        return 1

if __name__ == "__main__":
    try:
        exit_code = main()
        exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n🛑 Test interrupted by user")
        if gpio_available:
            try:
                turn_off_lights()
                GPIO.cleanup()
            except:
                pass
        exit(0)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        if gpio_available:
            try:
                turn_off_lights()
                GPIO.cleanup()
            except:
                pass
        exit(1)

