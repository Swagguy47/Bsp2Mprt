@echo off
set SCRIPT_DIR=%~dp0
cd /d "%SCRIPT_DIR%"

pyinstaller --onefile --icon=app.ico Bsp2Mprt.py