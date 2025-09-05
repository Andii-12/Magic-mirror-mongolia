#!/bin/bash

# Raspberry Pi 4 Optimization Script
# Run this to optimize your Pi 4 for MagicMirror²

echo "⚡ Raspberry Pi 4 Optimization for MagicMirror²"
echo "=============================================="
echo ""

# Check available memory
MEMORY=$(free -m | awk 'NR==2{printf "%.0f", $2}')
echo "📊 Current RAM: ${MEMORY}MB"

# Disable unnecessary services
echo "🔧 Disabling unnecessary services..."
sudo systemctl disable bluetooth
sudo systemctl disable hciuart
sudo systemctl disable ModemManager
sudo systemctl disable dphys-swapfile

# Optimize GPU memory split
echo "🎮 Optimizing GPU memory..."
if ! grep -q "gpu_mem=64" /boot/config.txt; then
    echo "gpu_mem=64" | sudo tee -a /boot/config.txt
    echo "✅ GPU memory set to 64MB"
else
    echo "✅ GPU memory already optimized"
fi

# Set up zram for better swap performance
echo "💾 Setting up zram swap..."
if ! dpkg -l | grep -q zram-tools; then
    sudo apt install -y zram-tools
fi

# Configure zram
sudo tee /etc/default/zramswap > /dev/null <<EOF
# Compression algorithm to use
ALGO=lz4

# Maximum amount of RAM to use for compressed swap
PERCENT=50

# Priority for the swap devices
PRIORITY=100
EOF

sudo systemctl enable zramswap
sudo systemctl start zramswap

# Optimize network
echo "🌐 Optimizing network settings..."
sudo tee -a /etc/sysctl.conf > /dev/null <<EOF

# Network optimizations
net.core.rmem_max = 16777216
net.core.wmem_max = 16777216
net.ipv4.tcp_rmem = 4096 65536 16777216
net.ipv4.tcp_wmem = 4096 65536 16777216
EOF

# Disable IPv6 (optional, saves memory)
echo "🔧 Disabling IPv6 (optional)..."
sudo tee -a /etc/sysctl.conf > /dev/null <<EOF

# Disable IPv6
net.ipv6.conf.all.disable_ipv6 = 1
net.ipv6.conf.default.disable_ipv6 = 1
EOF

# Optimize file system
echo "📁 Optimizing file system..."
sudo tee -a /etc/fstab > /dev/null <<EOF

# Optimize SD card performance
tmpfs /tmp tmpfs defaults,noatime,nosuid,size=100m 0 0
tmpfs /var/tmp tmpfs defaults,noatime,nosuid,size=30m 0 0
EOF

# Set up log rotation
echo "📝 Setting up log rotation..."
sudo tee /etc/logrotate.d/magicmirror > /dev/null <<EOF
/home/pi/Magic-mirror-mongolia/*.log {
    daily
    missingok
    rotate 7
    compress
    notifempty
    create 644 pi pi
}
EOF

# Create performance monitoring script
echo "📊 Creating performance monitor..."
cat > monitor_performance.sh << 'EOF'
#!/bin/bash
echo "📊 MagicMirror² Performance Monitor"
echo "=================================="
echo ""

while true; do
    clear
    echo "📊 MagicMirror² Performance Monitor"
    echo "=================================="
    echo ""
    
    # Memory usage
    echo "💾 Memory Usage:"
    free -h | grep -E "Mem|Swap"
    echo ""
    
    # CPU usage
    echo "🖥️  CPU Usage:"
    top -bn1 | grep "Cpu(s)" | awk '{print "   " $2 " user, " $4 " system, " $8 " idle"}'
    echo ""
    
    # Running processes
    echo "🔄 MagicMirror Processes:"
    ps aux | grep -E "(face_recognition|node|npm)" | grep -v grep
    echo ""
    
    # Temperature
    if [ -f "/sys/class/thermal/thermal_zone0/temp" ]; then
        TEMP=$(cat /sys/class/thermal/thermal_zone0/temp)
        TEMP_C=$((TEMP/1000))
        echo "🌡️  CPU Temperature: ${TEMP_C}°C"
        echo ""
    fi
    
    # Disk usage
    echo "💿 Disk Usage:"
    df -h / | tail -1
    echo ""
    
    echo "Press Ctrl+C to exit"
    sleep 5
done
EOF

chmod +x monitor_performance.sh

# Create cleanup script
echo "🧹 Creating cleanup script..."
cat > cleanup_system.sh << 'EOF'
#!/bin/bash
echo "🧹 MagicMirror² System Cleanup"
echo "============================="
echo ""

# Clear logs
echo "📝 Clearing old logs..."
find /home/pi/Magic-mirror-mongolia -name "*.log" -mtime +7 -delete
sudo journalctl --vacuum-time=7d

# Clear temporary files
echo "🗑️  Clearing temporary files..."
rm -rf /tmp/magicmirror_*
rm -rf /var/tmp/*

# Clear package cache
echo "📦 Clearing package cache..."
sudo apt autoremove -y
sudo apt autoclean

# Clear browser cache (if any)
echo "🌐 Clearing browser cache..."
rm -rf ~/.cache/chromium
rm -rf ~/.cache/mozilla

echo "✅ Cleanup complete!"
EOF

chmod +x cleanup_system.sh

# Apply optimizations
echo "🔄 Applying optimizations..."
sudo sysctl -p

# Restart services
echo "🔄 Restarting services..."
sudo systemctl restart zramswap

echo ""
echo "✅ Optimization complete!"
echo ""
echo "📋 What was optimized:"
echo "   ✅ Disabled unnecessary services"
echo "   ✅ Optimized GPU memory (64MB)"
echo "   ✅ Set up zram swap for better performance"
echo "   ✅ Optimized network settings"
echo "   ✅ Disabled IPv6 (saves memory)"
echo "   ✅ Optimized file system"
echo "   ✅ Set up log rotation"
echo "   ✅ Created performance monitoring tools"
echo ""
echo "🛠️  Available tools:"
echo "   ./monitor_performance.sh  - Monitor system performance"
echo "   ./cleanup_system.sh       - Clean up system"
echo ""
echo "🔄 Reboot recommended to apply all optimizations:"
echo "   sudo reboot"
echo ""
