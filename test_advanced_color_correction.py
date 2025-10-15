#!/usr/bin/env python3
"""
Advanced Color Correction Test for MagicMirror²
Tests multiple color correction algorithms to fix skin tone issues
"""

import cv2
import numpy as np
import time
from picamera2 import Picamera2
import libcamera

def apply_color_corrections(frame_rgb):
    """Apply multiple color correction methods and return results"""
    
    corrections = {}
    
    # Method 1: Basic RGB to BGR conversion
    corrections['basic_bgr'] = cv2.cvtColor(frame_rgb, cv2.COLOR_RGB2BGR)
    
    # Method 2: LAB color space correction
    frame_bgr = cv2.cvtColor(frame_rgb, cv2.COLOR_RGB2BGR)
    lab = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    
    # Reduce blue tint in B channel
    b = cv2.add(b, 10)  # Shift towards yellow
    a = cv2.add(a, 5)   # Shift towards red
    
    lab_corrected = cv2.merge([l, a, b])
    corrections['lab_corrected'] = cv2.cvtColor(lab_corrected, cv2.COLOR_LAB2BGR)
    
    # Method 3: HSV color space correction
    hsv = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2HSV)
    h, s, v = cv2.split(hsv)
    
    # Adjust hue to reduce purple/blue tint
    h = cv2.add(h, 5)  # Shift hue towards warmer tones
    s = cv2.multiply(s, 1.1)  # Increase saturation slightly
    v = cv2.multiply(v, 1.05)  # Increase brightness slightly
    
    hsv_corrected = cv2.merge([h, s, v])
    corrections['hsv_corrected'] = cv2.cvtColor(hsv_corrected, cv2.COLOR_HSV2BGR)
    
    # Method 4: BGR channel manipulation
    b, g, r = cv2.split(frame_bgr)
    
    # Reduce blue channel significantly
    b = cv2.multiply(b, 0.8)  # Reduce blue by 20%
    # Increase red channel
    r = cv2.multiply(r, 1.1)  # Increase red by 10%
    # Slightly increase green
    g = cv2.multiply(g, 1.02)  # Increase green by 2%
    
    corrections['channel_adjusted'] = cv2.merge([b, g, r])
    
    # Method 5: Gamma correction
    gamma = 1.1
    frame_gamma = np.power(frame_bgr / 255.0, gamma) * 255.0
    corrections['gamma_corrected'] = np.uint8(frame_gamma)
    
    # Method 6: Combined correction (most aggressive)
    # Start with channel adjustment
    b, g, r = cv2.split(frame_bgr)
    b = cv2.multiply(b, 0.75)  # Reduce blue by 25%
    r = cv2.multiply(r, 1.15)  # Increase red by 15%
    g = cv2.multiply(g, 1.05)  # Increase green by 5%
    
    combined = cv2.merge([b, g, r])
    
    # Apply gamma correction
    gamma = 1.15
    combined = np.power(combined / 255.0, gamma) * 255.0
    combined = np.uint8(combined)
    
    # Apply CLAHE for contrast
    lab = cv2.cvtColor(combined, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
    l = clahe.apply(l)
    lab = cv2.merge([l, a, b])
    corrections['combined_correction'] = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)
    
    return corrections

def test_camera_color_corrections():
    """Test camera with different color correction methods"""
    
    print("🎨 Advanced Color Correction Test for MagicMirror²")
    print("=" * 60)
    
    try:
        # Initialize camera
        camera = Picamera2()
        config = camera.create_preview_configuration(
            main={"size": (640, 480), "format": "RGB888"},
            transform=libcamera.Transform(hflip=0, vflip=0)
        )
        camera.configure(config)
        camera.start()
        time.sleep(1)
        
        print("📸 Capturing test frame...")
        frame_rgb = camera.capture_array()
        print(f"   Frame shape: {frame_rgb.shape}")
        
        # Apply all color corrections
        print("🔧 Applying color corrections...")
        corrections = apply_color_corrections(frame_rgb)
        
        # Save all corrected images
        print("💾 Saving corrected images...")
        for method_name, corrected_frame in corrections.items():
            filename = f"color_test_{method_name}_1080x1080.jpg"
            
            # Resize to 1080x1080 for consistency
            resized = cv2.resize(corrected_frame, (1080, 1080))
            
            success = cv2.imwrite(filename, resized, [cv2.IMWRITE_JPEG_QUALITY, 95])
            if success:
                print(f"   ✅ Saved: {filename}")
            else:
                print(f"   ❌ Failed: {filename}")
        
        camera.stop()
        camera.close()
        
        print("\n🎯 Color Correction Test Complete!")
        print("Check the saved images to see which method gives the best skin tones:")
        print("   • basic_bgr: Simple RGB to BGR conversion")
        print("   • lab_corrected: LAB color space adjustment")
        print("   • hsv_corrected: HSV color space adjustment")
        print("   • channel_adjusted: BGR channel manipulation")
        print("   • gamma_corrected: Gamma correction")
        print("   • combined_correction: All methods combined (recommended)")
        
    except Exception as e:
        print(f"❌ Error during color correction test: {e}")

