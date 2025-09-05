#!/bin/bash

# Personal API Module Setup Script
# This script helps set up the Personal API module for MagicMirror²

echo "🔧 Personal API Module Setup"
echo "============================"
echo ""

# Check if we're in a MagicMirror directory
if [ ! -f "package.json" ] || [ ! -d "modules" ]; then
    echo "❌ Error: This doesn't appear to be a MagicMirror² directory"
    echo "   Please run this script from your MagicMirror² root directory"
    exit 1
fi

echo "✅ MagicMirror² directory detected"
echo ""

# Test API connectivity
echo "🌐 Testing API connectivity..."
API_URL="https://calendar-app-production-6d2d.up.railway.app/api/magic-mirror/future-data"

if curl -s --head "$API_URL" | head -n 1 | grep -q "200 OK"; then
    echo "✅ API is accessible"
else
    echo "⚠️  Warning: API might not be accessible"
    echo "   URL: $API_URL"
fi
echo ""

# Check if personalapi module exists
if [ -d "modules/personalapi" ]; then
    echo "✅ Personal API module found"
else
    echo "❌ Personal API module not found"
    echo "   Please ensure the module is in modules/personalapi/"
    exit 1
fi

# Check if face recognition status file exists
STATUS_FILE="/tmp/magicmirror_face_status.json"
if [ -f "$STATUS_FILE" ]; then
    echo "✅ Face recognition status file found"
    echo "   Current status:"
    cat "$STATUS_FILE" | head -3
else
    echo "⚠️  Face recognition status file not found"
    echo "   File: $STATUS_FILE"
    echo "   This is normal if face recognition isn't running yet"
fi
echo ""

# Test the API with a sample request
echo "🧪 Testing API data structure..."
if command -v node &> /dev/null; then
    if [ -f "test_personal_api.js" ]; then
        echo "   Running API test..."
        node test_personal_api.js
    else
        echo "   Test script not found, skipping API test"
    fi
else
    echo "   Node.js not found, skipping API test"
fi
echo ""

# Check configuration
echo "📋 Configuration check..."
if grep -q "personalapi" config/config.js; then
    echo "✅ Personal API module found in config"
else
    echo "⚠️  Personal API module not found in config"
    echo "   Please add the module to your config/config.js:"
    echo ""
    echo "   {"
    echo "       module: \"personalapi\","
    echo "       position: \"middle_center\","
    echo "       header: \"Personal Schedule\","
    echo "       config: {"
    echo "           apiUrl: \"https://calendar-app-production-6d2d.up.railway.app/api/magic-mirror/future-data\","
    echo "           updateInterval: 5 * 60 * 1000,"
    echo "           animationSpeed: 2000,"
    echo "           statusFile: \"/tmp/magicmirror_face_status.json\","
    echo "           maxEvents: 5,"
    echo "           maxLists: 3,"
    echo "           showCompleted: false"
    echo "       }"
    echo "   }"
fi
echo ""

# Check dependencies
echo "📦 Checking dependencies..."
if [ -f "package.json" ]; then
    if grep -q "node-fetch" package.json; then
        echo "✅ node-fetch dependency found"
    else
        echo "⚠️  node-fetch dependency not found"
        echo "   Installing node-fetch..."
        npm install node-fetch
    fi
else
    echo "   package.json not found, skipping dependency check"
fi
echo ""

echo "🎉 Setup complete!"
echo ""
echo "📋 Next steps:"
echo "   1. Ensure face recognition is running"
echo "   2. Start MagicMirror²: npm start"
echo "   3. The module will show data for recognized users"
echo "   4. Check the middle_center position for personal schedule"
echo ""
echo "🔧 Troubleshooting:"
echo "   - Check browser console for errors"
echo "   - Verify API connectivity with: curl $API_URL"
echo "   - Test face recognition status file"
echo "   - Check module logs in MagicMirror²"
echo ""
echo "📚 For more information, see modules/personalapi/README.md"
