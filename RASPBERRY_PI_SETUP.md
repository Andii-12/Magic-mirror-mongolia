# Raspberry Pi 4 Complete Setup Guide

## 🍓 Prerequisites

### Hardware Requirements
- Raspberry Pi 4 (1GB+ RAM recommended)
- MicroSD card (32GB+)
- Camera module (for face recognition)
- Ultrasonic sensor (HC-SR04)
- Jumper wires
- Power supply (5V, 3A)

### Software Requirements
- Raspberry Pi OS (64-bit recommended)
- Node.js 18+ (22.14.0+ preferred)
- Python 3.8+
- OpenCV
- Picamera2

## 🚀 Complete Installation

### 1. System Setup

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install essential packages
sudo apt install -y git curl wget build-essential python3-pip python3-venv

# Install Node.js 22.x
curl -fsSL https://deb.nodesource.com/setup_22.x | sudo -E bash -
sudo apt-get install -y nodejs

# Verify installations
node --version  # Should be 22.x
npm --version
python3 --version
```

### 2. Clone and Setup MagicMirror²

```bash
# Clone the repository
git clone https://github.com/Andii-12/Magic-mirror-mongolia.git
cd Magic-mirror-mongolia

# Install dependencies
npm install --only=prod --omit=dev

# Run Mongolian setup
chmod +x setup-mongolian.sh
./setup-mongolian.sh
```

### 3. Install Python Dependencies

```bash
# Install OpenCV and camera libraries
sudo apt install -y python3-opencv python3-picamera2

# Install additional Python packages
pip3 install opencv-python RPi.GPIO numpy

# Install face recognition libraries
pip3 install face-recognition
```

### 4. Setup Face Recognition

```bash
# Create necessary directories
mkdir -p Images
mkdir -p /home/pi/haarcascades

# Download Haar cascade
wget -O /home/pi/haarcascades/haarcascade_frontalface_default.xml \
  https://raw.githubusercontent.com/opencv/opencv/master/data/haarcascades/haarcascade_frontalface_default.xml

# Set permissions
chmod 644 /home/pi/haarcascades/haarcascade_frontalface_default.xml
```

### 5. Hardware Setup

#### Camera Module
```bash
# Enable camera
sudo raspi-config
# Navigate to: Interface Options > Camera > Enable

# Test camera
libcamera-hello --list-cameras
```

#### Ultrasonic Sensor (HC-SR04)
```
Wiring:
- VCC → 5V (Pin 2)
- GND → Ground (Pin 6)
- TRIG → GPIO 23 (Pin 16)
- ECHO → GPIO 24 (Pin 18)
```

### 6. Configure Face Recognition

```bash
# Train faces
python3 train_faces.py

# Test face recognition
python3 test_face_recognition.py
```

## 🎯 Running the Complete System

### 1. Start Face Recognition System

```bash
# Terminal 1 - Start face recognition
python3 face_recognition_system.py
```

### 2. Start MagicMirror²

```bash
# Terminal 2 - Start MagicMirror
npm start
```

### 3. Auto-Start Setup (Optional)

```bash
# Create systemd service for face recognition
sudo nano /etc/systemd/system/magicmirror-face.service
```

Add this content:
```ini
[Unit]
Description=MagicMirror Face Recognition
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/Magic-mirror-mongolia
ExecStart=/usr/bin/python3 face_recognition_system.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start service
sudo systemctl enable magicmirror-face.service
sudo systemctl start magicmirror-face.service

# Create systemd service for MagicMirror
sudo nano /etc/systemd/system/magicmirror.service
```

Add this content:
```ini
[Unit]
Description=MagicMirror
After=network.target magicmirror-face.service

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/Magic-mirror-mongolia
ExecStart=/usr/bin/npm start
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start service
sudo systemctl enable magicmirror.service
sudo systemctl start magicmirror.service
```

## 🔧 Configuration Files

### Face Recognition Status File
The system creates `/tmp/magicmirror_face_status.json`:
```json
{
  "distance": 15,
  "person": "Andii",
  "active": true,
  "status": "recognized",
  "timestamp": "2025-01-27T10:30:00.000Z"
}
```

### MagicMirror² Config
Located at `config/config.js` - already configured for:
- Mongolian language
- Personal API integration
- Face recognition modules
- Weather and news

## 🐛 Troubleshooting

### Common Issues

**1. Camera not working:**
```bash
# Check camera
libcamera-hello --list-cameras
# Enable camera in raspi-config
sudo raspi-config
```

**2. Face recognition not detecting:**
```bash
# Check status file
cat /tmp/magicmirror_face_status.json
# Test face recognition
python3 test_face_recognition.py
```

**3. MagicMirror not starting:**
```bash
# Check logs
npm start 2>&1 | tee magicmirror.log
# Check configuration
node js/check_config.js
```

**4. Memory issues:**
```bash
# Check memory usage
free -h
# Increase swap if needed
sudo dphys-swapfile swapoff
sudo nano /etc/dphys-swapfile
# Change CONF_SWAPSIZE=100 to CONF_SWAPSIZE=512
sudo dphys-swapfile setup
sudo dphys-swapfile swapon
```

## 📊 Performance Optimization

### For 1GB RAM Pi 4:
```bash
# Disable unnecessary services
sudo systemctl disable bluetooth
sudo systemctl disable hciuart

# Optimize GPU memory split
sudo nano /boot/config.txt
# Add: gpu_mem=64

# Use zram for swap
sudo apt install zram-tools
```

## 🎉 Complete System Features

### What You'll Get:
1. **Mongolian Language Interface** - Complete translation
2. **Face Recognition** - Personalized greetings
3. **Personal API Integration** - Your calendar and todos
4. **Weather Display** - Current and forecast
5. **Mongolian News** - Local and international news
6. **Mongolian Holidays** - Cultural calendar
7. **Smart Proximity Detection** - Ultrasonic sensor
8. **Auto-Start** - Boots automatically

### Display Layout:
- **Top Left**: Clock and calendar
- **Top Right**: Weather
- **Middle Center**: Personal schedule (API data)
- **Bottom Bar**: Mongolian news
- **Face Recognition**: Personalized greetings

## 🚀 Quick Start Commands

```bash
# Complete setup (run once)
git clone https://github.com/Andii-12/Magic-mirror-mongolia.git
cd Magic-mirror-mongolia
chmod +x setup-mongolian.sh
./setup-mongolian.sh
sudo apt install -y python3-opencv python3-picamera2
pip3 install opencv-python RPi.GPIO numpy face-recognition

# Daily usage
python3 face_recognition_system.py &  # Start face recognition
npm start  # Start MagicMirror
```

## 📱 Remote Access

### Enable SSH:
```bash
sudo systemctl enable ssh
sudo systemctl start ssh
```

### Access from another device:
- Open browser to `http://[PI_IP]:8080`
- Use VNC for desktop access: `sudo apt install realvnc-vnc-server`

## 🔄 Updates

```bash
# Update MagicMirror
cd /home/pi/Magic-mirror-mongolia
git pull
npm install

# Update system
sudo apt update && sudo apt upgrade -y
```

---

**Your complete Mongolian MagicMirror² with Personal API integration is ready!** 🎉
