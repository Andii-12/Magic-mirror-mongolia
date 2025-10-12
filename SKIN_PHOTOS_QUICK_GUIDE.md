# 📸 Skin Photo Feature - Quick Reference

## How It Works

```
┌─────────────────────────────────────────────────────────┐
│  1. APPROACH MIRROR                                      │
│     Distance < 20cm                                      │
└─────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│  2. FACE RECOGNITION                                     │
│     Camera detects and recognizes face                  │
│     Confidence < 80 = Success                           │
└─────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│  3. CAPTURE HIGH-RES PHOTO                              │
│     📷 1920x1080 @ 95% quality                          │
│     ⏱️  Takes ~0.5 seconds                              │
└─────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│  4. SAVE TO FOLDER                                       │
│     📁 Skin/YourName/2025-10-12.jpg                     │
│     💾 ~500KB - 1MB per photo                           │
└─────────────────────────────────────────────────────────┘
```

---

## 📁 Folder Structure

```
MagicMirror/
├── Skin/                          ← New folder (auto-created)
│   ├── Andii/
│   │   ├── 2025-10-12.jpg        ← One photo per day
│   │   ├── 2025-10-13.jpg
│   │   └── 2025-10-14.jpg
│   ├── Jane/
│   │   └── 2025-10-12.jpg
│   └── Guest/
│       └── 2025-10-12.jpg
└── face_recognition_system.py     ← Modified file
```

---

## 🎯 Key Features

| Feature | Description |
|---------|-------------|
| **Automatic** | Captures photo after face recognition |
| **High Quality** | 1920x1080 resolution, 95% JPEG quality |
| **Smart Naming** | `YYYY-MM-DD.jpg` (adds time if duplicate) |
| **One Per Session** | Only one photo per recognition session |
| **Local Storage** | All photos saved on device |
| **Auto-Organize** | Separate folder for each person |

---

## 🚀 Quick Commands

### View Your Photos
```bash
# List all your photos
ls -la Skin/YourName/

# View most recent photo
ls -lt Skin/YourName/ | head -n 2

# Count total photos
find Skin/YourName/ -name "*.jpg" | wc -l
```

### Check Photo Details
```bash
# View file info
file Skin/YourName/2025-10-12.jpg

# Check file size
du -h Skin/YourName/2025-10-12.jpg

# View photo dimensions
identify Skin/YourName/2025-10-12.jpg
```

### Manage Storage
```bash
# Check total storage used
du -sh Skin/

# Backup photos
tar -czf skin_backup_$(date +%Y-%m-%d).tar.gz Skin/

# Delete old photos (30+ days)
find Skin/ -name "*.jpg" -mtime +30 -delete
```

---

## ⚙️ When Photos Are Taken

### ✅ Photo IS Taken When:
- Face successfully recognized (confidence < 80)
- First recognition of the session
- Camera is working properly
- Running on Raspberry Pi (not Windows)

### ❌ Photo NOT Taken When:
- Face not recognized (low confidence)
- Already saved one photo this session
- User moved away before capture
- Camera not initialized
- Running on Windows (development mode)

---

## 🔧 Troubleshooting

### Problem: No Photos Being Saved

**Check 1: Is camera working?**
```bash
vcgencmd get_camera
# Should show: supported=1 detected=1
```

**Check 2: Test camera manually**
```bash
libcamera-still -o test.jpg
```

**Check 3: Check permissions**
```bash
ls -ld Skin/
# Should show: drwxr-xr-x (readable/writable)
```

**Check 4: Check disk space**
```bash
df -h .
# Ensure you have free space
```

---

### Problem: Photos Are Blurry

**Solution 1: Check lighting**
- Ensure good lighting conditions
- Avoid backlighting

**Solution 2: Clean camera lens**
```bash
# Gently clean camera lens with soft cloth
```

**Solution 3: Check camera focus**
- Some cameras have manual focus
- Ensure proper distance from mirror

---

### Problem: Multiple Photos Same Day

This is **normal** behavior:
- First photo: `2025-10-12.jpg`
- Second photo (same day): `2025-10-12_14-30-45.jpg`
- System adds timestamp to prevent overwriting

---

## 📊 Storage Estimates

