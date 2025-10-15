#!/usr/bin/env python3
"""
Yellow-Green Color Cast Fix Test for MagicMirror²
Tests color correction specifically for yellow-green skin tone issues
"""

import cv2
import numpy as np
import time
from picamera2 import Picamera2
import libcamera

def test_yellow_green_fix():
    """Test color correction for yellow-green skin cast"""
    
    print("🟡🟢 YELLOW-GREEN SKIN TONE FIX TEST")
    print("=" * 50)
    print("This test will capture images with yellow-green color correction")
    print("to fix the sickly yellow-green skin tone issue.")
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
        
        # Test 1: Capture with yellow-green correction
        print("🔧 Test 1: Capturing with YELLOW-GREEN color correction...")
        
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
        
        # Apply yellow-green correction
        corrected_frame = apply_yellow_green_correction(frame_rgb)
        
        # Save corrected image
        cv2.imwrite("YELLOW_GREEN_FIX_TEST_1080.jpg", corrected_frame, [cv2.IMWRITE_JPEG_QUALITY, 95])
        print("   ✅ Saved: YELLOW_GREEN_FIX_TEST_1080.jpg")
        
        # Test 2: Compare with different libcamera-still settings
        print("")
        print("🔧 Test 2: Testing libcamera-still with tungsten white balance...")
        
        import subprocess
        
        # Test tungsten white balance (warmer tones)
        cmd_tungsten = [
            "libcamera-still",
            "-o", "YELLOW_GREEN_FIX_TUNGSTEN_1080.jpg",
            "--width", "1080",
            "--height", "1080",
            "-t", "1000",
            "-n",
            "--awb", "tungsten",
            "--saturation", "0.8",
            "--contrast", "1.1",
            "--brightness", "0.05",
            "--sharpness", "1.0"
        ]
        
        result = subprocess.run(cmd_tungsten, capture_output=True, text=True, timeout=5)
        
        if result.returncode == 0:
            print("   ✅ Saved: YELLOW_GREEN_FIX_TUNGSTEN_1080.jpg")
        else:
            print(f"   ❌ libcamera-still failed: {result.stderr}")
        
        # Test 3: Test with cloudy white balance
        print("")
        print("🔧 Test 3: Testing with cloudy white balance...")
        
        cmd_cloudy = [
            "libcamera-still",
            "-o", "YELLOW_GREEN_FIX_CLOUDY_1080.jpg",
            "--width", "1080",
            "--height", "1080",
            "-t", "1000",
            "-n",
            "--awb", "cloudy",
            "--saturation", "0.7",
            "--contrast", "1.05",
            "--brightness", "0.1",
            "--sharpness", "1.0"
        ]
        
        result = subprocess.run(cmd_cloudy, capture_output=True, text=True, timeout=5)
        
        if result.returncode == 0:
            print("   ✅ Saved: YELLOW_GREEN_FIX_CLOUDY_1080.jpg")
        else:
            print(f"   ❌ libcamera-still failed: {result.stderr}")
        
        # Restore preview configuration
        camera.stop()
        camera.configure(preview_config)
        camera.start()
        
        # Test 4: Quick preview tests
        print("")
        print("🔧 Test 4: Quick preview with yellow-green correction...")
        
        for i in range(3):
            frame_rgb = camera.capture_array()
            corrected = apply_yellow_green_correction(frame_rgb)
            filename = f"YELLOW_GREEN_FIX_PREVIEW_{i+1}.jpg"
            cv2.imwrite(filename, corrected, [cv2.IMWRITE_JPEG_QUALITY, 95])
            print(f"   ✅ Saved: {filename}")
            time.sleep(0.5)
        
        camera.stop()
        camera.close()
        
        print("")
        print("🎯 YELLOW-GREEN SKIN TONE FIX TEST COMPLETE!")
        print("=" * 50)
        print("Generated test images:")
        print("   • YELLOW_GREEN_FIX_TEST_1080.jpg - Main correction test")
        print("   • YELLOW_GREEN_FIX_TUNGSTEN_1080.jpg - Tungsten white balance")
        print("   • YELLOW_GREEN_FIX_CLOUDY_1080.jpg - Cloudy white balance")
        print("   • YELLOW_GREEN_FIX_PREVIEW_1-3.jpg - Quick preview tests")
        print("")
        print("🔍 CHECK THESE IMAGES:")
        print("   ✅ Skin should appear natural/warm (not yellow-green)")
        print("   ✅ Colors should look balanced and natural")
        print("   ✅ Overall image should have proper color temperature")
        print("   ✅ No sickly yellow-green cast")
        print("")
        print("🎯 BEST SETTINGS:")
        print("   • Tungsten white balance counteracts yellow-green")
        print("   • Reduced saturation prevents over-saturation")
        print("   • -35% green, +30% red, +5% blue channel correction")
        print("   • Hue shift away from yellow-green spectrum")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")

