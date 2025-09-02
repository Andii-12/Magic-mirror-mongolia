# MagicMirror² Mongolian Language Pack

🇲🇳 **Монгол хэл дэмжлэгтэй MagicMirror²**

A complete Mongolian language localization for MagicMirror², optimized for Raspberry Pi 4 with 1GB RAM.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Language: Mongolian](https://img.shields.io/badge/Language-Mongolian-red.svg)](https://en.wikipedia.org/wiki/Mongolian_language)
[![Platform: Raspberry Pi](https://img.shields.io/badge/Platform-Raspberry%20Pi-red.svg)](https://www.raspberrypi.org/)

## 🌟 Features

- ✅ **Complete Mongolian Translation** - 43+ translations covering all interface elements
- ✅ **Raspberry Pi 4 Optimized** - Performance tuned for 1GB RAM devices
- ✅ **Easy Setup** - Automated installation scripts for Linux and Windows
- ✅ **Mongolian Timezone** - Asia/Ulaanbaatar timezone support
- ✅ **Localized Content** - Weather, calendar, and news in Mongolian
- ✅ **Performance Optimized** - Reduced memory usage and optimized update intervals

## 🚀 Quick Start

### For Raspberry Pi 4:

```bash
# Clone this repository
git clone https://github.com/Andii-12/Magic-mirror-mongolia.git
cd Magic-mirror-mongolia

# Run the setup script
chmod +x setup-mongolian.sh
./setup-mongolian.sh

# Start MagicMirror²
npm start
```

### For Windows (Preparation):

```bash
# Run the Windows setup script
setup-mongolian.bat
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

## 🌐 Mongolian Translations

### Time & Date
- **Өнөөдөр** (Today)
- **Маргааш** (Tomorrow) 
- **Өчигдөр** (Yesterday)

### Weather
- **Цаг агаарын урьдчилсан мэдээ** (Weather Forecast)
- **Мэдрэгдэх** (Feels like)
- **Хур тунадасны магадлал** (Precipitation probability)

### Calendar
- **Цагийн хуваарь** (Schedule)
- **Удахгүй болох үйл явдал байхгүй** (No upcoming events)

### Compliments
- **Сайн өглөө!** (Good morning!)
- **Сайн өдөр!** (Good day!)
- **Сайн орой!** (Good evening!)

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

---

**Баярлалаа! (Thank you!)**

Enjoy your Mongolian MagicMirror² setup! 🪞✨

---

*Made with ❤️ for the Mongolian community*