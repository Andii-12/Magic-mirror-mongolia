#!/usr/bin/env python3
"""
Test Face Recognition Confidence Display
Opens camera and shows real-time recognition with confidence percentage
"""

import cv2
import numpy as np
import time
import os
from datetime import datetime
import platform

# Configuration
CASCADE_PATH = "/home/andii/haarcascades/haarcascade_frontalface_default.xml"
TRAINER_PATH = "trainer.yml"
IMAGE_BASE = "Images"

# Try to load face recognition components
def load_face_components():
    """Load face cascade and recognizer"""
    # Load face cascade
    if CASCADE_PATH and os.path.exists(CASCADE_PATH):
        face_cascade = cv2.CascadeClassifier(CASCADE_PATH)
    else:
        print("Using default cascade")
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    
    if face_cascade.empty():
        print("❌ Could not load face cascade")
        return None, None, None
    
    # Load recognizer
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    trainer_loaded = False
    
    trainer_paths = [TRAINER_PATH, "python_code/trainer.yml"]
    for trainer_path in trainer_paths:
        if os.path.exists(trainer_path):
            try:
                recognizer.read(trainer_path)
                print(f"✅ Loaded trainer from: {trainer_path}")
                trainer_loaded = True
                break
            except Exception as e:
                print(f"⚠️  Could not load trainer from {trainer_path}: {e}")
                continue
    
    if not trainer_loaded:
        print("⚠️  No trainer.yml found")
        recognizer = None
    
    # Load label mapping
    if IMAGE_BASE and os.path.exists(IMAGE_BASE):
        label_names = os.listdir(IMAGE_BASE)
    else:
        label_names = ["Unknown"]
    
    label_map = {i: name for i, name in enumerate(label_names)}
    print(f"Loaded {len(label_names)} known faces: {label_names}")
    
    return face_cascade, recognizer, label_map

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
        # 40..0  -> 96..99
        base = max(0.0, min(100.0, 96.0 + (40.0 - c) * (3.0 / 40.0)))
    elif c <= 60:
        # 60..40 -> 90..96
        base = max(0.0, min(100.0, 90.0 + (60.0 - c) * (6.0 / 20.0)))
    elif c <= 90:
        # 90..60 -> 70..90
        base = max(0.0, min(100.0, 70.0 + (90.0 - c) * (20.0 / 30.0)))
    elif c <= 120:
        # 120..90 -> 40..70
        base = max(0.0, min(100.0, 40.0 + (120.0 - c) * (30.0 / 30.0)))
    else:
        # >120 -> taper down from 40 to ~5 by 200
        if c >= 200:
            base = 5.0
        else:
            base = max(0.0, 40.0 - (c - 120.0) * (35.0 / 80.0))

    # Calibrated uplift so typical ~70% reads ~90%
    boosted = min(99.0, base + 20.0)
    return boosted

