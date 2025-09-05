#!/usr/bin/env python3
"""
Face Recognition System for MagicMirror²
Integrates ultrasonic sensor and camera for proximity detection and face recognition
Based on the working combined.py code
"""

import cv2
import json
import time
import os
import sys
import numpy as np
from datetime import datetime
import RPi.GPIO as GPIO
from picamera2 import Picamera2

# GPIO pins for ultrasonic sensor (matching your working code)
TRIG_PIN = 23  # GPIO pin for TRIG
ECHO_PIN = 24  # GPIO pin for ECHO

# Face recognition settings
STATUS_FILE = "/tmp/magicmirror_face_status.json"
PROXIMITY_THRESHOLD = 20  # cm
TIMEOUT_DELAY = 10  # seconds

# Face recognition paths (matching your working code)
CASCADE_PATH = "/home/andii/haarcascades/haarcascade_frontalface_default.xml"
TRAINER_PATH = "trainer.yml"  # Will check python_code/trainer.yml if not found
IMAGE_BASE = "Images"

class FaceRecognitionSystem:
    def __init__(self):
        self.current_person = None
        self.current_distance = 999
        self.is_active = False
        self.last_detection_time = None
        self.shutdown_timer = None
        
        # Initialize GPIO for ultrasonic sensor (matching your working code)
        try:
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(TRIG_PIN, GPIO.OUT)
            GPIO.setup(ECHO_PIN, GPIO.IN)
        except Exception as e:
            print(f"⚠️  GPIO setup warning: {e}")
            print("   Continuing without ultrasonic sensor...")
            self.gpio_available = False
        else:
            self.gpio_available = True
        
        # Load face recognition components (matching your working code)
        self.face_cascade = cv2.CascadeClassifier(CASCADE_PATH)
        self.recognizer = cv2.face.LBPHFaceRecognizer_create()
        
        # Try to load trainer.yml from multiple locations
        trainer_paths = [TRAINER_PATH, "python_code/trainer.yml"]
        trainer_loaded = False
        
        for trainer_path in trainer_paths:
            if os.path.exists(trainer_path):
                try:
                    self.recognizer.read(trainer_path)
                    print(f"✅ Loaded trainer from: {trainer_path}")
                    trainer_loaded = True
                    break
                except Exception as e:
                    print(f"⚠️  Could not load trainer from {trainer_path}: {e}")
                    continue
        
        if not trainer_loaded:
            raise Exception("Could not load trainer.yml from any location")
        
        # Load label mapping (matching your working code)
        if os.path.exists(IMAGE_BASE):
            self.label_names = os.listdir(IMAGE_BASE)
        else:
            self.label_names = []
        self.label_map = {i: name for i, name in enumerate(self.label_names)}
        
        print("Face Recognition System initialized")
        print(f"Loaded {len(self.label_names)} known faces: {self.label_names}")

    def get_distance(self):
        """Get distance from ultrasonic sensor in cm (matching your working code)"""
        if not self.gpio_available:
            return 999  # Return far distance if GPIO not available
            
        try:
            GPIO.output(TRIG_PIN, False)
            time.sleep(0.1)

            GPIO.output(TRIG_PIN, True)
            time.sleep(0.00001)
            GPIO.output(TRIG_PIN, False)

            while GPIO.input(ECHO_PIN) == 0:
                pulse_start = time.time()
            while GPIO.input(ECHO_PIN) == 1:
                pulse_end = time.time()

            pulse_duration = pulse_end - pulse_start
            distance = pulse_duration * 17150
            distance = round(distance, 2)
            return distance
            
        except Exception as e:
            print(f"Error reading distance: {e}")
            return 999

    def recognize_face_with_camera(self):
        """Recognize faces using Picamera2 (matching your working code)"""
        try:
            print(f"[INFO] Object detected at {self.current_distance}cm. Opening camera...")
            
            # Update status to show "detecting" state
            self.update_status_file()
            
            picam2 = Picamera2()
            config = picam2.create_preview_configuration(main={"size": (320, 240)})
            picam2.configure(config)
            picam2.start()
            time.sleep(1)  # small delay to let camera initialize

            frame = picam2.capture_array()
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)

            recognized_person = None
            if len(faces) > 0:
                for (x, y, w, h) in faces:
                    face_img = gray[y:y+h, x:x+w]
                    label, confidence = self.recognizer.predict(face_img)
                    name = self.label_map.get(label, "Unknown")
                    print(f"[INFO] Recognized: {name} (Confidence: {confidence:.2f})")
                    
                    # Only return known persons, not "Unknown"
                    if name != "Unknown":
                        recognized_person = name
                        break
                    else:
                        print(f"[INFO] Face detected but not recognized (confidence: {confidence:.2f})")
            else:
                print("[INFO] No face detected in frame!")

            picam2.close()
            
            # Don't update current_person here, let the main loop handle it
            return recognized_person
            
        except Exception as e:
            print(f"Error in face recognition: {e}")
            self.current_person = None
            self.update_status_file()
            return None

    def update_status_file(self):
        """Update the status file for MagicMirror²"""
        # Determine current status
        if not self.is_active:
            status_type = "waiting"
        elif self.current_person and self.current_person != "Unknown":
            status_type = "recognized"
        else:
            status_type = "detecting"
        
        status = {
            "distance": self.current_distance,
            "person": self.current_person,
            "active": self.is_active,
            "status": status_type,
            "timestamp": datetime.now().isoformat()
        }
        
        try:
            # Write to temporary file first, then rename to avoid corruption
            temp_file = STATUS_FILE + ".tmp"
            with open(temp_file, 'w') as f:
                json.dump(status, f, indent=2)
            # Atomic rename to avoid partial reads
            os.rename(temp_file, STATUS_FILE)
        except Exception as e:
            print(f"Error writing status file: {e}")

    def run(self):
        """Main loop (based on your working combined.py logic)"""
        print("Starting face recognition system...")
        print("Press Ctrl+C to stop")
        
        try:
            while True:
                # Get distance from ultrasonic sensor
                distance = self.get_distance()
                self.current_distance = distance
                
                # Check proximity (matching your working code)
                if distance <= PROXIMITY_THRESHOLD:
                    # Object detected within threshold
                    if not self.is_active:
                        print(f"Object detected at {distance}cm - starting face recognition")
                        self.is_active = True
                        self.last_detection_time = time.time()
                        self.shutdown_timer = None
                        self.current_person = None  # Reset person
                        self.update_status_file()  # Update status to show detecting
                    
                    # Keep trying face recognition until we get a known person
                    if self.current_person is None:
                        # Perform face recognition using your working method
                        person = self.recognize_face_with_camera()
                        if person and person != "Unknown":
                            print(f"Face recognized: {person}")
                            self.current_person = person
                        else:
                            print("Face not recognized yet, continuing to try...")
                            # Don't set to "Unknown", keep trying
                            self.current_person = None
                    
                    time.sleep(1)  # Shorter delay for continuous recognition attempts
                else:
                    # Object moved away
                    if self.is_active:
                        if self.shutdown_timer is None:
                            print(f"Object moved away ({distance}cm) - starting {TIMEOUT_DELAY}s shutdown timer")
                            self.shutdown_timer = time.time()
                        elif time.time() - self.shutdown_timer >= TIMEOUT_DELAY:
                            print("Timeout reached - logging out user")
                            self.is_active = False
                            self.current_person = None
                            self.shutdown_timer = None
                            # Update status file to clear user data
                            self.update_status_file()
                
                # Update status file for MagicMirror²
                self.update_status_file()
                
                # Small delay for sensor polling (matching your code)
                time.sleep(0.2)
                
        except KeyboardInterrupt:
            print("\nStopping face recognition system...")
        finally:
            self.cleanup()

    def cleanup(self):
        """Clean up resources"""
        GPIO.cleanup()
        print("Cleanup completed")

if __name__ == "__main__":
    system = FaceRecognitionSystem()
    system.run()
