@echo off
echo ============================================
echo Flow Launcher Gemini Plugin Installer
echo ============================================
echo.

REM Find Flow Launcher Python
echo [Step 1/5] Locating Flow Launcher Python...
set PYTHON_FOUND=0
for /f "tokens=*" %%i in ('dir /b /s "%APPDATA%\FlowLauncher\Environments\Python\PythonEmbeddable-*\python.exe" 2^>nul') do (
    set FLOW_PYTHON=%%i
    set PYTHON_DIR=%%~dpi
    set PYTHON_FOUND=1
    goto :found
)

:found
if %PYTHON_FOUND%==0 (
    echo ERROR: Flow Launcher Python not found!
    pause
    exit /b 1
)

echo Found: %FLOW_PYTHON%
echo Directory: %PYTHON_DIR%
echo.

REM Check Python version
echo [Step 2/5] Checking Python version...
"%FLOW_PYTHON%" --version
echo.

REM Check if this is embedded Python (needs special handling)
echo [Step 3/5] Configuring embedded Python for pip...

REM Embedded Python needs python311._pth file modification
set PTH_FILE=%PYTHON_DIR%python311._pth
if exist "%PTH_FILE%" (
    echo Found embedded Python configuration file.
    echo Enabling site-packages...
    
    REM Backup original
    copy "%PTH_FILE%" "%PTH_FILE%.backup" >nul 2>&1
    
    REM Check if import site is commented
    findstr /C:"#import site" "%PTH_FILE%" >nul
    if %ERRORLEVEL%==0 (
        echo Uncommenting 'import site'...
        powershell -Command "(Get-Content '%PTH_FILE%') -replace '#import site', 'import site' | Set-Content '%PTH_FILE%'"
    )
    
    REM Check if import site exists at all
    findstr /C:"import site" "%PTH_FILE%" >nul
    if %ERRORLEVEL% neq 0 (
        echo Adding 'import site'...
        echo import site >> "%PTH_FILE%"
    )
    
    echo Configuration updated.
) else (
    echo Not an embedded Python or already configured.
)
echo.

REM Download and install pip if needed
echo [Step 4/5] Installing/Updating pip...
"%FLOW_PYTHON%" -m ensurepip >nul 2>&1
"%FLOW_PYTHON%" -m pip --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo Pip not found. Downloading get-pip.py...
    
    REM Try with PowerShell
    powershell -Command "try { Invoke-WebRequest -Uri 'https://bootstrap.pypa.io/get-pip.py' -OutFile 'get-pip.py' -UseBasicParsing } catch { exit 1 }"
    
    if exist get-pip.py (
        echo Installing pip...
        "%FLOW_PYTHON%" get-pip.py --no-warn-script-location
        del get-pip.py
    ) else (
        echo Failed to download pip installer.
        echo Trying alternative method...
        
        REM Try curl
        curl -o get-pip.py https://bootstrap.pypa.io/get-pip.py
        if exist get-pip.py (
            "%FLOW_PYTHON%" get-pip.py --no-warn-script-location
            del get-pip.py
        ) else (
            echo ERROR: Could not install pip.
            echo Please install pip manually or check your internet connection.
            pause
            exit /b 1
        )
    )
)

echo Pip is available.
echo.

REM Upgrade pip
echo Upgrading pip...
"%FLOW_PYTHON%" -m pip install --upgrade pip --no-warn-script-location --quiet
echo.

REM Install packages one by one with verbose output
echo [Step 5/5] Installing packages...
echo.

echo Installing google-generativeai...
"%FLOW_PYTHON%" -m pip install google-generativeai --no-warn-script-location
echo.

echo Installing requests...
"%FLOW_PYTHON%" -m pip install requests --no-warn-script-location
echo.

echo Installing Flox-lib...
"%FLOW_PYTHON%" -m pip install Flox-lib --no-warn-script-location
echo.

echo Installing pyperclip...
"%FLOW_PYTHON%" -m pip install pyperclip --no-warn-script-location
echo.

REM Verify installation
echo ============================================
echo Verifying Installation
echo ============================================
echo.

set ALL_OK=1

"%FLOW_PYTHON%" -c "import google.generativeai; print('✓ google-generativeai installed successfully')" 2>nul || (echo ✗ google-generativeai FAILED & set ALL_OK=0)
"%FLOW_PYTHON%" -c "import requests; print('✓ requests installed successfully')" 2>nul || (echo ✗ requests FAILED & set ALL_OK=0)
"%FLOW_PYTHON%" -c "import flox; print('✓ flox installed successfully')" 2>nul || (echo ✗ flox FAILED & set ALL_OK=0)
"%FLOW_PYTHON%" -c "import pyperclip; print('✓ pyperclip installed successfully')" 2>nul || (echo ✗ pyperclip FAILED & set ALL_OK=0)

echo.
echo ============================================

if %ALL_OK%==1 (
    echo SUCCESS! All packages installed correctly.
    echo.
    echo NEXT STEPS:
    echo 1. CLOSE Flow Launcher completely ^(right-click tray icon → Exit^)
    echo 2. START Flow Launcher again
    echo 3. Get API key from: https://aistudio.google.com/app/apikey
    echo 4. Settings → Plugins → Gemini → Add API key
    echo 5. Test with: gemini hello world ^|^|
) else (
    echo.
    echo Some packages failed to install.
    echo.
    echo Please check the error messages above and try:
    echo 1. Running this script as Administrator
    echo 2. Checking your internet connection
    echo 3. Temporarily disabling antivirus
    echo.
    echo If problems persist, try manual installation:
    echo "%FLOW_PYTHON%" -m pip install google-generativeai requests Flox-lib pyperclip
)

echo.
pause