def test_skin_tone_detection():
    """Test skin tone detection and correction"""
    
    print("\n👤 Skin Tone Detection Test")
    print("=" * 40)
    
    # Define skin tone ranges in different color spaces
    skin_ranges = {
        'hsv': {
            'lower': np.array([0, 20, 70], dtype=np.uint8),
            'upper': np.array([20, 255, 255], dtype=np.uint8)
        },
        'ycrcb': {
            'lower': np.array([80, 133, 77], dtype=np.uint8),
            'upper': np.array([255, 173, 127], dtype=np.uint8)
        }
    }
    
    try:
        camera = Picamera2()
        config = camera.create_preview_configuration(
            main={"size": (640, 480), "format": "RGB888"},
            transform=libcamera.Transform(hflip=0, vflip=0)
        )
        camera.configure(config)
        camera.start()
        time.sleep(1)
        
        frame_rgb = camera.capture_array()
        frame_bgr = cv2.cvtColor(frame_rgb, cv2.COLOR_RGB2BGR)
        
        # Test skin tone detection in HSV
        hsv = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2HSV)
        skin_mask_hsv = cv2.inRange(hsv, skin_ranges['hsv']['lower'], skin_ranges['hsv']['upper'])
        
        # Test skin tone detection in YCrCb
        ycrcb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2YCrCb)
        skin_mask_ycrcb = cv2.inRange(ycrcb, skin_ranges['ycrcb']['lower'], skin_ranges['ycrcb']['upper'])
        
        # Combine masks
        skin_mask = cv2.bitwise_or(skin_mask_hsv, skin_mask_ycrcb)
        
        # Apply morphological operations to clean up the mask
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        skin_mask = cv2.morphologyEx(skin_mask, cv2.MORPH_OPEN, kernel)
        skin_mask = cv2.morphologyEx(skin_mask, cv2.MORPH_CLOSE, kernel)
        
        # Apply mask to original image
        skin_only = cv2.bitwise_and(frame_bgr, frame_bgr, mask=skin_mask)
        
        # Save results
        cv2.imwrite("skin_detection_original_1080.jpg", cv2.resize(frame_bgr, (1080, 1080)))
        cv2.imwrite("skin_detection_mask_1080.jpg", cv2.resize(skin_mask, (1080, 1080)))
        cv2.imwrite("skin_detection_only_1080.jpg", cv2.resize(skin_only, (1080, 1080)))
        
        print("✅ Skin tone detection test completed")
        print("   • skin_detection_original_1080.jpg: Original image")
        print("   • skin_detection_mask_1080.jpg: Detected skin areas")
        print("   • skin_detection_only_1080.jpg: Skin areas only")
        
        camera.stop()
        camera.close()
        
    except Exception as e:
        print(f"❌ Error during skin tone detection: {e}")

if __name__ == "__main__":
    print("🔧 Advanced Color Correction Test for MagicMirror²")
    print("This script will test multiple color correction methods to fix skin tone issues.")
    print("\nMake sure you're in good lighting conditions for accurate testing.")
    print("Press Enter to continue...")
    input()
    
    test_camera_color_corrections()
    test_skin_tone_detection()
    
    print("\n✅ All advanced color correction tests completed!")
    print("Review the generated images to determine the best color correction method.")
    print("The 'combined_correction' method is recommended for the best results.")
