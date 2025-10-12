# 🔍 Raspberry Pi - Debug Steps for Skin Photo Feature

## Your Situation
- ✅ Face recognition is working (showing "Сайн уу [name]")
- ❌ Photos are NOT being taken/saved
- ❌ Skin folder is NOT being created

## 📋 Follow These Steps on Your Raspberry Pi

### Step 1: Upload Files to Raspberry Pi

Make sure these files are on your Raspberry Pi:
- `face_recognition_system.py` (modified version with enhanced logging)
- `test_skin_photo.py` (test script)
- `diagnose_skin_photo.sh` (diagnostic script)
- `run_with_debug.sh` (debug runner)

### Step 2: Make Scripts Executable

```bash
chmod +x diagnose_skin_photo.sh
chmod +x run_with_debug.sh
chmod +x test_skin_photo.py
```

### Step 3: Run Diagnostic Script

```bash
./diagnose_skin_photo.sh
```

**What to look for:**
- ✅ All checks should pass
- ✅ Test file should be created in `Skin/TestUser/`
- ❌ If any check fails, note the error

### Step 4: Run Face Recognition with Debug Logging

```bash
./run_with_debug.sh
```

This will:
1. Start face recognition system
2. Save all output to a log file
3. Show you SKIN PHOTO messages and errors

### Step 5: Trigger Face Recognition

1. Stand in front of the camera (< 20cm)
2. Wait for face recognition
3. Watch the console output carefully

**Look for these messages:**

✅ **Success - Should see:**
```
✅ Face recognition successful: [YourName]

============================================================
[SKIN PHOTO] Starting photo capture for: [YourName]
============================================================
[INFO] Platform detected: Linux
[INFO] Base directory: /home/pi/MagicMirror/Skin
[INFO] Person directory: /home/pi/MagicMirror/Skin/[YourName]
✅ Directories created/verified
✅ Directory exists and is accessible
[INFO] Photo filename: 2025-10-12.jpg
[INFO] Reconfiguring camera for high-res capture...
[INFO] Camera configured to 1920x1080
[INFO] Capturing frame...
[INFO] Frame captured: (1080, 1920, 3)
✅ File created successfully!
✅ SKIN PHOTO SAVED SUCCESSFULLY!
============================================================
```

❌ **Problem - Look for:**
```
[ERROR] Camera not initialized
[ERROR] Failed to create directory
[ERROR] cv2.imwrite returned False
[ERROR] File does not exist after write
```

### Step 6: Verify Results

After face recognition:

```bash
# Check if Skin folder exists
ls -la | grep Skin

# Check person folders
ls -la Skin/

# Check photos
ls -la Skin/YourName/

# View photo details
file Skin/YourName/*.jpg
```

## 🔍 Common Issues on Raspberry Pi

### Issue 1: No SKIN PHOTO messages appear

**Possible causes:**
1. Face recognition failed (confidence > 80)
2. Function not being called
3. Code file not updated on Pi

**Check:**
```bash
# Verify the function call is in the code
grep -n "save_skin_photo" face_recognition_system.py

# Should show line ~476:
# self.save_skin_photo(name)
```

### Issue 2: Camera not initialized

**Check camera:**
```bash
# Check if camera is detected
vcgencmd get_camera
# Should show: supported=1 detected=1

# Test camera manually
libcamera-still -o test_camera.jpg

# Check if photo was created
ls -la test_camera.jpg
```

**If camera not working:**
```bash
# Enable camera
sudo raspi-config
# Navigate to: Interface Options > Camera > Enable
sudo reboot
```

### Issue 3: Permission denied

**Fix permissions:**
```bash
# Check current directory permissions
ls -ld .

# Make directory writable if needed
chmod 755 .

# Try creating Skin folder manually
mkdir -p Skin/TestUser
echo "test" > Skin/TestUser/test.txt

# If this works, the issue is in the code
```

### Issue 4: Disk space full