def apply_yellow_green_correction(frame_rgb):
    """Apply yellow-green color correction (same as updated face_recognition_system.py)"""
    try:
        # Convert RGB to BGR
        frame_bgr = cv2.cvtColor(frame_rgb, cv2.COLOR_RGB2BGR)
        
        print(f"   Original BGR means: B={frame_bgr[:,:,0].mean():.1f}, G={frame_bgr[:,:,1].mean():.1f}, R={frame_bgr[:,:,2].mean():.1f}")
        
        # YELLOW-GREEN color channel correction
        b, g, r = cv2.split(frame_bgr)
        
        # Reduce green by 35% (yellow-green skin fix)
        g_corrected = cv2.multiply(g, 0.65)
        
        # Increase red by 30% (natural skin tones)
        r_corrected = cv2.multiply(r, 1.3)
        
        # Increase blue by 5% (natural balance)
        b_corrected = cv2.multiply(b, 1.05)
        
        frame_channel_corrected = cv2.merge([b_corrected, g_corrected, r_corrected])
        
        # LAB color space correction
        lab = cv2.cvtColor(frame_channel_corrected, cv2.COLOR_BGR2LAB)
        l, a, b_lab = cv2.split(lab)
        
        # CLAHE for contrast
        clahe = cv2.createCLAHE(clipLimit=4.0, tileGridSize=(8,8))
        l = clahe.apply(l)
        
        # Strong LAB adjustments for yellow-green
        a = cv2.add(a, 15)  # Shift towards red
        b_lab = cv2.subtract(b_lab, 10)  # Shift away from yellow
        
        lab_corrected = cv2.merge([l, a, b_lab])
        frame_lab_corrected = cv2.cvtColor(lab_corrected, cv2.COLOR_LAB2BGR)
        
        # HSV hue adjustment
        hsv = cv2.cvtColor(frame_lab_corrected, cv2.COLOR_BGR2HSV)
        h, s, v = cv2.split(hsv)
        
        h = cv2.subtract(h, 12)  # Shift hue away from yellow-green
        s = cv2.multiply(s, 0.85)  # Reduce saturation
        v = cv2.multiply(v, 1.05)  # Increase brightness
        
        hsv_corrected = cv2.merge([h, s, v])
        frame_hsv_corrected = cv2.cvtColor(hsv_corrected, cv2.COLOR_HSV2BGR)
        
        # Gamma correction
        gamma = 1.2
        frame_final = np.power(frame_hsv_corrected / 255.0, gamma) * 255.0
        frame_final = np.uint8(frame_final)
        
        print(f"   Corrected BGR means: B={frame_final[:,:,0].mean():.1f}, G={frame_final[:,:,1].mean():.1f}, R={frame_final[:,:,2].mean():.1f}")
        print(f"   Applied: -35% green, +30% red, +5% blue, gamma={gamma}")
        
        return frame_final
        
    except Exception as e:
        print(f"   ⚠️ Correction failed: {e}")
        return cv2.cvtColor(frame_rgb, cv2.COLOR_RGB2BGR)

if __name__ == "__main__":
    print("🟡🟢 URGENT: Yellow-Green Skin Tone Fix Test")
    print("This will test the color correction to fix yellow-green skin issues.")
    print("")
    print("Make sure you're in good lighting conditions.")
    print("Press Enter to start the test...")
    input()
    
    test_yellow_green_fix()
    
    print("")
    print("✅ Test completed! Check the generated images for results.")
