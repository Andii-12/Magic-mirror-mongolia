# 🚀 Quick Start Guide

## 5-Minute Setup

### 1. Hardware Connection
```
Ultrasonic Sensor:
VCC → 5V (Pin 2)
GND → Ground (Pin 6)  
TRIG → GPIO 23 (Pin 16)
ECHO → GPIO 24 (Pin 18)

Camera: Enable in raspi-config
```

### 2. Install Dependencies
```bash
pip3 install opencv-python RPi.GPIO picamera2 numpy
npm install
```

### 3. Train Face Recognition
```bash
python3 train_faces.py
# Choose Option 1 → Enter name → Press Enter when ready
# Choose Option 2 → Wait for training
```

### 4. Start System
```bash
chmod +x start_magicmirror_proximity.sh
./start_magicmirror_proximity.sh
```

### 5. Test
- Move within 20cm of sensor
- See "Царай таниж байна"
- Get recognized → "Тавтай Морил [Name]"
- MagicMirror² interface appears

## 🎯 Expected Flow
1. **"Ойртож зогсоорой"** (Come closer)
2. **"Царай таниж байна"** (Recognizing)  
3. **"Тавтай Морил [Name]"** (Welcome)
4. **Main MagicMirror² interface**

## 🔧 Quick Fixes
- **No camera**: `sudo usermod -a -G video $USER`
- **No recognition**: `python3 train_faces.py` (retrain)
- **No sensor**: Check GPIO connections
- **No MagicMirror²**: `npm install && npm start`

---
**Full documentation**: See `README_FACE_RECOGNITION.md`
