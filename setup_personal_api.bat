@echo off
echo.
echo 🔧 Personal API Module Setup
echo ============================
echo.

REM Check if we're in a MagicMirror directory
if not exist "package.json" (
    echo ❌ Error: This doesn't appear to be a MagicMirror² directory
    echo    Please run this script from your MagicMirror² root directory
    pause
    exit /b 1
)

if not exist "modules" (
    echo ❌ Error: This doesn't appear to be a MagicMirror² directory
    echo    Please run this script from your MagicMirror² root directory
    pause
    exit /b 1
)

echo ✅ MagicMirror² directory detected
echo.

REM Test API connectivity
echo 🌐 Testing API connectivity...
set API_URL=https://calendar-app-production-6d2d.up.railway.app/api/magic-mirror/future-data

curl -s --head "%API_URL%" >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo ✅ API is accessible
) else (
    echo ⚠️  Warning: API might not be accessible
    echo    URL: %API_URL%
)
echo.

REM Check if personalapi module exists
if exist "modules\personalapi" (
    echo ✅ Personal API module found
) else (
    echo ❌ Personal API module not found
    echo    Please ensure the module is in modules\personalapi\
    pause
    exit /b 1
)

REM Check if face recognition status file exists
set STATUS_FILE=C:\tmp\magicmirror_face_status.json
if exist "%STATUS_FILE%" (
    echo ✅ Face recognition status file found
    echo    Current status:
    type "%STATUS_FILE%" | findstr /C:"person" /C:"active" /C:"distance"
) else (
    echo ⚠️  Face recognition status file not found
    echo    File: %STATUS_FILE%
    echo    This is normal if face recognition isn't running yet
)
echo.

REM Test the API with a sample request
echo 🧪 Testing API data structure...
where node >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    if exist "test_personal_api.js" (
        echo    Running API test...
        node test_personal_api.js
    ) else (
        echo    Test script not found, skipping API test
    )
) else (
    echo    Node.js not found, skipping API test
)
echo.

REM Check configuration
echo 📋 Configuration check...
findstr /C:"personalapi" config\config.js >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo ✅ Personal API module found in config
) else (
    echo ⚠️  Personal API module not found in config
    echo    Please add the module to your config\config.js:
    echo.
    echo    {
    echo        module: "personalapi",
    echo        position: "middle_center",
    echo        header: "Personal Schedule",
    echo        config: {
    echo            apiUrl: "https://calendar-app-production-6d2d.up.railway.app/api/magic-mirror/future-data",
    echo            updateInterval: 5 * 60 * 1000,
    echo            animationSpeed: 2000,
    echo            statusFile: "C:\tmp\magicmirror_face_status.json",
    echo            maxEvents: 5,
    echo            maxLists: 3,
    echo            showCompleted: false
    echo        }
    echo    }
)
echo.

REM Check dependencies
echo 📦 Checking dependencies...
if exist "package.json" (
    findstr /C:"node-fetch" package.json >nul 2>&1
    if %ERRORLEVEL% EQU 0 (
        echo ✅ node-fetch dependency found
    ) else (
        echo ⚠️  node-fetch dependency not found
        echo    Installing node-fetch...
        npm install node-fetch
    )
) else (
    echo    package.json not found, skipping dependency check
)
echo.

echo 🎉 Setup complete!
echo.
echo 📋 Next steps:
echo    1. Ensure face recognition is running
echo    2. Start MagicMirror²: npm start
echo    3. The module will show data for recognized users
echo    4. Check the middle_center position for personal schedule
echo.
echo 🔧 Troubleshooting:
echo    - Check browser console for errors
echo    - Verify API connectivity with: curl %API_URL%
echo    - Test face recognition status file
echo    - Check module logs in MagicMirror²
echo.
echo 📚 For more information, see modules\personalapi\README.md
echo.
pause