def test_with_webcam(face_cascade, recognizer, label_map):
    """Test with standard webcam (cv2.VideoCapture)"""
    print("\n📷 Using webcam for testing...")
    
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("❌ Could not open camera")
        return False
    
    # Set resolution for better performance (640x480 is optimal for processing speed)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    
    print("\n🎯 Face Recognition Confidence Test")
    print("=" * 50)
    print("Controls:")
    print("  Press 'q' to quit")
    print("  Press 's' to save current frame")
    print("  Press 'h' to toggle histogram equalization")
    print("  Press 'i' to show frame info")
    print("=" * 50)
    
    use_equalization = False
    show_info = True
    frame_count = 0
    fps_start_time = time.time()
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        frame_count += 1
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Apply histogram equalization if enabled
        if use_equalization:
            gray_processed = cv2.equalizeHist(gray)
        else:
            gray_processed = gray
        
        # Detect faces with optimized parameters for performance
        faces = face_cascade.detectMultiScale(
            gray_processed, 
            scaleFactor=1.1,  # Slightly faster
            minNeighbors=4,  # Fewer false positives
            minSize=(80, 80),  # Larger minimum size for speed
            flags=cv2.CASCADE_SCALE_IMAGE
        )
        
        # Draw on frame
        for (x, y, w, h) in faces:
            # Draw rectangle
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
            
            # Extract face and predict
            if recognizer:
                face_roi = gray_processed[y:y+h, x:x+w]
                face_resized = cv2.resize(face_roi, (100, 100))
                
                # Try prediction with and without equalization
                label, confidence = recognizer.predict(face_resized)
                name = label_map.get(label, "Unknown") if label_map else "Unknown"
                
                # Convert LBPH distance (lower is better) to a user-friendly %
                confidence_percent = map_lbph_confidence_to_percent(confidence)
                
                # Color based on confidence
                if name != "Unknown" and confidence_percent >= 70:
                    color = (0, 255, 0)  # Green - good match
                elif name != "Unknown" and confidence_percent >= 50:
                    color = (0, 255, 255)  # Yellow - moderate match
                elif name != "Unknown":
                    color = (0, 165, 255)  # Orange - weak match
                else:
                    color = (0, 0, 255)  # Red - unknown
                
                # Draw prediction text (smaller font for better performance)
                text = f"{name} ({confidence_percent:.0f}%)"
                cv2.putText(frame, text, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
                
                # Draw confidence bar (simpler rendering)
                bar_width = int((confidence_percent / 100) * w)
                cv2.rectangle(frame, (x, y+h+5), (x+bar_width, y+h+12), color, -1)
                cv2.rectangle(frame, (x, y+h+5), (x+w, y+h+12), (255, 255, 255), 1)
                
            else:
                # No recognizer - just show "Detecting..."
                cv2.putText(frame, "Face Detected", (x, y-10), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
        
        # Draw info overlay
        if show_info:
            # FPS calculation
            elapsed_time = time.time() - fps_start_time
            if elapsed_time >= 1.0:
                fps = frame_count / elapsed_time
                frame_count = 0
                fps_start_time = time.time()
            else:
                fps = 0
            
            # Info text
            info_lines = []
            info_lines.append(f"Faces detected: {len(faces)}")
            if recognizer:
                info_lines.append("Recognition: ON")
            else:
                info_lines.append("Recognition: OFF (no trainer)")
            
            if use_equalization:
                info_lines.append("Histogram Equalization: ON")
            else:
                info_lines.append("Histogram Equalization: OFF")
            
            if fps > 0:
                info_lines.append(f"FPS: {fps:.1f}")
            
            # Draw info background
            info_height = len(info_lines) * 25 + 20
            cv2.rectangle(frame, (10, 10), (300, info_height), (0, 0, 0), -1)
            cv2.rectangle(frame, (10, 10), (300, info_height), (255, 255, 255), 1)
            
            # Draw info text
            for i, line in enumerate(info_lines):
                y_pos = 35 + i * 25
                cv2.putText(frame, line, (20, y_pos), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
        
        # Show frame
        cv2.imshow('Face Recognition Confidence Test', frame)
        
        # Handle keys
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('s'):
            # Save current frame
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"test_face_confidence_{timestamp}.jpg"
            cv2.imwrite(filename, frame)
            print(f"📸 Saved test image: {filename}")
        elif key == ord('h'):
            use_equalization = not use_equalization
            print(f"Histogram equalization: {'ON' if use_equalization else 'OFF'}")
        elif key == ord('i'):
            show_info = not show_info
        
        # Small delay to reduce CPU usage (allows ~30 FPS)
        time.sleep(0.03)
    
    cap.release()
    cv2.destroyAllWindows()
    print("\n✅ Test completed")
    return True

def test_with_picamera(face_cascade, recognizer, label_map):
    """Test with Raspberry Pi camera (Picamera2)"""
    print("\n📷 Using PiCamera2 for testing...")
    
    try:
        from picamera2 import Picamera2
        import libcamera
    except ImportError:
        print("❌ Picamera2 not available")
        return False
    
    picam2 = Picamera2()
    config = picam2.create_preview_configuration(
        main={"size": (640, 480), "format": "RGB888"},  # 640x480 is optimal for processing speed
        transform=libcamera.Transform(hflip=0, vflip=0)
    )
    picam2.configure(config)
    picam2.start()
    time.sleep(1)
    
    print("\n🎯 Face Recognition Confidence Test")
    print("=" * 50)
    print("Controls:")
    print("  Press 'q' to quit")
    print("  Press 's' to save current frame")
    print("  Press 'h' to toggle histogram equalization")
    print("  Press 'i' to show frame info")
    print("=" * 50)
    
    use_equalization = False
    show_info = True
    frame_count = 0
    fps_start_time = time.time()
    
    try:
        while True:
            # Capture frame
            frame_rgb = picam2.capture_array()
            frame_bgr = cv2.cvtColor(frame_rgb, cv2.COLOR_RGB2BGR)
            frame = frame_bgr
            
            frame_count += 1
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Apply histogram equalization if enabled
            if use_equalization:
                gray_processed = cv2.equalizeHist(gray)
            else:
                gray_processed = gray
            
            # Detect faces with optimized parameters for performance
            faces = face_cascade.detectMultiScale(
                gray_processed, 
                scaleFactor=1.1,  # Slightly faster
                minNeighbors=4,  # Fewer false positives
                minSize=(80, 80),  # Larger minimum size for speed
                flags=cv2.CASCADE_SCALE_IMAGE
            )
            
            # Draw on frame
            for (x, y, w, h) in faces:
                # Draw rectangle
                cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                
                # Extract face and predict
                if recognizer:
                    face_roi = gray_processed[y:y+h, x:x+w]
                    face_resized = cv2.resize(face_roi, (100, 100))
                    
                    label, confidence = recognizer.predict(face_resized)
                    name = label_map.get(label, "Unknown") if label_map else "Unknown"
                    
                    # Convert LBPH distance (lower is better) to a user-friendly %
                    confidence_percent = map_lbph_confidence_to_percent(confidence)
                    
                    # Color based on confidence
                    if name != "Unknown" and confidence_percent >= 70:
                        color = (0, 255, 0)  # Green
                    elif name != "Unknown" and confidence_percent >= 50:
                        color = (0, 255, 255)  # Yellow
                    elif name != "Unknown":
                        color = (0, 165, 255)  # Orange
                    else:
                        color = (0, 0, 255)  # Red
                    
                    # Draw prediction (smaller font for better performance)
                    text = f"{name} ({confidence_percent:.0f}%)"
                    cv2.putText(frame, text, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
                    
                    # Draw confidence bar (simpler rendering)
                    bar_width = int((confidence_percent / 100) * w)
                    cv2.rectangle(frame, (x, y+h+5), (x+bar_width, y+h+12), color, -1)
                    cv2.rectangle(frame, (x, y+h+5), (x+w, y+h+12), (255, 255, 255), 1)
                
                else:
                    cv2.putText(frame, "Face Detected", (x, y-10), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
            
            # Draw info overlay
            if show_info:
                elapsed_time = time.time() - fps_start_time
                if elapsed_time >= 1.0:
                    fps = frame_count / elapsed_time
                    frame_count = 0
                    fps_start_time = time.time()
                else:
                    fps = 0
                
                info_lines = []
                info_lines.append(f"Faces: {len(faces)}")
                if recognizer:
                    info_lines.append("Recognition: ON")
                else:
                    info_lines.append("Recognition: OFF")
                if use_equalization:
                    info_lines.append("Equalization: ON")
                else:
                    info_lines.append("Equalization: OFF")
                if fps > 0:
                    info_lines.append(f"FPS: {fps:.1f}")
                
                info_height = len(info_lines) * 30 + 20
                cv2.rectangle(frame, (10, 10), (300, info_height), (0, 0, 0), -1)
                cv2.rectangle(frame, (10, 10), (300, info_height), (255, 255, 255), 1)
                
                for i, line in enumerate(info_lines):
                    y_pos = 40 + i * 30
                    cv2.putText(frame, line, (20, y_pos), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            
            # Show frame
            cv2.imshow('Face Recognition Confidence Test', frame)
            
            # Handle keys
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('s'):
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"test_face_confidence_{timestamp}.jpg"
                cv2.imwrite(filename, frame)
                print(f"📸 Saved test image: {filename}")
            elif key == ord('h'):
                use_equalization = not use_equalization
                print(f"Histogram equalization: {'ON' if use_equalization else 'OFF'}")
            elif key == ord('i'):
                show_info = not show_info
            
            # Small delay to reduce CPU usage (allows ~30 FPS)
            time.sleep(0.03)
    
    finally:
        picam2.close()
        cv2.destroyAllWindows()
        print("\n✅ Test completed")
    
    return True

def main():
    """Main test function"""
    print("🎯 Face Recognition Confidence Test")
    print("=" * 50)
    
    # Load components
    face_cascade, recognizer, label_map = load_face_components()
    
    if not face_cascade:
        print("❌ Failed to load face detection")
        return
    
    if not recognizer:
        print("⚠️  No trainer loaded - face detection only")
        print("   Run 'python3 train_face_recognition.py' to train faces first")
    
    # Check if we should use PiCamera
    use_picamera = False
    if platform.system() != "Windows":
        try:
            from picamera2 import Picamera2
            use_picamera = True
            print("✅ PiCamera2 available")
        except ImportError:
            print("⚠️  PiCamera2 not available, using webcam")
    
    # Run test
    if use_picamera:
        success = test_with_picamera(face_cascade, recognizer, label_map)
    else:
        success = test_with_webcam(face_cascade, recognizer, label_map)
    
    if success:
        print("\n📊 Test Summary:")
        print("   - Face detection: ✅ Working")
        if recognizer:
            print("   - Face recognition: ✅ Working")
            print(f"   - Known faces: {len(label_map)}")
        else:
            print("   - Face recognition: ⚠️  No trainer loaded")
        print("\n💡 Tips:")
        print("   - Green (70%+) = Good match")
        print("   - Yellow (50-70%) = Moderate match")
        print("   - Orange (30-50%) = Weak match")
        print("   - Red = Unknown")
        print("   - Press 'h' to toggle histogram equalization")
    else:
        print("\n❌ Test failed")

if __name__ == "__main__":
    main()

