# Quick Start Guide - Personal Finance Tracker

## 🚀 Getting Started

### Step 1: Verify Setup (Optional)
Run the verification script to ensure everything is ready:
```bash
python verify_setup.py
```

### Step 2: Launch the Application
Simply run:
```bash
python Project2.py
```

The application window will open with a modern, colorful interface!

## 📱 Using the Application

### Tab 1: ➕ Add Transaction
- Enter transaction details (amount, date, category, description)
- Click **"➕ Add Income"** for money coming in
- Click **"➖ Add Expense"** for money going out
- View quick stats on the right side

### Tab 2: 📋 View Transactions
- Scroll through all your transactions
- See income (💰) and expenses (💸) with color coding
- View by category and date

### Tab 3: 📊 Summary & Analytics
- **Total Income** - All money earned
- **Total Expenses** - All money spent
- **Current Balance** - Your net balance
- **Category Breakdown** - See spending by category

### Tab 4: 🎯 Savings Goals
- Create new savings goals
- Set target amount and description
- Track progress with visual progress bars
- See percentage completion

## 💾 Data Storage

Your data is automatically saved to `finance_data.json` in the same folder. 
- Data persists between sessions
- No need to manually save
- Safe and local - your data stays on your computer

## 🎨 Features

✅ Modern dark theme with cool colors
✅ Real-time balance updates
✅ Category-based organization
✅ Savings goal tracking
✅ Interactive and user-friendly interface
✅ Automatic data persistence

## ❓ Troubleshooting

**Application won't start?**
- Make sure Python 3.7+ is installed: `python --version`
- Run verification: `python verify_setup.py`

**Tkinter error?**
- Windows/Mac: Should work out of the box
- Linux: Install with `sudo apt-get install python3-tk`

**Data not saving?**
- Check file permissions in the project folder
- Ensure `finance_data.json` is writable

## 📝 Tips

- Use descriptive categories for better organization
- Set realistic savings goals
- Review your summary regularly
- The balance updates automatically in the header

Enjoy managing your finances! 💰


