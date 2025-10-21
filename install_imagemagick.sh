#!/bin/bash
# Install ImageMagick for color correction fallback

echo "🔧 Installing ImageMagick for color correction..."
echo "================================================"

# Update package list
sudo apt update

# Install ImageMagick
sudo apt install -y imagemagick

# Verify installation
if command -v convert &> /dev/null; then
    echo "✅ ImageMagick installed successfully!"
    echo "   Version: $(convert -version | head -n1)"
else
    echo "❌ ImageMagick installation failed!"
    exit 1
fi

echo ""
echo "🎯 ImageMagick is now available for color correction fallback!"
echo "   The system will use it if rpicam-still color correction fails."
