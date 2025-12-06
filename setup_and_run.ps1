# Personal Finance Tracker - Setup Script (PowerShell)
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Personal Finance Tracker - Setup Script" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if virtual environment already exists
if (Test-Path "venv") {
    Write-Host "Virtual environment already exists." -ForegroundColor Yellow
    Write-Host ""
} else {
    Write-Host "Step 1: Creating virtual environment..." -ForegroundColor Green
    python -m venv venv
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERROR: Failed to create virtual environment!" -ForegroundColor Red
        Write-Host "Make sure Python is installed and in your PATH." -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }
    Write-Host "Virtual environment created successfully!" -ForegroundColor Green
    Write-Host ""
}

Write-Host "Step 2: Activating virtual environment..." -ForegroundColor Green
& .\venv\Scripts\Activate.ps1
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Failed to activate virtual environment!" -ForegroundColor Red
    Write-Host "You may need to run: Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}
Write-Host "Virtual environment activated!" -ForegroundColor Green
Write-Host ""

Write-Host "Step 3: Upgrading pip..." -ForegroundColor Green
python -m pip install --upgrade pip --quiet
Write-Host ""

Write-Host "Step 4: Installing dependencies..." -ForegroundColor Green
pip install tkcalendar
if ($LASTEXITCODE -ne 0) {
    Write-Host "WARNING: Failed to install tkcalendar!" -ForegroundColor Yellow
    Write-Host "The application will still work but without calendar picker." -ForegroundColor Yellow
    Write-Host ""
} else {
    Write-Host "Dependencies installed successfully!" -ForegroundColor Green
    Write-Host ""
}

Write-Host "Step 5: Running application..." -ForegroundColor Green
Write-Host ""
python Project2.py

Write-Host ""
Write-Host "Application closed." -ForegroundColor Cyan
Read-Host "Press Enter to exit"


