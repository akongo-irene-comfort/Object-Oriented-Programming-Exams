# Setting Up and Running in Virtual Environment

## Step-by-Step Guide for Windows

### Step 1: Create a Virtual Environment

Open PowerShell or Command Prompt in your project directory and run:

```bash
python -m venv venv
```

This creates a folder named `venv` with the virtual environment.

### Step 2: Activate the Virtual Environment

**For PowerShell:**
```bash
.\venv\Scripts\Activate.ps1
```

**For Command Prompt (CMD):**
```bash
venv\Scripts\activate.bat
```

**Note:** If you get an execution policy error in PowerShell, run:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

After activation, you should see `(venv)` at the beginning of your command prompt.

### Step 3: Install Dependencies

Install the required packages:

```bash
# Install calendar picker (recommended)
pip install tkcalendar

# Or install all optional dependencies
pip install -r requirements-optional.txt
```

### Step 4: Run the Application

```bash
python Project2.py
```

### Step 5: Deactivate (When Done)

When you're finished, deactivate the virtual environment:

```bash
deactivate
```

---

## Quick Setup Script

You can also create a batch file to automate this process. Create `setup_and_run.bat`:

```batch
@echo off
echo Creating virtual environment...
python -m venv venv

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo Installing dependencies...
pip install --upgrade pip
pip install tkcalendar

echo Running application...
python Project2.py

pause
```

---

## Troubleshooting

### Virtual Environment Not Found
- Make sure Python is installed: `python --version`
- Use `python3` instead of `python` if needed

### Permission Errors
- Run PowerShell/CMD as Administrator
- Check execution policy: `Get-ExecutionPolicy`

### Module Not Found Errors
- Make sure virtual environment is activated (you should see `(venv)`)
- Reinstall dependencies: `pip install -r requirements-optional.txt`

---

## Alternative: Using Python's Built-in venv

If you prefer a different name for your virtual environment:

```bash
# Create with custom name
python -m venv myenv

# Activate
myenv\Scripts\activate

# Install and run
pip install tkcalendar
python Project2.py
```


