@echo off
title Smart Agriculture & Rural Tech Launcher
echo ========================================================
echo   SMART AGRICULTURE AND RURAL TECH PRESENTATION ENGINE
echo ========================================================
echo.

:: 1. Navigate to the project folder
cd /d "C:\Users\THRIVENI H M\OneDrive\Documents\New folder"

:: 2. Open the project folder in Windows Explorer
echo [1/3] Opening project folder in Explorer...
start explorer .

:: 3. Launch default web browser to the local application link
echo [2/3] Preparing web interface tab...
start http://127.0.0.1:5000/

:: 4. Make sure dependencies are installed and boot the backend server
echo [3/3] Checking requirements and starting backend server...
pip install -r requirements.txt
echo.
echo Server is launching. Please keep this black terminal window open!
echo.
python app.py

pause
