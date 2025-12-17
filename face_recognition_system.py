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
import libcamera
import subprocess

# GPIO pins for ultrasonic sensor (matching your working code)
TRIG_PIN = 5   # GPIO pin for TRIG
ECHO_PIN = 6   # GPIO pin for ECHO

# GPIO pin for 12V relay (single channel)
RELAY_PIN = 18  # GPIO pin for relay control

# Face recognition settings
STATUS_FILE = "/tmp/magicmirror_face_status.json"
PROXIMITY_THRESHOLD = 75  # cm
TIMEOUT_DELAY = 5  # seconds

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

# Color/WB configuration
# - SKIN_COLOR_MODE: auto | natural | aggressive | blue_fix
# - SKIN_AWB: rpicam white balance mode (auto|daylight|fluorescent|incandescent|tungsten|greyworld)
# - SKIN_AWB_GAINS: manual red,blue gains (e.g. "1.0,1.8" to cool down yellow cast)
SKIN_COLOR_MODE = os.environ.get('SKIN_COLOR_MODE', 'auto').lower()
SKIN_AWB = os.environ.get('SKIN_AWB', 'auto')
SKIN_AWB_GAINS = os.environ.get('SKIN_AWB_GAINS', '1.0,1.2')  # Balanced for natural skin tones
SKIN_DESATURATE = os.environ.get('SKIN_DESATURATE', 'false').lower() == 'true'

