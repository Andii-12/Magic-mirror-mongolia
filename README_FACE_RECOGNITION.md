# MagicMirror² Face Recognition System

A smart mirror system that uses ultrasonic sensors and face recognition to provide personalized greetings in Mongolian language.

## 🎯 Features

- **Proximity Detection**: Ultrasonic sensor detects when someone is within 20cm
- **Face Recognition**: Automatic face recognition using OpenCV and LBPH
- **Mongolian Interface**: All messages and greetings in Mongolian language
- **Interactive Training**: Easy-to-use training system with camera preview
- **Auto-Shutdown**: Automatically hides interface when no one is nearby
- **Personalized Greetings**: Shows "Тавтай Морил [Name]!" for recognized people

## 📋 System Requirements

### Hardware
- Raspberry Pi 4 (recommended)
- Raspberry Pi Camera Module or USB webcam
- Ultrasonic Sensor (HC-SR04)
- Jumper wires
- 5V power supply

### Software
- Raspberry Pi OS (latest)
- Python 3.7+
- Node.js 16+
- MagicMirror²

## 🔌 Hardware Setup

### Ultrasonic Sensor Connections
```
HC-SR04    →    Raspberry Pi
VCC        →    5V (Pin 2)
GND        →    Ground (Pin 6)
TRIG       →    GPIO 23 (Pin 16)
ECHO       →    GPIO 24 (Pin 18)
```

### Camera Setup
- **Pi Camera**: Enable in `raspi-config` → Interface Options → Camera
- **USB Camera**: Plug in and test with `ls /dev/video*`

## 🚀 Installation

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/MagicMirror-FaceRecognition.git
cd MagicMirror-FaceRecognition
```

### 2. Install Dependencies
```bash
# Install Python packages
pip3 install opencv-python RPi.GPIO picamera2 numpy

# Install MagicMirror² dependencies
npm install
```

### 3. Setup Face Recognition
```bash
# Make scripts executable
chmod +x setup-face-recognition.sh
chmod +x start_magicmirror_proximity.sh

# Run setup script
./setup-face-recognition.sh
```

## 🎓 Training the Face Recognition System

### Interactive Training
```bash
python3 train_faces.py
```

**Follow these steps:**
1. Choose **Option 1** (Add new person)
2. Enter the person's name (e.g., "John")
3. Camera preview will open showing your face
4. Press **Enter** to start capturing 40 photos
5. Wait for photo capture to complete
6. Choose **Option 2** (Train system)
7. Wait for training to complete
8. Choose **Option 4** (Exit)

### Training Tips
- **Good lighting**: Ensure face is well-lit
- **Look directly at camera**: Don't look away during capture
- **Clear background**: Avoid busy backgrounds
- **Different expressions**: System captures various expressions automatically

## 🧪 Testing the System

### Test Face Recognition Only
```bash
python3 test_recognition_only.py
```

### Test Full System
```bash
python3 test_face_recognition.py
```

## 🚀 Running the Complete System

### Option 1: Proximity-Controlled System (Recommended)
```bash
./start_magicmirror_proximity.sh
```

### Option 2: Manual Startup
```bash
# Terminal 1 - Start Face Recognition
python3 face_recognition_system.py

