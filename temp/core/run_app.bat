@echo off
echo Starting School Timetable Generator...
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ and try again
    pause
    exit /b 1
)

REM Check if required files exist
if not exist "app_gui.py" (
    echo ERROR: app_gui.py not found
    echo Please make sure you're in the correct directory
    pause
    exit /b 1
)

if not exist "database_setup.py" (
    echo ERROR: database_setup.py not found
    echo Please make sure all files are present
    pause
    exit /b 1
)

echo Checking system components...
python test_system.py
if errorlevel 1 (
    echo.
    echo WARNING: Some components failed tests
    echo The application may still work with reduced functionality
    echo.
)

echo.
echo Launching application...
echo Press Ctrl+C in this window to stop the application
echo.

python app_gui.py

echo.
echo Application closed.
pause