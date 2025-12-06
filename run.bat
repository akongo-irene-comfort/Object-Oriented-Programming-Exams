@echo off
REM Quick run script - assumes venv is already set up
if not exist "venv" (
    echo Virtual environment not found!
    echo Please run setup_and_run.bat first to set up the environment.
    pause
    exit /b 1
)

call venv\Scripts\activate.bat
python Project2.py


