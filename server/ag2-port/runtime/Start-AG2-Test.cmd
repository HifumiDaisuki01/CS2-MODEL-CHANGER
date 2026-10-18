@echo off
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0Start-AG2-Test.ps1" %*
pause
