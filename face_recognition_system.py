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

# Check if we're running on Windows (for development)
import platform
if platform.system() == "Windows":
    print("⚠️  Running on Windows - face recognition will be simulated")
    CASCADE_PATH = None
    TRAINER_PATH = None
    IMAGE_BASE = None

# Add test mode for ultrasonic sensor
TEST_MODE = os.environ.get('FACE_RECOGNITION_TEST', 'false').lower() == 'true'
if TEST_MODE:
    print("🧪 Running in TEST MODE - ultrasonic sensor will be simulated")

class FaceRecognitionSystem:
    def __init__(self):
        self.current_person = None
        self.current_distance = 999
        self.is_active = False
        self.last_detection_time = None
        self.shutdown_timer = None
        self.camera_opened = False
        self.face_recognition_attempted = False
        
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
        if CASCADE_PATH and os.path.exists(CASCADE_PATH):
            self.face_cascade = cv2.CascadeClassifier(CASCADE_PATH)
        else:
            print("⚠️  Face cascade not found - using default")
            self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        
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
            print("⚠️  No trainer.yml found - face recognition will be simulated")
            self.recognizer = None
        
        # Load label mapping (matching your working code)
        if IMAGE_BASE and os.path.exists(IMAGE_BASE):
            self.label_names = os.listdir(IMAGE_BASE)
        else:
            self.label_names = ["Unknown"]  # Default label
        self.label_map = {i: name for i, name in enumerate(self.label_names)}
        
        print("Face Recognition System initialized")
        print(f"Loaded {len(self.label_names)} known faces: {self.label_names}")

    def get_distance(self):
        """Get distance from ultrasonic sensor in cm with improved accuracy and error handling"""
        if not self.gpio_available or TEST_MODE:
            if TEST_MODE:
                # Simulate distance changes for testing
                import random
                # Simulate someone approaching and leaving
                if hasattr(self, '_test_distance_counter'):
                    self._test_distance_counter += 1
                else:
                    self._test_distance_counter = 0
                
                # Simulate approaching (distance decreasing)
                if self._test_distance_counter < 50:
                    return max(5, 50 - self._test_distance_counter)
                # Simulate staying close
                elif self._test_distance_counter < 100:
                    return random.uniform(10, 20)
                # Simulate moving away
                else:
                    return random.uniform(30, 100)
            return 999  # Return far distance if GPIO not available
            
        try:
            # Ensure trigger is low initially
            GPIO.output(TRIG_PIN, False)
            time.sleep(0.01)  # Reduced wait time

            # Send trigger pulse
            GPIO.output(TRIG_PIN, True)
            time.sleep(0.00001)  # 10 microseconds
            GPIO.output(TRIG_PIN, False)

            # Wait for echo to start (with timeout)
            timeout_start = time.time()
            while GPIO.input(ECHO_PIN) == 0:
                if time.time() - timeout_start > 0.1:  # 100ms timeout
                    print("Warning: Echo start timeout")
                    return 999
                pulse_start = time.time()

            # Wait for echo to end (with timeout)
            timeout_start = time.time()
            while GPIO.input(ECHO_PIN) == 1:
                if time.time() - timeout_start > 0.1:  # 100ms timeout
                    print("Warning: Echo end timeout")
                    return 999
                pulse_end = time.time()

            # Calculate distance
            pulse_duration = pulse_end - pulse_start
            
            # Validate pulse duration (should be reasonable for ultrasonic sensor)
            if pulse_duration < 0.0001 or pulse_duration > 0.1:  # 0.1ms to 100ms
                print(f"Warning: Invalid pulse duration: {pulse_duration}")
                return 999
            
            # Convert to distance (speed of sound = 34300 cm/s, divide by 2 for round trip)
            distance = (pulse_duration * 34300) / 2
            distance = round(distance, 2)
            
            # Validate distance range (2cm to 400cm)
            if distance < 2 or distance > 400:
                print(f"Warning: Distance out of range: {distance}cm")
                return 999
                
            return distance
            
        except Exception as e:
            print(f"Error reading distance: {e}")
            return 999

    def recognize_face_with_camera(self):
        """Recognize faces using Picamera2 - optimized for single attempt"""
        try:
            print(f"[INFO] Object detected at {self.current_distance}cm. Opening camera...")
            
            # Check if we're on Windows (simulation mode)
            if platform.system() == "Windows":
                print("[INFO] Windows detected - simulating face recognition")
                time.sleep(1)  # Simulate camera delay
                return "Andii"  # Return actual user for Windows
            
            # Initialize camera with minimal configuration
            picam2 = Picamera2()
            config = picam2.create_preview_configuration(main={"size": (320, 240)})
            picam2.configure(config)
            picam2.start()
            time.sleep(0.5)  # Reduced delay for faster initialization

            # Try to capture and recognize faces with multiple attempts
            recognized_person = None
            max_attempts = 3
            
            for attempt in range(max_attempts):
                try:
                    frame = picam2.capture_array()
                    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                    faces = self.face_cascade.detectMultiScale(gray, 1.1, 4, minSize=(50, 50))

                    if len(faces) > 0:
                        print(f"[INFO] {len(faces)} face(s) detected (attempt {attempt + 1})")
                        if self.recognizer:
                            for (x, y, w, h) in faces:
                                face_img = gray[y:y+h, x:x+w]
                                face_img = cv2.resize(face_img, (100, 100))  # Resize for consistency
                                label, confidence = self.recognizer.predict(face_img)
                                name = self.label_map.get(label, "Unknown")
                                print(f"[INFO] Recognized: {name} (Confidence: {confidence:.2f})")
                                
                                # Only return known persons with good confidence
                                if name != "Unknown" and confidence < 100:  # Lower confidence threshold
                                    recognized_person = name
                                    break
                                else:
                                    print(f"[INFO] Face detected but not recognized (confidence: {confidence:.2f})")
                        else:
                            # Simulate recognition for testing - return actual user from profiles
                            print("[INFO] Face recognition simulated - returning 'Andii'")
                            recognized_person = "Andii"
                            break
                    else:
                        print(f"[INFO] No face detected in frame (attempt {attempt + 1})")
                        time.sleep(0.2)  # Brief pause before next attempt
                        
                except Exception as e:
                    print(f"[WARNING] Camera capture attempt {attempt + 1} failed: {e}")
                    time.sleep(0.1)
                    continue
                
                # If we found a person, break out of attempts
                if recognized_person:
                    break

            # Always close camera
            picam2.close()
            
            if recognized_person:
                print(f"✅ Face recognition successful: {recognized_person}")
            else:
                print("❌ Face recognition failed after all attempts")
            
            return recognized_person
            
        except Exception as e:
            print(f"Error in face recognition: {e}")
            return None

    def update_status_file(self):
        """Update the status file for MagicMirror²"""
        # Determine current status based on distance and recognition state
        if self.current_distance > PROXIMITY_THRESHOLD:
            # Far from sensor - show "come closer" message
            status_type = "waiting"
            # Don't change active state or person if we're in timeout period
            if self.shutdown_timer is None:
                self.is_active = False
                self.current_person = None
                self.face_recognition_attempted = False
                self.camera_opened = False
        elif self.current_person and self.current_person != "Unknown":
            # Face recognized - show personal data
            status_type = "recognized"
            self.is_active = True
        elif self.current_distance <= PROXIMITY_THRESHOLD and not self.face_recognition_attempted:
            # Close to sensor but haven't tried face recognition yet - show "scanning face"
            status_type = "detecting"
            self.is_active = True
        elif self.current_distance <= PROXIMITY_THRESHOLD and self.face_recognition_attempted and not self.current_person:
            # Close to sensor but face recognition failed - show "scanning face" again
            status_type = "detecting"
            self.is_active = True
        else:
            # Default state - maintain current state
            if self.current_person:
                status_type = "recognized"
            elif self.is_active:
                status_type = "detecting"
            else:
                status_type = "waiting"
        
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
            # Only print status updates when they change significantly
            if not hasattr(self, 'last_printed_status') or self.last_printed_status != status:
                print(f"Status updated: {status}")
                self.last_printed_status = status.copy()
        except Exception as e:
            print(f"Error writing status file: {e}")

    def run(self):
        """Main loop with improved proximity detection and state management"""
        print("Starting face recognition system...")
        print(f"Proximity threshold: {PROXIMITY_THRESHOLD}cm")
        print(f"Timeout delay: {TIMEOUT_DELAY}s")
        print("Press Ctrl+C to stop")
        
        # Add distance smoothing for more stable readings
        distance_history = []
        HISTORY_SIZE = 3  # Reduced for faster response
        last_status_update = 0
        STATUS_UPDATE_INTERVAL = 0.2  # Update more frequently for better responsiveness
        
        # State tracking variables
        proximity_stable_count = 0
        PROXIMITY_STABLE_THRESHOLD = 2  # Need 2 consecutive readings under threshold
        away_stable_count = 0
        AWAY_STABLE_THRESHOLD = 3  # Need 3 consecutive readings over threshold
        
        try:
            while True:
                # Get distance from ultrasonic sensor
                distance = self.get_distance()
                
                # Add to history for smoothing
                distance_history.append(distance)
                if len(distance_history) > HISTORY_SIZE:
                    distance_history.pop(0)
                
                # Calculate smoothed distance (average of last few readings)
                smoothed_distance = sum(distance_history) / len(distance_history)
                self.current_distance = smoothed_distance
                
                # Debug output every 10 iterations
                if len(distance_history) % 10 == 0:
                    print(f"[DEBUG] Distance: {distance}cm (smoothed: {smoothed_distance:.1f}cm), Active: {self.is_active}, Person: {self.current_person}")
                
                # Check proximity with smoothed distance
                if smoothed_distance <= PROXIMITY_THRESHOLD:
                    # Object detected within threshold
                    proximity_stable_count += 1
                    away_stable_count = 0  # Reset away counter
                    
                    # Only activate if proximity is stable
                    if proximity_stable_count >= PROXIMITY_STABLE_THRESHOLD and not self.is_active:
                        print(f"🎯 Object detected at {smoothed_distance:.1f}cm - activating face recognition")
                        self.last_detection_time = time.time()
                        self.shutdown_timer = None
                        self.current_person = None  # Reset person
                        self.face_recognition_attempted = False
                        self.camera_opened = False
                        self.is_active = True
                        self.update_status_file()
                    
                    # Try face recognition when first activated
                    if self.is_active and self.current_person is None and not self.face_recognition_attempted:
                        # Wait 1 second for stable proximity before camera activation
                        if time.time() - self.last_detection_time > 1.0:
                            print("📷 Opening camera for face recognition...")
                            self.face_recognition_attempted = True
                            person = self.recognize_face_with_camera()
                            if person and person != "Unknown":
                                print(f"✅ Face recognized: {person}")
                                self.current_person = person
                                self.shutdown_timer = None
                                self.update_status_file()
                            else:
                                print("❌ Face not recognized - will retry in 3 seconds")
                                # Reset recognition attempt to retry
                                self.face_recognition_attempted = False
                                self.last_detection_time = time.time() - 1.0  # Allow retry in 1 second
                    
                    # If face already recognized, maintain the state and reset timeout
                    elif self.current_person is not None:
                        # Reset timeout timer since person is still present
                        self.shutdown_timer = None
                        # Only log every 10 seconds to reduce spam
                        if time.time() - self.last_detection_time > 10:
                            print(f"👤 User {self.current_person} is still present at {smoothed_distance:.1f}cm")
                            self.last_detection_time = time.time()
                    
                    # Update status file regularly when active
                    current_time = time.time()
                    if current_time - last_status_update > STATUS_UPDATE_INTERVAL:
                        self.update_status_file()
                        last_status_update = current_time
                    
                    time.sleep(0.2)  # Check every 0.2 seconds when active
                else:
                    # Object moved away - count consecutive away readings
                    away_stable_count += 1
                    proximity_stable_count = 0  # Reset proximity counter
                    
                    # Only deactivate if away for stable period
                    if away_stable_count >= AWAY_STABLE_THRESHOLD:
                        if self.current_person is not None:
                            print(f"👋 User {self.current_person} moved away ({smoothed_distance:.1f}cm) - starting {TIMEOUT_DELAY}s timeout")
                            # Start timeout timer instead of immediate logout
                            if self.shutdown_timer is None:
                                self.shutdown_timer = time.time()
                        elif self.is_active and self.shutdown_timer is None:
                            # No person recognized but was active - start timeout
                            self.shutdown_timer = time.time()
                            print(f"⏰ No face recognized, starting {TIMEOUT_DELAY}s timeout")
                    
                    # Check if timeout has elapsed
                    if self.shutdown_timer is not None:
                        elapsed = time.time() - self.shutdown_timer
                        if elapsed >= TIMEOUT_DELAY:
                            print(f"⏰ Timeout reached ({TIMEOUT_DELAY}s) - logging out user")
                            # Reset all states after timeout
                            self.current_person = None
                            self.is_active = False
                            self.face_recognition_attempted = False
                            self.camera_opened = False
                            self.shutdown_timer = None
                            self.update_status_file()
                        else:
                            # Still in timeout period - show countdown
                            remaining = TIMEOUT_DELAY - elapsed
                            if int(remaining) % 2 == 0:  # Log every 2 seconds during timeout
                                print(f"⏰ Timeout countdown: {remaining:.0f}s remaining")
                    
                    # Update status file during timeout
                    current_time = time.time()
                    if current_time - last_status_update > STATUS_UPDATE_INTERVAL:
                        self.update_status_file()
                        last_status_update = current_time
                    
                    time.sleep(0.3)  # Check every 0.3 seconds when away
                
        except KeyboardInterrupt:
            print("\n🛑 Stopping face recognition system...")
        finally:
            self.cleanup()

    def cleanup(self):
        """Clean up resources"""
        GPIO.cleanup()
        print("Cleanup completed")

if __name__ == "__main__":
    system = FaceRecognitionSystem()
    system.run()
