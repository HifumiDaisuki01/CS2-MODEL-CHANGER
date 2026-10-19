@echo off
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0Verify-Workshop-Project.ps1"
if errorlevel 1 (echo FAILED)
pause
