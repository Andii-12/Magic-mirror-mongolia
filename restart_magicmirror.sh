#!/bin/bash

echo "🔄 Restarting MagicMirror with Personal Data Fix"
echo "================================================"

# Check if pm2 is running
if command -v pm2 &> /dev/null; then
    echo "✅ PM2 found, restarting MagicMirror..."
    pm2 restart magicmirror
    if [ $? -eq 0 ]; then
        echo "✅ MagicMirror restarted successfully"
    else
        echo "❌ Failed to restart MagicMirror"
        exit 1
    fi
else
    echo "⚠️  PM2 not found, trying npm start..."
    npm start
fi

echo ""
echo "🎯 Personal Data Fix Applied:"
echo "============================="
echo "✅ Added fallback to local user profiles"
echo "✅ Added sample events and todos for testing"
echo "✅ Improved error handling and logging"
echo "✅ Fixed data flow between face recognition and modules"
echo ""
echo "📋 What should now work:"
echo "- Personal calendar shows events for recognized user"
echo "- Personal todo shows tasks for recognized user"
echo "- Data loads from local profiles when API fails"
echo "- Better error messages in console"
echo ""
echo "🔍 To verify:"
echo "1. Check browser console (F12) for any errors"
echo "2. Look for 'Personal API: Loaded from profiles' messages"
echo "3. Verify events and todos are displaying"
echo ""
echo "Restart complete! 🎉"
