#!/usr/bin/env python3
"""
Simple Ultrasonic Sensor Test
Tests HC-SR04 ultrasonic sensor with continuous distance measurements
"""

import time
import platform

# Check platform
IS_WINDOWS = platform.system() == "Windows"

# GPIO pins (same as face_recognition_system.py)
TRIG_PIN = 23  # GPIO pin for TRIG
ECHO_PIN = 24  # GPIO pin for ECHO

# Initialize GPIO
gpio_available = False

if not IS_WINDOWS:
    try:
        import RPi.GPIO as GPIO
        GPIO.setmode(GPIO.BCM)
        # TRIG as output, ECHO as input with a pull-down to avoid floating
        GPIO.setup(TRIG_PIN, GPIO.OUT)
        GPIO.setup(ECHO_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.output(TRIG_PIN, False)
        gpio_available = True
        print("✅ GPIO initialized successfully")
        time.sleep(0.05)  # let sensor settle
    except Exception as e:
        print(f"⚠️  GPIO initialization error: {e}")
        print("   Make sure you're running with sudo or have GPIO permissions")
        gpio_available = False
else:
    print("⚠️  Running on Windows - GPIO features disabled")
    gpio_available = False

def _single_pulse_distance():
    """Take one HC-SR04 reading. Returns distance in cm or None on failure."""
    # Ensure trigger is low
    GPIO.output(TRIG_PIN, False)
    time.sleep(0.001)

    # 10µs trigger pulse
    GPIO.output(TRIG_PIN, True)
    time.sleep(0.00001)
    GPIO.output(TRIG_PIN, False)

    # Wait for echo to go high (start)
    start = None
    timeout = time.perf_counter() + 0.04  # 40ms guard
    while GPIO.input(ECHO_PIN) == 0:
        if time.perf_counter() > timeout:
            return None
    start = time.perf_counter()

    # Wait for echo to go low (end)
    timeout = time.perf_counter() + 0.04
    while GPIO.input(ECHO_PIN) == 1:
        if time.perf_counter() > timeout:
            return None
    end = time.perf_counter()

    elapsed = end - start
    distance = (elapsed * 34300) / 2
    if 2 <= distance <= 400:
        return round(distance, 2)
    return None


def get_distance(samples=3):
    """Get a smoothed distance reading (median of N samples)."""
    if not gpio_available:
        return 999

    readings = []
    for _ in range(samples):
        d = _single_pulse_distance()
        if d is not None:
            readings.append(d)
        time.sleep(0.01)

    if not readings:
        return 999

    readings.sort()
    mid = len(readings) // 2
    if len(readings) % 2 == 1:
        return readings[mid]
    return round((readings[mid - 1] + readings[mid]) / 2, 2)

def test_ultrasonic_sensor():
    """Test ultrasonic sensor with continuous loop measurements"""
    print("\n" + "="*60)
    print("🔧 ULTRASONIC SENSOR TEST")
    print("="*60)
    print(f"TRIG Pin: GPIO {TRIG_PIN}")
    print(f"ECHO Pin: GPIO {ECHO_PIN}")
    print("")
    
    if not gpio_available:
        print("❌ GPIO not available - cannot test sensor")
        print("   Make sure you're running with: sudo python3 test_ultrasonic.py")
        return False
    
    print("📏 Starting continuous distance measurements...")
    print("   Press Ctrl+C to stop")
    print("-" * 60)
    print("")
    
    try:
        reading_count = 0
        while True:
            distance = get_distance(samples=5)
            reading_count += 1
            
            if distance != 999:
                print(f"Reading #{reading_count:4d}: {distance:6.2f} cm")
            else:
                print(f"Reading #{reading_count:4d}: ERROR (no valid reading)")
                print("   Tips: check 5V/GND, TRIG->GPIO23, ECHO->GPIO24 via divider,")
                print("         and ensure nothing is closer than 2cm or beyond 4m.")
            
            time.sleep(0.25)  # 250ms between readings
            
    except KeyboardInterrupt:
        print("\n")
        print("-" * 60)
        print("✅ Test stopped by user")
        return True
    except Exception as e:
        print(f"\n❌ Error during test: {e}")
        return False

def main():
    """Main test function"""
    print("\n" + "="*60)
    print("🚀 ULTRASONIC SENSOR TEST")
    print("="*60)
    print("")
    
    # Run continuous ultrasonic sensor test
    sensor_ok = test_ultrasonic_sensor()
    
    # Cleanup
    if gpio_available:
        try:
            GPIO.cleanup()
            print("🧹 GPIO cleanup completed")
        except:
            pass
    
    if sensor_ok:
        print("✅ Test completed successfully!")
        return 0
    else:
        print("❌ Test failed. Please check your wiring.")
        print("")
        print("🔧 Troubleshooting:")
        print("   1. Check wiring: TRIG->GPIO23, ECHO->GPIO24")
        print("   2. Verify sensor is powered (5V and GND)")
        print("   3. Check if sensor is connected properly")
        print("   4. Try running with: sudo python3 test_ultrasonic.py")
        return 1

if __name__ == "__main__":
    try:
        exit_code = main()
        exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n🛑 Test interrupted by user")
        if gpio_available:
            try:
                GPIO.cleanup()
            except:
                pass
        exit(0)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        if gpio_available:
            try:
                GPIO.cleanup()
            except:
                pass
        exit(1)

