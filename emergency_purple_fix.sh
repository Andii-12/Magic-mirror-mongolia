#!/bin/bash

# Emergency Purple Skin Tone Fix for MagicMirror²
# Applies the most aggressive color correction settings

echo "🚨 EMERGENCY PURPLE SKIN TONE FIX"
echo "================================="

# Check if running on Raspberry Pi
if ! grep -q "Raspberry Pi" /proc/cpuinfo; then
    echo "❌ This script is designed for Raspberry Pi only"
    exit 1
fi

echo "📸 Applying EMERGENCY color correction for purple skin tones..."

# 1. Test with most aggressive libcamera-still settings
echo "1️⃣ Testing ULTRA-AGGRESSIVE libcamera-still settings..."

libcamera-still -o "EMERGENCY_PURPLE_FIX_ULTRA.jpg" \
    -t 2000 \
    -n \
    --width 1080 \
    --height 1080 \
    --awb daylight \
    --saturation 1.5 \
    --contrast 1.3 \
    --brightness 0.2 \
    --sharpness 1.2 \
    --denoise cdn_off \
    --metering average

echo "   ✅ Saved: EMERGENCY_PURPLE_FIX_ULTRA.jpg"

# 2. Test with tungsten white balance (warmer tones)
echo "2️⃣ Testing with tungsten white balance (warmer tones)..."

libcamera-still -o "EMERGENCY_PURPLE_FIX_TUNGSTEN.jpg" \
    -t 2000 \
    -n \
    --width 1080 \
    --height 1080 \
    --awb tungsten \
    --saturation 1.4 \
    --contrast 1.2 \
    --brightness 0.15 \
    --sharpness 1.1

echo "   ✅ Saved: EMERGENCY_PURPLE_FIX_TUNGSTEN.jpg"

# 3. Test with cloudy white balance (neutral tones)
echo "3️⃣ Testing with cloudy white balance (neutral tones)..."

libcamera-still -o "EMERGENCY_PURPLE_FIX_CLOUDY.jpg" \
    -t 2000 \
    -n \
    --width 1080 \
    --height 1080 \
    --awb cloudy \
    --saturation 1.3 \
    --contrast 1.25 \
    --brightness 0.18 \
    --sharpness 1.15

echo "   ✅ Saved: EMERGENCY_PURPLE_FIX_CLOUDY.jpg"

# 4. Test with fluorescent white balance
echo "4️⃣ Testing with fluorescent white balance..."

libcamera-still -o "EMERGENCY_PURPLE_FIX_FLUORESCENT.jpg" \
    -t 2000 \
    -n \
    --width 1080 \
    --height 1080 \
    --awb fluorescent \
    --saturation 1.35 \
    --contrast 1.2 \
    --brightness 0.16 \
    --sharpness 1.1

echo "   ✅ Saved: EMERGENCY_PURPLE_FIX_FLUORESCENT.jpg"

# 5. Run Python test with aggressive correction
echo "5️⃣ Running Python aggressive correction test..."

if [ -f "test_purple_skin_fix.py" ]; then
    python3 test_purple_skin_fix.py
    echo "   ✅ Python correction test completed"
else
    echo "   ⚠️ Python test script not found"
fi

# 6. Summary
echo ""
echo "🚨 EMERGENCY PURPLE SKIN TONE FIX COMPLETE"
echo "=========================================="
echo "Generated emergency test images:"
echo "   • EMERGENCY_PURPLE_FIX_ULTRA.jpg - Ultra-aggressive settings"
echo "   • EMERGENCY_PURPLE_FIX_TUNGSTEN.jpg - Tungsten white balance"
echo "   • EMERGENCY_PURPLE_FIX_CLOUDY.jpg - Cloudy white balance"
echo "   • EMERGENCY_PURPLE_FIX_FLUORESCENT.jpg - Fluorescent white balance"
echo ""
echo "🔍 CHECK THESE IMAGES IMMEDIATELY:"
echo "   ✅ Look for natural skin tones (not purple/lavender)"
echo "   ✅ Eyes should appear normal (not yellow/orange)"
echo "   ✅ Overall image should look natural and warm"
echo ""
echo "🎯 RECOMMENDATIONS:"
echo "   1. If ULTRA settings work best, use saturation 1.5, contrast 1.3"
echo "   2. If tungsten works best, use --awb tungsten"
echo "   3. If cloudy works best, use --awb cloudy"
echo "   4. Update your face_recognition_system.py with the best settings"
echo ""
echo "⚡ URGENT NEXT STEPS:"
echo "   1. Review all emergency test images"
echo "   2. Identify which settings give the best skin tones"
echo "   3. Update the face_recognition_system.py accordingly"
echo "   4. Test with your actual face recognition system"
echo ""
echo "✅ Emergency fix complete!"
