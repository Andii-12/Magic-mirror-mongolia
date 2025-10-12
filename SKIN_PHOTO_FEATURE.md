# Skin Photo Feature Documentation

## 📸 Overview

The MagicMirror system now automatically captures high-resolution photos after successfully recognizing a person's face. These photos are organized by person and saved with the current date.

## 🎯 Purpose

This feature is designed for:
- Skin tracking and monitoring over time
- Personal photo diary
- Health and wellness monitoring
- Visual timeline of daily appearance

## 📁 Directory Structure

Photos are saved in the following structure:

```
Skin/
├── Andii/
│   ├── 2025-12-10.jpg
│   ├── 2025-12-11.jpg
│   └── 2025-12-12.jpg
├── Jane/
│   ├── 2025-12-10.jpg
│   └── 2025-12-11.jpg
└── Guest/
    └── 2025-12-10.jpg
```

## ⚙️ How It Works

### 1. Face Recognition
When someone approaches the mirror:
- Ultrasonic sensor detects proximity (< 20cm)
- Camera captures face and runs recognition
- If recognized successfully (confidence < 80), trigger photo capture

### 2. High-Resolution Photo Capture
After successful recognition:
- Camera temporarily switches to high-resolution mode (1920x1080)
- Captures a single high-quality photo (95% JPEG quality)
- Saves to `Skin/{PersonName}/{date}.jpg`
- Camera switches back to preview mode (640x480)

### 3. Smart Saving
- **One photo per session**: Only one photo is saved per recognition session
- **Date-based naming**: Photos are named with current date (YYYY-MM-DD)
- **Unique filenames**: If multiple photos on same day, adds timestamp (YYYY-MM-DD_HH-MM-SS)
- **Auto-directory creation**: Creates folders automatically if they don't exist

## 📐 Technical Specifications

### Photo Quality
- **Resolution**: 1920x1080 (fallback to 1280x720 if not supported)
- **Format**: JPEG
- **Quality**: 95% compression
- **Color**: RGB (converted to BGR for OpenCV)

### Storage
- **Location**: `./Skin/` directory (same level as script)
- **Naming**: `{PersonName}/{YYYY-MM-DD}.jpg`
- **Fallback**: If date exists, adds time: `{YYYY-MM-DD_HH-MM-SS}.jpg`

### Session Management
- **One photo per session**: Prevents multiple photos during same recognition
- **Reset on logout**: Flag resets after 10-second timeout
- **Reset on new session**: Flag resets when new person detected

## 🔧 Code Implementation

### Key Functions

#### `save_skin_photo(person_name)`
Main function that handles photo capture and saving:

```python
def save_skin_photo(self, person_name):
    """Save high-resolution photo after successful face recognition"""
    # Check if already saved this session
    # Create directory structure
    # Capture high-res photo
    # Save with date-based filename
    # Return to preview mode
```

#### Integration Points
1. Called after successful face recognition in `recognize_face_with_camera()`
2. Flag reset in `run()` loop when session ends
3. Flag reset when new session starts

### Session Tracking
```python
self.photo_saved_this_session = False  # Initially False
# Set to True after saving photo
# Reset to False when:
# - New recognition session starts
# - User logs out (after timeout)
```

## 🚀 Usage

### Automatic Operation
The feature works automatically:
1. Stand in front of mirror (< 20cm)
2. Face is recognized
3. High-res photo is captured and saved
4. Move away after 10 seconds to end session
5. Next time you approach, a new photo will be taken

### Manual Testing
To test the feature:
```bash
# Start the face recognition system
python3 face_recognition_system.py

# Or use the full system
./start.sh
```

### Check Saved Photos
```bash
# View saved photos
ls -la Skin/

# View photos for specific person
ls -la Skin/Andii/

# View most recent photo
ls -lt Skin/Andii/ | head -n 2
```

## 📊 Photo Organization Tips

### View by Date
```bash
# All photos from today
find Skin/ -name "$(date +%Y-%m-%d)*"

# All photos from specific date
find Skin/ -name "2025-12-10*"
```