| Usage Pattern | Photos/Month | Storage/Month |
|---------------|--------------|---------------|
| Once daily | 30 | ~15-30 MB |
| Twice daily | 60 | ~30-60 MB |
| 5x daily | 150 | ~75-150 MB |
| 10x daily | 300 | ~150-300 MB |

**Note:** Estimates assume 500KB-1MB per photo

---

## 🔒 Privacy Tips

### Keep Photos Private
```bash
# Set restrictive permissions
chmod 700 Skin/

# Only you can access:
# 7 (owner) = read/write/execute
# 0 (group) = no access
# 0 (others) = no access
```

### Regular Backups
```bash
# Create encrypted backup
tar -czf - Skin/ | gpg -c > skin_backup.tar.gz.gpg

# Restore from backup
gpg -d skin_backup.tar.gz.gpg | tar -xzf -
```

### Delete After Backup
```bash
# After backing up to external drive
rm -rf Skin/
```

---

## 📱 View Photos on Phone

### Method 1: USB Transfer
1. Connect Raspberry Pi via USB
2. Copy `Skin/` folder to phone
3. View with photo app

### Method 2: Network Transfer
```bash
# On Raspberry Pi, start simple web server
cd Skin
python3 -m http.server 8000

# On phone, open browser to:
http://[raspberry-pi-ip]:8000
```

### Method 3: Cloud Sync (Advanced)
- Set up automatic sync to Google Photos
- Use Dropbox/OneDrive sync
- Configure Nextcloud/ownCloud

---

## 🎨 Creative Uses

### Daily Selfie Diary
- Automatic photo each morning
- Track appearance changes over time
- Create time-lapse video

### Skin Health Tracking
- Monitor skin condition
- Track skincare routine results
- Before/after comparisons

### Daily Documentation
- Document daily life
- Create visual journal
- Share with family/friends

---

## 📈 Photo Timeline Example

```
January 2025
├── 2025-01-01.jpg  ← New Year
├── 2025-01-02.jpg
├── 2025-01-03.jpg
├── 2025-01-07.jpg  ← Weekly check
├── 2025-01-14.jpg
├── 2025-01-21.jpg
└── 2025-01-28.jpg

February 2025
├── 2025-02-04.jpg
├── 2025-02-11.jpg
├── 2025-02-14.jpg  ← Valentine's Day
└── 2025-02-25.jpg
```

---

## ⚡ Performance Impact

| Metric | Value |
|--------|-------|
| Additional time | +0.5 seconds |
| CPU usage | Minimal |
| Memory usage | +5-10 MB temporarily |
| Disk I/O | One write per session |
| Recognition delay | None (happens after) |

**Conclusion:** Minimal impact on system performance ✅

---

## 🛠️ Advanced Configuration

Want to customize? Edit `face_recognition_system.py`:

```python
# Line ~214: Base directory
skin_base_dir = "Skin"  # Change folder name

# Line ~238: Resolution
config = self.camera.create_still_configuration(
    main={"size": (1920, 1080)}  # Adjust resolution
)

# Line ~249: JPEG quality
cv2.imwrite(photo_path, frame_bgr, 
    [cv2.IMWRITE_JPEG_QUALITY, 95]  # 0-100
)
```

---

## ✨ Feature Summary

| Aspect | Details |
|--------|---------|
| 📸 Resolution | 1920x1080 (HD) |
| 💾 File Size | 500KB - 1MB |
| 📁 Organization | By person & date |
| ⚡ Speed | +0.5 seconds |
| 🔒 Privacy | Local storage |
| 🎯 Frequency | Once per session |

---

## 📞 Quick Help

**Issue**: Photos not saving?  
**Fix**: Check camera, permissions, disk space

**Issue**: Blurry photos?  
**Fix**: Clean lens, better lighting

**Issue**: Running out of space?  
**Fix**: Backup and delete old photos

**Issue**: Want higher quality?  
**Fix**: Edit JPEG_QUALITY in code

---

## 🎉 Enjoy!

Your MagicMirror now automatically captures daily photos!

- No manual intervention needed
- High quality photos
- Organized by date
- Private and secure

Just use your mirror normally and photos will be saved automatically! 📸✨

