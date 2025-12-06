@echo off
echo ========================================
echo Personal Finance Tracker - Setup Script
echo ========================================
echo.

REM Check if virtual environment already exists
if exist "venv" (
    echo Virtual environment already exists.
    echo.
) else (
    echo Step 1: Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo ERROR: Failed to create virtual environment!
        echo Make sure Python is installed and in your PATH.
        pause
        exit /b 1
    )
    echo Virtual environment created successfully!
    echo.
)

echo Step 2: Activating virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo ERROR: Failed to activate virtual environment!
    pause
    exit /b 1
)
echo Virtual environment activated!
echo.

echo Step 3: Upgrading pip...
python -m pip install --upgrade pip --quiet
echo.

echo Step 4: Installing dependencies...
pip install tkcalendar
if errorlevel 1 (
    echo WARNING: Failed to install tkcalendar!
    echo The application will still work but without calendar picker.
    echo.
) else (
    echo Dependencies installed successfully!
    echo.
)

echo Step 5: Running application...
echo.
python Project2.py

echo.
echo Application closed.
pause


