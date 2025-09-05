# Personal API Integration for MagicMirror²

## 🎯 Overview

I've successfully integrated your Personal API (`https://calendar-app-production-6d2d.up.railway.app/api/magic-mirror/future-data`) with the MagicMirror² Mongolian language pack. The integration fetches calendar events and todo lists, displaying them based on face recognition.

## 📁 Files Created

### Core Module Files
- `modules/personalapi/personalapi.js` - Main module logic
- `modules/personalapi/personalapi.css` - Styling and animations
- `modules/personalapi/node_helper.js` - Server-side API handling
- `modules/personalapi/README.md` - Detailed documentation

### Configuration & Setup
- `config/config.js` - Updated with Personal API module configuration
- `setup_personal_api.bat` - Windows setup script
- `setup_personal_api.sh` - Linux setup script
- `test_personal_api.js` - API testing script
- `demo_personal_api.html` - Visual demonstration

## 🔧 How It Works

### 1. Face Recognition Integration
```javascript
// Monitors face recognition status file
statusFile: "/tmp/magicmirror_face_status.json"

// When face is recognized, matches user name with API data
if (data.person && data.person !== self.currentUser) {
    self.currentUser = data.person;
    self.loadUserData();
}
```

### 2. API Data Fetching
```javascript
// Fetches from your API every 5 minutes
apiUrl: "https://calendar-app-production-6d2d.up.railway.app/api/magic-mirror/future-data"

// Processes the response structure:
{
  "users": [
    {
      "name": "Andii",
      "events": [...],
      "lists": [...]
    }
  ]
}
```

### 3. User-Specific Display
- Only shows data for the recognized user
- Displays events with color coding
- Shows todo lists with completion status
- Updates in real-time when user changes

## 📊 API Response Structure

Your API returns data in this format:

```json
{
  "message": "Future events and lists (today and beyond)",
  "date": "2025-09-05",
  "users": [
    {
      "name": "Andii",
      "events": [
        {
          "_id": "68ba8c238ea84e6d9cde97b5",
          "title": "Go to School",
          "description": "",
          "color": "#ef4444",
          "allDay": true,
          "startDate": "2025-09-07T16:00:00.000Z"
        }
      ],
      "lists": [
        {
          "_id": "68ba8c7a8ea84e6d9cde97c5",
          "title": "Meeting",
          "description": "",
          "listDate": "2025-09-08T00:00:00.000Z",
          "items": [
            {
              "_id": "68ba8c818ea84e6d9cde97c9",
              "title": "Meet Teacher",
              "description": "",
              "completed": false
            }
          ]
        }
      ]
    }
  ],
  "summary": {
    "totalUsers": 1,
    "totalEvents": 4,
    "totalLists": 2
  }
}
```

## 🎨 Visual Features

### Event Display
- **Color Coding**: Events show with their assigned colors
- **Smart Dates**: "Today", "Tomorrow", or formatted dates
- **All-Day Events**: Clearly marked
- **Hover Effects**: Interactive animations

### Todo Lists
- **Completion Status**: Checkboxes show completed/incomplete
- **Date Grouping**: Lists grouped by date
- **Item Details**: Titles and descriptions
- **Progress Tracking**: Visual completion indicators

## ⚙️ Configuration

The module is configured in `config/config.js`:

```javascript
{
    module: "personalapi",
    position: "middle_center",
    header: "Personal Schedule",
    config: {
        apiUrl: "https://calendar-app-production-6d2d.up.railway.app/api/magic-mirror/future-data",
        updateInterval: 5 * 60 * 1000, // 5 minutes
        animationSpeed: 2000,
        statusFile: "/tmp/magicmirror_face_status.json",
        maxEvents: 5,
        maxLists: 3,
        showCompleted: false,
        dateFormat: "MMM Do",
        timeFormat: "HH:mm"
    }
}
```

## 🚀 Setup Instructions

### 1. Test the API
```bash
node test_personal_api.js
```

### 2. Run Setup Script
```bash
# Windows
setup_personal_api.bat

# Linux
chmod +x setup_personal_api.sh
./setup_personal_api.sh
```

### 3. Start MagicMirror²
```bash
npm start
```

## 🔍 Testing Results

✅ **API Connectivity**: Successfully tested
- URL: `https://calendar-app-production-6d2d.up.railway.app/api/magic-mirror/future-data`
- Response: Valid JSON with user data
- Users: 1 (Andii)
- Events: 4 (Go to School, Work, Sport, hi)
- Lists: 2 (Meeting, Work must finish)

## 🎯 Key Features

### 1. **Face Recognition Integration**
- Monitors face recognition status file
- Matches recognized names with API users
- Updates display when user changes

### 2. **Real-time Updates**
- Fetches fresh data every 5 minutes
- Updates immediately when user changes
- Shows last update time

### 3. **Smart Display**
- Only shows data for current user
- Color-coded events
- Completion status for todos
- Responsive design

### 4. **Error Handling**
- Graceful API failure handling
- Loading states
- User feedback

## 📱 User Experience

### When Face is Recognized
1. **User Detection**: "Andii detected"
2. **Data Loading**: Fetches personal data
3. **Display Update**: Shows personal schedule
4. **Real-time Updates**: Refreshes every 5 minutes

### Display Layout
- **Header**: "Andii's Schedule"
- **Events Section**: Upcoming events with colors
- **Todo Section**: Task lists with completion status
- **Update Info**: Last refresh time

## 🔧 Troubleshooting

### Common Issues
1. **No Data Showing**: Check face recognition status
2. **API Errors**: Verify API connectivity
3. **User Not Found**: Ensure name matches exactly
4. **Display Issues**: Check browser console

### Debug Steps
1. Run `node test_personal_api.js`
2. Check face recognition status file
3. Verify module configuration
4. Check browser console for errors

## 🎉 Success!

The integration is complete and working! Your Personal API is now fully integrated with MagicMirror²:

- ✅ **API Integration**: Successfully fetching data
- ✅ **Face Recognition**: User-specific display
- ✅ **Visual Design**: Beautiful, responsive interface
- ✅ **Real-time Updates**: Dynamic content refresh
- ✅ **Error Handling**: Robust error management

The module will display personal calendar events and todo lists for recognized users, updating in real-time as people approach the mirror.

## 📚 Next Steps

1. **Test the Integration**: Run the setup script
2. **Customize Display**: Adjust colors and layout
3. **Add More Users**: Extend API with additional users
4. **Monitor Performance**: Check logs and performance
5. **Enjoy**: Your personalized MagicMirror² is ready!

---

**API Reference**: [https://calendar-app-production-6d2d.up.railway.app/api/magic-mirror/future-data](https://calendar-app-production-6d2d.up.railway.app/api/magic-mirror/future-data)

**Module Documentation**: `modules/personalapi/README.md`

**Demo**: Open `demo_personal_api.html` in your browser
