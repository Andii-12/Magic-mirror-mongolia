# Face Recognition Training Guide

This guide will help you train the face recognition system for your MagicMirror² Mongolian project.

## 🎯 Overview

The face recognition system uses OpenCV's LBPHFaceRecognizer to identify people and provide personalized content. You need to train it with photos of each person you want to recognize.

## 📁 File Structure

```
Magic-mirror-mongolia/
├── train_face_recognition.py      # Advanced training script
├── simple_train_faces.py          # Simple training script  
├── setup_face_training.py         # Setup directory structure
├── face_recognition_system.py     # Main face recognition system
├── Images/                        # Face training images
│   ├── Andii/                    # Photos of Andii
│   ├── Jane/                     # Photos of Jane
│   └── Guest/                    # Photos of Guest
├── trainer.yml                    # Trained model (generated)
└── labels.json                    # Label mappings (generated)
```

## 🚀 Quick Start

### Step 1: Setup Directory Structure
```bash
python3 setup_face_training.py
```

### Step 2: Add Face Photos
1. Go to the `Images/` directory
2. Create a folder for each person (e.g., `Andii/`, `Jane/`)
3. Add 40+ clear face photos to each folder
4. Use good lighting and front-facing photos

### Step 3: Train the Model
```bash
python3 simple_train_faces.py
```

### Step 4: Test the System
```bash
python3 face_recognition_system.py
```

## 📸 Photo Requirements

### ✅ Good Photos:
- Clear, well-lit face photos
- Front-facing (not side profile)
- Single person per photo
- Recent photos that look like you now
- Mix of different expressions
- Good resolution (not blurry)

### ❌ Avoid:
- Blurry or dark photos
- Side profiles or back of head
- Sunglasses or hats that obscure face
- Multiple people in one photo
- Very old photos (if appearance changed)
- Heavily edited or filtered photos

## 🔧 Training Scripts

### Simple Training (`simple_train_faces.py`)
- Quick and easy to use
- Good for beginners
- Basic error handling
- Creates `trainer.yml` and `labels.json`

### Advanced Training (`train_face_recognition.py`)
- More features and options
- Better error handling
- Camera testing included
- Detailed logging
- Cross-platform support

## 📊 Training Process

1. **Image Detection**: Script scans `Images/` directory
2. **Face Detection**: Uses OpenCV to find faces in photos
3. **Face Extraction**: Crops and resizes faces to 100x100 pixels
4. **Training**: LBPHFaceRecognizer learns from the faces
5. **Model Saving**: Creates `trainer.yml` file
6. **Label Mapping**: Creates `labels.json` with person names

## 🧪 Testing Your Training

### Test with Camera
```bash
python3 face_recognition_system.py
```

### Test with MagicMirror²
```bash
./start.sh
```

## 🔍 Troubleshooting

### "No faces detected" Error
- Check photo quality and lighting
- Ensure face is clearly visible
- Try different photos
- Make sure photos are in supported formats (.jpg, .png, .bmp)

### "Training failed" Error
- Ensure you have at least 3 faces total
- Check that images are not corrupted
- Verify directory structure is correct
- Make sure you have write permissions

### "Low confidence" Results
- Add more training photos (40+ per person recommended)
- Use better quality photos
- Ensure good lighting in photos
- Mix different expressions and angles

## 📋 Best Practices

### Photo Collection
1. **Quantity**: 40+ photos per person (more = better accuracy)
2. **Quality**: High resolution, good lighting
3. **Variety**: Different expressions and angles
4. **Consistency**: Recent photos that look like you now

### Training Process
1. **Organize**: Put photos in correct directories
2. **Test**: Run training and check for errors
3. **Validate**: Test with camera before using with MagicMirror²
4. **Update**: Retrain when appearance changes significantly

### File Management
- Keep `trainer.yml` in your MagicMirror² directory
- Backup your `Images/` folder
- Update training when adding new people
- Test regularly to ensure accuracy

## 🎯 Integration with MagicMirror²

The trained model integrates with your MagicMirror² system:

1. **Face Detection**: Ultrasonic sensor detects proximity
2. **Recognition**: Camera captures face and identifies person
3. **Personalization**: Shows personalized content for that person
4. **Timeout**: Logs out after 10 seconds of no detection

## 🔧 Configuration

### Face Recognition Settings
```python
# In face_recognition_system.py
PROXIMITY_THRESHOLD = 20  # cm
TIMEOUT_DELAY = 10        # seconds
CASCADE_PATH = "/path/to/haarcascade_frontalface_default.xml"
TRAINER_PATH = "trainer.yml"
```

### MagicMirror² Module Settings
```javascript
// In config.js
{
    module: "facerecognition",
    position: "top_left",
    config: {
        updateInterval: 1000,
        proximityThreshold: 20,
        timeoutDelay: 10000,
        greetingStyle: "large bright"
    }
}
```

## 📞 Support

If you encounter issues:

1. Check the troubleshooting section above
2. Verify your photo quality and quantity
3. Ensure proper directory structure
4. Test with the simple training script first
5. Check MagicMirror² logs for errors

## 🎉 Success!

Once training is complete, you should have:
- `trainer.yml` - The trained face recognition model
- `labels.json` - Person name mappings
- A working face recognition system
- Personalized MagicMirror² experience

Your MagicMirror² will now recognize faces and show personalized content in Mongolian!
