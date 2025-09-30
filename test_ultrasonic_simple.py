#!/usr/bin/env python3
"""
Simple ultrasonic sensor test
"""

import RPi.GPIO as GPIO
import time
import sys

# GPIO pins for ultrasonic sensor
TRIG_PIN = 23  # GPIO pin for TRIG
ECHO_PIN = 24  # GPIO pin for ECHO

def get_distance():
    """Get distance from ultrasonic sensor in cm"""
    try:
        # Ensure trigger is low initially
        GPIO.output(TRIG_PIN, False)
        time.sleep(0.01)

        # Send trigger pulse
        GPIO.output(TRIG_PIN, True)
        time.sleep(0.00001)  # 10 microseconds
        GPIO.output(TRIG_PIN, False)

        # Wait for echo to start
        timeout_start = time.time()
        while GPIO.input(ECHO_PIN) == 0:
            if time.time() - timeout_start > 0.1:  # 100ms timeout
                return 999
            pulse_start = time.time()

        # Wait for echo to end
        timeout_start = time.time()
        while GPIO.input(ECHO_PIN) == 1:
            if time.time() - timeout_start > 0.1:  # 100ms timeout
                return 999
            pulse_end = time.time()

        # Calculate distance
        pulse_duration = pulse_end - pulse_start
        distance = (pulse_duration * 34300) / 2
        distance = round(distance, 2)
        
        # Validate distance range
        if distance < 2 or distance > 400:
            return 999
            
        return distance
        
    except Exception as e:
        print(f"Error reading distance: {e}")
        return 999

def main():
    print("Ultrasonic Sensor Test")
    print("Press Ctrl+C to stop")
    
    try:
        # Initialize GPIO
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(TRIG_PIN, GPIO.OUT)
        GPIO.setup(ECHO_PIN, GPIO.IN)
        
        print("GPIO initialized successfully")
        
        while True:
            distance = get_distance()
            if distance < 20:
                print(f"🎯 Object detected at {distance}cm - UNDER THRESHOLD")
            else:
                print(f"📏 Distance: {distance}cm")
            time.sleep(0.5)
            
    except KeyboardInterrupt:
        print("\nStopping test...")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        GPIO.cleanup()
        print("GPIO cleaned up")

if __name__ == "__main__":
    main()
