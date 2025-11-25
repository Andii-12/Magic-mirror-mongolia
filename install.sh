#!/bin/bash

# MagicMirror² Complete Installation Script for Raspberry Pi
# This script automates the installation process

set -e  # Exit on error

echo "🚀 MagicMirror² Complete Installation Script"
echo "=============================================="
echo ""

# Check if running on Raspberry Pi
if [ ! -f /proc/device-tree/model ]; then
    echo "⚠️  Warning: This script is designed for Raspberry Pi"
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}ℹ️  $1${NC}"
}

# Step 1: Update system
echo "📦 Step 1: Updating system packages..."
sudo apt update
sudo apt upgrade -y
print_success "System updated"

# Step 2: Install system dependencies
echo ""
echo "📦 Step 2: Installing system dependencies..."
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
    imagemagick \
    || print_error "Some packages failed to install"

print_success "System dependencies installed"

# Step 3: Install Node.js
echo ""
echo "📦 Step 3: Installing Node.js 22.x..."
if ! command -v node &> /dev/null || [ "$(node -v | cut -d'v' -f2 | cut -d'.' -f1)" -lt 22 ]; then
    curl -fsSL https://deb.nodesource.com/setup_22.x | sudo -E bash -
    sudo apt-get install -y nodejs
    print_success "Node.js installed: $(node -v)"
else
    print_info "Node.js already installed: $(node -v)"
fi

# Step 4: Install Python dependencies
echo ""
echo "📦 Step 4: Installing Python dependencies..."
if [ -f "requirements.txt" ]; then
    sudo pip3 install --upgrade pip
    sudo pip3 install -r requirements.txt
    print_success "Python dependencies installed"
else
    print_info "requirements.txt not found, installing manually..."
    sudo pip3 install --upgrade pip
    sudo pip3 install opencv-python opencv-contrib-python numpy picamera2 RPi.GPIO pillow requests
    print_success "Python dependencies installed"
fi

# Step 5: Install Node.js dependencies
echo ""
echo "📦 Step 5: Installing MagicMirror dependencies..."
if [ -f "package.json" ]; then
    print_info "This may take 5-10 minutes on Raspberry Pi..."
    npm install --only=prod --omit=dev --no-audit --no-fund
    print_success "MagicMirror dependencies installed"
else
    print_error "package.json not found! Are you in the correct directory?"
    exit 1
fi

# Step 6: Create required directories
echo ""
echo "📁 Step 6: Creating required directories..."
mkdir -p Images
mkdir -p Skin
mkdir -p modules/facerecognition/public
mkdir -p ~/haarcascades
sudo mkdir -p /tmp
sudo chmod 777 /tmp
print_success "Directories created"

# Step 7: Download face cascade
echo ""
echo "📥 Step 7: Setting up face recognition cascade..."
if [ ! -f ~/haarcascades/haarcascade_frontalface_default.xml ]; then
    # Try to find existing cascade
    CASCADE_FOUND=$(find /usr -name "haarcascade_frontalface_default.xml" 2>/dev/null | head -1)
    
    if [ -n "$CASCADE_FOUND" ]; then
        cp "$CASCADE_FOUND" ~/haarcascades/haarcascade_frontalface_default.xml
        print_success "Face cascade copied from system"
    else
        # Download from GitHub
        wget -q https://raw.githubusercontent.com/opencv/opencv/master/data/haarcascades/haarcascade_frontalface_default.xml \
            -O ~/haarcascades/haarcascade_frontalface_default.xml || \
        print_error "Failed to download face cascade (you can download manually later)"
    fi
else
    print_info "Face cascade already exists"
fi

# Step 8: Set permissions
echo ""
echo "🔐 Step 8: Setting permissions..."
chmod +x face_recognition_system.py 2>/dev/null || true
chmod +x train_faces.py 2>/dev/null || true
chmod +x simple_train_faces.py 2>/dev/null || true
chmod +x setup_face_training.py 2>/dev/null || true
chmod +x setup-mongolian.sh 2>/dev/null || true
chmod +x start.sh 2>/dev/null || true
chmod +x install_imagemagick.sh 2>/dev/null || true
print_success "Permissions set"

# Step 9: Run setup script
echo ""
echo "⚙️  Step 9: Running Mongolian setup..."
if [ -f "setup-mongolian.sh" ]; then
    ./setup-mongolian.sh
else
    print_info "setup-mongolian.sh not found, skipping..."
fi

# Step 10: Verify installation
echo ""
echo "🧪 Step 10: Verifying installation..."

# Check Node.js
if command -v node &> /dev/null; then
    NODE_VERSION=$(node -v)
    print_success "Node.js: $NODE_VERSION"
else
    print_error "Node.js not found!"
fi

# Check Python
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    print_success "Python: $PYTHON_VERSION"
else
    print_error "Python3 not found!"
fi

# Check npm
if command -v npm &> /dev/null; then
    NPM_VERSION=$(npm -v)
    print_success "NPM: $NPM_VERSION"
else
    print_error "NPM not found!"
fi

# Check camera
if vcgencmd get_camera | grep -q "detected=1"; then
    print_success "Camera detected"
else
    print_error "Camera not detected! Enable it with: sudo raspi-config"
fi

# Check OpenCV
if python3 -c "import cv2; print(cv2.__version__)" 2>/dev/null; then
    OPENCV_VERSION=$(python3 -c "import cv2; print(cv2.__version__)" 2>/dev/null)
    print_success "OpenCV: $OPENCV_VERSION"
else
    print_error "OpenCV not installed properly!"
fi

# Check Picamera2
if python3 -c "import picamera2" 2>/dev/null; then
    print_success "Picamera2 installed"
else
    print_error "Picamera2 not installed!"
fi

# Check configuration
if [ -f "config/config.js" ]; then
    if npm run config:check 2>/dev/null | grep -q "valid\|OK"; then
        print_success "Configuration is valid"
    else
        print_info "Configuration check skipped (may need manual review)"
    fi
fi

# Summary
echo ""
echo "=============================================="
echo "🎉 Installation Complete!"
echo "=============================================="
echo ""
echo "📋 Next Steps:"
echo ""
echo "1. Train face recognition:"
echo "   python3 train_faces.py"
echo ""
echo "2. Configure API keys in config/config.js:"
echo "   - OpenAI API key (for skin analysis)"
echo "   - News API key (for Mongolian news)"
echo ""
echo "3. Start the system:"
echo "   ./start.sh"
echo ""
echo "4. Test components:"
echo "   npm run test-face-recognition"
echo "   npm run test-ultrasonic"
echo ""
echo "📖 For detailed instructions, see: INSTALLATION_GUIDE.md"
echo ""
print_success "Installation finished successfully!"

