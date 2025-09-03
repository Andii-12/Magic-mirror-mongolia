#!/usr/bin/env python3
"""
GPIO Cleanup Script
Cleans up GPIO pins and processes that might be using them
"""

import os
import subprocess
import time

def cleanup_gpio():
    """Clean up GPIO pins and related processes"""
    print("🧹 Cleaning up GPIO pins and processes...")
    
    # Kill any Python processes that might be using GPIO
    try:
        subprocess.run(["pkill", "-f", "python.*face_recognition"], check=False)
        subprocess.run(["pkill", "-f", "python.*combined"], check=False)
        print("   ✅ Killed face recognition processes")
    except:
        pass
    
    # Wait a moment for processes to die
    time.sleep(2)
    
    # Clean up GPIO using Python
    try:
        import RPi.GPIO as GPIO
        GPIO.cleanup()
        print("   ✅ Python GPIO cleanup completed")
    except Exception as e:
        print(f"   ⚠️  Python GPIO cleanup: {e}")
    
    # Clean up GPIO using system command
    try:
        subprocess.run(["sudo", "gpio", "unexportall"], check=False)
        print("   ✅ System GPIO cleanup completed")
    except Exception as e:
        print(f"   ⚠️  System GPIO cleanup: {e}")
    
    # Reset GPIO pins to input mode
    try:
        import RPi.GPIO as GPIO
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(23, GPIO.IN)
        GPIO.setup(24, GPIO.IN)
        GPIO.cleanup()
        print("   ✅ GPIO pins reset to input mode")
    except Exception as e:
        print(f"   ⚠️  GPIO reset: {e}")
    
    print("🎉 GPIO cleanup completed!")

if __name__ == "__main__":
    cleanup_gpio()
