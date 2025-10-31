# MagicMirror² Mongolian Language Pack

🇲🇳 **Монгол хэл дэмжлэгтэй MagicMirror²**

A complete Mongolian language localization for MagicMirror² with face recognition, optimized for Raspberry Pi 4.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Language: Mongolian](https://img.shields.io/badge/Language-Mongolian-red.svg)](https://en.wikipedia.org/wiki/Mongolian_language)
[![Platform: Raspberry Pi](https://img.shields.io/badge/Platform-Raspberry%20Pi-red.svg)](https://www.raspberrypi.org/)

## 🌟 Features

- ✅ **Complete Mongolian Translation** - All interface elements in Mongolian
- ✅ **Face Recognition** - Personalized experience with ultrasonic sensor
- ✅ **Personal Data** - User-specific calendar and todo lists
- ✅ **Raspberry Pi 4 Optimized** - Performance tuned for 1GB RAM
- ✅ **Mongolian Timezone** - Asia/Ulaanbaatar timezone support
- ✅ **Standalone Operation** - No browser needed

## 🎭 Face Recognition Training

### Quick Training Guide

The MagicMirror² Mongolian project includes a comprehensive face recognition system. To train the system to recognize faces:

#### **Option 1: All-in-One Training Script**
```bash
# Run the complete training system
python3 train_faces.py

# Follow the interactive menu:
# 1. Setup directories
# 2. Collect images with webcam
# 3. Process existing images
# 4. Train face recognition model
# 5. Test trained model
# 6. Show training status
# 7. Complete training workflow (recommended)
```

#### **Option 2: Step-by-Step Training**

**Step 1: Setup Training Environment**
```bash
# Create directory structure
python3 setup_face_training.py

# This creates:
# Images/
# ├── Andii/          # Add 40+ photos here
# ├── Jane/           # Add 40+ photos here
# └── Default/        # Add 40+ photos here
```

**Step 2: Add Face Photos**
- Add **40+ clear face photos** per person to their directory
- Use good lighting and front-facing photos
- Supported formats: `.jpg`, `.jpeg`, `.png`, `.bmp`
- Avoid blurry or side-profile photos

**Step 3: Train the Model**
```bash
# Simple training (recommended)
python3 simple_train_faces.py

# Advanced training with more options
python3 train_face_recognition.py
```

**Step 4: Test the Training**
```bash
# Verify training setup
python3 test_face_training.py

# Test with live camera and confidence display (NEW!)
npm run test-face-confidence
# or directly:
python3 test_face_confidence.py

# Alternative: Test with old method
python3 train_faces.py
# Select option 5: Test trained model
```

**New: Face Confidence Test Tool** 🎯
- Shows real-time recognition with confidence percentage
- Color-coded: Green (70%+) = Good, Yellow (50-70%) = Moderate, Red = Unknown
- Supports both webcam and PiCamera
- Press 'h' to toggle histogram equalization
- Press 's' to save test images
- Press 'q' to quit

### 📸 Image Collection Tips

#### **Best Practices:**
- **Quantity**: 40+ photos per person (more = better accuracy)
- **Quality**: High resolution, good lighting
- **Variety**: Different expressions and angles
- **Consistency**: Recent photos that look like you now

#### **Good Photos:**
- ✅ Clear, well-lit face
- ✅ Front-facing angle
- ✅ Different expressions
- ✅ Good contrast
- ✅ Recent photos

#### **Avoid These:**
- ❌ Blurry or dark photos
- ❌ Side profiles
- ❌ Sunglasses or hats
- ❌ Very old photos
- ❌ Group photos

### 🔧 Training Scripts

| Script | Purpose | Best For |
|--------|---------|----------|
| `train_faces.py` | **Complete training system** | **All users** |
| `simple_train_faces.py` | Quick and easy training | Beginners |
| `train_face_recognition.py` | Advanced training options | Power users |
| `test_face_confidence.py` | **Real-time confidence display** | **Testing & Debugging** |
| `setup_face_training.py` | Directory setup | Initial setup |
| `test_face_training.py` | Verify training | Testing |

### 🎯 Training Results

After successful training, you'll get:
- `trainer.yml` - The trained face recognition model
- `labels.json` - Person labels and IDs
- `training_summary.json` - Training statistics

### 🚀 Integration with MagicMirror²

Once training is complete:
1. Copy `trainer.yml` to your MagicMirror² directory
2. Copy `labels.json` to your MagicMirror² directory
3. Start the complete system: `./start.sh`

The face recognition system will:
- Detect when someone approaches (ultrasonic sensor)
- Recognize faces and greet users in Mongolian
- Show personalized content (calendar, todos, news)
- Display Mongolian greetings and messages

### 🐛 Troubleshooting Face Training

#### **"No faces detected" Error:**
- Add more photos (40+ recommended)
- Use better quality photos
- Ensure good lighting
- Check face is clearly visible

#### **"Low confidence" Results:**
- Add more training photos
- Use better quality photos
- Mix different expressions
- Ensure consistent lighting

#### **Camera Issues:**
- Check camera permissions
- Ensure camera is not in use by other apps
- Try different camera (if available)
- On Windows: Use manual photo collection

### 📚 Detailed Documentation

For complete face training documentation, see:
- [FACE_TRAINING_README.md](FACE_TRAINING_README.md) - Comprehensive training guide
- [MagicMirror² Face Recognition](https://docs.magicmirror.builders/modules/face-recognition.html)

## 🚀 Quick Start

### For Raspberry Pi 4:

```bash
# Clone this repository
git clone https://github.com/Andii-12/Magic-mirror-mongolia.git
cd Magic-mirror-mongolia

# Run the setup script
chmod +x setup-mongolian.sh
./setup-mongolian.sh

# Start the complete system (face recognition + ultrasonic + MagicMirror² + personal data)
chmod +x start.sh
./start.sh
```

## 📋 What's Included

| File | Description |
|------|-------------|
| `translations/mn.json` | Complete Mongolian translation file |
| `config/config.mn.js` | Optimized configuration for Pi 4 |
| `setup-mongolian.sh` | Linux setup script |
| `setup-mongolian.bat` | Windows setup script |
| `test-mongolian.js` | Validation test script |
| `MONGOLIAN_SETUP.md` | Detailed documentation |

### 🎭 Face Recognition Training Scripts

| Script | Purpose | Best For |
|--------|---------|----------|
| `train_faces.py` | **Complete training system** | **All users** |
| `simple_train_faces.py` | Quick and easy training | Beginners |
| `train_face_recognition.py` | Advanced training options | Power users |
| `setup_face_training.py` | Directory setup | Initial setup |
| `test_face_training.py` | Verify training | Testing |
| `collect_face_images.py` | Webcam image collection | Image gathering |
| `prepare_images.py` | Image processing | Quality enhancement |
| `FACE_TRAINING_README.md` | Complete training guide | Documentation |

## 🌐 Mongolian Translations

### Time & Date
- **Өнөөдөр** (Today)
- **Маргааш** (Tomorrow) 
- **Өчигдөр** (Yesterday)
- **Даваа гараг** (Monday)
- **Мягмар гараг** (Tuesday)
- **Лхагва гараг** (Wednesday)
- **Пүрэв гараг** (Thursday)
- **Баасан гараг** (Friday)
- **Бямба гараг** (Saturday)
- **Ням гараг** (Sunday)

### Weather
- **Цаг агаарын урьдчилсан мэдээ** (Weather Forecast)
- **Мэдрэгдэх** (Feels like)
- **Хур тунадасны магадлал** (Precipitation probability)

### Calendar
- **Цагийн хуваарь** (Schedule)
- **Удахгүй болох үйл явдал байхгүй** (No upcoming events)
- **Монголын баярын өдрүүд** (Mongolian Holidays) - Powered by [Calendarific API](https://calendarific.com/api/v2/holidays?&api_key=VhaBu1hTpO9OtGRyFbPUxY6vhO2nrqbL&country=MN&year=2025)
  - **Шинэ жилийн өдөр** (New Year's Day)
  - **Шинэ жилийн баяр** (Tsagaan Sar - Lunar New Year)
  - **Олон улсын эмэгтэйчүүдийн өдөр** (International Women's Day)
  - **Наадам** (Naadam Festival)
  - **Тусгаар тогтнолын өдөр** (Independence Day)

### Compliments
- **Сайн өглөө!** (Good morning!)
- **Өглөөний мэнд!** (Morning greetings!)
- **Сайхан өдөр байна шүү!** (It's a beautiful day!)
- **Таны өдөр амжилттай болтугай!** (May your day be successful!)
- **Хүч чадалтай байгаарай!** (Stay strong!)
- **Амьдрал сайхан байна!** (Life is beautiful!)
- **Бүх зүйл сайн болно!** (Everything will be fine!)
- **Эерэг энергитэй байгаарай!** (Stay positive!)

### News
- **Монголын мэдээ** (Mongolian News)
- **Монголын Үндэсний Радио Телевиз** (Mongolian National Broadcasting)
- **BBC News** (International News)
- **CNN World News** (International News)
- **Al Jazeera English** (International News)

## 🔧 Troubleshooting

### Windows Issues:

**Node.js Version Compatibility:**
- If you get "Unsupported engine" errors, the setup script automatically uses `--force`
- Your Node.js v22.3.0 is compatible (minimum required: v18.0.0)

**Startup Issues:**
- Use `npm start` (now configured for Windows)
- Alternative: `npm run start:windows`
- For server-only mode: `npm run server` (opens in browser)

**PowerShell Execution Policy:**
- If scripts won't run: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`

## ⚙️ Configuration

### Language Settings
```javascript
language: "mn",                    // Mongolian language code
locale: "mn-MN",                   // Mongolian locale
timezone: "Asia/Ulaanbaatar"       // Ulaanbaatar timezone
```

### Performance Optimizations
- Reduced logging levels for Pi 4
- Limited module entries (5 max calendar, 3 days weather)
- Optimized update intervals
- Memory-efficient settings

## 🔧 System Requirements

- **Node.js**: 22.14.0 or higher
- **Platform**: Raspberry Pi 4 (optimized for 1GB RAM)
- **OS**: Raspberry Pi OS or compatible Linux distribution

## 📖 Documentation

For detailed setup instructions, customization options, and troubleshooting, see:
- [MONGOLIAN_SETUP.md](MONGOLIAN_SETUP.md) - Complete setup guide
- [MagicMirror² Documentation](https://docs.magicmirror.builders/)

## 🧪 Testing

Validate your setup:
```bash
node test-mongolian.js
```

## 🤝 Contributing

Contributions are welcome! If you find translation errors or want to improve the Mongolian language support:

1. Fork the repository
2. Edit `translations/mn.json`
3. Test your changes with `node test-mongolian.js`
4. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [MagicMirror²](https://github.com/MagicMirrorOrg/MagicMirror) - The original smart mirror platform
- Mongolian language community for translation assistance
- Raspberry Pi community for optimization tips

## 📞 Support

If you encounter any issues:

1. Check the [troubleshooting section](MONGOLIAN_SETUP.md#-troubleshooting) in the documentation
2. Run the test script: `node test-mongolian.js`
3. Open an [issue](https://github.com/Andii-12/Magic-mirror-mongolia/issues) on GitHub

## 🎯 Quick Reference

### Face Training Commands
```bash
# Complete training workflow
python3 train_faces.py

# Quick training
python3 simple_train_faces.py

# Test training
python3 test_face_training.py
```

### MagicMirror² Commands
```bash
# Start complete system
./start.sh

# Start MagicMirror² only
npm start

# Test Mongolian setup
node test-mongolian.js
```

### File Locations
- **Face Training**: `Images/` directory
- **Trained Model**: `trainer.yml`, `labels.json`
- **Config**: `config/config.mn.js`
- **Translations**: `translations/mn.json`

---

**Баярлалаа! (Thank you!)**

Enjoy your Mongolian MagicMirror² setup! 🪞✨

---

*Made with ❤️ for the Mongolian community*