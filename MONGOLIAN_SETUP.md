# MagicMirror² Mongolian Language Setup

🇲🇳 **Монгол хэл дэмжлэгтэй MagicMirror² тохиргоо**

This guide helps you set up MagicMirror² with Mongolian language support on your Raspberry Pi 4 with 1GB RAM.

## 📋 What's Included

- ✅ Complete Mongolian translation file (`translations/mn.json`)
- ✅ Optimized configuration for Raspberry Pi 4 (`config/config.mn.js`)
- ✅ Setup scripts for both Linux and Windows
- ✅ Performance optimizations for 1GB RAM

## 🚀 Quick Setup

### Option 1: Automated Setup (Recommended)

**On Windows (for preparation):**
```bash
setup-mongolian.bat
```

**On Raspberry Pi 4:**
```bash
chmod +x setup-mongolian.sh
./setup-mongolian.sh
```

### Option 2: Manual Setup

1. **Copy the Mongolian config:**
   ```bash
   cp config/config.mn.js config/config.js
   ```

2. **Update your config to use Mongolian:**
   ```javascript
   language: "mn",
   locale: "mn-MN",
   ```

3. **Start MagicMirror²:**
   ```bash
   npm start
   ```

## 🌐 Mongolian Translations

The following elements are now in Mongolian:

- **Time and Date**: "Өнөөдөр" (Today), "Маргааш" (Tomorrow)
- **Weather**: "Цаг агаарын урьдчилсан мэдээ" (Weather Forecast)
- **Calendar**: "Цагийн хуваарь" (Schedule)
- **Compliments**: "Сайн өглөө!" (Good morning!)
- **Error Messages**: All system messages in Mongolian
- **Wind Directions**: "Хойд" (North), "Зүүн" (East), etc.

## ⚙️ Configuration Details

### Language Settings
```javascript
language: "mn",           // Mongolian language code
locale: "mn-MN",          // Mongolian locale
timezone: "Asia/Ulaanbaatar"  // Ulaanbaatar timezone
```

### Performance Optimizations for Pi 4 (1GB RAM)
- Reduced logging levels
- Limited module entries
- Optimized update intervals
- Disabled unnecessary features

### Default Modules Included
- **Clock**: Digital display with Mongolian date format
- **Weather**: Current weather and 3-day forecast
- **Calendar**: Event display with Mongolian translations
- **Compliments**: Mongolian greetings for different times
- **News**: Mongolian news feed (configurable)
- **Update Notifications**: System update alerts

## 🎯 Customization

### Weather Location
Update coordinates in `config/config.js`:
```javascript
lat: 47.8864,  // Your latitude
lon: 106.9057, // Your longitude
```

### Calendar Sources
Add your calendar URLs:
```javascript
calendars: [
    {
        url: "https://your-calendar-url.ics",
        symbol: "calendar-check"
    }
]
```

### News Sources
Configure Mongolian news feeds:
```javascript
feeds: [
    {
        title: "Монголын мэдээ",
        url: "https://www.montsame.mn/mn/rss.xml"
    }
]
```

## 🔧 Performance Tips for Pi 4 (1GB RAM)

1. **Close unnecessary applications** before starting MagicMirror²
2. **Use a swap file** if you experience memory issues:
   ```bash
   sudo dphys-swapfile swapoff
   sudo nano /etc/dphys-swapfile
   # Change CONF_SWAPSIZE=100 to CONF_SWAPSIZE=512
   sudo dphys-swapfile setup
   sudo dphys-swapfile swapon
   ```
3. **Monitor memory usage**:
   ```bash
   free -h
   htop
   ```
4. **Disable GPU acceleration** if not needed (saves ~100MB RAM)

## 🐛 Troubleshooting

### Common Issues

**Memory Issues:**
- Reduce `maxNumberOfDays` in weather config
- Lower `maximumEntries` in calendar config
- Disable unnecessary modules

**Language Not Loading:**
- Check that `translations/mn.json` exists
- Verify `language: "mn"` in config
- Restart MagicMirror²

**Performance Issues:**
- Increase update intervals
- Reduce animation speeds
- Close other applications

### Logs and Debugging
```bash
# Check configuration
node js/check_config.js

# View logs
tail -f ~/.pm2/logs/magicmirror-out.log

# Start in development mode
npm run start:dev
```

## 📚 Additional Resources

- [MagicMirror² Documentation](https://docs.magicmirror.builders/)
- [Mongolian Language Support](https://en.wikipedia.org/wiki/Mongolian_language)
- [Raspberry Pi 4 Optimization Guide](https://www.raspberrypi.org/documentation/configuration/)

## 🤝 Contributing

If you find any translation errors or want to improve the Mongolian language support:

1. Edit `translations/mn.json`
2. Test your changes
3. Submit a pull request

## 📄 License

This Mongolian language pack follows the same MIT license as MagicMirror².

---

**Баярлалаа! (Thank you!)**

Enjoy your Mongolian MagicMirror² setup! 🪞✨
