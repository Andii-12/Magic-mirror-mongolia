@echo off
echo.
echo 🪟 MagicMirror² Mongolian Language Setup for Windows
echo ====================================================
echo.

echo 🔧 Setting up Mongolian language support...
echo 📁 Setting up Mongolian configuration...

REM Copy the Mongolian configuration
if exist "config\config.mn.js" (
    copy "config\config.mn.js" "config\config.js" >nul
    echo    ✅ Configuration copied successfully
) else (
    echo    ❌ config\config.mn.js not found
    pause
    exit /b 1
)

echo.
echo 📦 Checking Node.js version...
node --version
echo.

echo 📦 Installing dependencies...
echo    This may take a few minutes...
npm install --force --no-audit --no-fund --no-update-notifier

if %ERRORLEVEL% NEQ 0 (
    echo    ❌ npm install failed
    echo    💡 Try running: npm install --force
    pause
    exit /b 1
)

echo.
echo ✅ Installation complete!
echo.
echo 🌐 Mongolian language is now configured!
echo    Language code: mn
echo    Locale: mn-MN
echo    Timezone: Asia/Ulaanbaatar (adjust in config if needed)
echo    Day names: Даваа гараг, Мягмар гараг, Лхагва гараг, etc.
echo    News feeds: Mongolian National Broadcasting, BBC, CNN, Al Jazeera
echo.
echo 📋 Next steps:
echo    1. Customize the weather location in config\config.js (lat/lon)
echo    2. Mongolian holidays are already configured (Tsagaan Sar, Naadam, etc.)
echo    3. Add your own calendar URLs if needed
echo    4. Adjust news feeds for Mongolian sources
echo    5. Start MagicMirror² with: npm start
echo.
echo 🚀 To start MagicMirror²:
echo    npm start
echo.
echo 💡 Alternative start commands:
echo    npm run start:windows     - Windows Electron app
echo    npm run server            - Server only mode (for browser)
echo.
echo 🇲🇳 Баярлалаа! (Thank you!)
echo.
pause
