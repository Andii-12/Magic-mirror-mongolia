#!/bin/bash

# Face Recognition Training Setup Script
# This script helps you set up the face recognition training system

echo "🎓 Face Recognition Training Setup"
echo "=================================="

# Create Images directory if it doesn't exist
if [ ! -d "Images" ]; then
    echo "📁 Creating Images directory..."
    mkdir -p Images
    echo "✅ Created Images directory"
fi

# Check if Images directory is empty
if [ -z "$(ls -A Images)" ]; then
    echo ""
    echo "📋 Setup Instructions:"
    echo "====================="
    echo "1. Create folders for each person you want to recognize:"
    echo "   mkdir -p Images/YourName"
    echo "   mkdir -p Images/FamilyMember"
    echo ""
    echo "2. Add photos to each folder:"
    echo "   cp photo1.jpg Images/YourName/"
    echo "   cp photo2.jpg Images/YourName/"
    echo ""
    echo "3. Run the training script:"
    echo "   python3 train_faces.py"
    echo ""
    echo "4. Test the system:"
    echo "   python3 test_face_recognition.py"
    echo ""
    echo "5. Start the full system:"
    echo "   ./start_magicmirror_proximity.sh"
else
    echo "📁 Images directory already contains data"
    echo "   Found: $(ls Images | wc -l) person folders"
    echo ""
    echo "🚀 Ready to train! Run:"
    echo "   python3 train_faces.py"
fi

echo ""
echo "📝 Tips for good face recognition:"
echo "=================================="
echo "• Use clear, well-lit photos"
echo "• Include multiple photos per person (3-5 recommended)"
echo "• Make sure faces are clearly visible"
echo "• Avoid photos with sunglasses or heavy shadows"
echo "• Use photos with different angles/expressions"
