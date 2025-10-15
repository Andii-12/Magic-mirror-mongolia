#!/usr/bin/env python3
"""
Immediate Test for Purple Skin Tone Fix
Tests the aggressive color correction specifically for purple/lavender skin issues
"""

import cv2
import numpy as np
import time
from picamera2 import Picamera2
import libcamera

def test_immediate_color_fix():
    """Test immediate color correction for purple skin tones"""
    
    print("🚨 IMMEDIATE PURPLE SKIN TONE FIX TEST")
    print("=" * 50)
    print("This test will capture images with the new aggressive color correction")
    print("to fix purple/lavender skin tone issues.")
    print("")
    
    try:
        # Initialize camera
        print("📸 Initializing camera...")
        camera = Picamera2()
        
        # Preview configuration
        preview_config = camera.create_preview_configuration(
            main={"size": (640, 480), "format": "RGB888"},
            transform=libcamera.Transform(hflip=0, vflip=0)
        )
        camera.configure(preview_config)
        camera.start()
        time.sleep(1)
        
        print("✅ Camera ready!")
        print("")
        
        # Test 1: Capture with new aggressive correction
        print("🔧 Test 1: Capturing with AGGRESSIVE color correction...")
        
        # Configure for high-res capture
        still_config = camera.create_still_configuration(
            main={"size": (1080, 1080), "format": "RGB888"},
            buffer_count=1,
            transform=libcamera.Transform(hflip=0, vflip=0)
        )
        
        camera.stop()
        camera.configure(still_config)
        camera.start()
        time.sleep(0.5)
        
        # Capture frame
        frame_rgb = camera.capture_array("main")
        print(f"   Captured frame: {frame_rgb.shape}")
        
        # Apply the new aggressive correction
        corrected_frame = apply_aggressive_correction(frame_rgb)
        
        # Save corrected image
        cv2.imwrite("PURPLE_FIX_TEST_1080.jpg", corrected_frame, [cv2.IMWRITE_JPEG_QUALITY, 95])
        print("   ✅ Saved: PURPLE_FIX_TEST_1080.jpg")
        
        # Test 2: Compare with libcamera-still
        print("")
        print("🔧 Test 2: Testing libcamera-still with aggressive settings...")
        
        import subprocess
        
        cmd = [
            "libcamera-still",
            "-o", "PURPLE_FIX_LIBCAMERA_1080.jpg",
            "--width", "1080",
            "--height", "1080",
            "-t", "1000",
            "-n",
            "--awb", "daylight",
            "--saturation", "1.4",
            "--contrast", "1.2",
            "--brightness", "0.15",
            "--sharpness", "1.1",
            "--denoise", "cdn_off"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
        
        if result.returncode == 0:
            print("   ✅ Saved: PURPLE_FIX_LIBCAMERA_1080.jpg")
        else:
            print(f"   ❌ libcamera-still failed: {result.stderr}")
        
        # Restore preview configuration
        camera.stop()
        camera.configure(preview_config)
        camera.start()
        
        # Test 3: Quick preview test
        print("")
        print("🔧 Test 3: Quick preview with color correction...")
        
        for i in range(3):
            frame_rgb = camera.capture_array()
            corrected = apply_aggressive_correction(frame_rgb)
            filename = f"PURPLE_FIX_PREVIEW_{i+1}.jpg"
            cv2.imwrite(filename, corrected, [cv2.IMWRITE_JPEG_QUALITY, 95])
            print(f"   ✅ Saved: {filename}")
            time.sleep(0.5)
        
        camera.stop()
        camera.close()
        
        print("")
        print("🎯 PURPLE SKIN TONE FIX TEST COMPLETE!")
        print("=" * 50)
        print("Generated test images:")
        print("   • PURPLE_FIX_TEST_1080.jpg - Main correction test")
        print("   • PURPLE_FIX_LIBCAMERA_1080.jpg - libcamera-still test")
        print("   • PURPLE_FIX_PREVIEW_1-3.jpg - Quick preview tests")
        print("")
        print("🔍 CHECK THESE IMAGES:")
        print("   ✅ Skin should appear natural/warm (not purple/lavender)")
        print("   ✅ Eyes should appear normal (not yellow/orange)")
        print("   ✅ Overall colors should look natural")
        print("   ✅ Image should have good contrast and detail")
        print("")
        print("If colors still look wrong, the issue may be:")
        print("   1. Hardware-level camera problem")
        print("   2. Lighting conditions")
        print("   3. Need even more aggressive correction")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")

def apply_aggressive_correction(frame_rgb):
    """Apply the same aggressive correction as in face_recognition_system.py"""
    try:
        # Convert RGB to BGR
        frame_bgr = cv2.cvtColor(frame_rgb, cv2.COLOR_RGB2BGR)
        
        print(f"   Original BGR means: B={frame_bgr[:,:,0].mean():.1f}, G={frame_bgr[:,:,1].mean():.1f}, R={frame_bgr[:,:,2].mean():.1f}")
        
        # AGGRESSIVE color channel correction
        b, g, r = cv2.split(frame_bgr)
        
        # Reduce blue by 40% (purple skin fix)
        b_corrected = cv2.multiply(b, 0.6)
        
        # Increase red by 25% (warm skin tones)
        r_corrected = cv2.multiply(r, 1.25)
        
        # Increase green by 8% (natural balance)
        g_corrected = cv2.multiply(g, 1.08)
        
        frame_channel_corrected = cv2.merge([b_corrected, g_corrected, r_corrected])
        
        # LAB color space correction
        lab = cv2.cvtColor(frame_channel_corrected, cv2.COLOR_BGR2LAB)
        l, a, b_lab = cv2.split(lab)
        
        # CLAHE for contrast
        clahe = cv2.createCLAHE(clipLimit=4.0, tileGridSize=(8,8))
        l = clahe.apply(l)
        
        # Strong LAB adjustments
        a = cv2.add(a, 12)  # Shift towards red
        b_lab = cv2.add(b_lab, 15)  # Shift towards yellow
        
        lab_corrected = cv2.merge([l, a, b_lab])
        frame_lab_corrected = cv2.cvtColor(lab_corrected, cv2.COLOR_LAB2BGR)
        
        # HSV hue adjustment
        hsv = cv2.cvtColor(frame_lab_corrected, cv2.COLOR_BGR2HSV)
        h, s, v = cv2.split(hsv)
        
        h = cv2.add(h, 8)  # Shift hue away from purple
        s = cv2.multiply(s, 1.1)  # Increase saturation
        v = cv2.multiply(v, 1.05)  # Increase brightness
        
        hsv_corrected = cv2.merge([h, s, v])
        frame_hsv_corrected = cv2.cvtColor(hsv_corrected, cv2.COLOR_HSV2BGR)
        
        # Gamma correction
        gamma = 1.2
        frame_final = np.power(frame_hsv_corrected / 255.0, gamma) * 255.0
        frame_final = np.uint8(frame_final)
        
        print(f"   Corrected BGR means: B={frame_final[:,:,0].mean():.1f}, G={frame_final[:,:,1].mean():.1f}, R={frame_final[:,:,2].mean():.1f}")
        print(f"   Applied: -40% blue, +25% red, +8% green, gamma={gamma}")
        
        return frame_final
        
    except Exception as e:
        print(f"   ⚠️ Correction failed: {e}")
        return cv2.cvtColor(frame_rgb, cv2.COLOR_RGB2BGR)

if __name__ == "__main__":
    print("🚨 URGENT: Purple Skin Tone Fix Test")
    print("This will test the aggressive color correction to fix purple/lavender skin issues.")
    print("")
    print("Make sure you're in good lighting conditions.")
    print("Press Enter to start the test...")
    input()
    
    test_immediate_color_fix()
    
    print("")
    print("✅ Test completed! Check the generated images for results.")
