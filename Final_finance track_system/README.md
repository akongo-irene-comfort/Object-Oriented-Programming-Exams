# Personal Finance Tracker - Modern GUI Edition

A modern, interactive personal finance tracking application built with Python and Tkinter, following Object-Oriented Programming principles.

## Features

- 💰 **Income & Expense Tracking** - Add and categorize all your financial transactions
- 📊 **Real-time Analytics** - View summaries, category breakdowns, and balance tracking
- 🎯 **Savings Goals** - Set and track progress toward your financial goals
- 💾 **Data Persistence** - All data is saved locally in JSON format
- 🎨 **Modern UI** - Beautiful dark theme with cool colors and interactive elements

## Requirements

### Python Version
- **Python 3.7 or higher** is required

### Dependencies

**Core Application (No Installation Needed!):**
- All required modules (`tkinter`, `json`, `datetime`, `os`, `typing`) are part of Python's standard library
- No additional packages need to be installed to run the application

**Optional Dependencies:**
- `matplotlib>=3.5.0` - Only needed if you want to add chart/visualization features in the future

## Installation

### Option 1: Using Virtual Environment (Recommended)

**Windows - Quick Setup:**
```bash
# Double-click setup_and_run.bat or run in terminal:
setup_and_run.bat
```

**Windows - Manual Setup:**
```bash
# Create virtual environment
python -m venv venv

# Activate (PowerShell)
.\venv\Scripts\Activate.ps1

# Activate (Command Prompt)
venv\Scripts\activate.bat

# Install dependencies
pip install tkcalendar

# Run application
python Project2.py
```

**After first setup, use run.bat for quick start:**
```bash
run.bat
```

### Option 2: Run Directly (Without Virtual Environment)
Since all dependencies are standard library modules, you can run the application directly:

```bash
python Project2.py
```

**Note:** For calendar date picker, install tkcalendar:
```bash
pip install tkcalendar
```

### Option 3: Install All Optional Dependencies
If you want all features including visualizations:

```bash
pip install -r requirements-optional.txt
```

This installs:
- `tkcalendar` - Calendar date picker (recommended)
- `matplotlib` - For future chart/visualization features

## Usage

1. **Run the application:**
   ```bash
   python Project2.py
   ```

2. **Add Transactions:**
   - Go to the "➕ Add Transaction" tab
   - Enter amount, date, category, and description
   - Click "➕ Add Income" or "➖ Add Expense"

3. **View Transactions:**
   - Check the "📋 View Transactions" tab to see all your entries

4. **View Summary:**
   - Go to "📊 Summary & Analytics" for income, expenses, balance, and category breakdown

5. **Set Goals:**
   - Use the "🎯 Savings Goals" tab to create and track savings goals

## Data Storage

All financial data is automatically saved to `finance_data.json` in the same directory as the application. Your data persists between sessions.

## Project Structure

- `Project2.py` - Main application file with all classes and GUI
- `finance_data.json` - Data storage file (created automatically)
- `requirements.txt` - Requirements file (no packages needed for core functionality)
- `requirements-optional.txt` - Optional dependencies for visualizations

## OOP Design

The application follows Object-Oriented Programming principles:

- **Transaction** (Base Class) - Abstract financial entry
- **Income** (Subclass) - Inherits from Transaction
- **Expense** (Subclass) - Inherits from Transaction
- **Category** - Manages transaction categories
- **Goal** - Manages savings goals
- **BudgetManager** - Main controller class
- **FinanceTrackerGUI** - GUI application class

## Color Scheme

- **Background:** Dark Navy (#0a0e27)
- **Cards:** Dark Blue-Gray (#1a1f3a)
- **Primary:** Indigo (#6366f1)
- **Success:** Green (#10b981)
- **Danger:** Red (#ef4444)
- **Accents:** Purple & Cyan

## Virtual Environment Guide

### Why Use a Virtual Environment?
- Keeps your project dependencies isolated
- Prevents conflicts with other Python projects
- Makes it easier to manage dependencies
- Recommended for all Python projects

### Quick Start with Virtual Environment

**First Time Setup:**
1. Run `setup_and_run.bat` (Windows) or `setup_and_run.ps1` (PowerShell)
2. The script will:
   - Create a virtual environment
   - Install required dependencies
   - Launch the application

**Subsequent Runs:**
- Use `run.bat` for quick start
- Or manually activate: `venv\Scripts\activate` then `python Project2.py`

**Deactivate when done:**
```bash
deactivate
```

See `SETUP_VENV.md` for detailed instructions.

## Troubleshooting

### Virtual Environment Issues

**PowerShell Execution Policy Error:**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**Virtual Environment Not Activating:**
- Make sure you're in the project directory
- Check that `venv` folder exists
- Try: `python -m venv venv` to recreate

### Tkinter Not Found
If you get an error about tkinter not being available:
- **Windows/Mac:** Tkinter should be included with Python
- **Linux:** Install with: `sudo apt-get install python3-tk` (Ubuntu/Debian) or `sudo yum install python3-tkinter` (CentOS/RHEL)

### Import Errors
Make sure you're using Python 3.7 or higher:
```bash
python --version
```

**Calendar Not Working:**
- Install tkcalendar: `pip install tkcalendar`
- Or run: `pip install -r requirements-optional.txt`

## License

This project is part of an academic assignment for Object-Oriented Programming.

## Author

Irene COMFORT AKONGO - S25M19/001 B34971

