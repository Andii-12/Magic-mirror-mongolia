#!/usr/bin/env python3

import cv2
import json
import time
import os
import sys
import numpy as np
from datetime import datetime
import RPi.GPIO as GPIO
from picamera2 import Picamera2
import libcamera
import subprocess
import platform

TRIG_PIN = 23
ECHO_PIN = 24
RELAY_PIN = 18

STATUS_FILE = "/tmp/magicmirror_face_status.json"
PROXIMITY_THRESHOLD = 20
TIMEOUT_DELAY = 5

CASCADE_PATH = "/home/andii/haarcascades/haarcascade_frontalface_default.xml"
TRAINER_PATH = "trainer.yml"
IMAGE_BASE = "Images"

TEST_MODE = os.environ.get('FACE_RECOGNITION_TEST', 'false').lower() == 'true'

class FaceRecognitionSystem:
    
    def __init__(self):
        print("=" * 60)
        print("Face Recognition System starting...")
        print("=" * 60)
        
        self.current_person = None
        self.current_distance = 999
        self.is_active = False
        self.last_detection_time = None
        self.shutdown_timer = None
        self.camera = None
        self.face_recognition_attempted = False
        self.recognition_locked = False
        self.current_confidence = 0
        self.recognition_image_path = None
        
        self.baseline_distance = None
        self._baseline_samples = []
        self.baseline_ready = False
        self.effective_proximity_threshold = PROXIMITY_THRESHOLD
        
        self.lights_on = False
        self.relay_available = False
        self.lights_stable_count = 0
        self.lights_off_stable_count = 0
        
        self._init_gpio()
        self._init_face_recognition()
        
        print("System initialized!")
        print("=" * 60)
    
    def _init_gpio(self):
        try:
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(TRIG_PIN, GPIO.OUT)
            GPIO.setup(ECHO_PIN, GPIO.IN)
            GPIO.setup(RELAY_PIN, GPIO.OUT)
            GPIO.output(RELAY_PIN, GPIO.HIGH)
            print("GPIO initialized")
            self.gpio_available = True
            self.relay_available = True
        except Exception as e:
            print(f"GPIO error: {e}")
            self.gpio_available = False
            self.relay_available = False
    
    def _init_face_recognition(self):
        cascade_paths = [
            CASCADE_PATH,
            "haarcascades/haarcascade_frontalface_default.xml",
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        ]
        
        for cascade_path in cascade_paths:
            if os.path.exists(cascade_path) or cascade_path == cascade_paths[-1]:
                try:
                    self.face_cascade = cv2.CascadeClassifier(cascade_path)
                    if not self.face_cascade.empty():
                        print(f"Cascade loaded: {cascade_path}")
                        break
                except Exception as e:
                    print(f"Cascade error: {e}")
                    continue
        
        self.recognizer = cv2.face.LBPHFaceRecognizer_create()
        if os.path.exists(TRAINER_PATH):
            try:
                self.recognizer.read(TRAINER_PATH)
                print(f"Trainer loaded: {TRAINER_PATH}")
            except Exception as e:
                print(f"Trainer error: {e}")
                self.recognizer = None
        else:
            print("trainer.yml not found")
            self.recognizer = None
        
        if os.path.exists(IMAGE_BASE):
            self.label_names = os.listdir(IMAGE_BASE)
        else:
            self.label_names = ["Unknown"]
        self.label_map = {i: name for i, name in enumerate(self.label_names)}
        print(f"{len(self.label_names)} faces loaded: {self.label_names}")
    
    def get_distance(self):
        if not self.gpio_available or TEST_MODE:
            if TEST_MODE:
                return 15
            return 999
        
        try:
            GPIO.output(TRIG_PIN, False)
            time.sleep(0.001)
            GPIO.output(TRIG_PIN, True)
            time.sleep(0.00001)
            GPIO.output(TRIG_PIN, False)
            
            start_time = time.time()
            timeout = start_time + 0.05
            while GPIO.input(ECHO_PIN) == 0:
                if time.time() > timeout:
                    return 999
                start_time = time.time()
            
            stop_time = time.time()
            timeout = stop_time + 0.05
            while GPIO.input(ECHO_PIN) == 1:
                if time.time() > timeout:
                    return 999
                stop_time = time.time()
            
            elapsed = stop_time - start_time
            distance = (elapsed * 34300) / 2
            
            if 2 <= distance <= 400:
                return round(distance, 2)
            return 999
        except Exception as e:
            print(f"Distance reading error: {e}")
            return 999
    
    def recognize_face(self):
        if platform.system() == "Windows" or TEST_MODE:
            if self.label_names and len(self.label_names) > 0:
                import random
                return random.choice(self.label_names)
            return "Guest 1"
        
        if self.camera is None:
            try:
                self.camera = Picamera2()
                config = self.camera.create_preview_configuration(
                    main={"size": (640, 480), "format": "RGB888"}
                )
                self.camera.configure(config)
                self.camera.start()
                time.sleep(1)
            except Exception as e:
                print(f"Camera initialization error: {e}")
                return None
        
        try:
            frame_rgb = self.camera.capture_array()
            frame = cv2.cvtColor(frame_rgb, cv2.COLOR_RGB2BGR)
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            faces = self.face_cascade.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=4,
                minSize=(60, 60)
            )
            
            if len(faces) > 0:
                largest_face = max(faces, key=lambda f: f[2] * f[3])
                x, y, w, h = largest_face
                face_img = gray[y:y+h, x:x+w]
                face_img = cv2.resize(face_img, (100, 100))
                face_img = cv2.equalizeHist(face_img)
                
                if self.recognizer:
                    label, confidence = self.recognizer.predict(face_img)
                    name = self.label_map.get(label, "Unknown")
                    
                    if confidence < 90:
                        print(f"Recognized: {name} (confidence: {confidence:.2f})")
                        return name
                    else:
                        print(f"Not recognized (confidence: {confidence:.2f})")
                        return "Guest 1"
                else:
                    return "Guest 1"
            else:
                print("No face detected")
                return None
        except Exception as e:
            print(f"Face recognition error: {e}")
            return None
    
    def update_status_file(self):
        status = {
            "distance": self.current_distance,
            "person": self.current_person,
            "active": self.is_active,
            "status": "recognized" if self.current_person else "detecting",
            "confidence": self.current_confidence,
            "timestamp": datetime.now().isoformat()
        }
        
        try:
            temp_file = STATUS_FILE + ".tmp"
            with open(temp_file, 'w') as f:
                json.dump(status, f)
            os.rename(temp_file, STATUS_FILE)
        except Exception as e:
            print(f"Status file write error: {e}")
    
    def turn_on_lights(self):
        if self.relay_available:
            GPIO.output(RELAY_PIN, GPIO.LOW)
            self.lights_on = True
            print("Lights turned on")
    
    def turn_off_lights(self):
        if self.relay_available:
            GPIO.output(RELAY_PIN, GPIO.HIGH)
            self.lights_on = False
            print("Lights turned off")
    
    def control_lights(self, distance):
        if not self.relay_available:
            return
        
        if distance <= PROXIMITY_THRESHOLD and not self.lights_on:
            self.lights_stable_count += 1
            if self.lights_stable_count >= 2:
                self.turn_on_lights()
                self.lights_stable_count = 0
        elif distance > PROXIMITY_THRESHOLD + 10 and self.lights_on:
            self.lights_off_stable_count += 1
            if self.lights_off_stable_count >= 5:
                self.turn_off_lights()
                self.lights_off_stable_count = 0
        else:
            self.lights_stable_count = 0
            self.lights_off_stable_count = 0
    
    def run(self):
        print("\n" + "=" * 60)
        print("Face Recognition System running...")
        print(f"Proximity threshold: {PROXIMITY_THRESHOLD}cm")
        print(f"Timeout: {TIMEOUT_DELAY} seconds")
        print("=" * 60)
        print("Press Ctrl+C to stop\n")
        
        distance_history = []
        HISTORY_SIZE = 5
        proximity_stable_count = 0
        PROXIMITY_STABLE_THRESHOLD = 3
        
        try:
            while True:
                distance = self.get_distance()
                
                distance_history.append(distance)
                if len(distance_history) > HISTORY_SIZE:
                    distance_history.pop(0)
                
                valid_distances = [d for d in distance_history if d < 400 and d != 999]
                if valid_distances:
                    valid_distances.sort()
                    median = valid_distances[len(valid_distances) // 2]
                    smoothed_distance = (median * 0.7 + sum(valid_distances) / len(valid_distances) * 0.3)
                else:
                    smoothed_distance = distance if distance < 400 else 999
                
                self.current_distance = smoothed_distance
                
                if not self.baseline_ready:
                    if smoothed_distance < 400 and smoothed_distance != 999:
                        self._baseline_samples.append(smoothed_distance)
                    if len(self._baseline_samples) >= 20:
                        self._baseline_samples.sort()
                        self.baseline_distance = self._baseline_samples[len(self._baseline_samples) // 2]
                        if self.baseline_distance <= PROXIMITY_THRESHOLD * 2:
                            self.effective_proximity_threshold = max(5, self.baseline_distance * 0.6)
                        else:
                            self.effective_proximity_threshold = PROXIMITY_THRESHOLD
                        self.baseline_ready = True
                        print(f"Baseline: {self.baseline_distance:.1f}cm, Threshold: {self.effective_proximity_threshold:.1f}cm")
                    
                    if not self.baseline_ready:
                        time.sleep(0.3)
                        continue
                
                self.control_lights(smoothed_distance)
                
                if smoothed_distance <= self.effective_proximity_threshold:
                    proximity_stable_count += 1
                    
                    if proximity_stable_count >= PROXIMITY_STABLE_THRESHOLD and not self.is_active:
                        print(f"Person detected! ({smoothed_distance:.1f}cm)")
                        self.is_active = True
                        self.last_detection_time = time.time()
                        self.current_person = None
                        self.face_recognition_attempted = False
                        self.update_status_file()
                    
                    if self.is_active and self.current_person is None and not self.face_recognition_attempted:
                        if time.time() - self.last_detection_time > 0.3:
                            print("Starting face recognition...")
                            self.face_recognition_attempted = True
                            person = self.recognize_face()
                            if person:
                                print(f"Recognized: {person}")
                                self.current_person = person
                                self.shutdown_timer = None
                                self.update_status_file()
                            else:
                                print("Face not recognized")
                                self.update_status_file()
                    
                    if time.time() - self.last_detection_time > 0.5:
                        self.update_status_file()
                        self.last_detection_time = time.time()
                    
                    time.sleep(0.2)
                else:
                    proximity_stable_count = 0
                    
                    if self.is_active or self.current_person:
                        print(f"Person moved away ({smoothed_distance:.1f}cm)")
                        self.is_active = False
                        self.current_person = None
                        self.face_recognition_attempted = False
                        self.turn_off_lights()
                        self.update_status_file()
                    
                    time.sleep(0.3)
                
        except KeyboardInterrupt:
            print("\n\nStopping system...")
        finally:
            self.cleanup()
    
    def cleanup(self):
        if self.camera:
            try:
                self.camera.close()
                print("Camera closed")
            except:
                pass
        
        if self.relay_available and self.lights_on:
            self.turn_off_lights()
        
        GPIO.cleanup()
        print("Cleanup completed")

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("Face Recognition System - Main Code")
    print("=" * 60)
    
    system = FaceRecognitionSystem()
    system.run()
