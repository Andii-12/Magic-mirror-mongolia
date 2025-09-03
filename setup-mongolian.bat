@echo off
REM MagicMirror² Mongolian Language Setup Script for Raspberry Pi 4
REM This script helps configure MagicMirror² for Mongolian language support

echo 🇲🇳 MagicMirror² Mongolian Language Setup for Raspberry Pi 4
echo ==============================================================

REM Check if we're on Raspberry Pi (this won't work on Windows, but good for reference)
echo 📊 Setting up Mongolian language support...

REM Create backup of original config if it exists
if exist "config\config.js" (
    echo 💾 Creating backup of existing config...
    for /f "tokens=2 delims==" %%a in ('wmic OS Get localdatetime /value') do set "dt=%%a"
    set "YY=%dt:~2,2%" & set "YYYY=%dt:~0,4%" & set "MM=%dt:~4,2%" & set "DD=%dt:~6,2%"
    set "HH=%dt:~8,2%" & set "Min=%dt:~10,2%" & set "Sec=%dt:~12,2%"
    set "timestamp=%YYYY%%MM%%DD%_%HH%%Min%%Sec%"
    copy "config\config.js" "config\config.js.backup.%timestamp%"
)

REM Copy Mongolian config
echo 📝 Setting up Mongolian configuration...
copy "config\config.mn.js" "config\config.js"

REM Check if Node.js is installed
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Node.js is not installed or not in PATH
    echo    Please install Node.js 22.14.0+ from https://nodejs.org/
    pause
    exit /b 1
)

REM Check Node.js version
for /f "tokens=1 delims=v" %%i in ('node --version') do set NODE_VERSION=%%i
echo 📦 Node.js version: %NODE_VERSION%

REM Install dependencies if needed
if not exist "node_modules" (
    echo 📦 Installing dependencies...
    npm install --only=prod --omit=dev
)

REM Test configuration
echo 🧪 Testing configuration...
node js\check_config.js
if %errorlevel% equ 0 (
    echo ✅ Configuration is valid!
) else (
    echo ❌ Configuration has errors. Please check the output above.
    pause
    exit /b 1
)

echo.
echo 🎉 Setup complete!
echo.
echo 📋 Next steps:
echo    1. Transfer these files to your Raspberry Pi 4
echo    2. Customize the weather location in config/config.js (lat/lon)
echo    3. Mongolian holidays are already configured (Tsagaan Sar, Naadam, etc.)
echo    4. Add your own calendar URLs if needed
echo    5. Adjust news feeds for Mongolian sources
echo    6. On Pi 4, run: chmod +x setup-mongolian.sh
echo    7. On Pi 4, run: ./setup-mongolian.sh
echo    8. Start MagicMirror² with: npm start
echo.
echo 🔧 Performance tips for Pi 4 with 1GB RAM:
echo    - Close unnecessary applications
echo    - Consider using a swap file if needed
echo    - Monitor memory usage with: free -h
echo    - Use 'npm run start:dev' for development with DevTools
echo.
echo 🌐 Mongolian language is now configured!
echo    Language code: mn
echo    Locale: mn-MN
echo    Timezone: Asia/Ulaanbaatar (adjust in config if needed)
echo    Day names: Даваа гараг, Мягмар гараг, Лхагва гараг, etc.
echo.
pause
