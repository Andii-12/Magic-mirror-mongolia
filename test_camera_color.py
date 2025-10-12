#!/usr/bin/env python3
"""
Test script to verify camera color output
"""

import cv2
import time
import os
from datetime import datetime
from picamera2 import Picamera2

print("="*70)
print("CAMERA COLOR TEST")
print("="*70)

# Initialize camera
print("\n1. Initializing camera...")
try:
    camera = Picamera2()
    print("✅ Camera initialized")
except Exception as e:
    print(f"❌ Camera initialization failed: {e}")
    exit(1)

# Test different formats
formats_to_test = [
    ("RGB888", cv2.COLOR_RGB2BGR),
    ("BGR888", None),  # No conversion needed
]

test_dir = "Skin/ColorTest"
os.makedirs(test_dir, exist_ok=True)

for format_name, conversion in formats_to_test:
    print(f"\n{'='*70}")
    print(f"Testing format: {format_name}")
    print(f"{'='*70}")
    
    try:
        # Stop camera if running
        try:
            camera.stop()
        except:
            pass
        
        # Configure for high-res capture
        config = camera.create_still_configuration(
            main={"size": (1920, 1080), "format": format_name},
            buffer_count=1
        )
        
        print(f"[INFO] Configuring camera with {format_name}...")
        camera.configure(config)
        camera.start()
        
        # Let camera adjust (important for color balance!)
        print(f"[INFO] Waiting for auto white balance and exposure...")
        time.sleep(1.0)  # Longer wait for better color
        
        # Capture frame
        print(f"[INFO] Capturing frame...")
        frame = camera.capture_array("main")
        print(f"[INFO] Captured shape: {frame.shape}")
        
        # Convert if needed
        if conversion is not None:
            print(f"[INFO] Converting color space...")
            frame = cv2.cvtColor(frame, conversion)
            save_name = f"{format_name}_converted"
        else:
            print(f"[INFO] No conversion needed (already BGR)")
            save_name = format_name
        
        # Save image
        filename = f"{test_dir}/test_{save_name}_{datetime.now().strftime('%H-%M-%S')}.jpg"
        print(f"[INFO] Saving to: {filename}")
        success = cv2.imwrite(filename, frame, [cv2.IMWRITE_JPEG_QUALITY, 95])
        
        if success and os.path.exists(filename):
            file_size = os.path.getsize(filename)
            print(f"✅ Saved successfully!")
            print(f"   File: {filename}")
            print(f"   Size: {file_size} bytes ({file_size/1024:.2f} KB)")
            
            # Analyze colors
            b, g, r = cv2.split(frame)
            print(f"   Color channels:")
            print(f"      Blue  (B): min={b.min()}, max={b.max()}, mean={b.mean():.1f}")
            print(f"      Green (G): min={g.min()}, max={g.max()}, mean={g.mean():.1f}")
            print(f"      Red   (R): min={r.min()}, max={r.max()}, mean={r.mean():.1f}")
        else:
            print(f"❌ Failed to save")
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

# Cleanup
try:
    camera.stop()
    camera.close()
except:
    pass

print("\n" + "="*70)
print("TEST COMPLETE")
print("="*70)
print(f"\nTest images saved to: {test_dir}/")
print(f"View them to see which format has correct colors!")
print(f"\nCommand to view files:")
print(f"  ls -lh {test_dir}/")
print(f"\nExpected: BGR888 (no conversion) should have correct colors")
print("="*70)

