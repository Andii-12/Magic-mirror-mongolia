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
TRAINER_PATH = "trainer.yml"
IMAGE_BASE = "Images"

class FaceRecognitionSystem:
    def __init__(self):
        self.current_person = None
        self.current_distance = 999
        self.is_active = False
        self.last_detection_time = None
        self.shutdown_timer = None
        
        # Initialize GPIO for ultrasonic sensor (matching your working code)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(TRIG_PIN, GPIO.OUT)
        GPIO.setup(ECHO_PIN, GPIO.IN)
        
        # Load face recognition components (matching your working code)
        self.face_cascade = cv2.CascadeClassifier(CASCADE_PATH)
        self.recognizer = cv2.face.LBPHFaceRecognizer_create()
        self.recognizer.read(TRAINER_PATH)
        
        # Load label mapping (matching your working code)
        self.label_names = os.listdir(IMAGE_BASE)
        self.label_map = {i: name for i, name in enumerate(self.label_names)}
        
        print("Face Recognition System initialized")
        print(f"Loaded {len(self.label_names)} known faces: {self.label_names}")

    def get_distance(self):
        """Get distance from ultrasonic sensor in cm (matching your working code)"""
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
                    recognized_person = name
                    break
            else:
                print("[INFO] No face detected in frame!")

            picam2.close()
            
            # Update status with recognition result
            self.current_person = recognized_person
            self.update_status_file()
            
            return recognized_person
            
        except Exception as e:
            print(f"Error in face recognition: {e}")
            self.current_person = None
            self.update_status_file()
            return None

    def update_status_file(self):
        """Update the status file for MagicMirror²"""
        status = {
            "distance": self.current_distance,
            "person": self.current_person,
            "active": self.is_active,
            "timestamp": datetime.now().isoformat()
        }
        
        try:
            with open(STATUS_FILE, 'w') as f:
                json.dump(status, f)
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
                    
                    # Only perform face recognition once per detection
                    if self.current_person is None:
                        # Perform face recognition using your working method
                        person = self.recognize_face_with_camera()
                        if person:
                            print(f"Face recognized: {person}")
                            self.current_person = person
                        else:
                            print("No face recognized")
                            self.current_person = "Unknown"
                    
                    time.sleep(2)  # Wait longer to avoid multiple triggers
                else:
                    # Object moved away
                    if self.is_active:
                        if self.shutdown_timer is None:
                            print(f"Object moved away ({distance}cm) - starting {TIMEOUT_DELAY}s shutdown timer")
                            self.shutdown_timer = time.time()
                        elif time.time() - self.shutdown_timer >= TIMEOUT_DELAY:
                            print("Timeout reached - shutting down MagicMirror")
                            self.is_active = False
                            self.current_person = None
                            self.shutdown_timer = None
                            # Shutdown MagicMirror
                            os.system("pkill -f 'node.*electron'")
                
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
