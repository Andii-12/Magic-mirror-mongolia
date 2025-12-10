# 🚀 Raspberry Pi Installation Guide

Complete step-by-step installation guide for MagicMirror² with Face Recognition on Raspberry Pi 4.

---

## 📋 Prerequisites

- **Raspberry Pi 4** (1GB+ RAM recommended)
- **Raspberry Pi OS** (Bullseye or newer)
- **Camera Module** (Raspberry Pi Camera v2 or v3)
- **Ultrasonic Sensor** (HC-SR04) - GPIO pins 5 (TRIG) and 6 (ECHO)
- **Relay Module** (12V) - GPIO pin 18
- **Internet connection** for initial setup

---

## 🔧 Step 1: System Setup

### 1.1 Update Raspberry Pi OS

```bash
sudo apt update
sudo apt upgrade -y
sudo reboot
```

### 1.2 Enable Camera Interface

```bash
sudo raspi-config
```

Navigate to:
- **Interface Options** → **Camera** → **Enable**
- **Interface Options** → **I2C** → **Enable** (if needed)
- **Advanced Options** → **Expand Filesystem** → **Enable**

Reboot after changes:
```bash
sudo reboot
```

### 1.3 Install System Dependencies

```bash
# Install essential build tools
sudo apt install -y \
    build-essential \
    python3 \
    python3-pip \
    python3-dev \
    python3-venv \
    git \
    curl \
    wget \
    libcamera-dev \
    libcamera-apps \
    libopencv-dev \
    python3-opencv \
    libatlas-base-dev \
    libjpeg-dev \
    libpng-dev \
    libtiff-dev \
    libavcodec-dev \
    libavformat-dev \
    libswscale-dev \
    libv4l-dev \
    libxvidcore-dev \
    libx264-dev \
    libfontconfig1-dev \
    libcairo2-dev \
    libgdk-pixbuf2.0-dev \
    libpango1.0-dev \
    libgtk2.0-dev \
    libgtk-3-dev \
    libatlas-base-dev \
    liblapack-dev \
    libblas-dev \
    libhdf5-dev \
    libhdf5-serial-dev \
    libharfbuzz0b \
    libwebp-dev \
    libtiff5-dev \
    libopenexr-dev \
    libgstreamer1.0-dev \
    libgstreamer-plugins-base1.0-dev \
    libavresample-dev \
    libtheora-dev \
    libvorbis-dev \
    libx264-dev \
    libopencore-amrnb-dev \
    libopencore-amrwb-dev \
    libv4l-dev \
    libxvidcore-dev \
    libtbb-dev \
    libeigen3-dev \
    python3-pyqt5 \
    libqt5gui5 \
    libqt5webkit5 \
    libqt5test5 \
    python3-pyqt5 \
    qtbase5-dev \
    qtchooser \
    qt5-qmake \
    qtbase5-dev-tools \
    imagemagick
```

### 1.4 Install ImageMagick (for color correction)

```bash
chmod +x install_imagemagick.sh
./install_imagemagick.sh
```

Or manually:
```bash
sudo apt install -y imagemagick
```

---

## 📦 Step 2: Install Node.js

MagicMirror² requires **Node.js 22.14.0 or higher**.

### 2.1 Install Node.js 22.x

```bash
# Download and install Node.js 22.x
curl -fsSL https://deb.nodesource.com/setup_22.x | sudo -E bash -
sudo apt-get install -y nodejs

# Verify installation
node -v  # Should show v22.x.x
npm -v   # Should show 10.x.x
```

### 2.2 Install PM2 (Optional - for process management)

```bash
sudo npm install -g pm2
```

---

## 🐍 Step 3: Install Python Dependencies

### 3.1 Install Python Packages

```bash
# Install required Python packages
sudo pip3 install --upgrade pip
sudo pip3 install \
    opencv-python \
    opencv-contrib-python \
    numpy \
    picamera2 \
    RPi.GPIO \
    pillow \
    requests
```

**Note:** If `opencv-python` installation fails, try:
```bash
sudo apt install -y python3-opencv
```

### 3.2 Verify Camera Access

```bash
# Test camera
libcamera-hello --list-cameras
libcamera-hello -t 0  # Preview camera (press Ctrl+C to exit)
```

Or with rpicam:
```bash
rpicam-hello --list-cameras
rpicam-hello -t 0
```

---

## 📥 Step 4: Clone/Download MagicMirror Project

### 4.1 Navigate to Home Directory

```bash
cd ~
```

### 4.2 Clone or Copy Project

