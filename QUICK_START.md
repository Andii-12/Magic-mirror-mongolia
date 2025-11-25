# ⚡ Quick Start Guide

Fast installation and startup commands for Raspberry Pi.

---

## 🚀 One-Command Installation

```bash
# Make install script executable and run
chmod +x install.sh
./install.sh
```

This will install everything automatically!

---

## 📦 Manual Installation (Step by Step)

### 1. Install System Dependencies
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y build-essential python3 python3-pip git curl libcamera-dev libcamera-apps python3-opencv imagemagick
```

### 2. Install Node.js 22.x
```bash
curl -fsSL https://deb.nodesource.com/setup_22.x | sudo -E bash -
sudo apt-get install -y nodejs
```

### 3. Install Python Packages
```bash
sudo pip3 install --upgrade pip
sudo pip3 install -r requirements.txt
# OR manually:
sudo pip3 install opencv-python numpy picamera2 RPi.GPIO pillow requests
```

### 4. Install MagicMirror Dependencies
```bash
npm install --only=prod --omit=dev --no-audit --no-fund
```

### 5. Setup Mongolian Configuration
```bash
chmod +x setup-mongolian.sh
./setup-mongolian.sh
```

---

## 🎓 Train Face Recognition

```bash
# Interactive training (recommended)
python3 train_faces.py

# Quick training
python3 simple_train_faces.py
```

**Add photos to:** `Images/PersonName/` (40+ photos per person)

---

## ▶️ Start the System

```bash
# Start everything (face recognition + MagicMirror)
./start.sh

# OR manually:
# Terminal 1:
python3 face_recognition_system.py &

# Terminal 2:
npm start
```

---

## 🧪 Test Components

```bash
# Test face recognition (simulation mode)
npm run test-face-recognition

# Test ultrasonic sensor
npm run test-ultrasonic

# Test face confidence display
npm run test-face-confidence

# Test relay
python3 scripts/test-relay.py

# Check configuration
npm run config:check
```

---

## 🔧 Common Commands

```bash
# View face recognition status
cat /tmp/magicmirror_face_status.json

# Check system resources
free -h
df -h

# View logs (if using PM2)
pm2 logs

# Restart system
./start.sh
```

---

## ⚙️ Configuration Files

- **MagicMirror Config**: `config/config.js`
- **Face Recognition**: `face_recognition_system.py` (lines 20-35)
- **Training Images**: `Images/PersonName/`
- **Skin Photos**: `Skin/PersonName/`

---

## 🐛 Quick Troubleshooting

**Camera not working:**
```bash
sudo raspi-config  # Enable camera
vcgencmd get_camera  # Check status
```

**GPIO permission denied:**
```bash
sudo usermod -a -G gpio $USER
# Log out and back in
```

**Node.js version wrong:**
```bash
curl -fsSL https://deb.nodesource.com/setup_22.x | sudo -E bash -
sudo apt-get install -y nodejs
```

**Python packages missing:**
```bash
sudo pip3 install -r requirements.txt
```

**Memory issues (1GB RAM):**
```bash
# Increase swap
sudo dphys-swapfile swapoff
sudo nano /etc/dphys-swapfile  # Change to 2048
sudo dphys-swapfile setup
sudo dphys-swapfile swapon
```

---

## 📍 File Locations

```
~/MagicMirror-master/
├── face_recognition_system.py  # Main Python script
├── config/config.js             # MagicMirror config
├── Images/                      # Training photos
├── Skin/                        # Skin analysis photos
├── trainer.yml                  # Trained model
├── labels.json                  # Person labels
└── /tmp/magicmirror_face_status.json  # Status file
```

---

## 🎯 Essential Settings

**In `config/config.js`:**
- Line 240: OpenAI API key (for skin analysis)
- Line 135: News API key (for Mongolian news)
- Line 104-105: Weather coordinates (Ulaanbaatar)

**In `face_recognition_system.py`:**
- Line 29: Proximity threshold (20cm)
- Line 33: Cascade path
- Line 25: Relay GPIO pin (18)

---

## ✅ Verification Checklist

- [ ] Node.js 22.x: `node -v`
- [ ] Python 3.7+: `python3 --version`
- [ ] Camera enabled: `vcgencmd get_camera`
- [ ] Dependencies installed: `npm list` and `pip3 list`
- [ ] Face recognition trained: `ls trainer.yml`
- [ ] Configuration valid: `npm run config:check`
- [ ] System starts: `./start.sh`

---

**For detailed instructions, see:** `INSTALLATION_GUIDE.md`

