@echo off
REM run-start.bat - wrapper to run the PowerShell startup script from the repo folder
SET scriptDir=%~dp0
echo Running START_SYSTEM.ps1 from %scriptDir%
powershell -NoProfile -ExecutionPolicy Bypass -File "%scriptDir%START_SYSTEM.ps1" %*
