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
TRIG_PIN = 23  # GPIO pin for TRIG
ECHO_PIN = 24  # GPIO pin for ECHO

# GPIO pin for 12V relay (single channel)
RELAY_PIN = 18  # GPIO pin for relay control

# Face recognition settings
STATUS_FILE = "/tmp/magicmirror_face_status.json"
PROXIMITY_THRESHOLD = 20  # cm
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
        
        # Log messages for display (Mongolian)
        self.log_messages = []  # Store last 5 log messages in Mongolian
        self.max_log_messages = 5  # Maximum number of log messages to keep
        
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
        """Initialize camera once and reuse it"""
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
                time.sleep(1)  # Let camera stabilize
                print("[INFO] Camera initialized successfully")
            except Exception as e:
                print(f"[ERROR] Camera initialization failed: {e}")
                self.camera = None

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
        """Ultra-fast face recognition with camera reuse"""
        try:
            print(f"[INFO] Object detected at {self.current_distance}cm. Starting recognition...")
            
            # Check if we're on Windows (simulation mode)
            if platform.system() == "Windows":
                print("[INFO] Windows detected - simulating face recognition")
                time.sleep(0.5)  # Reduced simulation delay
                
                # For Windows simulation, first check if we have known users
                if self.label_names and len(self.label_names) > 0 and self.label_names[0] != "Unknown":
                    # We have known users - simulate recognizing one of them
                    import random
                    known_user = random.choice(self.label_names)
                    print(f"[INFO] Windows simulation: Simulating recognition of known user: {known_user}")
                    
                    # Reset photo flag for Windows simulation
                    if self.current_person != known_user:
                        self.photo_saved_this_session = False
                        print(f"[INFO] Windows simulation mode, resetting photo flag for {known_user}")
                    
                    # Save photo even in Windows simulation mode
                    photo_saved = self.save_skin_photo(known_user)
                    if photo_saved:
                        # Get the photo path for the trigger
                        current_date = datetime.now().strftime("%Y-%m-%d")
                        photo_path = os.path.join(os.getcwd(), "Skin", known_user, f"{current_date}.jpg")
                        self.trigger_skin_analysis(known_user, photo_path)
                    
                    return known_user  # Return known user name for Windows simulation
                else:
                    # No known users - simulate unknown face as guest
                    print("[INFO] Windows simulation: No known users found, simulating guest")
                    guest_name = self.handle_unknown_person()
                    
                    # Reset photo flag for Windows simulation
                    if self.current_person != guest_name:
                        self.photo_saved_this_session = False
                        print(f"[INFO] Windows simulation mode, resetting photo flag for {guest_name}")
                    
                    # Save photo even in Windows simulation mode
                    photo_saved = self.save_skin_photo(guest_name)
                    if photo_saved:
                        # Get the photo path for the trigger
                        current_date = datetime.now().strftime("%Y-%m-%d")
                        photo_path = os.path.join(os.getcwd(), "Skin", guest_name, f"{current_date}.jpg")
                        self.trigger_skin_analysis(guest_name, photo_path)
                    
                    return guest_name  # Return guest name for Windows simulation
            
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
                    print(f"[INFO] Recognition cancelled - user moved away ({live_distance:.1f}cm)")
                    return None

                # Capture frame
                frame_rgb = self.camera.capture_array()
                # Convert RGB to BGR for OpenCV processing
                frame = cv2.cvtColor(frame_rgb, cv2.COLOR_RGB2BGR)
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                
                # Optimized face detection - faster parameters
                faces = self.face_cascade.detectMultiScale(
                    gray, 
                    scaleFactor=1.05,  # Faster than 1.1
                    minNeighbors=3,    # Faster than 4
                    minSize=(60, 60),  # Slightly larger minimum size
                    flags=cv2.CASCADE_SCALE_IMAGE
                )

                if len(faces) > 0:
                    print(f"[INFO] {len(faces)} face(s) detected")
                    if self.recognizer:
                        print(f"[DEBUG] Recognizer available, known faces: {self.label_names}")
                        # Process the largest face (most likely to be the person)
                        largest_face = max(faces, key=lambda face: face[2] * face[3])
                        x, y, w, h = largest_face
                        
                        face_img = gray[y:y+h, x:x+w]
                        face_img = cv2.resize(face_img, (100, 100))
                        
                        # Apply histogram equalization for better recognition
                        face_img = cv2.equalizeHist(face_img)
                        
                        label, confidence = self.recognizer.predict(face_img)
                        name = self.label_map.get(label, "Unknown")
                        
                        # Calculate confidence percentage (for LBPH: lower = better)
                        confidence_percent = self.map_lbph_confidence_to_percent(confidence)
                        self.current_confidence = confidence_percent
                        
                        print(f"[INFO] Recognized: {name} (Confidence: {confidence:.2f}, Percent: {confidence_percent:.1f}%)")
                        print(f"[DEBUG] Label: {label}, Label map: {self.label_map}")
                        print(f"[DEBUG] Setting current_confidence to: {confidence_percent}%")
                        
                        # Check if face is recognized with good confidence (lower=better)
                        # Threshold tuned to align with ~90%+ mapping for strong matches
                        if name != "Unknown" and confidence < 110:
                            print(f"✅ Face recognition successful: {name} (confidence: {confidence:.2f}, {confidence_percent:.1f}%)")
                            print(f"[DEBUG] Known user detected - NOT a guest")
                            
                            # Save recognition image using rpicam-still (same colors as skin photos)
                            try:
                                # Ensure static dir exists and save as a fixed name
                                # Get MagicMirror root directory (parent of this script's directory)
                                script_dir = os.path.dirname(os.path.abspath(__file__))
                                # If script is in root, use it; otherwise go up one level
                                if os.path.basename(script_dir) == "MagicMirror-master" or os.path.exists(os.path.join(script_dir, "package.json")):
                                    project_root = script_dir
                                else:
                                    # Go up one level to find MagicMirror root
                                    project_root = os.path.dirname(script_dir)
                                static_dir = os.path.join(project_root, "modules", "facerecognition", "public")
                                os.makedirs(static_dir, exist_ok=True)
                                file_fs_path = os.path.join(static_dir, "recognition.jpg")
                                print(f"[DEBUG] Recognition image will be saved to: {file_fs_path}")
                                print(f"[DEBUG] Recognition image URL will be: /facerecognition/public/recognition.jpg")
                                
                                # Try to capture with rpicam-still first (better quality)
                                # Only stop camera if rpicam-still is available and we're on Linux
                                camera_was_running = False
                                use_rpicam = False
                                
                                # Check if we should try rpicam-still
                                if platform.system() != "Windows":
                                    try:
                                        result_check = subprocess.run(["which", "rpicam-still"], capture_output=True, text=True, timeout=2)
                                        if result_check.returncode == 0:
                                            use_rpicam = True
                                    except:
                                        pass
                                
                                if use_rpicam:
                                    # Temporarily stop Picamera2 to free camera for rpicam-still
                                    if self.camera is not None:
                                        try:
                                            self.camera.stop()
                                            camera_was_running = True
                                            time.sleep(1.0)  # Give camera time to release
                                            print(f"[DEBUG] Camera stopped for rpicam-still")
                                        except Exception as e:
                                            print(f"[WARNING] Failed to stop camera: {e}")
                                            camera_was_running = False
                                
                                # Capture with rpicam-still or fallback to Picamera2
                                if use_rpicam:
                                    capture_success = self.capture_recognition_image_with_rpicam(file_fs_path)
                                else:
                                    # Use Picamera2 directly (no need to stop camera)
                                    capture_success = self.capture_recognition_image_with_picamera2(file_fs_path)
                                
                                if capture_success and os.path.exists(file_fs_path):
                                    # URL path for browser (MagicMirror node_helper registers /facerecognition/public route)
                                    self.recognition_image_path = "/facerecognition/public/recognition.jpg"
                                    self.add_log_message("Зураг хадгалж байна...")
                                    file_size = os.path.getsize(file_fs_path)
                                    print(f"[DEBUG] ✓ Saved recognition image: {file_fs_path} ({file_size} bytes)")
                                    print(f"[DEBUG] Recognition image path set to: {self.recognition_image_path}")
                                else:
                                    print(f"[ERROR] Recognition image capture failed completely")
                                    self.recognition_image_path = None
                                
                                # Restart Picamera2 if we stopped it for rpicam-still
                                if camera_was_running and self.camera is not None:
                                    try:
                                        self.camera.start()
                                        time.sleep(0.5)  # Let camera stabilize
                                        print(f"[DEBUG] Camera restarted after recognition image capture")
                                    except Exception as e:
                                        print(f"[WARNING] Failed to restart camera: {e}")
                                        self.initialize_camera()  # Try full reinitialize if restart fails
                                
                            except Exception as e:
                                print(f"[WARNING] Failed to save recognition image: {e}")
                                import traceback
                                traceback.print_exc()
                                self.recognition_image_path = None
                            
                            # Reset photo flag for this person if it's a new recognition
                            print(f"[DEBUG] Current person: {self.current_person}, Recognized person: {name}")
                            if self.current_person != name:
                                self.photo_saved_this_session = False
                                print(f"[INFO] New person detected in recognition, resetting photo flag")
                                print(f"[DEBUG] Photo flag reset to: {self.photo_saved_this_session}")
                            else:
                                print(f"[INFO] Same person recognized, checking photo flag: {self.photo_saved_this_session}")
                            
                            # Save high-resolution skin photo after successful recognition
                            photo_saved = self.save_skin_photo(name)
                            
                            # Trigger skin analysis if photo was saved
                            if photo_saved:
                                # Get the photo path for the trigger
                                current_date = datetime.now().strftime("%Y-%m-%d")
                                photo_path = os.path.join(os.getcwd(), "Skin", name, f"{current_date}.jpg")
                                self.trigger_skin_analysis(name, photo_path)
                            
                            # Sticky identity
                            self.last_recognized_name = name
                            self.last_recognized_time = time.time()
                            self.unknown_attempts = 0
                            
                            # CRITICAL: Verify image path is set before returning
                            if not self.recognition_image_path:
                                print(f"[WARNING] Image path is NOT set after recognition! Attempting to recover...")
                                # Try to recover - check if file exists
                                script_dir = os.path.dirname(os.path.abspath(__file__))
                                if os.path.basename(script_dir) == "MagicMirror-master" or os.path.exists(os.path.join(script_dir, "package.json")):
                                    project_root = script_dir
                                else:
                                    project_root = os.path.dirname(script_dir)
                                image_file = os.path.join(project_root, "modules", "facerecognition", "public", "recognition.jpg")
                                if os.path.exists(image_file):
                                    self.recognition_image_path = "/facerecognition/public/recognition.jpg"
                                    print(f"[DEBUG] Recovered image path: {self.recognition_image_path}")
                                else:
                                    print(f"[ERROR] Image file does not exist at: {image_file}")
                            else:
                                print(f"[DEBUG] Image path is correctly set: {self.recognition_image_path}")
                            
                            print(f"[DEBUG] Returning from recognize_face_with_camera: name={name}, image_path={self.recognition_image_path}")
                            return name
                        else:
                            # Face detected but not recognized (high confidence = bad match, or name is "Unknown")
                            print(f"[INFO] Face detected but not recognized (confidence: {confidence:.2f}, name: {name})")
                            print(f"[DEBUG] Confidence threshold check: name != 'Unknown' = {name != 'Unknown'}, confidence < 80 = {confidence < 80}")
                            # If we recently recognized someone, prefer sticky identity for a short window
                            now_ts = time.time()
                            if self.last_recognized_name and (now_ts - self.last_recognized_time) < 8.0:
                                print(f"[INFO] Using sticky identity: {self.last_recognized_name}")
                                return self.last_recognized_name

                            # Increment unknown attempts and only assign a guest after 2 consecutive failures
                            self.unknown_attempts += 1
                            if self.unknown_attempts < 2:
                                print(f"[INFO] Unknown attempt {self.unknown_attempts}/2 - will retry before assigning guest")
                                return None

                            # Handle unknown person as guest after consecutive failures
                            guest_name = self.handle_unknown_person()
                            print(f"[DEBUG] Guest name generated: {guest_name}")
                            print(f"[DEBUG] This person will be marked as guest (is_guest=True)")
                            
                            # Save recognition image for guest
                            try:
                                # Get MagicMirror root directory
                                script_dir = os.path.dirname(os.path.abspath(__file__))
                                if os.path.basename(script_dir) == "MagicMirror-master" or os.path.exists(os.path.join(script_dir, "package.json")):
                                    project_root = script_dir
                                else:
                                    project_root = os.path.dirname(script_dir)
                                static_dir = os.path.join(project_root, "modules", "facerecognition", "public")
                                os.makedirs(static_dir, exist_ok=True)
                                file_fs_path = os.path.join(static_dir, "recognition.jpg")
                                
                                # Try to capture with rpicam-still first (better quality)
                                camera_was_running = False
                                use_rpicam = False
                                
                                # Check if we should try rpicam-still
                                if platform.system() != "Windows":
                                    try:
                                        result_check = subprocess.run(["which", "rpicam-still"], capture_output=True, text=True, timeout=2)
                                        if result_check.returncode == 0:
                                            use_rpicam = True
                                    except:
                                        pass
                                
                                if use_rpicam:
                                    # Temporarily stop Picamera2 to free camera for rpicam-still
                                    if self.camera is not None:
                                        try:
                                            self.camera.stop()
                                            camera_was_running = True
                                            time.sleep(1.0)  # Give camera time to release
                                            print(f"[DEBUG] Camera stopped for rpicam-still (guest)")
                                        except Exception as e:
                                            print(f"[WARNING] Failed to stop camera: {e}")
                                            camera_was_running = False
                                
                                # Capture with rpicam-still or fallback to Picamera2
                                if use_rpicam:
                                    capture_success = self.capture_recognition_image_with_rpicam(file_fs_path)
                                else:
                                    # Use Picamera2 directly (no need to stop camera)
                                    capture_success = self.capture_recognition_image_with_picamera2(file_fs_path)
                                
                                if capture_success and os.path.exists(file_fs_path):
                                    self.recognition_image_path = "/facerecognition/public/recognition.jpg"
                                    file_size = os.path.getsize(file_fs_path)
                                    print(f"[DEBUG] ✓ Saved guest recognition image: {file_fs_path} ({file_size} bytes)")
                                    print(f"[DEBUG] Recognition image path: {self.recognition_image_path}")
                                else:
                                    print(f"[ERROR] Guest recognition image capture failed completely")
                                    self.recognition_image_path = None
                                
                                # Restart Picamera2 if we stopped it for rpicam-still
                                if camera_was_running and self.camera is not None:
                                    try:
                                        self.camera.start()
                                        time.sleep(0.5)  # Let camera stabilize
                                        print(f"[DEBUG] Camera restarted after guest recognition image capture")
                                    except Exception as e:
                                        print(f"[WARNING] Failed to restart camera: {e}")
                                        self.initialize_camera()  # Try full reinitialize if restart fails
                                
                            except Exception as e:
                                print(f"[WARNING] Failed to save guest recognition image: {e}")
                                import traceback
                                traceback.print_exc()
                                self.recognition_image_path = None
                            
                            # Reset photo flag for guest
                            if self.current_person != guest_name:
                                self.photo_saved_this_session = False
                                print(f"[INFO] Guest mode, resetting photo flag")
                            
                            # Save photo for guest
                            photo_saved = self.save_skin_photo(guest_name)
                            if photo_saved:
                                # Get the photo path for the trigger
                                current_date = datetime.now().strftime("%Y-%m-%d")
                                photo_path = os.path.join(os.getcwd(), "Skin", guest_name, f"{current_date}.jpg")
                                self.trigger_skin_analysis(guest_name, photo_path)
                            
                            print(f"[DEBUG] Returning guest name: {guest_name}")
                            return guest_name
                    else:
                        # No recognizer available - treat as unknown face (guest)
                        print("[INFO] No recognizer available - treating as unknown face (guest)")
                        
                        # Handle unknown person as guest
                        # Prefer sticky identity if very recent
                        now_ts = time.time()
                        if self.last_recognized_name and (now_ts - self.last_recognized_time) < 8.0:
                            print(f"[INFO] Using sticky identity without recognizer: {self.last_recognized_name}")
                            return self.last_recognized_name
                        guest_name = self.handle_unknown_person()
                        
                        # Save recognition image for guest (no recognizer case)
                        try:
                            # Get MagicMirror root directory
                            script_dir = os.path.dirname(os.path.abspath(__file__))
                            if os.path.basename(script_dir) == "MagicMirror-master" or os.path.exists(os.path.join(script_dir, "package.json")):
                                project_root = script_dir
                            else:
                                project_root = os.path.dirname(script_dir)
                            static_dir = os.path.join(project_root, "modules", "facerecognition", "public")
                            os.makedirs(static_dir, exist_ok=True)
                            file_fs_path = os.path.join(static_dir, "recognition.jpg")
                            
                            # Try to capture with rpicam-still first (better quality)
                            camera_was_running = False
                            use_rpicam = False
                            
                            # Check if we should try rpicam-still
                            if platform.system() != "Windows":
                                try:
                                    result_check = subprocess.run(["which", "rpicam-still"], capture_output=True, text=True, timeout=2)
                                    if result_check.returncode == 0:
                                        use_rpicam = True
                                except:
                                    pass
                            
                            if use_rpicam:
                                # Temporarily stop Picamera2 to free camera for rpicam-still
                                if self.camera is not None:
                                    try:
                                        self.camera.stop()
                                        camera_was_running = True
                                        time.sleep(1.0)  # Give camera time to release
                                        print(f"[DEBUG] Camera stopped for rpicam-still (guest, no recognizer)")
                                    except Exception as e:
                                        print(f"[WARNING] Failed to stop camera: {e}")
                                        camera_was_running = False
                            
                            # Capture with rpicam-still or fallback to Picamera2
                            if use_rpicam:
                                capture_success = self.capture_recognition_image_with_rpicam(file_fs_path)
                            else:
                                # Use Picamera2 directly (no need to stop camera)
                                capture_success = self.capture_recognition_image_with_picamera2(file_fs_path)
                            
                            if capture_success and os.path.exists(file_fs_path):
                                self.recognition_image_path = "/facerecognition/public/recognition.jpg"
                                file_size = os.path.getsize(file_fs_path)
                                print(f"[DEBUG] ✓ Saved guest recognition image (no recognizer): {file_fs_path} ({file_size} bytes)")
                                print(f"[DEBUG] Recognition image path: {self.recognition_image_path}")
                            else:
                                print(f"[ERROR] Guest recognition image capture failed completely (no recognizer)")
                                self.recognition_image_path = None
                            
                            # Restart Picamera2 if we stopped it for rpicam-still
                            if camera_was_running and self.camera is not None:
                                try:
                                    self.camera.start()
                                    time.sleep(0.5)  # Let camera stabilize
                                    print(f"[DEBUG] Camera restarted after guest recognition image capture (no recognizer)")
                                except Exception as e:
                                    print(f"[WARNING] Failed to restart camera: {e}")
                                    self.initialize_camera()  # Try full reinitialize if restart fails
                            
                        except Exception as e:
                            print(f"[WARNING] Failed to save guest recognition image (no recognizer): {e}")
                            import traceback
                            traceback.print_exc()
                            self.recognition_image_path = None
                        
                        # Reset photo flag for guest
                        if self.current_person != guest_name:
                            self.photo_saved_this_session = False
                            print(f"[INFO] Guest mode, resetting photo flag")
                        
                        # Save photo for guest
                        photo_saved = self.save_skin_photo(guest_name)
                        if photo_saved:
                            # Get the photo path for the trigger
                            current_date = datetime.now().strftime("%Y-%m-%d")
                            photo_path = os.path.join(os.getcwd(), "Skin", guest_name, f"{current_date}.jpg")
                            self.trigger_skin_analysis(guest_name, photo_path)
                        
                        # CRITICAL: Verify image path is set for guest before returning
                        if not self.recognition_image_path:
                            print(f"[WARNING] Guest image path is NOT set! Attempting to recover...")
                            # Try to recover - check if file exists
                            script_dir = os.path.dirname(os.path.abspath(__file__))
                            if os.path.basename(script_dir) == "MagicMirror-master" or os.path.exists(os.path.join(script_dir, "package.json")):
                                project_root = script_dir
                            else:
                                project_root = os.path.dirname(script_dir)
                            image_file = os.path.join(project_root, "modules", "facerecognition", "public", "recognition.jpg")
                            if os.path.exists(image_file):
                                self.recognition_image_path = "/facerecognition/public/recognition.jpg"
                                print(f"[DEBUG] Recovered guest image path: {self.recognition_image_path}")
                            else:
                                print(f"[ERROR] Guest image file does not exist at: {image_file}")
                        else:
                            print(f"[DEBUG] Guest image path is correctly set: {self.recognition_image_path}")
                        
                        print(f"[DEBUG] Returning guest name: {guest_name}, image_path={self.recognition_image_path}")
                        return guest_name
                else:
                    print("[INFO] No face detected in frame")
                    
            except Exception as e:
                print(f"[WARNING] Camera capture failed: {e}")
                return None
            
            return None
            
        except Exception as e:
            print(f"Error in face recognition: {e}")
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
            # Far from sensor
            if self.shutdown_timer is not None:
                # In timeout countdown: keep user and active state
                status_type = "timeout"
                self.is_active = True
            else:
                # Just stepped away but no timeout started yet: keep current state
                # If user is recognized, keep showing their data
                status_type = "recognized" if self.current_person else "waiting"
        
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
        
        # Stable relay control constants - prevent flickering
        LIGHTS_ON_STABLE_THRESHOLD = 2  # Require 2 consecutive readings to turn on
        LIGHTS_OFF_STABLE_THRESHOLD = 5  # Require 5 consecutive readings to turn off (prevent flicker)
        LIGHTS_OFF_BUFFER = 10  # Larger buffer to prevent rapid toggling
        
        # Longer debounce to prevent rapid toggling
        MIN_ON_SECONDS = 0.5  # Minimum time between turning on
        MIN_OFF_SECONDS = 2.0  # Minimum time between turning off (prevent flicker)
        now = time.time()

        # Global block to avoid re-toggling too soon - increased delay
        if now < self.relay_block_until:
            return
        
        # IMPORTANT: If person is close (within threshold) and lights are already on, keep them on
        # This prevents flickering when status changes but person is still present
        if distance <= PROXIMITY_THRESHOLD and self.lights_on:
            # Person is close and lights are on - keep them on, reset counters to maintain state
            self.lights_stable_count = LIGHTS_ON_STABLE_THRESHOLD
            self.lights_off_stable_count = 0
            return  # Skip further processing to prevent any toggling

        # Schmitt-trigger style control with maintain-on buffer zone
        threshold_on = PROXIMITY_THRESHOLD
        threshold_off = PROXIMITY_THRESHOLD + LIGHTS_OFF_BUFFER
        
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
        PROXIMITY_STABLE_THRESHOLD = 3  # Require more stable proximity before activation
        away_stable_count = 0
        AWAY_STABLE_THRESHOLD = 4  # Require more stability before starting timeout
        
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
                
                # Control lights based on proximity
                self.control_lights_based_on_proximity(smoothed_distance)
                
                # Debug output every 10 iterations
                if len(distance_history) % 10 == 0:
                    print(f"[DEBUG] Distance: {distance}cm (smoothed: {smoothed_distance:.1f}cm), Active: {self.is_active}, Person: {self.current_person}, Lights: {'ON' if self.lights_on else 'OFF'} (on_stable: {self.lights_stable_count}, off_stable: {self.lights_off_stable_count})")
                
                # Check proximity with smoothed distance
                if smoothed_distance <= PROXIMITY_THRESHOLD:
                    # Object detected within threshold
                    proximity_stable_count += 1
                    away_stable_count = 0  # Reset away counter

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
                        # Pre-warm camera for faster recognition
                        self.initialize_camera()
                        self.update_status_file()
                    
                    # Try face recognition when first activated
                    if self.is_active and self.current_person is None and not self.face_recognition_attempted and not self.recognition_locked:
                        # Ensure detection time is set
                        if self.last_detection_time is None:
                            self.last_detection_time = time.time()
                        # Wait only ~0.3 seconds for stable proximity before camera activation
                        if time.time() - self.last_detection_time > 0.3:
                            print("📷 Starting face recognition...")
                            self.add_log_message("Царай танилт эхэлж байна...")
                            self.face_recognition_attempted = True
                            person = self.recognize_face_with_camera()
                            print(f"[DEBUG] Face recognition returned: {person}")
                            if person and person != "Unknown":
                                print(f"✅ Face recognized: {person}")
                                self.add_log_message(f"Царай танигдлаа: {person}")
                                self.current_person = person
                                self.shutdown_timer = None
                                # Lock recognition until user leaves and logs out
                                self.recognition_locked = True
                                
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
                                        self.recognition_image_path = "/facerecognition/public/recognition.jpg"
                                        print(f"[DEBUG] Found existing image file, setting path: {self.recognition_image_path}")
                                
                                # Update status file with all recognition data (person, confidence, image)
                                print(f"[DEBUG] Updating status file with person={person}, confidence={self.current_confidence}%, image={self.recognition_image_path}")
                                print(f"[DEBUG] Image path before update: {self.recognition_image_path}")
                                
                                # CRITICAL: Double-check image path is still set before updating status
                                if not self.recognition_image_path:
                                    print(f"[ERROR] Image path lost after setting current_person! Recovering...")
                                    script_dir = os.path.dirname(os.path.abspath(__file__))
                                    if os.path.basename(script_dir) == "MagicMirror-master" or os.path.exists(os.path.join(script_dir, "package.json")):
                                        project_root = script_dir
                                    else:
                                        project_root = os.path.dirname(script_dir)
                                    image_file = os.path.join(project_root, "modules", "facerecognition", "public", "recognition.jpg")
                                    if os.path.exists(image_file):
                                        self.recognition_image_path = "/facerecognition/public/recognition.jpg"
                                        print(f"[DEBUG] Recovered image path in main loop: {self.recognition_image_path}")
                                
                                # Update immediately with all data
                                print(f"[DEBUG] Calling update_status_file() with person={self.current_person}, image={self.recognition_image_path}")
                                self.update_status_file()
                                
                                # Force multiple updates after delays to ensure frontend receives image
                                import threading
                                def delayed_update(delay, update_num):
                                    time.sleep(delay)
                                    # Re-check image file exists before updating
                                    if not self.recognition_image_path:
                                        script_dir = os.path.dirname(os.path.abspath(__file__))
                                        if os.path.basename(script_dir) == "MagicMirror-master" or os.path.exists(os.path.join(script_dir, "package.json")):
                                            project_root = script_dir
                                        else:
                                            project_root = os.path.dirname(script_dir)
                                        image_file = os.path.join(project_root, "modules", "facerecognition", "public", "recognition.jpg")
                                        if os.path.exists(image_file):
                                            self.recognition_image_path = "/facerecognition/public/recognition.jpg"
                                            print(f"[DEBUG] Recovered image in delayed update #{update_num}")
                                    print(f"[DEBUG] Delayed update #{update_num} - person={self.current_person}, image={self.recognition_image_path}")
                                    self.update_status_file()
                                
                                # Send updates at 0.3s, 0.8s, 1.5s, and 3.0s to ensure frontend gets it
                                threading.Thread(target=lambda: delayed_update(0.3, 1), daemon=True).start()
                                threading.Thread(target=lambda: delayed_update(0.8, 2), daemon=True).start()
                                threading.Thread(target=lambda: delayed_update(1.5, 3), daemon=True).start()
                                threading.Thread(target=lambda: delayed_update(3.0, 4), daemon=True).start()
                            else:
                                print("❌ Face not recognized or cancelled - locking recognition until user moves away")
                                self.add_log_message("Царай танихгүй байна")
                                # Lock recognition to prevent repeated attempts while user is still present
                                self.recognition_locked = True
                                # Keep face_recognition_attempted = True so it doesn't retry immediately
                                self.update_status_file()
                    
                    # If face already recognized, maintain the state and reset timeout
                    elif self.current_person is not None:
                        # Reset timeout timer since person is still present
                        self.shutdown_timer = None
                        # Only log every 10 seconds to reduce spam
                        if time.time() - self.last_detection_time > 10:
                            print(f"👤 User {self.current_person} is still present at {smoothed_distance:.1f}cm, image={self.recognition_image_path}")
                            self.last_detection_time = time.time()
                        # Periodically update status to ensure image path is included
                        current_time = time.time()
                        if current_time - last_status_update > STATUS_UPDATE_INTERVAL:
                            # Ensure image path is still set if person is recognized
                            if self.recognition_image_path is None and self.current_person:
                                print(f"[DEBUG] Image path is None for recognized person {self.current_person}, checking file...")
                                # Try to verify if image file exists
                                script_dir = os.path.dirname(os.path.abspath(__file__))
                                if os.path.basename(script_dir) == "MagicMirror-master" or os.path.exists(os.path.join(script_dir, "package.json")):
                                    project_root = script_dir
                                else:
                                    project_root = os.path.dirname(script_dir)
                                image_file = os.path.join(project_root, "modules", "facerecognition", "public", "recognition.jpg")
                                if os.path.exists(image_file):
                                    self.recognition_image_path = "/facerecognition/public/recognition.jpg"
                                    print(f"[DEBUG] Found existing image file, setting path: {self.recognition_image_path}")
                            self.update_status_file()
                            last_status_update = current_time
                    
                    # Update status file regularly when active (if not already updated above)
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
                                self.add_log_message("Мэдрэгчээс хүн холдсон")
                                self.shutdown_timer = time.time()
                        elif self.is_active and self.shutdown_timer is None:
                            # No person recognized but was active - start timeout
                            self.shutdown_timer = time.time()
                            print(f"⏰ No face recognized, starting {TIMEOUT_DELAY}s timeout")
                            self.add_log_message("Хүн хэт алсаж байна...")
                            # Reset recognition lock when user moves away (allows recognition next time)
                            if self.recognition_locked:
                                self.recognition_locked = False
                                print("🔓 Recognition lock reset - will try again when user returns")
                    
                    # Check if timeout has elapsed
                    if self.shutdown_timer is not None:
                        elapsed = time.time() - self.shutdown_timer
                        if elapsed >= TIMEOUT_DELAY:
                            print(f"⏰ Timeout reached ({TIMEOUT_DELAY}s) - logging out user")
                            self.add_log_message("Систем хүлээж байна...")
                            # Reset all states after timeout
                            self.current_person = None
                            self.current_confidence = 0
                            self.recognition_image_path = None
                            self.is_active = False
                            self.face_recognition_attempted = False
                            self.camera_opened = False
                            self.shutdown_timer = None
                            self.recognition_locked = False  # Allow recognition next time
                            # Ensure lights are turned off on timeout
                            if self.lights_on:
                                try:
                                    self.turn_off_lights()
                                except Exception as e:
                                    print(f"[WARNING] Failed to turn off lights on timeout: {e}")
                            # Don't reset photo_saved_this_session here - only reset when new person detected
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
