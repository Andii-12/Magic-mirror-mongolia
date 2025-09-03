import RPi.GPIO as GPIO
import time
import cv2
from picamera2 import Picamera2
import os
import numpy as np

# Ultrasonic pins
TRIG = 23  # GPIO pin for TRIG
ECHO = 24  # GPIO pin for ECHO

# Setup GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(TRIG, GPIO.OUT)
GPIO.setup(ECHO, GPIO.IN)

# Load Haarcascade and trained recognizer
cascade_path = "/home/andii/haarcascades/haarcascade_frontalface_default.xml"
face_cascade = cv2.CascadeClassifier(cascade_path)
recognizer = cv2.face.LBPHFaceRecognizer_create()
recognizer.read("trainer.yml")

# Map folder names to labels
image_base = "Images"
label_names = os.listdir(image_base)
label_map = {i: name for i, name in enumerate(label_names)}

def get_distance():
    GPIO.output(TRIG, False)
    time.sleep(0.1)

    GPIO.output(TRIG, True)
    time.sleep(0.00001)
    GPIO.output(TRIG, False)

    while GPIO.input(ECHO) == 0:
        pulse_start = time.time()
    while GPIO.input(ECHO) == 1:
        pulse_end = time.time()

    pulse_duration = pulse_end - pulse_start
    distance = pulse_duration * 17150
    distance = round(distance, 2)
    return distance

try:
    while True:
        dist = get_distance()
        if dist <= 20:
            print(f"[INFO] Object detected at {dist}cm. Opening camera...")
            picam2 = Picamera2()
            config = picam2.create_preview_configuration(main={"size": (320, 240)})
            picam2.configure(config)
            picam2.start()
            time.sleep(1)  # small delay to let camera initialize

            frame = picam2.capture_array()
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, 1.3, 5)

            recognized = False
            for (x, y, w, h) in faces:
                face_img = gray[y:y+h, x:x+w]
                label, confidence = recognizer.predict(face_img)
                name = label_map.get(label, "Unknown")
                print(f"[INFO] Recognized: {name} (Confidence: {confidence:.2f})")
                recognized = True
                break

            if not recognized:
                print("[INFO] No recognized face detected!")

            picam2.close()
            time.sleep(1)  # avoid multiple triggers instantly

        time.sleep(0.2)  # small delay for sensor polling

except KeyboardInterrupt:
    print("[INFO] Exiting...")
    GPIO.cleanup()
