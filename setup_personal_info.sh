#!/bin/bash

# Setup script for MagicMirror² Personal Information System
# Adds personalized calendar, todo lists, and other info for recognized users

echo "🎭 Setting up MagicMirror² Personal Information System"
echo "====================================================="

# Check if we're in the right directory
if [ ! -f "package.json" ]; then
    echo "❌ Error: Please run this script from the MagicMirror² root directory"
    exit 1
fi

# Create module directories
echo "📁 Creating module directories..."
mkdir -p modules/personaltodo
mkdir -p modules/personalcalendar

echo "✅ Module directories created"

# Check if user_profiles.json exists
if [ ! -f "user_profiles.json" ]; then
    echo "📋 Creating default user profiles..."
    echo "   You can customize this later with: python3 manage_profiles.py"
else
    echo "✅ User profiles already exist"
fi

# Make scripts executable
echo "🔧 Making scripts executable..."
chmod +x manage_profiles.py 2>/dev/null || echo "   (Windows: scripts are already executable)"

echo ""
echo "🎉 Personal Information System Setup Complete!"
echo ""
echo "📋 Next Steps:"
echo "1. Configure user profiles:"
echo "   python3 manage_profiles.py"
echo ""
echo "2. Add your personal information:"
echo "   - Calendar URLs (Google Calendar ICS format)"
echo "   - Todo lists"
echo "   - Weather preferences"
echo "   - News feeds"
echo ""
echo "3. Start the system:"
echo "   bash start_lightweight.sh"
echo ""
echo "📖 Features Available:"
echo "   📅 Personal Calendar - Shows your upcoming events"
echo "   📝 Personal Todo List - Your daily tasks"
echo "   🌤️ Personal Weather - Your location's weather"
echo "   📰 Personal News - Your preferred news sources"
echo "   👋 Personalized Greetings - Time-based greetings"
echo ""
echo "🔧 Configuration:"
echo "   - Edit user_profiles.json to customize settings"
echo "   - Use manage_profiles.py for easy management"
echo "   - Each recognized person gets their own information"
echo ""
echo "✨ The system will automatically show personal information"
echo "   when someone is recognized by face recognition!"
