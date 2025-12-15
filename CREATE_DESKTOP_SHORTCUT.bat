@echo off
echo Creating desktop shortcut for TopStyle Business Management System...

set "DESKTOP=%USERPROFILE%\Desktop"
set "PROJECT_PATH=%~dp0"
set "SHORTCUT_NAME=TopStyle Business Management.lnk"

echo Creating shortcut: %DESKTOP%\%SHORTCUT_NAME%

powershell -Command "& {$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%DESKTOP%\%SHORTCUT_NAME%'); $Shortcut.TargetPath = '%PROJECT_PATH%QUICK_START.bat'; $Shortcut.WorkingDirectory = '%PROJECT_PATH%'; $Shortcut.Description = 'TopStyle Business Management System - One-Click Startup'; $Shortcut.IconLocation = '%PROJECT_PATH%static\favicon.ico'; $Shortcut.Save()}"

if exist "%DESKTOP%\%SHORTCUT_NAME%" (
    echo ✓ Desktop shortcut created successfully!
    echo You can now double-click the shortcut on your desktop to start the system.
) else (
    echo ❌ Failed to create desktop shortcut.
    echo You can still run the system using QUICK_START.bat
)

echo.
echo Available startup methods:
echo 1. Double-click desktop shortcut (if created successfully)
echo 2. Double-click QUICK_START.bat
echo 3. Run: python auto_start.py
echo 4. Run: python run.py start
echo 5. Run: START_SYSTEM.bat
echo 6. Run: START_SYSTEM.ps1
echo.
pause
