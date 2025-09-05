# 🍓 Complete Raspberry Pi 4 Setup Guide

## 🎯 What You'll Get

A fully functional MagicMirror² with:
- 🇲🇳 **Mongolian Language Support** - Complete interface translation
- 👤 **Face Recognition** - Personalized greetings and content
- 📅 **Personal API Integration** - Your calendar events and todos
- 🌤️ **Weather Display** - Current weather and forecasts
- 📰 **Mongolian News** - Local and international news
- 🎉 **Mongolian Holidays** - Cultural calendar events
- 📱 **Smart Proximity Detection** - Ultrasonic sensor integration
- 🚀 **Auto-Start** - Boots automatically on power-on

## 📋 Hardware Requirements

### Essential Components
- **Raspberry Pi 4** (1GB+ RAM recommended)
- **MicroSD Card** (32GB+, Class 10+)
- **Power Supply** (5V, 3A, USB-C)
- **Camera Module** (Pi Camera v2 or v3)
- **Ultrasonic Sensor** (HC-SR04)
- **Jumper Wires** (Male-to-Female)
- **Breadboard** (optional, for prototyping)

### Optional Components
- **Touchscreen Display** (7" or 10" recommended)
- **Case** (with camera cutout)
- **Heat Sinks** (for better thermal management)
- **Fan** (for heavy usage)

## 🔌 Hardware Wiring

### Camera Module
```
Camera Module → Raspberry Pi
- Red wire → 5V (Pin 2)
- Black wire → Ground (Pin 6)
- Yellow wire → SDA (Pin 3)
- Orange wire → SCL (Pin 5)
```

### Ultrasonic Sensor (HC-SR04)
```
HC-SR04 → Raspberry Pi
- VCC → 5V (Pin 2)
- GND → Ground (Pin 6)
- TRIG → GPIO 23 (Pin 16)
- ECHO → GPIO 24 (Pin 18)
```

## 🚀 Quick Start (3 Steps)

### Step 1: Prepare Raspberry Pi
```bash
# Flash Raspberry Pi OS (64-bit) to SD card
# Enable SSH and camera in raspi-config
sudo raspi-config
```

### Step 2: Clone and Setup
```bash
# Clone the repository
git clone https://github.com/Andii-12/Magic-mirror-mongolia.git
cd Magic-mirror-mongolia

# Run complete setup
chmod +x setup_pi4_complete.sh
./setup_pi4_complete.sh
```

### Step 3: Start the System
```bash
# Quick start
chmod +x quick_start_pi4.sh
./quick_start_pi4.sh
```

## 📖 Detailed Installation

### 1. System Preparation

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install essential packages
sudo apt install -y git curl wget build-essential python3-pip python3-venv python3-dev

# Install Node.js 22.x
curl -fsSL https://deb.nodesource.com/setup_22.x | sudo -E bash -
sudo apt-get install -y nodejs

# Verify installation
node --version  # Should be 22.x+
npm --version
```

### 2. Python Dependencies

```bash
# Install OpenCV and camera libraries
sudo apt install -y python3-opencv python3-picamera2 python3-numpy

# Install additional packages
pip3 install opencv-python RPi.GPIO numpy face-recognition requests
```

### 3. Face Recognition Setup

```bash
# Create directories
mkdir -p Images /home/pi/haarcascades

# Download face detection model
wget -O /home/pi/haarcascades/haarcascade_frontalface_default.xml \
  https://raw.githubusercontent.com/opencv/opencv/master/data/haarcascades/haarcascade_frontalface_default.xml

# Enable camera
sudo raspi-config
# Navigate to: Interface Options > Camera > Enable
```

### 4. Train Face Recognition

```bash
# Train faces for recognition
python3 train_faces.py

# Test face recognition
python3 test_face_recognition.py
```

## 🎮 Running the System

### Method 1: Quick Start (Recommended)
```bash
./quick_start_pi4.sh
```

### Method 2: Manual Start
```bash
# Terminal 1 - Face recognition
python3 face_recognition_system.py

# Terminal 2 - MagicMirror
npm start
```

### Method 3: System Services
```bash
# Start services
sudo systemctl start magicmirror-face.service
sudo systemctl start magicmirror.service

# Check status
sudo systemctl status magicmirror-face.service
sudo systemctl status magicmirror.service
```

## ⚡ Performance Optimization

### For 1GB RAM Pi 4:
```bash
# Run optimization script
chmod +x pi4_optimization.sh
./pi4_optimization.sh

# Reboot to apply changes
sudo reboot
```

### Manual Optimizations:
```bash
# Disable unnecessary services
sudo systemctl disable bluetooth hciuart ModemManager