### Count Photos
```bash
# Total photos
find Skin/ -name "*.jpg" | wc -l

# Photos per person
for dir in Skin/*/; do 
    echo "$(basename "$dir"): $(find "$dir" -name "*.jpg" | wc -l)"
done
```

### Create Monthly Archive
```bash
# Archive photos by month
year_month=$(date +%Y-%m)
tar -czf "skin_photos_${year_month}.tar.gz" Skin/
```

## 🔒 Privacy & Security

### Important Notes
- Photos are stored **locally** on the Raspberry Pi
- **No cloud upload** by default
- Only captured after **successful recognition**
- One photo per session prevents excessive captures

### Recommendations
1. **Backup regularly**: Copy Skin/ folder to external storage
2. **Secure access**: Ensure only authorized users can access Pi
3. **Review periodically**: Delete old photos if not needed
4. **Encrypt storage**: Consider encrypting the Skin/ folder

### Delete Photos
```bash
# Delete all photos for a person
rm -rf Skin/PersonName/

# Delete photos older than 30 days
find Skin/ -name "*.jpg" -mtime +30 -delete

# Delete all photos (use with caution!)
rm -rf Skin/
```

## 🐛 Troubleshooting

### No Photos Being Saved

**Check camera initialization:**
```bash
# Look for camera errors in logs
python3 face_recognition_system.py 2>&1 | grep -i camera
```

**Check permissions:**
```bash
# Ensure write permissions
ls -ld Skin/
chmod 755 Skin/
```

### Low-Quality Photos

The system automatically tries multiple resolutions:
1. **First attempt**: 1920x1080 (Full HD)
2. **Fallback**: 1280x720 (HD)
3. **Quality**: 95% JPEG compression

If photos are still low quality:
- Check camera focus
- Ensure good lighting
- Clean camera lens

### Multiple Photos Same Day

If you see filenames like `2025-12-10_14-30-45.jpg`:
- This means multiple sessions on the same day
- System adds timestamp to prevent overwriting
- This is normal behavior

### Disk Space Issues

**Check available space:**
```bash
df -h .
du -sh Skin/
```

**Estimate storage:**
- Average photo: ~500KB - 1MB
- 100 photos: ~50-100MB
- 1000 photos: ~500MB - 1GB

## 📈 Future Enhancements

Possible improvements:
1. **Cloud backup**: Auto-upload to Google Drive/Dropbox
2. **Face cropping**: Save only face region instead of full frame
3. **Metadata**: Add timestamp, lighting conditions, confidence score
4. **Comparison**: Generate before/after comparisons
5. **Analytics**: Track changes over time
6. **Thumbnails**: Generate preview thumbnails
7. **Web interface**: View photos through browser

## 🔍 Configuration Options

You can customize the feature by modifying these constants in `face_recognition_system.py`:

```python
# Photo settings (in save_skin_photo function)
SKIN_BASE_DIR = "Skin"              # Base directory
HIGH_RES = (1920, 1080)             # High resolution
FALLBACK_RES = (1280, 720)          # Fallback resolution
JPEG_QUALITY = 95                   # JPEG quality (0-100)

# Session settings
PHOTO_SAVED_FLAG = False            # Reset per session
```

## 📞 Support

If you encounter issues:
1. Check the logs for error messages
2. Verify camera is working: `vcgencmd get_camera`
3. Test camera manually: `libcamera-still -o test.jpg`
4. Ensure Python libraries are installed: `pip3 list | grep opencv`

## ✅ Summary

- ✅ **Automatic**: Captures photo after face recognition
- ✅ **High-quality**: 1920x1080 at 95% JPEG quality
- ✅ **Organized**: Folders by person, files by date
- ✅ **Smart**: One photo per session, unique filenames
- ✅ **Local**: All photos stored on device
- ✅ **Efficient**: Quick capture, minimal delay

Enjoy tracking your daily appearance with the Skin Photo Feature! 📸

