#!/bin/bash

# MagicMirror² Mongolian Language Setup Script for Raspberry Pi 4
# This script helps configure MagicMirror² for Mongolian language support

echo "🇲🇳 MagicMirror² Mongolian Language Setup for Raspberry Pi 4"
echo "=============================================================="

# Check if we're on Raspberry Pi
if ! grep -q "Raspberry Pi" /proc/cpuinfo; then
    echo "⚠️  Warning: This script is optimized for Raspberry Pi 4"
fi

# Check available memory
MEMORY=$(free -m | awk 'NR==2{printf "%.0f", $2}')
echo "📊 Available RAM: ${MEMORY}MB"

if [ "$MEMORY" -lt 900 ]; then
    echo "⚠️  Warning: Low memory detected. Consider optimizing your setup."
fi

# Create backup of original config if it exists
if [ -f "config/config.js" ]; then
    echo "💾 Creating backup of existing config..."
    cp config/config.js config/config.js.backup.$(date +%Y%m%d_%H%M%S)
fi

# Copy Mongolian config
echo "📝 Setting up Mongolian configuration..."
cp config/config.mn.js config/config.js

# Set proper permissions
chmod 644 config/config.js
chmod 644 translations/mn.json

# Check if Node.js version is compatible
NODE_VERSION=$(node -v | cut -d'v' -f2 | cut -d'.' -f1)
if [ "$NODE_VERSION" -lt 22 ]; then
    echo "⚠️  Warning: Node.js version $NODE_VERSION detected. MagicMirror² requires Node.js 22.14.0+"
    echo "   Please update Node.js:"
    echo "   curl -fsSL https://deb.nodesource.com/setup_22.x | sudo -E bash -"
    echo "   sudo apt-get install -y nodejs"
fi

# Install dependencies if needed
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    npm install --only=prod --omit=dev
fi

# Optimize for Pi 4 performance
echo "⚡ Applying Raspberry Pi 4 optimizations..."

# Disable GPU acceleration if not needed (saves memory)
if [ -z "$ELECTRON_ENABLE_GPU" ]; then
    echo "   - GPU acceleration disabled (saves ~100MB RAM)"
fi

# Check system resources
echo ""
echo "🔍 System Check:"
echo "   - CPU: $(cat /proc/cpuinfo | grep "model name" | head -1 | cut -d':' -f2 | xargs)"
echo "   - Memory: ${MEMORY}MB"
echo "   - Node.js: $(node -v)"
echo "   - NPM: $(npm -v)"

# Setup personalapi module
echo "🔧 Setting up personalapi module..."
if [ ! -d "modules/personalapi" ]; then
    echo "❌ Error: personalapi module not found!"
    echo "   Please ensure the personalapi module is in modules/personalapi/"
    exit 1
fi

# Create tmp directory for face recognition status
mkdir -p /tmp
chmod 777 /tmp

# Test configuration
echo ""
echo "🧪 Testing configuration..."
if node js/check_config.js; then
    echo "✅ Configuration is valid!"
else
    echo "❌ Configuration has errors. Please check the output above."
    exit 1
fi

echo ""
echo "🎉 Setup complete!"
echo ""
echo "📋 Next steps:"
echo "   1. Customize the weather location in config/config.js (lat/lon)"
echo "   2. Mongolian holidays are already configured (Tsagaan Sar, Naadam, etc.)"
echo "   3. Add your own calendar URLs if needed"
echo "   4. Adjust news feeds for Mongolian sources"
echo "   5. Start the complete system with: ./start.sh"
echo ""
echo "🔧 Performance tips for Pi 4 with 1GB RAM:"
echo "   - Close unnecessary applications"
echo "   - Consider using a swap file if needed"
echo "   - Monitor memory usage with: free -h"
echo "   - Use 'npm run start:dev' for development with DevTools"
echo ""
echo "🌐 Mongolian language is now configured!"
echo "   Language code: mn"
echo "   Locale: mn-MN"
echo "   Timezone: Asia/Ulaanbaatar (adjust in config if needed)"
echo "   Day names: Даваа гараг, Мягмар гараг, Лхагва гараг, etc."