**Check and clean:**
```bash
# Check disk space
df -h

# Clean up if needed
sudo apt-get clean
sudo apt-get autoremove

# Remove old logs
rm -f *.log
```

## 📊 Quick Checklist

Run through this checklist:

- [ ] Files uploaded to Raspberry Pi
- [ ] Scripts made executable (`chmod +x`)
- [ ] Diagnostic script run (`./diagnose_skin_photo.sh`)
- [ ] All diagnostic checks passed
- [ ] Face recognition system started (`./run_with_debug.sh`)
- [ ] Face successfully recognized (see name in console)
- [ ] Look for `[SKIN PHOTO]` messages in console
- [ ] Check for `[ERROR]` messages
- [ ] Verify `Skin/` folder created (`ls -la Skin/`)
- [ ] Check for photo files (`ls -la Skin/YourName/`)

## 🎯 What to Do Next

### If Diagnostic Script Passes But Photos Still Not Saved:

1. **Capture the log file:**
   ```bash
   ./run_with_debug.sh
   # After face recognition, press Ctrl+C
   # Log file will be saved
   ```

2. **Check the log for SKIN PHOTO messages:**
   ```bash
   grep -A 20 "SKIN PHOTO" face_recognition_debug_*.log
   ```

3. **Check for errors:**
   ```bash
   grep "ERROR" face_recognition_debug_*.log
   ```

4. **Share the output:**
   - Copy the SKIN PHOTO section from the log
   - Copy any ERROR messages
   - This will show exactly where it's failing

### If No SKIN PHOTO Messages Appear:

The function is not being called. Check:

```bash
# 1. Verify code has the function call
grep -C 5 "save_skin_photo" face_recognition_system.py | grep -A 5 "Face recognition successful"

# 2. Check confidence level
# Look in the log for:
grep "Confidence:" face_recognition_debug_*.log
# Confidence should be < 80 to trigger photo
```

## 💡 Expected Console Output

When everything works, you should see this sequence:

```
[INFO] Object detected at 15.2cm. Starting recognition...
[INFO] 1 face(s) detected
[INFO] Recognized: YourName (Confidence: 45.23)
✅ Face recognition successful: YourName

============================================================
[SKIN PHOTO] Starting photo capture for: YourName
============================================================
[INFO] Platform detected: Linux
[INFO] Base directory: /home/pi/MagicMirror/Skin
[INFO] Person directory: /home/pi/MagicMirror/Skin/YourName
✅ Directories created/verified: /home/pi/MagicMirror/Skin/YourName
✅ Directory exists and is accessible
[INFO] Photo filename: 2025-10-12.jpg
[INFO] Full path: /home/pi/MagicMirror/Skin/YourName/2025-10-12.jpg
[INFO] Reconfiguring camera for high-res capture...
[INFO] Camera configured to 1920x1080
[INFO] Capturing frame...
[INFO] Frame captured: (1080, 1920, 3)
[INFO] Converting color space...
[INFO] Writing image to disk...
✅ File created successfully!
   Path: /home/pi/MagicMirror/Skin/YourName/2025-10-12.jpg
   Size: 523456 bytes (511.19 KB)

✅ SKIN PHOTO SAVED SUCCESSFULLY!
   Person: YourName
   File: /home/pi/MagicMirror/Skin/YourName/2025-10-12.jpg
   Resolution: 1920x1080, Quality: 95%
============================================================
```

## 🚀 Quick Start

Run these commands in order on your Raspberry Pi:

```bash
# 1. Run diagnostics
./diagnose_skin_photo.sh

# 2. Run face recognition with logging
./run_with_debug.sh

# 3. After recognition, check results
ls -laR Skin/

# 4. View the log
cat face_recognition_debug_*.log | grep -A 30 "SKIN PHOTO"
```

The enhanced logging will show **exactly** what's happening!

---

**Need help?** Share the output from the diagnostic script and the face recognition log.

