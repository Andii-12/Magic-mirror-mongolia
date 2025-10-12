# 🔧 Skin Photo Feature - Troubleshooting Guide

## Problem: Folders Not Created / Photos Not Saved

If the `Skin/` folder is not being created and photos are not being saved, follow these steps:

---

## Step 1: Run the Test Script

First, let's verify that basic file operations work:

```bash
# Make the test script executable
chmod +x test_skin_photo.py

# Run the test
python3 test_skin_photo.py
```

**Expected Output:**
```
====================================================================
SKIN PHOTO FEATURE - DEBUG TEST
====================================================================

1. CHECKING CURRENT DIRECTORY
--------------------------------------------------
Current working directory: /home/pi/MagicMirror

2. TESTING DIRECTORY CREATION
--------------------------------------------------
Base directory will be: /home/pi/MagicMirror/Skin
Person directory will be: /home/pi/MagicMirror/Skin/TestUser
✅ Directories created successfully!
✅ Directory exists and is accessible

3. TESTING FILE CREATION
--------------------------------------------------
Test file will be: /home/pi/MagicMirror/Skin/TestUser/test_2025-10-12.txt
✅ Test file created
✅ File exists!
   Size: 67 bytes

[... more tests ...]

✅ All tests passed!
```

**If test fails:** Note the error message and continue to Step 2.

---

## Step 2: Check Platform

The code skips photo saving on Windows by default. Check your platform:

```bash
python3 -c "import platform; print(f'Platform: {platform.system()}')"
```

**If Windows:**
- Set environment variable to enable test mode:
  ```bash
  # Windows PowerShell
  $env:SKIN_PHOTO_TEST="1"
  
  # Windows CMD
  set SKIN_PHOTO_TEST=1
  
  # Linux/Mac
  export SKIN_PHOTO_TEST=1
  ```

**If Raspberry Pi/Linux:** Continue to Step 3.

---

## Step 3: Check Logs During Recognition

Run the face recognition system and watch for detailed logs:

```bash
# Start the system
python3 face_recognition_system.py

# Watch for these log messages after face recognition:
```

**Look for:**
```
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
============================================================
```

---

## Common Issues & Solutions

### Issue 1: "Windows detected - skipping photo save"

**Cause:** Running on Windows without test mode enabled.

**Solution:**
```bash
# Enable test mode
export SKIN_PHOTO_TEST=1  # Linux/Mac
$env:SKIN_PHOTO_TEST="1"  # Windows PowerShell

# Then run again
python3 face_recognition_system.py
```

---

### Issue 2: "Camera not initialized, cannot save photo"

**Cause:** Camera failed to initialize.

**Solution:**
```bash
# Check camera
vcgencmd get_camera
# Should show: supported=1 detected=1

# Test camera manually
libcamera-still -o test.jpg

# If camera not working, fix camera first
sudo raspi-config
# Navigate to Interface Options > Camera > Enable
```

---

### Issue 3: No logs appear for photo saving

**Cause:** Function is not being called.

**Check:**
1. Is face recognition working?
2. Is confidence threshold met (< 80)?
3. Is the function being called?

**Debug:**
```bash
# Add temporary debug line in face_recognition_system.py
# After line 358 where save_skin_photo() is called:
print("DEBUG: About to call save_skin_photo()")
self.save_skin_photo(name)
print("DEBUG: save_skin_photo() returned")
```

---

### Issue 4: Directory permission denied

**Cause:** No write permissions in current directory.

**Solution:**
```bash
# Check current user
whoami

# Check directory permissions
ls -ld .
ls -ld Skin/ 2>/dev/null

# Fix permissions if needed
chmod 755 .
chmod 755 Skin/ 2>/dev/null
```

---

### Issue 5: Disk full

**Cause:** No space left on device.

**Solution:**
```bash
# Check disk space
df -h .

# Clean up if needed
sudo apt-get clean
sudo apt-get autoremove

# Check again
df -h .
```

---

### Issue 6: Working directory is wrong

**Cause:** Script is running from different directory.

**Solution:**
```bash
# Check where script is running from
python3 -c "import os; print(f'CWD: {os.getcwd()}')"

# Navigate to correct directory
cd /path/to/MagicMirror

# Then run
python3 face_recognition_system.py
```

---

## Step 4: Manual Test

Let's manually test the photo saving function:

