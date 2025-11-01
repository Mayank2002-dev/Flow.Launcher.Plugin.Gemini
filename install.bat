@echo off
echo ============================================
echo Flow Launcher Gemini Plugin Installer
echo ============================================
echo.

REM Get the plugin directory
set PLUGIN_DIR=%~dp0
set FLOW_PLUGINS=%APPDATA%\FlowLauncher\Plugins
set DEST_DIR=%FLOW_PLUGINS%\Flow.Launcher.Plugin.Gemini

echo Plugin source: %PLUGIN_DIR%
echo Flow Launcher plugins: %FLOW_PLUGINS%
echo.

REM Check if Flow Launcher is installed
if not exist "%FLOW_PLUGINS%" (
    echo ERROR: Flow Launcher plugins directory not found!
    echo Please install Flow Launcher first: https://www.flowlauncher.com/
    pause
    exit /b 1
)

REM Create destination directory if it doesn't exist
if not exist "%DEST_DIR%" (
    echo Creating plugin directory...
    mkdir "%DEST_DIR%"
)

echo Copying plugin files...
xcopy /E /I /Y "%PLUGIN_DIR%*" "%DEST_DIR%"

REM Check if Python is available
echo.
echo Checking for Python...
where python >nul 2>nul
if %ERRORLEVEL% == 0 (
    echo Python found! Installing dependencies...
    python -m pip install -r "%DEST_DIR%\requirements.txt"
) else (
    echo Python not found in PATH.
    echo Trying Flow Launcher's Python...
    set FL_PYTHON=%APPDATA%\FlowLauncher\Environments\Python\python.exe
    if exist "!FL_PYTHON!" (
        echo Found Flow Launcher Python!
        "!FL_PYTHON!" -m pip install -r "%DEST_DIR%\requirements.txt"
    ) else (
        echo WARNING: Could not find Python!
        echo Please install dependencies manually:
        echo   pip install -r requirements.txt
    )
)

echo.
echo ============================================
echo Installation complete!
echo ============================================
echo.
echo Next steps:
echo 1. Restart Flow Launcher
echo 2. Go to Settings ^> Plugins ^> Gemini
echo 3. Enter your Google Gemini API key
echo 4. Start using: gemini [your prompt] ^|^|
echo.
echo Get your free API key from:
echo https://aistudio.google.com/app/apikey
echo.
pause