If you have the project files, copy them to:
```bash
# Create directory
mkdir -p ~/MagicMirror-master
cd ~/MagicMirror-master

# Copy your project files here (via USB, SCP, or Git)
```

Or if using Git:
```bash
git clone <your-repo-url> ~/MagicMirror-master
cd ~/MagicMirror-master
```

---

## 📦 Step 5: Install MagicMirror Dependencies

### 5.1 Install Node.js Dependencies

```bash
cd ~/MagicMirror-master

# Install production dependencies only (faster, smaller)
npm install --only=prod --omit=dev --no-audit --no-fund

# OR install all dependencies (for development)
npm install --no-audit --no-fund
```

**Note:** This may take 5-10 minutes on Raspberry Pi.

### 5.2 Verify Installation

```bash
# Check if node_modules exists
ls -la node_modules/ | head -20

# Test configuration
npm run config:check
```

---

## 🎯 Step 6: Setup Face Recognition

### 6.1 Create Required Directories

```bash
cd ~/MagicMirror-master

# Create directories for face training
mkdir -p Images
mkdir -p Skin
mkdir -p modules/facerecognition/public

# Create tmp directory for status file
sudo mkdir -p /tmp
sudo chmod 777 /tmp
```

### 6.2 Install Face Cascade (if not already present)

```bash
# Check if haarcascade exists
if [ ! -f "/home/pi/haarcascades/haarcascade_frontalface_default.xml" ]; then
    # Create directory
    mkdir -p ~/haarcascades
    
    # Download haarcascade
    cd ~/haarcascades
    wget https://raw.githubusercontent.com/opencv/opencv/master/data/haarcascades/haarcascade_frontalface_default.xml
    
    # Or copy from OpenCV installation
    sudo find /usr -name "haarcascade_frontalface_default.xml" -exec cp {} ~/haarcascades/ \;
fi
```

### 6.3 Set Permissions

```bash
cd ~/MagicMirror-master

# Make Python scripts executable
chmod +x face_recognition_system.py
chmod +x train_faces.py
chmod +x simple_train_faces.py
chmod +x setup_face_training.py

# Make shell scripts executable
chmod +x setup-mongolian.sh
chmod +x start.sh
chmod +x install_imagemagick.sh
```

---

## ⚙️ Step 7: Configure System

### 7.1 Run Setup Script

```bash
cd ~/MagicMirror-master
./setup-mongolian.sh
```

This script will:
- ✅ Check system requirements
- ✅ Setup Mongolian language configuration
- ✅ Install dependencies
- ✅ Verify configuration

### 7.2 Configure Face Recognition Paths

Edit `face_recognition_system.py` if needed:
```python
# Line 33: Update cascade path if different
CASCADE_PATH = "/home/pi/haarcascades/haarcascade_frontalface_default.xml"
```

### 7.3 Configure API Keys

Edit `config/config.js`:

```javascript
// Line 135: Mongolian News API key
apiKey: "pub_cb951c5b3961435ea0feb4edc321f1d2",  // Replace with your key

// Line 240: OpenAI API key for skin analysis
apiKey: "sk-...",  // Replace with your OpenAI API key
```

---

## 🎓 Step 8: Train Face Recognition

### 8.1 Setup Training Environment

```bash
cd ~/MagicMirror-master
python3 setup_face_training.py
```

This creates the `Images/` directory structure.

### 8.2 Add Training Photos

For each person, add **40+ photos** to:
```
Images/
├── Andii/     # Add 40+ photos here
├── Jane/      # Add 40+ photos here
└── Default/   # Add 40+ photos here
```

**Photo Requirements:**
- ✅ Clear, front-facing photos
- ✅ Good lighting
- ✅ Different expressions
- ✅ Formats: `.jpg`, `.jpeg`, `.png`, `.bmp`

### 8.3 Train the Model

**Option 1: Interactive Training (Recommended)**
```bash
python3 train_faces.py
# Follow the menu:
# 1. Setup directories
# 2. Collect images with webcam
# 3. Process existing images
# 4. Train face recognition model
# 5. Test trained model
# 7. Complete training workflow
```

**Option 2: Simple Training**
```bash
python3 simple_train_faces.py
```

### 8.4 Verify Training

After training, you should have:
- ✅ `trainer.yml` - Trained model
- ✅ `labels.json` - Person labels

Test the training:
```bash
npm run test-face-confidence
# or
python3 test_face_confidence.py
```

---

## 🚀 Step 9: Start the System

### 9.1 Test Individual Components