```python
# Create test file: test_manual_photo.py
import os
from datetime import datetime

# Test directory creation
person_name = "ManualTest"
skin_base = os.path.join(os.getcwd(), "Skin")
person_dir = os.path.join(skin_base, person_name)

print(f"Creating: {person_dir}")

try:
    os.makedirs(person_dir, exist_ok=True)
    print("✅ Directory created")
    
    # Test file creation
    current_date = datetime.now().strftime("%Y-%m-%d")
    test_file = os.path.join(person_dir, f"{current_date}.txt")
    
    with open(test_file, 'w') as f:
        f.write(f"Manual test at {datetime.now()}\n")
    
    print(f"✅ File created: {test_file}")
    print(f"✅ SUCCESS! File system is working correctly.")
    
    # Verify
    if os.path.exists(test_file):
        print(f"✅ File verified: {os.path.getsize(test_file)} bytes")
    
except Exception as e:
    print(f"❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
```

Run it:
```bash
python3 test_manual_photo.py
```

---

## Step 5: Check Face Recognition Integration

Verify the function is being called:

```bash
# Search for the function call
grep -n "save_skin_photo" face_recognition_system.py

# Should show line ~358:
# self.save_skin_photo(name)
```

**If not found:** The function call might be missing. Check line 358 in `face_recognition_system.py`.

---

## Step 6: Enable Maximum Logging

Add extra logging to see exactly what's happening:

```python
# Edit face_recognition_system.py
# At the top of save_skin_photo() function (line ~198), add:
print(f"\n{'='*70}")
print(f"SAVE_SKIN_PHOTO CALLED!")
print(f"Person: {person_name}")
print(f"Session flag: {self.photo_saved_this_session}")
print(f"Camera: {self.camera}")
print(f"Platform: {platform.system()}")
print(f"{'='*70}\n")
```

---

## Step 7: Verify File After Recognition

After face recognition completes:

```bash
# Check if Skin folder was created
ls -la | grep Skin

# If exists, check contents
ls -la Skin/

# Check specific person
ls -la Skin/YourName/

# Check file details
file Skin/YourName/*.jpg
```

---

## Expected Behavior

**When Working Correctly:**

1. Face recognized → Console shows:
   ```
   ============================================================
   [SKIN PHOTO] Starting photo capture for: YourName
   ============================================================
   ```

2. Directories created → Shows:
   ```
   ✅ Directories created/verified
   ✅ Directory exists and is accessible
   ```

3. Photo captured → Shows:
   ```
   ✅ File created successfully!
   ```

4. File system shows:
   ```bash
   $ ls -la Skin/YourName/
   -rw-r--r-- 1 pi pi 523456 Oct 12 10:30 2025-10-12.jpg
   ```

---

## Quick Diagnostic Checklist

- [ ] Test script passes (`python3 test_skin_photo.py`)
- [ ] Platform is Linux/Raspberry Pi (or test mode enabled on Windows)
- [ ] Camera is initialized (`vcgencmd get_camera`)
- [ ] Face recognition is working (person name detected)
- [ ] Confidence threshold met (< 80)
- [ ] Function is being called (logs appear)
- [ ] Write permissions are correct (`ls -ld .`)
- [ ] Disk space available (`df -h .`)
- [ ] Running from correct directory (`pwd`)
- [ ] No errors in console output

---

## Still Not Working?

### Collect Debug Info

Run this command and save the output:

```bash
# Create debug report
{
    echo "=== SYSTEM INFO ==="
    uname -a
    python3 --version
    
    echo -e "\n=== PLATFORM ==="
    python3 -c "import platform; print(f'Platform: {platform.system()}')"
    
    echo -e "\n=== CURRENT DIRECTORY ==="
    pwd
    ls -la | head -20
    
    echo -e "\n=== DISK SPACE ==="
    df -h .
    
    echo -e "\n=== SKIN FOLDER ==="
    ls -la Skin/ 2>&1 || echo "Skin folder does not exist"
    
    echo -e "\n=== CAMERA ==="
    vcgencmd get_camera 2>&1 || echo "Not a Raspberry Pi"
    
    echo -e "\n=== TEST ==="
    python3 test_skin_photo.py 2>&1
    
} > skin_photo_debug.txt

# View the report
cat skin_photo_debug.txt
```

Share this debug report for further assistance.

---

## Contact for Help

If you've tried all these steps and it's still not working, please provide:

1. Debug report (`skin_photo_debug.txt`)
2. Console output from face recognition
3. Platform (Windows/Linux/Raspberry Pi)
4. Python version
5. Any error messages

---

## Success Criteria

✅ **Everything is working when:**

1. Face recognition completes successfully
2. Console shows "SKIN PHOTO SAVED SUCCESSFULLY"
3. `Skin/YourName/` directory exists
4. `2025-10-12.jpg` file exists (or current date)
5. File size is ~500KB - 1MB
6. File can be opened as a valid image

---

Good luck! The detailed logging should help you identify exactly where the issue is occurring. 🎯