class FaceRecognitionSystem:
    def __init__(self):
        self.current_person = None
        self.current_distance = 999
        self.is_active = False
        self.last_detection_time = None
        self.shutdown_timer = None
        self.camera_opened = False
        self.face_recognition_attempted = False
        self.camera = None  # Reuse camera instance
        self.recognition_locked = False  # Prevent re-recognition until user leaves
        self.photo_saved_this_session = False  # Track if photo was saved for current recognition
        self.last_photo_time = 0  # Track when last photo was saved
        self.guest_counter = 0  # Counter for unknown persons (guests)
        self.known_guests = {}  # Track guest names and their numbers
        self.current_confidence = 0  # Current recognition confidence percentage
        self.recognition_image_path = None  # Path to the captured/recognition image
        self.unknown_attempts = 0  # Count consecutive unknown recognitions before assigning guest
        self.last_recognized_name = None  # Sticky identity name
        self.last_recognized_time = 0  # Sticky identity timestamp
        # Baseline distance calibration (to avoid false triggers when nobody is there)
        self.baseline_distance = None
        self._baseline_samples = []
        self.baseline_ready = False
        self.effective_proximity_threshold = PROXIMITY_THRESHOLD
        # Person change detection
        self.last_person_name = None  # Track last recognized person to detect changes
        self.person_stable_start_time = None  # When current person was first detected
        self.min_stable_time_before_recognition = 1.0  # Minimum 1 second stable before recognition
        
        # Log messages for display (Mongolian)
        self.log_messages = []  # Store last 5 log messages in Mongolian
        self.max_log_messages = 5  # Maximum number of log messages to keep
        self._last_distance_log_time = 0  # Throttle ultrasonic log messages
        self._last_distance_log_value = None  # Track last logged distance
        
        # Relay control variables
        self.lights_on = False  # Track if lights are currently on
        self.relay_available = False  # Track if relay GPIO is available
        self.lights_stable_count = 0  # Count stable readings for lights
        self.lights_off_stable_count = 0  # Count stable readings for lights off
        self.last_light_change_time = 0  # Debounce relay toggles
        self.relay_block_until = 0  # Absolute time until which no relay toggles are allowed
        
        # Initialize GPIO for ultrasonic sensor and relay (matching your working code)
        try:
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(TRIG_PIN, GPIO.OUT)
            GPIO.setup(ECHO_PIN, GPIO.IN)
            # Setup relay pin as output
            GPIO.setup(RELAY_PIN, GPIO.OUT)
            # Initialize relay pin to OFF (HIGH = relay OFF for normally-closed relay)
            GPIO.output(RELAY_PIN, GPIO.HIGH)
            print("✅ GPIO setup complete - Ultrasonic sensor + single relay")
            self.gpio_available = True
            self.relay_available = True
        except Exception as e:
            print(f"⚠️  GPIO setup warning: {e}")
            print("   Continuing without ultrasonic sensor and relay...")
            self.gpio_available = False
            self.relay_available = False
        
        # Load face recognition components (matching your working code)
        # Try multiple cascade locations in order of preference
        cascade_paths = []
        if CASCADE_PATH:
            cascade_paths.append(CASCADE_PATH)
        # Add relative path option
        cascade_paths.append("haarcascades/haarcascade_frontalface_default.xml")
        # Add OpenCV default as final fallback
        cascade_paths.append(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        
        cascade_loaded = False
        for cascade_path in cascade_paths:
            if os.path.exists(cascade_path) or cascade_path == cascade_paths[-1]:  # Always try OpenCV default
                try:
                    self.face_cascade = cv2.CascadeClassifier(cascade_path)
                    # Verify the cascade was loaded correctly by checking if it's empty
                    if self.face_cascade.empty():
                        print(f"⚠️  Cascade file at {cascade_path} is empty or invalid - trying next")
                        continue
                    else:
                        print(f"✅ Loaded face cascade from: {cascade_path}")
                        cascade_loaded = True
                        break
                except Exception as e:
                    print(f"⚠️  Failed to load cascade from {cascade_path}: {e}")
                    if cascade_path != cascade_paths[-1]:
                        print("⚠️  Trying next cascade location...")
                        continue
                    else:
                        # This was the last option (OpenCV default)
                        print(f"❌ CRITICAL: Failed to load default cascade: {e}")
                        print("❌ Face recognition will not work without a valid cascade file")
                        raise SystemError("Cannot initialize face cascade classifier - face recognition disabled")
        
        if not cascade_loaded:
            print(f"❌ CRITICAL: Could not load any cascade file")
            print("❌ Face recognition will not work without a valid cascade file")
            raise SystemError("Cannot initialize face cascade classifier - face recognition disabled")
        
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
        else:
            # Validate that the recognizer has been trained
            try:
                # Try to get the number of classes
                if hasattr(self.recognizer, 'getLabelsCount'):
                    labels_count = self.recognizer.getLabelsCount()
                    print(f"✅ Recognizer trained with {labels_count} classes")
                else:
                    print("✅ Recognizer loaded successfully")
            except Exception as e:
                print(f"⚠️  Recognizer validation failed: {e}")
                self.recognizer = None
        
        # Load label mapping (matching your working code)
        if IMAGE_BASE and os.path.exists(IMAGE_BASE):
            self.label_names = os.listdir(IMAGE_BASE)
        else:
            self.label_names = ["Unknown"]  # Default label
        self.label_map = {i: name for i, name in enumerate(self.label_names)}
        
        print("Face Recognition System initialized")
        print(f"Loaded {len(self.label_names)} known faces: {self.label_names}")
        
        # Add initial log message
        self.add_log_message("Хэт авианы мэдрэгч ажиллаж байна...")

    def add_log_message(self, message):
        """Add a log message in Mongolian (keep only last 5 messages)"""
        self.log_messages.append(message)
        if len(self.log_messages) > self.max_log_messages:
            self.log_messages.pop(0)  # Remove oldest message
    
    @staticmethod
    def map_lbph_confidence_to_percent(confidence: float) -> float:
        """Map OpenCV LBPH confidence (lower is better) to a user-friendly 0-100%.
        Tuned so strong matches show ~90%+ while weak/unknown trend low.

        Piecewise-linear mapping based on empirical LBPH ranges:
          - <=40   -> ~96-99%
          - 40-60  -> ~90-96%
          - 60-90  -> ~70-90%
          - 90-120 -> ~40-70%
          - >120   -> down to 0-40%
        """
        c = float(confidence)
        if c <= 0:
            base = 99.0
        elif c <= 40:
            base = max(0.0, min(100.0, 96.0 + (40.0 - c) * (3.0 / 40.0)))
        elif c <= 60:
            base = max(0.0, min(100.0, 90.0 + (60.0 - c) * (6.0 / 20.0)))
        elif c <= 90:
            base = max(0.0, min(100.0, 70.0 + (90.0 - c) * (20.0 / 30.0)))
        elif c <= 120:
            base = max(0.0, min(100.0, 40.0 + (120.0 - c) * (30.0 / 30.0)))
        else:
            if c >= 200:
                base = 5.0
            else:
                base = max(0.0, 40.0 - (c - 120.0) * (35.0 / 80.0))

        boosted = min(99.0, base + 20.0)
        return boosted

    def handle_unknown_person(self):
        """Handle unknown person as a guest"""
        # Generate a unique guest identifier based on timestamp
        import hashlib
        timestamp = str(int(time.time()))
        guest_hash = hashlib.md5(timestamp.encode()).hexdigest()[:8]
        
        print(f"[DEBUG] Handling unknown person - timestamp: {timestamp}, hash: {guest_hash}")
        
        # Check if this guest was seen recently (within 5 minutes)
        current_time = time.time()
        for guest_id, guest_data in self.known_guests.items():
            if current_time - guest_data['last_seen'] < 300:  # 5 minutes
                if guest_data['hash'] == guest_hash:
                    print(f"🔄 Returning guest detected: {guest_data['name']}")
                    return guest_data['name']
        
        # New guest - assign next number
        self.guest_counter += 1
        guest_name = f"Зочин {self.guest_counter}"
        
        # Store guest info
        self.known_guests[guest_name] = {
            'name': guest_name,
            'hash': guest_hash,
            'first_seen': current_time,
            'last_seen': current_time,
            'is_guest': True
        }
        
        print(f"👋 New guest detected: {guest_name}")
        print(f"[DEBUG] Guest counter: {self.guest_counter}, Known guests: {list(self.known_guests.keys())}")
        return guest_name

    def apply_skin_tone_correction(self, frame_rgb):
        """Apply color correction.
        Modes:
        - auto (default): no manual correction; use camera's auto WB for natural colors
        - natural: gray-world white balance + mild contrast; no hue/saturation shifts
        - aggressive: legacy strong adjustments for yellow-green cast
        - blue_fix: specific fix for blue-purple skin tone issues
        """
        try:
            # Convert RGB to BGR for OpenCV processing
            frame_bgr = cv2.cvtColor(frame_rgb, cv2.COLOR_RGB2BGR)

            if SKIN_COLOR_MODE in ('auto', 'off', 'none'):
                # Pass-through: trust camera auto white balance
                # Avoid any manual channel/hue changes to prevent blue tint
                return frame_bgr

            if SKIN_COLOR_MODE == 'blue_fix':
                # Specific fix for blue-purple skin tone issues
                print(f"[INFO] Blue-purple fix mode applied")
                
                # Convert to LAB for better color correction
                lab = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2LAB)
                l, a, b = cv2.split(lab)
                
                # Reduce blue channel significantly
                b = cv2.subtract(b, 15)  # Reduce blue-yellow component
                a = cv2.add(a, 8)        # Increase green-red component
                
                # Merge corrected LAB channels
                lab_corrected = cv2.merge([l, a, b])
                frame_lab_corrected = cv2.cvtColor(lab_corrected, cv2.COLOR_LAB2BGR)
                
                # Additional RGB channel adjustments
                b, g, r = cv2.split(frame_lab_corrected)
                r = cv2.multiply(r, 1.3)  # Boost red significantly
                g = cv2.multiply(g, 1.1)  # Slight green boost
                b = cv2.multiply(b, 0.7)  # Reduce blue significantly
                
                # Merge and apply gamma correction
                corrected = cv2.merge([b, g, r])
                corrected = np.clip(corrected, 0, 255).astype(np.uint8)
                
                # Apply gamma correction for better skin tones
                gamma = 1.2
                corrected = np.power(corrected / 255.0, 1.0/gamma) * 255.0
                corrected = np.clip(corrected, 0, 255).astype(np.uint8)
                
                return corrected

            elif SKIN_COLOR_MODE == 'natural':
                # Gray-world white balance: equalize average of channels
                b, g, r = cv2.split(frame_bgr)
                mean_b = float(b.mean()) + 1e-6
                mean_g = float(g.mean()) + 1e-6
                mean_r = float(r.mean()) + 1e-6
                mean_gray = (mean_b + mean_g + mean_r) / 3.0

                kb = mean_gray / mean_b
                kg = mean_gray / mean_g
                kr = mean_gray / mean_r

                b_corr = cv2.multiply(b, kb)
                g_corr = cv2.multiply(g, kg)
                r_corr = cv2.multiply(r, kr)
                wb = cv2.merge([b_corr, g_corr, r_corr])
                wb = np.clip(wb, 0, 255).astype(np.uint8)

                # Mild local contrast enhancement in LAB
                lab = cv2.cvtColor(wb, cv2.COLOR_BGR2LAB)
                l, a, b_lab = cv2.split(lab)
                clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
                l = clahe.apply(l)
                lab_corrected = cv2.merge([l, a, b_lab])
                natural = cv2.cvtColor(lab_corrected, cv2.COLOR_LAB2BGR)

                print(f"[INFO] Natural color mode applied (gray-world WB + mild CLAHE)")
                return natural

            # Aggressive legacy pipeline (previous behavior)
            print(f"[INFO] Aggressive color mode applied")
            b, g, r = cv2.split(frame_bgr)
            g_corrected = cv2.multiply(g, 0.75)
            r_corrected = cv2.multiply(r, 1.15)
            b_corrected = cv2.multiply(b, 1.05)
            frame_channel_corrected = cv2.merge([b_corrected, g_corrected, r_corrected])

            lab = cv2.cvtColor(frame_channel_corrected, cv2.COLOR_BGR2LAB)
            l, a, b_lab = cv2.split(lab)
            clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
            l = clahe.apply(l)
            a = cv2.add(a, 6)
            b_lab = cv2.subtract(b_lab, 4)
            lab_corrected = cv2.merge([l, a, b_lab])
            frame_lab_corrected = cv2.cvtColor(lab_corrected, cv2.COLOR_LAB2BGR)

            # Subtle HSV tweaks
            hsv = cv2.cvtColor(frame_lab_corrected, cv2.COLOR_BGR2HSV)
            h, s, v = cv2.split(hsv)
            s = cv2.multiply(s, 0.95)
            v = cv2.multiply(v, 1.03)
            hsv_corrected = cv2.merge([h, s, v])
            out = cv2.cvtColor(hsv_corrected, cv2.COLOR_HSV2BGR)
            return out

        except Exception as e:
            print(f"[WARNING] Color correction failed: {e}")
            return cv2.cvtColor(frame_rgb, cv2.COLOR_RGB2BGR)

    def get_distance(self):
        """Get distance from ultrasonic sensor in cm with improved accuracy and error handling
        Take multiple micro-samples and return a median-filtered value to reject spikes.
        """
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
            def read_once():
                # Ensure trigger is low initially
                GPIO.output(TRIG_PIN, False)
                time.sleep(0.001)
                # Send trigger pulse
                GPIO.output(TRIG_PIN, True)
                time.sleep(0.00001)
                GPIO.output(TRIG_PIN, False)

                # Wait for echo start
                start_deadline = time.time() + 0.05
                while GPIO.input(ECHO_PIN) == 0:
                    if time.time() > start_deadline:
                        return None
                pulse_start = time.time()

                # Wait for echo end
                end_deadline = time.time() + 0.05
                while GPIO.input(ECHO_PIN) == 1:
                    if time.time() > end_deadline:
                        return None
                pulse_end = time.time()

                pulse_duration = pulse_end - pulse_start
                if pulse_duration < 0.00005 or pulse_duration > 0.1:
                    return None
                distance = (pulse_duration * 34300) / 2
                if distance < 2 or distance > 400:
                    return None
                return round(distance, 2)

            # Take multiple samples and median-filter
            samples = []
            for _ in range(3):
                d = read_once()
                if d is not None:
                    samples.append(d)
                time.sleep(0.002)

            if not samples:
                return 999
            samples.sort()
            median = samples[len(samples)//2]
            # Soft-limit sudden drops/jumps by clamping to previous reading window
            if hasattr(self, '_last_distance_valid'):
                prev = self._last_distance_valid
                # Allow change by at most 20cm per cycle to reject spikes
                if abs(median - prev) > 20:
                    median = prev + (20 if median > prev else -20)
            self._last_distance_valid = median
            return median
        except Exception as e:
            print(f"Error reading distance: {e}")
            return 999

    def initialize_camera(self):
        """Initialize camera once and reuse it - OPTIMIZED with verification"""
        if self.camera is None and platform.system() != "Windows":
            try:
                print("[INFO] Initializing camera...")
                self.camera = Picamera2()
                config = self.camera.create_preview_configuration(
                    main={"size": (640, 480), "format": "RGB888"},
                    transform=libcamera.Transform(hflip=0, vflip=0)
                )
                self.camera.configure(config)
                self.camera.start()
                time.sleep(0.5)  # Give camera time to stabilize
                
                # Verify camera is actually working by attempting a test capture
                try:
                    test_frame = self.camera.capture_array()
                    if test_frame is None or test_frame.size == 0:
                        print("[ERROR] Camera test capture returned empty frame")
                        self.camera.stop()
                        self.camera.close()
                        self.camera = None
                        return False
                    print(f"[INFO] ✅ Camera initialized successfully (test frame: {test_frame.shape})")
                    return True
                except Exception as e:
                    print(f"[ERROR] Camera test capture failed: {e}")
                    try:
                        self.camera.stop()
                        self.camera.close()
                    except:
                        pass
                    self.camera = None
                    return False
            except Exception as e:
                print(f"[ERROR] Camera initialization failed: {e}")
                import traceback
                traceback.print_exc()
                self.camera = None
                return False
        elif self.camera is not None:
            # Camera already initialized, verify it's still working
            try:
                test_frame = self.camera.capture_array()
                if test_frame is None or test_frame.size == 0:
                    print("[WARNING] Camera appears to be broken, reinitializing...")
                    try:
                        self.camera.stop()
                        self.camera.close()
                    except:
                        pass
                    self.camera = None
                    return self.initialize_camera()
                return True
            except Exception as e:
                print(f"[WARNING] Camera verification failed: {e}, reinitializing...")
                try:
                    self.camera.stop()
                    self.camera.close()
                except:
                    pass
                self.camera = None
                return self.initialize_camera()
        return True
    
    def _save_recognition_image_from_frame(self, frame, x, y, w, h, person_name):
        """FAST: Save recognition image from current frame with natural color correction"""
        try:
            # Extract face region first
            face_roi = frame[y:y+h, x:x+w]
            
            # Apply natural color correction to fix blue tint
            face_corrected = self._apply_natural_color_correction(face_roi)
            
            # Resize to 300x300
            face_resized = cv2.resize(face_corrected, (300, 300), interpolation=cv2.INTER_AREA)
            
            # Save to recognition location
            script_dir = os.path.dirname(os.path.abspath(__file__))
            if os.path.basename(script_dir) == "MagicMirror-master" or os.path.exists(os.path.join(script_dir, "package.json")):
                project_root = script_dir
            else:
                project_root = os.path.dirname(script_dir)
            
            recognition_dir = os.path.join(project_root, "modules", "facerecognition", "public")
            os.makedirs(recognition_dir, exist_ok=True)
            recognition_file = os.path.join(recognition_dir, "recognition.jpg")
            
            cv2.imwrite(recognition_file, face_resized, [cv2.IMWRITE_JPEG_QUALITY, 90])
            self.recognition_image_path = "/modules/facerecognition/public/recognition.jpg"
        except Exception as e:
            print(f"[WARNING] Failed to save recognition image: {e}")
            self.recognition_image_path = None
    
    def _apply_natural_color_correction(self, frame_bgr):
        """Apply natural color correction to fix blue tint - optimized for speed"""
        try:
            # Gray-world white balance: equalize average of channels (fixes color cast)
            b, g, r = cv2.split(frame_bgr)
            mean_b = float(b.mean()) + 1e-6
            mean_g = float(g.mean()) + 1e-6
            mean_r = float(r.mean()) + 1e-6
            mean_gray = (mean_b + mean_g + mean_r) / 3.0

            # Calculate correction factors
            kb = mean_gray / mean_b
            kg = mean_gray / mean_g
            kr = mean_gray / mean_r

            # Apply white balance correction
            b_corr = cv2.multiply(b, kb)
            g_corr = cv2.multiply(g, kg)
            r_corr = cv2.multiply(r, kr)
            wb = cv2.merge([b_corr, g_corr, r_corr])
            wb = np.clip(wb, 0, 255).astype(np.uint8)

            # Additional fix for blue tint: reduce blue channel slightly, boost red
            b_final, g_final, r_final = cv2.split(wb)
            b_final = cv2.multiply(b_final, 0.95)  # Slightly reduce blue
            r_final = cv2.multiply(r_final, 1.05)  # Slightly boost red for warmer skin tones
            corrected = cv2.merge([b_final, g_final, r_final])
            corrected = np.clip(corrected, 0, 255).astype(np.uint8)

            return corrected
        except Exception as e:
            print(f"[WARNING] Color correction failed: {e}")
            return frame_bgr
    
    def _async_save_skin_photo_and_trigger(self, person_name):
        """ASYNC: Save skin photo and trigger analysis in background thread"""
        try:
            print(f"[INFO] Starting async skin photo save for: {person_name}")
            photo_saved = self.save_skin_photo(person_name)
            if photo_saved:
                print(f"[INFO] Skin photo saved successfully for: {person_name}")
                # Copy the newly saved skin photo to recognition location
                self.copy_latest_skin_photo_to_recognition(person_name)
                
                # Find the actual photo path (might have timestamp if duplicate)
                skin_dir = os.path.join(os.getcwd(), "Skin", person_name)
                if os.path.exists(skin_dir):
                    # Find the most recent photo
                    image_files = []
                    for file in os.listdir(skin_dir):
                        if file.lower().endswith(('.jpg', '.jpeg', '.png')):
                            file_path = os.path.join(skin_dir, file)
                            if os.path.isfile(file_path):
                                mtime = os.path.getmtime(file_path)
                                image_files.append((mtime, file_path))
                    
                    if image_files:
                        # Sort by modification time (newest first)
                        image_files.sort(reverse=True)
                        photo_path = image_files[0][1]
                        print(f"[INFO] Triggering skin analysis with photo: {photo_path}")
                        self.trigger_skin_analysis(person_name, photo_path)
                    else:
                        print(f"[WARNING] No photos found in {skin_dir} for skin analysis")
                else:
                    print(f"[WARNING] Skin directory not found: {skin_dir}")
            else:
                print(f"[WARNING] Skin photo save failed for: {person_name}")
        except Exception as e:
            print(f"[ERROR] Async skin photo save failed: {e}")
            import traceback
            traceback.print_exc()

    def capture_recognition_image_with_rpicam(self, output_path):
        """Capture recognition image using rpicam-still with natural colors (same as skin photos)"""
        try:
            # Check platform - skip on Windows
            if platform.system() == "Windows":
                print(f"[INFO] Windows detected - using Picamera2 fallback for recognition image")
                return self.capture_recognition_image_with_picamera2(output_path)
            
            # Check if rpicam-still is available
            try:
                result_check = subprocess.run(["which", "rpicam-still"], capture_output=True, text=True)
                if result_check.returncode != 0:
                    print(f"[WARNING] rpicam-still not found, using Picamera2 fallback")
                    return self.capture_recognition_image_with_picamera2(output_path)
            except Exception as e:
                print(f"[WARNING] rpicam-still check failed: {e}, using Picamera2 fallback")
                return self.capture_recognition_image_with_picamera2(output_path)
            
            # Ensure output directory exists
            output_dir = os.path.dirname(output_path)
            os.makedirs(output_dir, exist_ok=True)
            print(f"[DEBUG] Output directory ensured: {output_dir}")
            
            # Use rpicam-still with same settings as skin photos but smaller size
            cmd = [
                "rpicam-still",
                "-o", output_path,
                "--width", "200",
                "--height", "200",
                "-t", "2000",  # 2 second timeout
                "--immediate",  # Capture immediately
                "--awb", f"{SKIN_AWB}"
            ]
            
            # Add manual gains if specified (but skip for auto WB)
            if SKIN_AWB_GAINS and SKIN_AWB_GAINS.strip() and SKIN_AWB != "auto":
                cmd += ["--awbgains", f"{SKIN_AWB_GAINS}"]
            
            # Add desaturation only if requested
            if SKIN_DESATURATE:
                cmd += ["--saturation", "0"]
            
            print(f"[DEBUG] Running rpicam-still command: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            
            print(f"[DEBUG] rpicam-still return code: {result.returncode}")
            print(f"[DEBUG] rpicam-still stdout: {result.stdout}")
            if result.stderr:
                print(f"[DEBUG] rpicam-still stderr: {result.stderr}")
            
            if result.returncode == 0 and os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                file_size = os.path.getsize(output_path)
                print(f"[DEBUG] ✓ Captured recognition image with rpicam-still: {output_path} ({file_size} bytes)")
                return True
            else:
                print(f"[WARNING] rpicam-still capture failed (code: {result.returncode}), trying Picamera2 fallback")
                print(f"[DEBUG] File exists: {os.path.exists(output_path)}, Size: {os.path.getsize(output_path) if os.path.exists(output_path) else 0}")
                return self.capture_recognition_image_with_picamera2(output_path)
                
        except Exception as e:
            print(f"[WARNING] Error capturing recognition image with rpicam-still: {e}")
            import traceback
            traceback.print_exc()
            print(f"[INFO] Trying Picamera2 fallback...")
            return self.capture_recognition_image_with_picamera2(output_path)
    
    def capture_recognition_image_with_picamera2(self, output_path):
        """Fallback: Capture recognition image using Picamera2 directly"""
        try:
            print(f"[DEBUG] Attempting to capture recognition image with Picamera2: {output_path}")
            
            # Ensure output directory exists
            output_dir = os.path.dirname(output_path)
            os.makedirs(output_dir, exist_ok=True)
            
            # Check if camera is available
            if self.camera is None:
                print(f"[WARNING] Camera not initialized, trying to initialize...")
                self.initialize_camera()
                if self.camera is None:
                    print(f"[ERROR] Cannot capture image - camera not available")
                    return False
            
            # Capture frame from existing camera
            try:
                frame_rgb = self.camera.capture_array()
                # Convert RGB to BGR for OpenCV
                frame_bgr = cv2.cvtColor(frame_rgb, cv2.COLOR_RGB2BGR)
                
                # Resize to 200x200 for recognition image
                frame_resized = cv2.resize(frame_bgr, (200, 200))
                
                # Save image
                cv2.imwrite(output_path, frame_resized, [cv2.IMWRITE_JPEG_QUALITY, 85])
                
                # Verify file was saved
                if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                    file_size = os.path.getsize(output_path)
                    print(f"[DEBUG] ✓ Captured recognition image with Picamera2: {output_path} ({file_size} bytes)")
                    return True
                else:
                    print(f"[ERROR] Picamera2 capture failed - file not created or empty")
                    return False
                    
            except Exception as e:
                print(f"[ERROR] Failed to capture frame from Picamera2: {e}")
                import traceback
                traceback.print_exc()
                return False
                
        except Exception as e:
            print(f"[ERROR] Error in capture_recognition_image_with_picamera2: {e}")
            import traceback
            traceback.print_exc()
            return False

    def copy_latest_skin_photo_to_recognition(self, person_name):
        """Copy the latest skin photo from Skin folder to recognition image location"""
        try:
            # Get MagicMirror root directory
            script_dir = os.path.dirname(os.path.abspath(__file__))
            if os.path.basename(script_dir) == "MagicMirror-master" or os.path.exists(os.path.join(script_dir, "package.json")):
                project_root = script_dir
            else:
                project_root = os.path.dirname(script_dir)
            
            # Source: Latest image from Skin/{PersonName}/ directory
            skin_dir = os.path.join(project_root, "Skin", person_name)
            recognition_dir = os.path.join(project_root, "modules", "facerecognition", "public")
            recognition_file = os.path.join(recognition_dir, "recognition.jpg")
            
            # Check if skin directory exists
            if not os.path.exists(skin_dir):
                print(f"[DEBUG] Skin directory does not exist yet: {skin_dir}")
                return False
            
            # Find latest image in Skin directory
            image_files = []
            for file in os.listdir(skin_dir):
                if file.lower().endswith(('.jpg', '.jpeg', '.png')):
                    file_path = os.path.join(skin_dir, file)
                    if os.path.isfile(file_path):
                        mtime = os.path.getmtime(file_path)
                        image_files.append((mtime, file_path))
            
            if not image_files:
                print(f"[DEBUG] No images found in {skin_dir}")
                return False
            
            # Sort by modification time (newest first)
            image_files.sort(reverse=True)
            latest_image_path = image_files[0][1]
            
            print(f"[DEBUG] Found latest skin photo: {latest_image_path}")
            
            # Ensure recognition directory exists
            os.makedirs(recognition_dir, exist_ok=True)
            
            # Copy and resize the latest image to recognition location (300x300)
            import shutil
            import cv2
            
            # Read the original image
            img = cv2.imread(latest_image_path)
            if img is not None:
                # Resize to 300x300
                img_resized = cv2.resize(img, (300, 300), interpolation=cv2.INTER_AREA)
                # Save the resized image
                cv2.imwrite(recognition_file, img_resized, [cv2.IMWRITE_JPEG_QUALITY, 85])
                print(f"[DEBUG] Resized image from {img.shape[1]}x{img.shape[0]} to 300x300")
            else:
                # Fallback to copy if cv2 fails
                print(f"[WARNING] Failed to read image with cv2, using copy instead")
                shutil.copy2(latest_image_path, recognition_file)
            
            # Verify the copied file exists and is valid
            if os.path.exists(recognition_file) and os.path.getsize(recognition_file) > 0:
                file_size = os.path.getsize(recognition_file)
                # Verify it's actually a valid image file by checking first few bytes (JPEG magic numbers)
                try:
                    with open(recognition_file, 'rb') as f:
                        header = f.read(3)
                        if header.startswith(b'\xff\xd8\xff'):  # JPEG magic number
                            print(f"[DEBUG] ✓ Copied latest skin photo to recognition image: {recognition_file} ({file_size} bytes) - Valid JPEG")
                        else:
                            print(f"[WARNING] Copied file exists but may not be a valid JPEG (header: {header.hex()})")
                except Exception as e:
                    print(f"[WARNING] Error verifying image file: {e}")
                
                self.recognition_image_path = "/modules/facerecognition/public/recognition.jpg"
                print(f"[DEBUG] Set recognition_image_path to: {self.recognition_image_path}")
                return True
            else:
                print(f"[WARNING] Failed to copy skin photo to recognition location")
                return False
                
        except Exception as e:
            print(f"[WARNING] Error copying latest skin photo: {e}")
            import traceback
            traceback.print_exc()
            return False

    def save_skin_photo(self, person_name):
        """Save high-resolution photo using rpicam after successful face recognition"""
        try:
            print(f"\n{'='*60}")
            print(f"[SKIN PHOTO] Starting rpicam photo capture for: {person_name}")
            print(f"[DEBUG] photo_saved_this_session: {self.photo_saved_this_session}")
            print(f"{'='*60}")
            
            # Skip if photo already saved for this session, unless enough time has passed
            current_time = time.time()
            time_since_last_photo = current_time - self.last_photo_time
            PHOTO_INTERVAL = 300  # Allow new photo every 5 minutes (300 seconds) - more frequent for testing
            
            if self.photo_saved_this_session and time_since_last_photo < PHOTO_INTERVAL:
                print(f"[INFO] Photo already saved for this recognition session")
                print(f"[INFO] Time since last photo: {time_since_last_photo:.0f}s (interval: {PHOTO_INTERVAL}s)")
                print(f"[INFO] Skipping photo save to prevent duplicates")
                return False
            elif self.photo_saved_this_session and time_since_last_photo >= PHOTO_INTERVAL:
                print(f"[INFO] Enough time has passed since last photo, allowing new photo")
                print(f"[INFO] Resetting photo flag for new photo")
                self.photo_saved_this_session = False
            else:
                print(f"[INFO] Photo flag is False, proceeding with photo capture")
            
            # Check platform
            current_platform = platform.system()
            print(f"[INFO] Platform detected: {current_platform}")
            
            # Skip on Windows (no camera) - but allow if SKIN_PHOTO_TEST env variable is set
            if current_platform == "Windows":
                if not os.environ.get('SKIN_PHOTO_TEST'):
                    print("[INFO] Windows detected - skipping photo save")
                    print("[INFO] To test on Windows, set SKIN_PHOTO_TEST=1 environment variable")
                    return False
                else:
                    print("[WARNING] Windows test mode - photo will be simulated")
            
            # Create directory structure: Skin/{PersonName}/
            # Use absolute path to be sure where files are saved
            current_working_dir = os.getcwd()
            skin_base_dir = os.path.join(current_working_dir, "Skin")
            person_dir = os.path.join(skin_base_dir, person_name)
            
            print(f"[INFO] Current working directory: {current_working_dir}")
            print(f"[INFO] Base directory: {skin_base_dir}")
            print(f"[INFO] Person directory: {person_dir}")
            
            # Create directories if they don't exist
            try:
                os.makedirs(person_dir, exist_ok=True)
                print(f"✅ Directories created/verified: {person_dir}")
                
                # Verify directory was actually created
                if os.path.isdir(person_dir):
                    print(f"✅ Directory exists and is accessible")
                else:
                    print(f"[ERROR] Directory not accessible: {person_dir}")
                    return False
                    
            except Exception as e:
                print(f"[ERROR] Failed to create directory: {e}")
                import traceback
                traceback.print_exc()
                return False
            
            # Get current date for filename (YYYY-MM-DD format)
            current_date = datetime.now().strftime("%Y-%m-%d")
            
            # Check if photo with this date already exists
            photo_filename = f"{current_date}.jpg"
            photo_path = os.path.join(person_dir, photo_filename)
            
            print(f"[INFO] Photo filename: {photo_filename}")
            print(f"[INFO] Full photo path: {photo_path}")
            print(f"[DEBUG] Photo path exists: {os.path.exists(photo_path)}")
            
            # If file exists, add time to make it unique
            if os.path.exists(photo_path):
                print(f"[INFO] File already exists, adding timestamp")
                current_datetime = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                photo_filename = f"{current_datetime}.jpg"
                photo_path = os.path.join(person_dir, photo_filename)
                print(f"[INFO] New filename: {photo_filename}")
            
            # Windows test mode - create dummy file
            if current_platform == "Windows" and os.environ.get('SKIN_PHOTO_TEST'):
                print(f"[TEST MODE] Creating test file...")
                try:
                    # Create a simple test file
                    with open(photo_path, 'w') as f:
                        f.write(f"Test photo for {person_name} on {current_date}\n")
                    
                    # Verify file was created
                    if os.path.exists(photo_path):
                        file_size = os.path.getsize(photo_path)
                        print(f"✅ Test file created: {photo_path}")
                        print(f"   File size: {file_size} bytes")
                        self.photo_saved_this_session = True
                        self.last_photo_time = time.time()
                        return True
                    else:
                        print(f"[ERROR] Test file not created")
                        return False
                except Exception as e:
                    print(f"[ERROR] Failed to create test file: {e}")
                    import traceback
                    traceback.print_exc()
                    return False
            
            # CRITICAL: Stop Picamera2 before using rpicam-still
            print(f"[INFO] Stopping Picamera2 to free camera for rpicam-still...")
            camera_was_running = False
            if hasattr(self, 'camera') and self.camera is not None:
                try:
                    # First try to stop gracefully
                    self.camera.stop()
                    camera_was_running = True
                    print(f"[INFO] Picamera2 stopped successfully")
                    
                    # Give camera time to fully release
                    time.sleep(3.0)  # Increased wait time
                    
                    # Force close the camera object
                    try:
                        self.camera.close()
                        print(f"[INFO] Picamera2 closed completely")
                    except Exception as e:
                        print(f"[WARNING] Failed to close Picamera2: {e}")
                    
                    # Additional check - kill any remaining camera processes
                    try:
                        subprocess.run(["pkill", "-f", "rpicam"], capture_output=True)
                        subprocess.run(["pkill", "-f", "libcamera"], capture_output=True)
                        subprocess.run(["pkill", "-f", "picamera"], capture_output=True)
                        time.sleep(1.0)  # Wait for processes to die
                        print(f"[INFO] Killed any remaining camera processes")
                    except Exception as e:
                        print(f"[WARNING] Failed to kill camera processes: {e}")
                    
                    # Reset camera object to None to ensure it's completely released
                    self.camera = None
                    print(f"[INFO] Camera object reset to None")
                        
                except Exception as e:
                    print(f"[WARNING] Failed to stop Picamera2: {e}")
                    camera_was_running = False
            
            # Use rpicam-still for perfect color accuracy (NO BLUE/PURPLE ISSUES!)
            print(f"[INFO] Using rpicam-still for perfect color photo capture...")
            print(f"[DEBUG] Target photo path: {photo_path}")
            print(f"[DEBUG] Person directory exists: {os.path.exists(person_dir)}")
            
            try:
                # Check if rpicam-still is available
                try:
                    result_check = subprocess.run(["which", "rpicam-still"], capture_output=True, text=True)
                    if result_check.returncode != 0:
                        print(f"[WARNING] rpicam-still not found, trying libcamera-still")
                        raise Exception("rpicam-still not available")
                except Exception as e:
                    print(f"[WARNING] rpicam-still check failed: {e}")
                    raise Exception("rpicam-still not available")
                
                # Now camera should be free for rpicam-still
                print(f"[INFO] Camera is now free, using rpicam-still...")
                
                # Use rpicam-still with normal camera settings
                cmd = [
                    "rpicam-still",
                    "-o", photo_path,
                    "--width", "1080",
                    "--height", "1080",
                    "-t", "3000",  # 3 second timeout
                    "--immediate",  # Capture immediately
                    "--awb", f"{SKIN_AWB}"
                ]
                # Only add manual gains if specified (let auto WB work naturally otherwise)
                if SKIN_AWB_GAINS and SKIN_AWB_GAINS.strip() and SKIN_AWB == "auto":
                    # Skip manual gains for auto WB - let it work naturally
                    pass
                elif SKIN_AWB_GAINS and SKIN_AWB_GAINS.strip():
                    cmd += ["--awbgains", f"{SKIN_AWB_GAINS}"]
                # Add desaturation only if requested
                if SKIN_DESATURATE:
                    cmd += ["--saturation", "0"]
                
                print(f"[INFO] Running rpicam command: {' '.join(cmd)}")
                print(f"[DEBUG] Working directory: {os.getcwd()}")
                print(f"[DEBUG] Target file: {photo_path}")
                print(f"[DEBUG] Parent directory exists: {os.path.exists(os.path.dirname(photo_path))}")
                
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
                
                print(f"[DEBUG] rpicam return code: {result.returncode}")
                print(f"[DEBUG] rpicam stdout: {result.stdout}")
                print(f"[DEBUG] rpicam stderr: {result.stderr}")
                print(f"[DEBUG] Photo file exists after capture: {os.path.exists(photo_path)}")
                
                # Check if file was created and has content
                if os.path.exists(photo_path):
                    file_size = os.path.getsize(photo_path)
                    print(f"[DEBUG] Photo file size: {file_size} bytes")
                    if file_size == 0:
                        print(f"[ERROR] Photo file is empty!")
                        os.remove(photo_path)  # Remove empty file
                
                # Camera is still running for face recognition
                print(f"[INFO] Camera remains active for face recognition")
                
                if result.returncode == 0 and os.path.exists(photo_path) and os.path.getsize(photo_path) > 0:
                    file_size = os.path.getsize(photo_path)
                    print(f"✅ Photo captured with rpicam-still!")
                    print(f"   Path: {photo_path}")
                    print(f"   Size: {file_size} bytes ({file_size/1024:.2f} KB)")
                    print(f"   Resolution: 1080x1080")
                    print(f"   Quality: Perfect color (no blue/purple issues)")
                    print(f"\n✅ SKIN PHOTO SAVED SUCCESSFULLY!")
                    print(f"   Person: {person_name}")
                    print(f"   Method: rpicam-still (perfect color)")
                    print(f"{'='*60}\n")
                    
                    self.photo_saved_this_session = True
                    self.last_photo_time = time.time()
                    
                    # Trigger skin analysis with the captured photo
                    self.trigger_skin_analysis(person_name, photo_path)
                    
                    # Restart Picamera2 for face recognition
                    if camera_was_running:
                        print(f"[INFO] Restarting Picamera2 for face recognition...")
                        try:
                            # Reinitialize camera since we set it to None
                            self.initialize_camera()
                            print(f"[INFO] Picamera2 restarted successfully")
                        except Exception as e:
                            print(f"[WARNING] Failed to restart Picamera2: {e}")
                    
                    return True
                else:
                    print(f"[WARNING] rpicam-still failed: {result.stderr}")
                    print(f"[INFO] Trying alternative rpicam-still with different color settings...")
                    
                    # Try alternative rpicam-still command with normal auto white balance
                    cmd_alt = [
                        "rpicam-still",
                        "-o", photo_path,
                        "--width", "1080",
                        "--height", "1080",
                        "-t", "3000",  # Longer timeout
                        "--immediate",
                        "--awb", "auto"  # Normal auto white balance for natural colors
                    ]
                    if SKIN_DESATURATE:
                        cmd_alt += ["--saturation", "0"]
                    
                    print(f"[INFO] Running alternative rpicam command: {' '.join(cmd_alt)}")
                    result_alt = subprocess.run(cmd_alt, capture_output=True, text=True, timeout=20)
                    
                    if result_alt.returncode == 0 and os.path.exists(photo_path) and os.path.getsize(photo_path) > 0:
                        file_size = os.path.getsize(photo_path)
                        print(f"✅ Photo captured with alternative rpicam-still!")
                        print(f"   Path: {photo_path}")
                        print(f"   Size: {file_size} bytes ({file_size/1024:.2f} KB)")
                        print(f"   Method: rpicam-still (alternative color settings)")
                        
                        self.photo_saved_this_session = True
                        self.last_photo_time = time.time()
                        self.trigger_skin_analysis(person_name, photo_path)
                        
                        # Restart Picamera2 for face recognition
                        if camera_was_running:
                            print(f"[INFO] Restarting Picamera2 for face recognition...")
                            try:
                                self.camera.start()
                                print(f"[INFO] Picamera2 restarted successfully")
                            except Exception as e:
                                print(f"[WARNING] Failed to restart Picamera2: {e}")
                        
                        return True
                    else:
                        print(f"[WARNING] Alternative rpicam-still also failed: {result_alt.stderr}")
                        print(f"[INFO] Trying third method: rpicam-still with raw capture...")
                        
                        # Third method: Use basic capture
                        cmd_raw = [
                            "rpicam-still",
                            "-o", photo_path,
                            "--width", "1080",
                            "--height", "1080",
                            "-t", "2000",
                            "--immediate"
                        ]
                        if SKIN_DESATURATE:
                            cmd_raw += ["--saturation", "0"]
                        
                        print(f"[INFO] Running basic capture command: {' '.join(cmd_raw)}")
                        result_raw = subprocess.run(cmd_raw, capture_output=True, text=True, timeout=15)
                        
                        if result_raw.returncode == 0 and os.path.exists(photo_path) and os.path.getsize(photo_path) > 0:
                            file_size = os.path.getsize(photo_path)
                            print(f"✅ Photo captured with basic method!")
                            print(f"   Path: {photo_path}")
                            print(f"   Size: {file_size} bytes ({file_size/1024:.2f} KB)")
                            print(f"   Method: rpicam-still (basic)")
                            
                            self.photo_saved_this_session = True
                            self.last_photo_time = time.time()
                            self.trigger_skin_analysis(person_name, photo_path)
                            
                            # Restart Picamera2 for face recognition
                            if camera_was_running:
                                print(f"[INFO] Restarting Picamera2 for face recognition...")
                                try:
                                    self.camera.start()
                                    print(f"[INFO] Picamera2 restarted successfully")
                                except Exception as e:
                                    print(f"[WARNING] Failed to restart Picamera2: {e}")
                            
                            return True
                        else:
                            print(f"[WARNING] Basic capture failed: {result_raw.stderr}")
                        
                        print(f"[WARNING] All rpicam-still methods failed")
                        raise Exception(f"All rpicam-still methods failed")
                    
            except Exception as e:
                print(f"[WARNING] rpicam-still method failed: {e}")
            
            # Fallback 4: Try manual color correction with ImageMagick
            try:
                print(f"[INFO] Trying manual color correction with ImageMagick...")
                
                # First capture with basic settings
                basic_cmd = [
                    "rpicam-still",
                    "-o", photo_path,
                    "--width", "1080",
                    "--height", "1080",
                    "-t", "2000",
                    "--immediate",
                    "--awb", "auto"
                ]
                if SKIN_DESATURATE:
                    basic_cmd += ["--saturation", "0"]
                
                result_basic = subprocess.run(basic_cmd, capture_output=True, text=True, timeout=10)
                
                if result_basic.returncode == 0 and os.path.exists(photo_path) and os.path.getsize(photo_path) > 0:
                    # Apply desaturation/grayscale if requested, otherwise keep photo as-is (normal camera)
                    if SKIN_DESATURATE:
                        temp_path = photo_path.replace('.jpg', '_temp.jpg')
                        convert_cmd = [
                            "convert", photo_path,
                            "-colorspace", "Gray",
                            temp_path
                        ]
                        print(f"[INFO] Applying grayscale conversion...")
                        result_convert = subprocess.run(convert_cmd, capture_output=True, text=True, timeout=10)
                        
                        if result_convert.returncode == 0 and os.path.exists(temp_path) and os.path.getsize(temp_path) > 0:
                            os.replace(temp_path, photo_path)
                            file_size = os.path.getsize(photo_path)
                            print(f"✅ Photo captured with grayscale conversion!")
                            print(f"   Path: {photo_path}")
                            print(f"   Size: {file_size} bytes ({file_size/1024:.2f} KB)")
                        else:
                            print(f"[WARNING] ImageMagick grayscale conversion failed")
                            if os.path.exists(temp_path):
                                os.remove(temp_path)
                            # Use original photo anyway
                    else:
                        # Normal camera - use photo as-is without processing
                        file_size = os.path.getsize(photo_path)
                        print(f"✅ Photo captured with normal camera settings!")
                        print(f"   Path: {photo_path}")
                        print(f"   Size: {file_size} bytes ({file_size/1024:.2f} KB)")
                    
                    file_size = os.path.getsize(photo_path)
                    print(f"   Method: rpicam-still (normal camera)")
                    
                    self.photo_saved_this_session = True
                    self.last_photo_time = time.time()
                    self.trigger_skin_analysis(person_name, photo_path)
                    
                    # Restart Picamera2 for face recognition
                    if camera_was_running:
                        print(f"[INFO] Restarting Picamera2 for face recognition...")
                        try:
                            self.camera.start()
                            print(f"[INFO] Picamera2 restarted successfully")
                        except Exception as e:
                            print(f"[WARNING] Failed to restart Picamera2: {e}")
                    
                    return True
                else:
                    print(f"[WARNING] Basic rpicam-still failed: {result_basic.stderr}")
                    
            except Exception as e:
                print(f"[WARNING] ImageMagick method failed: {e}")
            
            # Final fallback: Try rpicam-still with basic settings
            print(f"[INFO] Final fallback: Trying rpicam-still with basic settings...")
            try:
                basic_cmd = [
                    "rpicam-still",
                    "-o", photo_path,
                    "--width", "1080",
                    "--height", "1080",
                    "-t", "3000",  # 3 second timeout
                    "--immediate",
                    "--awb", "auto"  # Normal auto white balance
                ]
                if SKIN_DESATURATE:
                    basic_cmd += ["--saturation", "0"]
                
                print(f"[INFO] Running basic rpicam command: {' '.join(basic_cmd)}")
                result = subprocess.run(basic_cmd, capture_output=True, text=True, timeout=15)
                
                if result.returncode == 0 and os.path.exists(photo_path) and os.path.getsize(photo_path) > 0:
                    file_size = os.path.getsize(photo_path)
                    print(f"✅ Photo captured with basic rpicam-still!")
                    print(f"   Path: {photo_path}")
                    print(f"   Size: {file_size} bytes ({file_size/1024:.2f} KB)")
                    print(f"   Method: Basic rpicam-still")
                    
                    self.photo_saved_this_session = True
                    self.last_photo_time = time.time()
                    self.trigger_skin_analysis(person_name, photo_path)
                    
                    # Restart Picamera2 for face recognition
                    if camera_was_running:
                        print(f"[INFO] Restarting Picamera2 for face recognition...")
                        try:
                            # Reinitialize camera since we set it to None
                            self.initialize_camera()
                            print(f"[INFO] Picamera2 restarted successfully")
                        except Exception as e:
                            print(f"[WARNING] Failed to restart Picamera2: {e}")
                    
                    return True
                else:
                    print(f"[WARNING] Basic rpicam-still failed: {result.stderr}")
                    
            except Exception as e:
                print(f"[WARNING] Basic rpicam-still method failed: {e}")
            
            # All methods failed - restart Picamera2 anyway
            print(f"\n[ERROR] All rpicam-still methods failed!")
            print(f"Tried: rpicam-still with color correction, ImageMagick correction, basic rpicam-still")
            print(f"Camera hardware may not be properly connected or enabled")
            
            # Restart Picamera2 for face recognition even if photo failed
            if camera_was_running:
                print(f"[INFO] Restarting Picamera2 for face recognition...")
                try:
                    self.camera.start()
                    print(f"[INFO] Picamera2 restarted successfully")
                except Exception as e:
                    print(f"[WARNING] Failed to restart Picamera2: {e}")
            
            return False
        
        except Exception as e:
            # Overall error handler
            print(f"\n[ERROR] Unexpected error in save_skin_photo: {e}")
            import traceback
            traceback.print_exc()
            print(f"{'='*60}\n")
            return False

    def trigger_skin_analysis(self, person_name, photo_path):
        """Trigger skin analysis by writing a signal file with photo path"""
        try:
            analysis_trigger_file = f"/tmp/skin_analysis_trigger_{person_name}.json"
            trigger_data = {
                "person": person_name,
                "photo_path": photo_path,
                "timestamp": datetime.now().isoformat(),
                "triggered": True
            }
            
            with open(analysis_trigger_file, 'w') as f:
                json.dump(trigger_data, f, indent=2)
            
            print(f"[INFO] Skin analysis triggered for {person_name}")
            print(f"   Photo path: {photo_path}")
            
        except Exception as e:
            print(f"[WARNING] Failed to trigger skin analysis: {e}")

    def recognize_face_with_camera(self):
        """Ultra-fast face recognition with camera reuse - OPTIMIZED FOR SPEED"""
        try:
            # Check if we're on Windows (simulation mode)
            if platform.system() == "Windows":
                import random
                if self.label_names and len(self.label_names) > 0 and self.label_names[0] != "Unknown":
                    known_user = random.choice(self.label_names)
                    # Async photo save for Windows
                    if self.current_person != known_user:
                        self.photo_saved_this_session = False
                    import threading
                    threading.Thread(target=lambda: self.save_skin_photo(known_user), daemon=True).start()
                    if self.relay_available and not self.lights_on:
                        self.turn_on_lights()
                    return known_user
                else:
                    guest_name = self.handle_unknown_person()
                    if self.current_person != guest_name:
                        self.photo_saved_this_session = False
                    import threading
                    threading.Thread(target=lambda: self.save_skin_photo(guest_name), daemon=True).start()
                    return guest_name
            
            # Initialize camera if not already done
            if self.camera is None:
                self.initialize_camera()
                if self.camera is None:
                    return None
            
            # Single fast attempt with optimized parameters
            try:
                # Instant cancel if user moved away
                live_distance = self.get_distance()
                if live_distance > PROXIMITY_THRESHOLD:
                    print(f"[INFO] User moved away during recognition ({live_distance:.1f}cm > {PROXIMITY_THRESHOLD}cm)")
                    return None

                # Capture frame - FAST
                try:
                    frame_rgb = self.camera.capture_array()
                    if frame_rgb is None or frame_rgb.size == 0:
                        print("[WARNING] Camera capture returned empty frame")
                        return None
                except Exception as e:
                    print(f"[ERROR] Camera capture failed: {e}")
                    # Try to reinitialize camera
                    self.camera = None
                    self.initialize_camera()
                    return None
                
                # Convert RGB to BGR for OpenCV processing
                frame = cv2.cvtColor(frame_rgb, cv2.COLOR_RGB2BGR)
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                
                # ULTRA-OPTIMIZED face detection - maximum speed
                faces = self.face_cascade.detectMultiScale(
                    gray, 
                    scaleFactor=1.1,      # Balanced for speed/accuracy
                    minNeighbors=2,       # Reduced from 3 for speed
                    minSize=(60, 60),     # Reduced from 80x80 to detect smaller faces
                    maxSize=(400, 400),   # Increased max size to detect larger faces
                    flags=cv2.CASCADE_SCALE_IMAGE | cv2.CASCADE_DO_CANNY_PRUNING  # Additional speed optimization
                )

                print(f"[DEBUG] Face detection found {len(faces)} face(s)")

                if len(faces) > 0:
                    if self.recognizer:
                        # Process the largest face (most likely to be the person)
                        largest_face = max(faces, key=lambda face: face[2] * face[3])
                        x, y, w, h = largest_face
                        
                        # FAST face processing - resize and equalize in one go
                        face_img = cv2.resize(gray[y:y+h, x:x+w], (100, 100))
                        face_img = cv2.equalizeHist(face_img)
                        
                        # Recognition - FAST
                        label, confidence = self.recognizer.predict(face_img)
                        name = self.label_map.get(label, "Unknown")
                        confidence_percent = self.map_lbph_confidence_to_percent(confidence)
                        self.current_confidence = confidence_percent
                        
                        print(f"[DEBUG] Recognition result: label={label}, name={name}, confidence={confidence:.2f}, confidence_percent={confidence_percent:.1f}%")
                        print(f"[DEBUG] Label in label_map: {label in self.label_map}, Name in label_names: {name in self.label_names if name != 'Unknown' else False}")
                        
                        # Check if this is a trained face (in label_map)
                        # IMPORTANT: Even if label exists, we must verify confidence is good
                        is_trained_face = (name != "Unknown" and name in self.label_names and label in self.label_map)
                        
                        # Additional safety check: if confidence is very high (> 100), it's likely a false positive
                        # even if the label matches a trained face
                        if is_trained_face and confidence > 100:
                            print(f"[WARNING] Label {label} ({name}) returned but confidence {confidence:.2f} is too high - likely false positive")
                            is_trained_face = False  # Treat as unknown
                        
                        # IMPORTANT: Even if label is in label_map, we need to verify confidence is actually good
                        # LBPH confidence: lower is better (0 = perfect match, higher = worse match)
                        # If confidence is too high (> 100), it's likely a false positive even if label matches
                        
                        if is_trained_face:
                            # This is a trained face - but we need STRICT confidence check to prevent false positives
                            # Accept ONLY if BOTH conditions are met:
                            # 1. confidence < 90 (good match - lower is better)
                            # 2. confidence_percent > 60 (at least 60% match)
                            # This prevents guests from being recognized as trained faces
                            
                            if confidence < 90 and confidence_percent > 60:
                                print(f"✅ Recognized trained face: {name} (confidence: {confidence:.2f}, {confidence_percent:.0f}%)")
                                
                                # Prefer latest saved skin photo for UI (instant display); fall back to live frame
                                if not self.copy_latest_skin_photo_to_recognition(name):
                                    self._save_recognition_image_from_frame(frame, x, y, w, h, name)
                                
                                # Reset photo flag for this person if it's a new recognition
                                if self.current_person != name:
                                    self.photo_saved_this_session = False
                                
                                # ASYNC: Save high-resolution skin photo in background (DON'T BLOCK!)
                                import threading
                                threading.Thread(
                                    target=self._async_save_skin_photo_and_trigger,
                                    args=(name,),
                                    daemon=True
                                ).start()
                                
                                # Sticky identity
                                self.last_recognized_name = name
                                self.last_recognized_time = time.time()
                                self.unknown_attempts = 0
                                
                                # Turn on lights when a trained face is recognized
                                if self.relay_available and not self.lights_on:
                                    self.turn_on_lights()
                                
                                return name
                            else:
                                # Trained face label returned but confidence is too low - likely a FALSE POSITIVE
                                # This means someone else (guest) is being matched to a trained face incorrectly
                                print(f"[WARNING] ⚠️ False positive detected: label={label} maps to '{name}' but confidence is too low ({confidence:.2f}, {confidence_percent:.0f}%)")
                                print(f"[WARNING] This is likely a guest, not {name}. Treating as unknown.")
                                
                                # Use sticky identity ONLY if:
                                # 1. Last recognized was this same person
                                # 2. Very recent (within 5 seconds, not 10)
                                # 3. Confidence is not terrible (at least < 110)
                                now_ts = time.time()
                                if (self.last_recognized_name == name and 
                                    (now_ts - self.last_recognized_time) < 5.0 and
                                    confidence < 110):
                                    print(f"[INFO] Using sticky identity for {name} (last recognized {now_ts - self.last_recognized_time:.1f}s ago, confidence acceptable)")
                                    return name
                                else:
                                    # Confidence is too low or too much time passed - treat as guest
                                    print(f"[INFO] Confidence too low or sticky expired - treating as guest")
                                    # Don't retry - go straight to guest handling
                                    self.unknown_attempts = 2  # Set to 2 so it goes to guest handling
                        else:
                            # Not a trained face OR label returned but not in label_map - this is truly unknown
                            print(f"[INFO] Unknown face detected (label={label}, name={name}, confidence: {confidence:.2f}, {confidence_percent:.0f}%)")
                            
                            # Clear sticky identity for unknown faces
                            self.last_recognized_name = None
                            self.last_recognized_time = 0
                            
                            self.unknown_attempts += 1
                            if self.unknown_attempts < 2:
                                # Allow one retry in case it's a trained face with bad angle/lighting
                                return None

                            # Handle unknown person as guest
                            guest_name = self.handle_unknown_person()
                            
                            # Prefer latest skin photo if any; fall back to live frame
                            if not self.copy_latest_skin_photo_to_recognition(guest_name):
                                self._save_recognition_image_from_frame(frame, x, y, w, h, guest_name)
                            
                            # Reset photo flag for guest
                            if self.current_person != guest_name:
                                self.photo_saved_this_session = False
                            
                            # ASYNC: Save photo for guest in background
                            import threading
                            threading.Thread(
                                target=self._async_save_skin_photo_and_trigger,
                                args=(guest_name,),
                                daemon=True
                            ).start()
                            
                            return guest_name
                    else:
                        # No recognizer available - treat as unknown face (guest)
                        largest_face = max(faces, key=lambda face: face[2] * face[3])
                        x, y, w, h = largest_face
                        
                        # Prefer sticky identity if very recent
                        now_ts = time.time()
                        if self.last_recognized_name and (now_ts - self.last_recognized_time) < 8.0:
                            return self.last_recognized_name
                        
                        guest_name = self.handle_unknown_person()
                        
                        # Prefer latest skin photo if any; fall back to live frame
                        if not self.copy_latest_skin_photo_to_recognition(guest_name):
                            self._save_recognition_image_from_frame(frame, x, y, w, h, guest_name)
                        
                        # Reset photo flag for guest
                        if self.current_person != guest_name:
                            self.photo_saved_this_session = False
                        
                        # ASYNC: Save photo for guest in background
                        import threading
                        threading.Thread(
                            target=self._async_save_skin_photo_and_trigger,
                            args=(guest_name,),
                            daemon=True
                        ).start()
                        
                        return guest_name
                else:
                    # No faces detected - this is not an error, just no face in frame
                    print(f"[INFO] No faces detected in frame (attempt {self.unknown_attempts + 1})")
                    return None
                    
            except Exception as e:
                print(f"[ERROR] Face recognition error: {e}")
                import traceback
                traceback.print_exc()
                # Don't return None on error - try to recover
                # Check if camera is still working
                try:
                    if self.camera is not None:
                        test_frame = self.camera.capture_array()
                        if test_frame is None or test_frame.size == 0:
                            print("[WARNING] Camera appears broken, will reinitialize on next attempt")
                            self.camera = None
                except:
                    print("[WARNING] Camera test failed, will reinitialize on next attempt")
                    self.camera = None
                return None
            
            # This should not be reached, but just in case
            print("[WARNING] Face recognition reached end without returning")
            return None
            
        except Exception as e:
            print(f"[ERROR] Critical error in face recognition: {e}")
            import traceback
            traceback.print_exc()
            return None

    def update_status_file(self):
        """Update the status file for MagicMirror²"""
        # Determine current status based on distance and recognition state
        # IMPORTANT: Check if close first, even if timeout is active (person might have returned)
        if self.current_distance <= PROXIMITY_THRESHOLD:
            # Close to sensor - check recognition state
            if self.current_person and self.current_person != "Unknown":
                # Face recognized - show personal data
                status_type = "recognized"
                self.is_active = True
            elif not self.face_recognition_attempted:
                # Close to sensor but haven't tried face recognition yet - show "scanning face"
                status_type = "detecting"
                self.is_active = True
            elif self.face_recognition_attempted and not self.current_person:
                # Close to sensor but face recognition failed - show "scanning face" again
                status_type = "detecting"
                self.is_active = True
            else:
                # Default: detecting if active, otherwise waiting
                status_type = "detecting" if self.is_active else "waiting"
        elif self.current_distance > PROXIMITY_THRESHOLD:
            # Far from sensor - person has moved away
            # Always set active to False when away (regardless of timeout)
            # Note: Don't modify self.current_person here - it's cleared in main loop
            self.is_active = False
            
            if self.shutdown_timer is not None:
                # In timeout countdown: show waiting status
                status_type = "waiting"
            else:
                # Just stepped away: show waiting status
                status_type = "waiting"
        
        # Check if current person is a guest
        is_guest = False
        if self.current_person:
            # Only log guest checking when person changes
            current_person_key = self.current_person
            if not hasattr(self, 'last_checked_person') or self.last_checked_person != current_person_key:
                print(f"[DEBUG] Checking guest status for: {self.current_person}")
                self.last_checked_person = current_person_key
            
            # Check if person is in known_guests dictionary (proper guest detection)
            if self.current_person in self.known_guests and self.known_guests[self.current_person].get('is_guest', False):
                is_guest = True
            # Also check if name starts with "Зочин" as fallback
            elif self.current_person.startswith("Зочин"):
                is_guest = True
            # If person is in label_names (trained faces), they are NOT a guest
            elif self.current_person in self.label_names:
                is_guest = False
            else:
                is_guest = False
        
        status = {
            "distance": self.current_distance,
            "person": self.current_person,
            "active": self.is_active,
            "status": status_type,
            "is_guest": is_guest,
            "confidence": self.current_confidence,
            "recognition_image": self.recognition_image_path if self.recognition_image_path else None,
            "log_messages": self.log_messages[-self.max_log_messages:],  # Last 5 messages
            "timestamp": datetime.now().isoformat()
        }
        
        # Debug: Always log when person is recognized and image should be present
        if self.current_person and self.current_person != "Unknown":
            print(f"[DEBUG] Status file write - person={self.current_person}, recognition_image={status['recognition_image']}, self.recognition_image_path={self.recognition_image_path}")
        
        # Only log debug status when it actually changes significantly
        status_key = (self.current_person, status_type, self.current_distance <= PROXIMITY_THRESHOLD, self.recognition_image_path)
        if not hasattr(self, 'last_status_key') or self.last_status_key != status_key:
            print(f"[DEBUG] Final status: person={self.current_person}, is_guest={is_guest}, status={status_type}, confidence={self.current_confidence}%, image={self.recognition_image_path}, distance={self.current_distance:.1f}cm")
            self.last_status_key = status_key
        
        try:
            # Write to temporary file first, then rename to avoid corruption
            temp_file = STATUS_FILE + ".tmp"
            with open(temp_file, 'w') as f:
                json.dump(status, f, separators=(",", ":"))  # compact for faster writes
            # Atomic rename to avoid partial reads
            os.rename(temp_file, STATUS_FILE)
            # Only print status updates when they change significantly (key fields only)
            status_hash_key = (
                status.get("person"),
                status.get("status"),
                status.get("active"),
                round(status.get("distance", 0))  # Round distance to reduce noise
            )
            if not hasattr(self, 'last_printed_status_hash') or self.last_printed_status_hash != status_hash_key:
                print(f"Status updated: person={status['person']}, status={status['status']}, active={status['active']}, distance={status['distance']:.1f}cm")
                self.last_printed_status_hash = status_hash_key
        except Exception as e:
            print(f"Error writing status file: {e}")

    def turn_on_lights(self):
        """Turn on the relay-controlled lights"""
        if not self.relay_available:
            print("⚠️  Relay not available - cannot control lights")
            return False
        
        try:
            # Turn on relay (LOW = relay ON for normally-closed relay)
            GPIO.output(RELAY_PIN, GPIO.LOW)
            self.lights_on = True
            self.add_log_message("Гэрэл асаж байна...")
            print("💡 Lights turned ON")
            return True
        except Exception as e:
            print(f"❌ Error turning on lights: {e}")
            return False

    def turn_off_lights(self):
        """Turn off the relay-controlled lights"""
        if not self.relay_available:
            print("⚠️  Relay not available - cannot control lights")
            return False
        
        try:
            # Turn off relay (HIGH = relay OFF for normally-closed relay)
            GPIO.output(RELAY_PIN, GPIO.HIGH)
            self.lights_on = False
            self.add_log_message("Гэрэл унтарч байна...")
            print("🌙 Lights turned OFF")
            return True
        except Exception as e:
            print(f"❌ Error turning off lights: {e}")
            return False

    def control_lights_based_on_proximity(self, distance):
        """Control lights based on proximity detection - stable control to prevent flickering"""
        if not self.relay_available:
            return
        
        # Ignore invalid/noisy readings
        if distance >= 400 or distance == 999:
            return
        
        # Stable relay control constants - quicker response but still debounced
        LIGHTS_ON_STABLE_THRESHOLD = 1  # Turn on after first stable detection
        LIGHTS_OFF_STABLE_THRESHOLD = 3  # Shorter delay to turn off
        LIGHTS_OFF_BUFFER = 6  # Smaller buffer for faster off response
        
        # Debounce: keep short to speed up visual response without chatter
        MIN_ON_SECONDS = 0.2  # Minimum time between turning on
        MIN_OFF_SECONDS = 1.0  # Minimum time between turning off
        now = time.time()

        # Global block to avoid re-toggling too soon - increased delay
        if now < self.relay_block_until:
            return
        
        # IMPORTANT: If person is close (within threshold) and lights are already on, keep them on
        # This prevents flickering when status changes but person is still present
        if distance <= self.effective_proximity_threshold and self.lights_on:
            # Person is close and lights are on - keep them on, reset counters to maintain state
            self.lights_stable_count = LIGHTS_ON_STABLE_THRESHOLD
            self.lights_off_stable_count = 0
            return  # Skip further processing to prevent any toggling

        # Schmitt-trigger style control with maintain-on buffer zone
        threshold_on = self.effective_proximity_threshold
        threshold_off = self.effective_proximity_threshold + LIGHTS_OFF_BUFFER
        
        # Check if lights should be ON (within threshold)
        if distance <= threshold_on:
            # Person is close - increment stable count to turn on lights
            self.lights_stable_count += 1
            self.lights_off_stable_count = 0  # Reset off counter
            
            # Turn on lights when detected (with stability requirement)
            if self.lights_stable_count >= LIGHTS_ON_STABLE_THRESHOLD and not self.lights_on:
                # Check debounce time
                time_since_last_change = now - self.last_light_change_time
                if time_since_last_change >= MIN_ON_SECONDS:
                    if self.turn_on_lights():
                        self.last_light_change_time = now
                        self.relay_block_until = now + 2.0  # Block for 2 seconds to prevent rapid toggling
                        self.lights_stable_count = 0  # Reset counter after action
                        print(f"💡 Lights ON - Proximity detected at {distance:.1f}cm")
        else:
            # Check if lights should be OFF (beyond threshold + buffer)
            if distance > threshold_off:
                self.lights_off_stable_count += 1
                self.lights_stable_count = 0  # Reset on counter
                
                # Turn off lights if stable for required readings and currently on
                if self.lights_off_stable_count >= LIGHTS_OFF_STABLE_THRESHOLD and self.lights_on:
                    # Check debounce time
                    time_since_last_change = now - self.last_light_change_time
                    if time_since_last_change >= MIN_OFF_SECONDS:
                        if self.turn_off_lights():
                            self.last_light_change_time = now
                            self.relay_block_until = now + 2.0  # Block for 2 seconds to prevent rapid toggling
                            self.lights_off_stable_count = 0  # Reset counter after action
            else:
                # In the buffer zone (between threshold and threshold+buffer)
                # Maintain current state but allow gradual state change
                # Don't reset counters aggressively - allow accumulation
                if not self.lights_on:
                    # Moving away but still in buffer - reset off counter to prevent premature off
                    self.lights_off_stable_count = max(0, self.lights_off_stable_count - 1)
                else:
                    # Moving closer but still in buffer - reset on counter to prevent premature on
                    self.lights_stable_count = max(0, self.lights_stable_count - 1)

    def run(self):
        """Main loop with improved proximity detection and state management"""
        print("Starting face recognition system...")
        print(f"Proximity threshold: {PROXIMITY_THRESHOLD}cm")
        print(f"Timeout delay: {TIMEOUT_DELAY}s")
        print(f"Relay control: ON IMMEDIATELY when detected at <{PROXIMITY_THRESHOLD}cm (BEFORE recognition), OFF at >{PROXIMITY_THRESHOLD + 8}cm")
        print("   Response time: ~0.3s turn on, ~1.5s turn off")
        print("Press Ctrl+C to stop")
        
        # Add distance smoothing for more stable readings
        distance_history = []
        HISTORY_SIZE = 5  # Larger window for smoother response, filter out noise
        last_status_update = 0
        STATUS_UPDATE_INTERVAL = 0.5  # Update 2x/sec - reduces file I/O and relay flicker
        
        # State tracking variables
        proximity_stable_count = 0
        PROXIMITY_STABLE_THRESHOLD = 1  # Trigger immediately when within threshold
        away_stable_count = 0
        AWAY_STABLE_THRESHOLD = 2  # Faster shutdown when user walks away
        previous_smoothed_distance = None
        
        try:
            while True:
                # Get distance from ultrasonic sensor
                distance = self.get_distance()
                
                # Add to history for smoothing
                distance_history.append(distance)
                if len(distance_history) > HISTORY_SIZE:
                    distance_history.pop(0)
                
                # Calculate smoothed distance (median for better noise rejection, then average)
                valid_distances = [d for d in distance_history if d < 400 and d != 999]  # Filter out invalid readings
                if len(valid_distances) > 0:
                    valid_distances.sort()
                    median_distance = valid_distances[len(valid_distances) // 2]
                    # Use median as base, average only for fine-tuning
                    smoothed_distance = (median_distance * 0.7 + sum(valid_distances) / len(valid_distances) * 0.3)
                else:
                    smoothed_distance = distance if distance < 400 else 999
                self.current_distance = smoothed_distance

                # --- Baseline calibration phase (avoid triggering when nobody is near) ---
                # Collect a number of initial readings and treat them as "no person" baseline.
                # We will only start reacting when distance becomes clearly closer than this baseline.
                if not self.baseline_ready:
                    if smoothed_distance < 400 and smoothed_distance != 999:
                        self._baseline_samples.append(smoothed_distance)
                    # Use about ~20 samples for baseline (≈ 4–6 seconds depending on branch sleeps)
                    if len(self._baseline_samples) >= 20:
                        self._baseline_samples.sort()
                        mid = len(self._baseline_samples) // 2
                        self.baseline_distance = self._baseline_samples[mid]
                        # Use fixed threshold to avoid overshooting when baseline is close
                        self.effective_proximity_threshold = PROXIMITY_THRESHOLD
                        self.baseline_ready = True
                        print(
                            f"[INFO] Baseline distance calibrated at {self.baseline_distance:.1f}cm, "
                            f"effective proximity threshold set to {self.effective_proximity_threshold:.1f}cm"
                        )

                    # During baseline calibration, keep lights off and do not start recognition
                    if not self.baseline_ready:
                        if self.lights_on and self.relay_available:
                            self.turn_off_lights()
                        # Slow down a bit during calibration
                        time.sleep(0.3)
                        continue

                # Keep an updated effective threshold even after baseline (in case env changes)
                if self.baseline_ready and self.baseline_distance is not None:
                    # Keep threshold fixed at configured value for reliable triggering
                    self.effective_proximity_threshold = PROXIMITY_THRESHOLD
                
                # Control lights based on proximity
                self.control_lights_based_on_proximity(smoothed_distance)
                
                # Debug output every 50 iterations (reduced frequency for speed)
                if len(distance_history) % 50 == 0:
                    print(f"Distance: {smoothed_distance:.1f}cm, Person: {self.current_person}, Lights: {'ON' if self.lights_on else 'OFF'}")

                # Throttled ultrasonic log (max every 1s, only valid distances)
                now_ts = time.time()
                if smoothed_distance < 400 and smoothed_distance != 999:
                    if (now_ts - self._last_distance_log_time) > 1.0:
                        if self._last_distance_log_value is None or abs(smoothed_distance - self._last_distance_log_value) >= 3:
                            self.add_log_message(f"Мэдрэгч: {smoothed_distance:.0f}см")
                            self._last_distance_log_time = now_ts
                            self._last_distance_log_value = smoothed_distance
                
                # Check proximity with smoothed distance and calibrated threshold
                if smoothed_distance <= self.effective_proximity_threshold:
                    # Object detected within threshold
                    proximity_stable_count += 1
                    away_stable_count = 0  # Reset away counter
                    
                    # If person was away and now close again, reset stable time
                    if self.person_stable_start_time is None and self.is_active:
                        self.person_stable_start_time = time.time()
                        print(f"[INFO] Person returned - resetting stable time for recognition")

                    # Immediately publish 'detecting' status so UI shows scanning text
                    # even before full activation kicks in
                    if not self.is_active and (time.time() - last_status_update > STATUS_UPDATE_INTERVAL):
                        self.update_status_file()
                        last_status_update = time.time()

                    # Ensure we have a baseline detection time for timing-based checks
                    if self.last_detection_time is None:
                        self.last_detection_time = time.time()
                    
                    # Only activate if proximity is stable
                    if proximity_stable_count >= PROXIMITY_STABLE_THRESHOLD and not self.is_active:
                        print(f"🎯 Object detected at {smoothed_distance:.1f}cm - activating face recognition")
                        self.add_log_message(f"Хүн илрэв ({smoothed_distance:.0f}см зайд)")
                        self.last_detection_time = time.time()
                        self.person_stable_start_time = time.time()  # Start tracking stable time
                        self.shutdown_timer = None
                        self.current_person = None  # Reset person
                        self.unknown_attempts = 0   # Reset unknown counter on new activation
                        self.current_confidence = 0  # Reset confidence
                        self.recognition_image_path = None  # Reset image
                        self.face_recognition_attempted = False
                        self.recognition_locked = False  # Reset lock on new activation
                        self.camera_opened = False
                        # Don't reset photo_saved_this_session here - only reset when new person detected
                        self.is_active = True
                        # Ensure relay turns on immediately when activation occurs
                        if self.relay_available and not self.lights_on:
                            self.turn_on_lights()
                        # Pre-warm camera for faster recognition
                        self.initialize_camera()
                        self.update_status_file()
                    
                    # Try face recognition when first activated
                    if self.is_active and self.current_person is None and not self.recognition_locked:
                        # Ensure detection time is set
                        if self.last_detection_time is None:
                            self.last_detection_time = time.time()
                        
                        # Initialize stable time tracking
                        if self.person_stable_start_time is None:
                            self.person_stable_start_time = time.time()
                        
                        # Wait for minimum stable time before attempting recognition (reduced to 0.5 second for faster response)
                        # This ensures person is properly positioned and not just passing by
                        time_since_stable = time.time() - self.person_stable_start_time
                        time_since_detection = time.time() - self.last_detection_time
                        
                        # Require both: minimum stable time AND minimum detection time (reduced thresholds)
                        if time_since_stable >= 0.5 and time_since_detection >= 0.3:
                            # Ensure camera is initialized and working before attempting recognition
                            if self.camera is None:
                                print("[INFO] Camera not initialized, initializing now...")
                                self.initialize_camera()
                                if self.camera is None:
                                    print("[WARNING] Camera initialization failed, will retry...")
                                    time.sleep(0.2)
                                    continue
                            
                            # Check if camera is actually working
                            try:
                                # Quick test capture to verify camera is working
                                test_frame = self.camera.capture_array()
                                if test_frame is None or test_frame.size == 0:
                                    print("[WARNING] Camera test capture failed, reinitializing...")
                                    self.camera = None
                                    self.initialize_camera()
                                    time.sleep(0.2)
                                    continue
                            except Exception as e:
                                print(f"[WARNING] Camera test failed: {e}, reinitializing...")
                                self.camera = None
                                self.initialize_camera()
                                time.sleep(0.2)
                                continue
                            
                            if not self.face_recognition_attempted:
                                self.add_log_message("Царай танилт эхэлж байна...")
                                self.face_recognition_attempted = True
                            
                            print(f"[INFO] Attempting face recognition (stable: {time_since_stable:.1f}s, detection: {time_since_detection:.1f}s)")
                            person = self.recognize_face_with_camera()
                            
                            if person and person != "Unknown":
                                # Check if person changed - if so, reset everything
                                person_changed = (self.current_person is not None and 
                                                 self.current_person != person)
                                
                                if person_changed:
                                    print(f"[INFO] ⚠️ Person changed from {self.current_person} to {person} - resetting state")
                                    # Clear old person's data completely
                                    self.photo_saved_this_session = False
                                    self.unknown_attempts = 0
                                    self.recognition_image_path = None
                                    # Clear any old recognition images
                                    try:
                                        script_dir = os.path.dirname(os.path.abspath(__file__))
                                        if os.path.basename(script_dir) == "MagicMirror-master" or os.path.exists(os.path.join(script_dir, "package.json")):
                                            project_root = script_dir
                                        else:
                                            project_root = os.path.dirname(script_dir)
                                        old_image = os.path.join(project_root, "modules", "facerecognition", "public", "recognition.jpg")
                                        if os.path.exists(old_image):
                                            os.remove(old_image)
                                            print(f"[INFO] Removed old recognition image for person change")
                                    except Exception as e:
                                        print(f"[WARNING] Failed to remove old image: {e}")
                                
                                self.add_log_message(f"Царай танигдлаа: {person}")
                                self.current_person = person
                                self.last_person_name = person  # Update last person
                                self.shutdown_timer = None
                                # Lock recognition only after SUCCESSFUL recognition
                                # But allow periodic re-verification (handled in main loop)
                                self.recognition_locked = True
                                
                                # Ensure lights are on for recognized trained face
                                if self.relay_available and not self.lights_on:
                                    print(f"💡 Ensuring lights are ON for recognized user: {person}")
                                    self.turn_on_lights()
                                
                                # Ensure image path is still set (it should be from recognize_face_with_camera)
                                if not self.recognition_image_path:
                                    # If image path is missing, try to find the file
                                    script_dir = os.path.dirname(os.path.abspath(__file__))
                                    if os.path.basename(script_dir) == "MagicMirror-master" or os.path.exists(os.path.join(script_dir, "package.json")):
                                        project_root = script_dir
                                    else:
                                        project_root = os.path.dirname(script_dir)
                                    image_file = os.path.join(project_root, "modules", "facerecognition", "public", "recognition.jpg")
                                    if os.path.exists(image_file):
                                        self.recognition_image_path = "/modules/facerecognition/public/recognition.jpg"
                                        print(f"[DEBUG] Found existing image file, setting path: {self.recognition_image_path}")
                                
                                # Update immediately with all data
                                self.update_status_file()
                                
                                # Single delayed update to refresh image after async save completes
                                import threading
                                def delayed_update():
                                    time.sleep(2.0)  # Wait for async skin photo to complete
                                    if self.current_person == person:
                                        self.copy_latest_skin_photo_to_recognition(person)
                                        self.update_status_file()
                                threading.Thread(target=delayed_update, daemon=True).start()
                            elif person is None:
                                # Recognition failed (no face detected or camera error) - allow retry
                                print(f"[INFO] Face recognition returned None - will retry (attempt {self.unknown_attempts + 1})")
                                # Don't lock recognition on failure - allow retries
                                # Reset attempt flag after a delay to allow retry
                                if self.unknown_attempts >= 3:
                                    # After 3 failed attempts, wait longer before retrying
                                    self.add_log_message("Царай танихгүй байна - дахин оролдоно...")
                                    self.face_recognition_attempted = False  # Allow retry
                                    self.unknown_attempts = 0  # Reset counter
                                    time.sleep(1.0)  # Wait before next attempt
                                else:
                                    self.unknown_attempts += 1
                                self.update_status_file()
                            else:
                                # Person is "Unknown" or guest - this is still a successful detection
                                self.add_log_message(f"Зочин танигдлаа: {person}")
                                self.current_person = person
                                self.last_person_name = person
                                self.shutdown_timer = None
                                # Lock recognition after guest detection too
                                self.recognition_locked = True
                                self.update_status_file()
                    
                    # If face already recognized, maintain the state and reset timeout
                    elif self.current_person is not None:
                        # Reset timeout timer since person is still present
                        self.shutdown_timer = None
                        
                        # Periodically re-verify the person is still the same (every 8 seconds)
                        # This prevents showing other people's faces if someone else approaches
                        current_time = time.time()
                        if not hasattr(self, 'last_verification_time'):
                            self.last_verification_time = 0
                        
                        # Re-verify every 8 seconds to ensure it's still the same person
                        # Only if recognition is locked (to avoid constant re-checking)
                        if self.recognition_locked and (current_time - self.last_verification_time) > 8.0:
                            self.last_verification_time = current_time
                            # Unlock recognition for a quick re-check
                            print(f"[INFO] Periodic verification - re-checking if {self.current_person} is still present")
                            self.recognition_locked = False
                            self.face_recognition_attempted = False
                            self.person_stable_start_time = time.time()  # Reset stable time
                        
                        # Check if distance changed significantly (might be a different person)
                        # If distance changes by more than 30cm while person is recognized, 
                        # it might indicate a person change - allow re-recognition
                        elif previous_smoothed_distance is not None and self.recognition_locked:
                            distance_change = abs(smoothed_distance - previous_smoothed_distance)
                            if distance_change > 30:
                                # Significant distance change - might be a new person
                                # Unlock recognition to allow re-check
                                print(f"[INFO] Significant distance change ({distance_change:.1f}cm) - unlocking recognition for re-check")
                                self.recognition_locked = False
                                self.face_recognition_attempted = False
                                self.person_stable_start_time = time.time()  # Reset stable time
                        
                        # Periodically update status
                        current_time = time.time()
                        if current_time - last_status_update > STATUS_UPDATE_INTERVAL:
                            # Quick check if image path needs recovery
                            if self.recognition_image_path is None and self.current_person:
                                script_dir = os.path.dirname(os.path.abspath(__file__))
                                if os.path.basename(script_dir) == "MagicMirror-master" or os.path.exists(os.path.join(script_dir, "package.json")):
                                    project_root = script_dir
                                else:
                                    project_root = os.path.dirname(script_dir)
                                image_file = os.path.join(project_root, "modules", "facerecognition", "public", "recognition.jpg")
                                if os.path.exists(image_file):
                                    self.recognition_image_path = "/modules/facerecognition/public/recognition.jpg"
                            self.update_status_file()
                            last_status_update = current_time
                        
                        # Update previous distance for next iteration
                        previous_smoothed_distance = smoothed_distance
                    
                    # Update status file regularly when active (if not already updated above)
                    current_time = time.time()
                    if current_time - last_status_update > STATUS_UPDATE_INTERVAL:
                        self.update_status_file()
                        last_status_update = current_time
                    
                    time.sleep(0.1)  # Check every 0.1 seconds when active (faster response)
                else:
                    # Object moved away - count consecutive away readings
                    away_stable_count += 1
                    proximity_stable_count = 0  # Reset proximity counter
                    # Reset stable time when person moves away
                    self.person_stable_start_time = None
                    
                    # Only deactivate if away for stable period
                    if away_stable_count >= AWAY_STABLE_THRESHOLD:
                        # Immediately clear active state and turn off lights when person moves away
                        if self.is_active or self.current_person is not None:
                            # Clear active state
                            if self.is_active:
                                self.is_active = False
                                print(f"🔴 Deactivated - person moved away ({smoothed_distance:.1f}cm)")
                            
                            # Turn off lights immediately when person moves away
                            if self.lights_on and self.relay_available:
                                print(f"🌙 Turning off lights - person moved away")
                                self.turn_off_lights()
                            
                            # Clear recognition state immediately (don't wait for timeout)
                            if self.current_person is not None:
                                print(f"👋 User {self.current_person} moved away - clearing state")
                                self.add_log_message("Мэдрэгчээс хүн холдсон")
                                # Clear person immediately - UI should show "waiting" instead of "recognizing"
                                self.current_person = None
                                self.current_confidence = 0
                                self.recognition_image_path = None
                                self.face_recognition_attempted = False
                                self.recognition_locked = False
                                # Reset person tracking for next detection
                                self.last_person_name = None
                                self.person_stable_start_time = None
                                # Reset photo flag when person leaves (next person can get new photo)
                                self.photo_saved_this_session = False
                            
                            # Start timeout timer for final cleanup
                            if self.shutdown_timer is None:
                                self.shutdown_timer = time.time()
                                print(f"⏰ Starting {TIMEOUT_DELAY}s timeout for final cleanup")
                            
                            # Immediately update status file to reflect cleared state
                            self.update_status_file()
                        elif self.shutdown_timer is None:
                            # No person recognized but was active - start timeout
                            self.shutdown_timer = time.time()
                            print(f"⏰ No face recognized, starting {TIMEOUT_DELAY}s timeout")
                            self.add_log_message("Хүний зай хол байна...")
                            # Reset recognition lock when user moves away (allows recognition next time)
                            if self.recognition_locked:
                                self.recognition_locked = False
                                print("🔓 Recognition lock reset - will try again when user returns")
                            # Reset person tracking for next detection
                            self.last_person_name = None
                            self.person_stable_start_time = None
                            # Reset photo flag when no person detected (next person can get new photo)
                            self.photo_saved_this_session = False
                            # Turn off lights if still on
                            if self.lights_on and self.relay_available:
                                print(f"🌙 Turning off lights - no person detected")
                                self.turn_off_lights()
                            # Update status immediately
                            self.update_status_file()
                    
                    # Check if timeout has elapsed
                    if self.shutdown_timer is not None:
                        elapsed = time.time() - self.shutdown_timer
                        if elapsed >= TIMEOUT_DELAY:
                            print(f"⏰ Timeout reached ({TIMEOUT_DELAY}s) - final cleanup")
                            self.add_log_message("Систем хүлээж байна...")
                            # Final cleanup - ensure all states are cleared
                            self.current_person = None
                            self.current_confidence = 0
                            self.recognition_image_path = None
                            self.is_active = False
                            self.face_recognition_attempted = False
                            self.camera_opened = False
                            self.shutdown_timer = None
                            self.recognition_locked = False  # Allow recognition next time
                            # Reset person tracking for next detection
                            self.last_person_name = None
                            self.person_stable_start_time = None
                            # Reset photo flag on timeout (next person can get new photo)
                            self.photo_saved_this_session = False
                            # Ensure lights are turned off on timeout (should already be off, but double-check)
                            if self.lights_on and self.relay_available:
                                try:
                                    self.turn_off_lights()
                                except Exception as e:
                                    print(f"[WARNING] Failed to turn off lights on timeout: {e}")
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
        if self.camera is not None:
            try:
                self.camera.close()
                print("[INFO] Camera closed")
            except Exception as e:
                print(f"[WARNING] Error closing camera: {e}")
        
        # Turn off lights before cleanup
        if self.relay_available and self.lights_on:
            try:
                self.turn_off_lights()
                print("[INFO] Lights turned off during cleanup")
            except Exception as e:
                print(f"[WARNING] Error turning off lights: {e}")
        
        GPIO.cleanup()
        print("Cleanup completed")

if __name__ == "__main__":
    system = FaceRecognitionSystem()
    system.run()