**Test Ultrasonic Sensor:**
```bash
npm run test-ultrasonic
# or
python3 scripts/test-ultrasonic-sensor.py
```

**Test Face Recognition (Test Mode):**
```bash
npm run test-face-recognition
# or
FACE_RECOGNITION_TEST=true python3 face_recognition_system.py
```

**Test Relay:**
```bash
python3 scripts/test-relay.py
```

### 9.2 Start Complete System

**Option 1: Using Start Script (Recommended)**
```bash
cd ~/MagicMirror-master
./start.sh
```

**Option 2: Manual Start**
```bash
cd ~/MagicMirror-master

# Terminal 1: Start face recognition
python3 face_recognition_system.py &

# Terminal 2: Start MagicMirror
npm start
```

**Option 3: Using PM2 (Background Process)**
```bash
cd ~/MagicMirror-master

# Start face recognition
pm2 start face_recognition_system.py --name face-recognition --interpreter python3

# Start MagicMirror
pm2 start npm --name magicmirror -- start

# View logs
pm2 logs

# Save PM2 configuration
pm2 save
pm2 startup
```

---

## 🔧 Step 10: Auto-Start on Boot (Optional)

### 10.1 Create Systemd Service

Create `/etc/systemd/system/magicmirror.service`:

```bash
sudo nano /etc/systemd/system/magicmirror.service
```

Add:
```ini
[Unit]
Description=MagicMirror² with Face Recognition
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/MagicMirror-master
ExecStart=/bin/bash /home/pi/MagicMirror-master/start.sh
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### 10.2 Enable Service

```bash
sudo systemctl daemon-reload
sudo systemctl enable magicmirror.service
sudo systemctl start magicmirror.service

# Check status
sudo systemctl status magicmirror.service

# View logs
sudo journalctl -u magicmirror.service -f
```

---

## 🧪 Troubleshooting

### Camera Issues

```bash
# Check camera is enabled
vcgencmd get_camera

# Should return: supported=1 detected=1

# Test camera
libcamera-hello -t 0
```

### GPIO Issues

```bash
# Check GPIO permissions
groups  # Should include 'gpio'

# Add user to gpio group
sudo usermod -a -G gpio $USER
# Log out and back in
```

### Node.js Issues

```bash
# Clear npm cache
npm cache clean --force

# Reinstall dependencies
rm -rf node_modules package-lock.json
npm install --only=prod --omit=dev
```

### Python Issues

```bash
# Reinstall Python packages
sudo pip3 install --upgrade --force-reinstall opencv-python picamera2 RPi.GPIO numpy

# Check Python version
python3 --version  # Should be 3.7+
```

### Memory Issues (1GB RAM)

```bash
# Increase swap space
sudo dphys-swapfile swapoff
sudo nano /etc/dphys-swapfile
# Change CONF_SWAPSIZE=100 to CONF_SWAPSIZE=2048
sudo dphys-swapfile setup
sudo dphys-swapfile swapon
```

---

## 📝 Quick Reference Commands

```bash
# Start system
./start.sh

# Test face recognition
npm run test-face-recognition

# Test ultrasonic sensor
npm run test-ultrasonic

# Check configuration
npm run config:check

# Train faces
python3 train_faces.py

# View face recognition logs
tail -f /tmp/magicmirror_face_status.json

# Check system resources
free -h
df -h
top
```

---

## ✅ Verification Checklist

- [ ] Node.js 22.x installed (`node -v`)
- [ ] Python 3.7+ installed (`python3 --version`)
- [ ] Camera enabled and working
- [ ] GPIO permissions set
- [ ] MagicMirror dependencies installed (`npm install`)
- [ ] Python packages installed (`pip3 install`)
- [ ] Face recognition trained (`trainer.yml` exists)
- [ ] Configuration valid (`npm run config:check`)
- [ ] Status file created (`/tmp/magicmirror_face_status.json`)
- [ ] System starts successfully (`./start.sh`)

---

## 🎉 Success!

Your MagicMirror² system should now be running! 

- **MagicMirror UI**: http://localhost:8080
- **Face Recognition**: Running in background
- **Status File**: `/tmp/magicmirror_face_status.json`

**Next Steps:**
1. Train faces for all users
2. Configure API keys in `config/config.js`
3. Customize weather location
4. Adjust proximity threshold if needed
5. Test relay lights

---

## 📞 Support

If you encounter issues:
1. Check logs: `tail -f /tmp/magicmirror_face_status.json`
2. Test components individually
3. Verify all dependencies are installed
4. Check GPIO connections
5. Review configuration files

**Happy Mirroring! 🪞✨**

