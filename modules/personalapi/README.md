# Personal API Module

A MagicMirror² module that fetches personal calendar events and todo lists from your custom API and displays them based on face recognition.

## Features

- 🔍 **Face Recognition Integration**: Only shows data for the recognized user
- 📅 **Calendar Events**: Displays upcoming events with colors and dates
- 📋 **Todo Lists**: Shows personal task lists with completion status
- 🎨 **Color Coding**: Events display with their assigned colors
- ⏰ **Smart Date Formatting**: Shows "Today", "Tomorrow", or formatted dates
- 🔄 **Auto Updates**: Fetches fresh data every 5 minutes
- 📱 **Responsive Design**: Works on different screen sizes

## API Integration

This module integrates with your personal API at:
`https://calendar-app-production-6d2d.up.railway.app/api/magic-mirror/future-data`

### API Response Format

The module expects the API to return data in this format:

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

## Configuration

Add this module to your `config/config.js`:

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

### Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `apiUrl` | String | Required | URL of your personal API |
| `updateInterval` | Number | 300000 | How often to fetch data (ms) |
| `animationSpeed` | Number | 2000 | Animation speed for updates (ms) |
| `statusFile` | String | "/tmp/magicmirror_face_status.json" | Face recognition status file |
| `maxEvents` | Number | 5 | Maximum events to display |
| `maxLists` | Number | 3 | Maximum todo lists to display |
| `showCompleted` | Boolean | false | Show completed todo items |
| `dateFormat` | String | "MMM Do" | Date format for events |
| `timeFormat` | String | "HH:mm" | Time format for events |

## Face Recognition Integration

The module integrates with the face recognition system:

1. **Status Monitoring**: Checks `/tmp/magicmirror_face_status.json` every second
2. **User Matching**: Matches recognized names with API user data
3. **Dynamic Display**: Only shows data for the current user
4. **Real-time Updates**: Updates immediately when user changes

### Face Recognition Status File Format

```json
{
  "distance": 15,
  "person": "Andii",
  "active": true,
  "status": "recognized",
  "timestamp": "2025-01-27T10:30:00.000Z"
}
```

## Installation

1. **Copy the module** to your MagicMirror² modules directory:
   ```bash
   cp -r modules/personalapi /path/to/MagicMirror/modules/
   ```

2. **Add to configuration** in `config/config.js` (see Configuration section above)

3. **Install dependencies** (if needed):
   ```bash
   npm install node-fetch
   ```

4. **Test the API**:
   ```bash
   node test_personal_api.js
   ```

## Testing

Run the test script to verify API connectivity:

```bash
node test_personal_api.js
```

This will:
- Test the API endpoint
- Display the data structure
- Show user information
- Verify the integration

## Styling

The module includes comprehensive CSS styling:

- **Responsive Design**: Adapts to different screen sizes
- **Color Coding**: Events display with their assigned colors
- **Hover Effects**: Interactive elements with smooth transitions
- **Loading States**: Visual feedback during data fetching
- **Animations**: Smooth fade-in effects for new content

## Troubleshooting

### Common Issues

**No data showing:**
- Check if face recognition is working
- Verify the API URL is correct
- Check browser console for errors
- Ensure the user name matches exactly

**API errors:**
- Test the API URL directly in browser
- Check internet connection
- Verify API server is running
- Check API response format

**Face recognition not working:**
- Ensure face recognition module is running
- Check the status file path
- Verify the status file format
- Check file permissions

### Debug Mode

Enable debug logging by adding to your config:

```javascript
logLevel: ["INFO", "WARN", "ERROR", "DEBUG", "LOG"]
```

## Dependencies

- **MagicMirror²**: Core framework
- **node-fetch**: For API requests (in node helper)
- **moment.js**: For date formatting
- **Face Recognition Module**: For user detection

## License

This module follows the same MIT license as MagicMirror².

## Support

For issues and questions:
1. Check the troubleshooting section
2. Run the test script
3. Check browser console for errors
4. Verify API connectivity
