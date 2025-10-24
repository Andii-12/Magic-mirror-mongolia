#!/usr/bin/env python3
"""
Test script for 12V 2-channel relay control
Tests GPIO pins 18 and 19 for relay control
"""

import RPi.GPIO as GPIO
import time
import sys

# GPIO pin for 12V relay (single channel)
RELAY_PIN = 18  # GPIO pin for relay control

def setup_gpio():
    """Setup GPIO pins for relay control"""
    try:
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(RELAY_PIN, GPIO.OUT)
        # Initialize relay pin to OFF (LOW = relay OFF, HIGH = relay ON)
        GPIO.output(RELAY_PIN, GPIO.LOW)
        print("✅ GPIO setup complete - single relay ready")
        return True
    except Exception as e:
        print(f"❌ GPIO setup failed: {e}")
        return False

def turn_on_lights():
    """Turn on relay"""
    try:
        GPIO.output(RELAY_PIN, GPIO.HIGH)
        print("💡 Lights turned ON")
        return True
    except Exception as e:
        print(f"❌ Error turning on lights: {e}")
        return False

def turn_off_lights():
    """Turn off relay"""
    try:
        GPIO.output(RELAY_PIN, GPIO.LOW)
        print("🌙 Lights turned OFF")
        return True
    except Exception as e:
        print(f"❌ Error turning off lights: {e}")
        return False

def test_relay_sequence():
    """Test relay with a sequence of on/off cycles"""
    print("🧪 Starting relay test sequence...")
    print("   This will turn lights ON and OFF in 3-second intervals")
    print("   Press Ctrl+C to stop the test")
    print()
    
    try:
        cycle = 1
        while True:
            print(f"--- Cycle {cycle} ---")
            
            # Turn on lights
            turn_on_lights()
            time.sleep(3)
            
            # Turn off lights
            turn_off_lights()
            time.sleep(3)
            
            cycle += 1
            
    except KeyboardInterrupt:
        print("\n🛑 Test stopped by user")
    except Exception as e:
        print(f"❌ Test error: {e}")
    finally:
        # Ensure lights are off
        turn_off_lights()
        GPIO.cleanup()
        print("✅ Test completed - GPIO cleaned up")

def main():
    """Main test function"""
    print("🔌 12V Single Relay Test")
    print("=" * 25)
    print(f"Relay Pin: GPIO {RELAY_PIN}")
    print()
    
    # Check if running on Raspberry Pi
    try:
        with open('/proc/device-tree/model', 'r') as f:
            model = f.read().strip()
            print(f"✅ Raspberry Pi detected: {model}")
    except:
        print("⚠️  Not running on Raspberry Pi - GPIO may not work")
    
    # Setup GPIO
    if not setup_gpio():
        print("❌ Cannot proceed without GPIO setup")
        sys.exit(1)
    
    # Run test
    test_relay_sequence()

if __name__ == "__main__":
    main()
