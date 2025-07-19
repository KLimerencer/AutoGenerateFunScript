@echo off
REM Launch the AIfunScript GUI

python gui_detector.py
if %errorlevel% neq 0 (
    echo.
    echo Failed to launch the GUI. Make sure Python is installed and requirements are met.
    pause
) 