# Optimize GPU memory
echo "gpu_mem=64" | sudo tee -a /boot/config.txt

# Set up zram swap
sudo apt install zram-tools
sudo systemctl enable zramswap
```

## 🔧 Configuration

### Face Recognition Status
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

### Personal API Integration
- **API URL**: `https://calendar-app-production-6d2d.up.railway.app/api/magic-mirror/future-data`
- **Update Interval**: 5 minutes
- **User Matching**: Based on face recognition name

### MagicMirror² Config
Located at `config/config.js` - pre-configured for:
- Mongolian language interface
- Personal API integration
- Face recognition modules
- Weather and news feeds
- Mongolian holidays

## 🐛 Troubleshooting

### Common Issues

**1. Camera not working:**
```bash
# Check camera
libcamera-hello --list-cameras
# Enable in raspi-config
sudo raspi-config
```

**2. Face recognition not detecting:**
```bash
# Check status file
cat /tmp/magicmirror_face_status.json
# Test face recognition
python3 test_face_recognition.py
# Train faces
python3 train_faces.py
```

**3. MagicMirror not starting:**
```bash
# Check logs
npm start 2>&1 | tee magicmirror.log
# Check configuration
node js/check_config.js
# Check dependencies
npm install
```

**4. Memory issues:**
```bash
# Check memory usage
free -h
# Monitor performance
./monitor_performance.sh
# Clean up system
./cleanup_system.sh
```

**5. API not working:**
```bash
# Test API connectivity
curl https://calendar-app-production-6d2d.up.railway.app/api/magic-mirror/future-data
# Check network
ping google.com
```

### Debug Commands

```bash
# Check system status
python3 test_system.py

# Monitor performance
./monitor_performance.sh

# Check logs
sudo journalctl -u magicmirror-face.service -f
sudo journalctl -u magicmirror.service -f

# Check processes
ps aux | grep -E "(face_recognition|node|npm)"
```

## 📱 Remote Access

### SSH Access
```bash
# Enable SSH
sudo systemctl enable ssh
sudo systemctl start ssh

# Connect from another device
ssh pi@[PI_IP_ADDRESS]
```

### Web Access
- **Local**: `http://localhost:8080`
- **Remote**: `http://[PI_IP_ADDRESS]:8080`

### VNC Access
```bash
# Install VNC server
sudo apt install realvnc-vnc-server

# Enable VNC
sudo raspi-config
# Navigate to: Interface Options > VNC > Enable
```

## 🔄 Updates and Maintenance

### Update System
```bash
# Update MagicMirror
cd /home/pi/Magic-mirror-mongolia
git pull
npm install

# Update system
sudo apt update && sudo apt upgrade -y
```

### Clean Up
```bash
# Run cleanup script
./cleanup_system.sh

# Clear logs
sudo journalctl --vacuum-time=7d
```

### Backup
```bash
# Backup configuration
tar -czf magicmirror_backup_$(date +%Y%m%d).tar.gz \
  config/ modules/ Images/ trainer.yml
```

## 📊 System Monitoring

### Performance Monitor
```bash
# Real-time monitoring
./monitor_performance.sh
```

### Log Monitoring
```bash
# Face recognition logs
sudo journalctl -u magicmirror-face.service -f

# MagicMirror logs
sudo journalctl -u magicmirror.service -f

# System logs
sudo journalctl -f
```

## 🎯 Features Overview

### Display Layout
- **Top Left**: Clock and calendar
- **Top Right**: Weather (current and forecast)
- **Middle Center**: Personal schedule (from your API)
- **Bottom Bar**: Mongolian news
- **Face Recognition**: Personalized greetings overlay

### Personal API Integration
- Fetches calendar events and todo lists
- Shows only data for recognized users
- Color-coded events
- Completion status for todos
- Real-time updates every 5 minutes

### Face Recognition
- Proximity detection with ultrasonic sensor
- Camera-based face recognition
- Personalized greetings in Mongolian
- User-specific content display
- Auto-hide when no one is present

## 🎉 Success!

Your complete Mongolian MagicMirror² with Personal API integration is ready! The system will:

1. **Boot automatically** on power-on
2. **Detect faces** and show personalized content
3. **Display your calendar** and todos from the API
4. **Show weather** and news in Mongolian
5. **Update in real-time** as people approach

## 📞 Support

If you encounter issues:
1. Check the troubleshooting section
2. Run `python3 test_system.py`
3. Check logs with `sudo journalctl -f`
4. Monitor performance with `./monitor_performance.sh`

---

**Your personalized Mongolian MagicMirror² is ready to use!** 🎉🇲🇳