# Terminal 2 - Start MagicMirror²
npm start
```

## 📱 User Experience Flow

### 1. Initial State
- **Screen**: Black background
- **Message**: "Ойртож зогсоорой" (Come closer and stop)

### 2. Proximity Detected (Within 20cm)
- **Screen**: Face icon appears with pulse animation
- **Message**: "Царай таниж байна" (Recognizing face)

### 3. Face Recognized
- **Screen**: Face icon continues
- **Message**: "Тавтай Морил [Name]" (Welcome [Name])

### 4. Main Interface
- **Screen**: Full MagicMirror² interface appears
- **Top**: "Тавтай Морил [Name]!" greeting
- **Content**: All configured modules (clock, weather, news, etc.)

### 5. Auto-Hide
- **Trigger**: Move away for 10+ seconds
- **Action**: Interface hides automatically

## ⚙️ Configuration

### Face Recognition Settings
Edit `config/config.mn.js`:
```javascript
{
    module: "facerecognition",
    position: "top_center",
    config: {
        proximityThreshold: 20,        // Distance threshold in cm
        timeoutDelay: 10000,           // Auto-hide delay in ms
        greetingDuration: 5000,        // Greeting display time
        greetings: {
            "default": "Тавтай Морил {name}!",
            "unknown": "Таныг танихгүй байна"
        }
    }
}
```

### Overlay Messages
```javascript
{
    module: "facerecognitionoverlay",
    config: {
        messages: {
            detecting: "Царай таниж байна",
            recognized: "Тавтай Морил",
            unknown: "Таныг танихгүй байна",
            waiting: "Ойртож зогсоорой"
        }
    }
}
```

## 📁 File Structure

```
MagicMirror-FaceRecognition/
├── modules/
│   ├── facerecognition/           # Main greeting module
│   └── facerecognitionoverlay/    # Full-screen overlay
├── Images/                        # Training photos
│   ├── Person1/
│   └── Person2/
├── python_code/                   # Original working code
├── face_recognition_system.py     # Main recognition script
├── train_faces.py                 # Interactive training
├── test_recognition_only.py       # Recognition test
├── start_magicmirror_proximity.sh # Startup script
├── trainer.yml                    # Trained model
└── config/config.mn.js           # MagicMirror² config
```

## 🔧 Troubleshooting

### Common Issues

**1. Camera not working:**
```bash
# Test camera
python3 test_recognition_only.py

# Check camera permissions
sudo usermod -a -G video $USER
```

**2. Ultrasonic sensor not responding:**
```bash
# Test GPIO
python3 -c "import RPi.GPIO as GPIO; print('GPIO OK')"

# Check connections
gpio readall
```

**3. Face recognition not working:**
```bash
# Check if trainer.yml exists
ls -la trainer.yml python_code/trainer.yml

# Retrain the system
python3 train_faces.py
```

**4. MagicMirror² not starting:**
```bash
# Check npm dependencies
npm install

# Test MagicMirror²
npm start
```

### Debug Commands

**Check system status:**
```bash
# View status file
cat /tmp/magicmirror_face_status.json

# Check running processes
ps aux | grep python
ps aux | grep node
```

**View logs:**
```bash
# MagicMirror² logs
tail -f ~/.pm2/logs/MagicMirror-out.log

# Face recognition logs
python3 face_recognition_system.py
```

## 🎨 Customization

### Adding New People
1. Run `python3 train_faces.py`
2. Choose Option 1 (Add new person)
3. Enter name and follow prompts
4. Choose Option 2 (Train system)

### Changing Messages
Edit the `messages` section in `config/config.mn.js`:
```javascript
messages: {
    detecting: "Your custom message",
    recognized: "Your welcome message",
    waiting: "Your waiting message"
}
```

### Adjusting Sensitivity
```javascript
config: {
    proximityThreshold: 15,  // Lower = more sensitive
    timeoutDelay: 15000,     // Longer delay before hide
}
```

## 📊 Performance Tips

- **Use Pi Camera**: Better performance than USB cameras
- **Good lighting**: Improves recognition accuracy
- **Multiple photos**: Train with 40+ photos per person
- **Clear backgrounds**: Avoid busy backgrounds during training
- **Regular retraining**: Retrain when recognition accuracy drops

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- MagicMirror² community
- OpenCV developers
- Raspberry Pi Foundation
- Mongolian language support contributors

## 📞 Support

For issues and questions:
- Create an issue on GitHub
- Check the troubleshooting section
- Review the MagicMirror² documentation

---

**Made with ❤️ for the Mongolian MagicMirror² community**
