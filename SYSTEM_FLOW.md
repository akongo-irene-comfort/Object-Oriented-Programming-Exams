# Personal Finance Tracker - Complete System Flow

## 🔄 Complete User Flow

### 1. Application Start
```
Start Application
    ↓
Landing Page (Welcome Screen)
```

### 2. New User Registration Flow
```
Landing Page
    ↓ (Click "Sign Up")
Sign Up Page
    ↓ (Enter: Username, Password, Confirm Password)
    ↓ (Click "CREATE ACCOUNT")
Registration Processing
    ↓ (Auto-login)
Main Application
    ↓ (User can now use all features)
```

### 3. Existing User Login Flow
```
Landing Page
    ↓ (Click "Login")
Login Page
    ↓ (Enter: Username, Password)
    ↓ (Click "LOGIN")
Main Application
    ↓ (User can now use all features)
```

### 4. Logout Flow
```
Main Application
    ↓ (Click "🚪 Logout" button in header)
    ↓ (Confirm logout)
Landing Page
```

## 📋 Page Connections

### Landing Page
- **Buttons:**
  - "🔐 Login" → Opens Login Page
  - "✨ Sign Up" → Opens Sign Up Page

### Login Page
- **Fields:**
  - Username (required)
  - Password (required)
- **Buttons:**
  - "LOGIN" → Authenticates and opens Main App
  - "SIGN UP NOW" → Opens Sign Up Page
  - "← Back to Home" → Returns to Landing Page
- **Features:**
  - Enter key support
  - Clear error messages
  - Auto-focus on fields

### Sign Up Page
- **Fields:**
  - Username (required, must be unique)
  - Password (required, minimum 4 characters)
  - Confirm Password (required, must match)
- **Buttons:**
  - "CREATE ACCOUNT" → Registers user, auto-logs in, opens Main App
  - "← Back to Home" → Returns to Landing Page
- **Features:**
  - Real-time validation
  - Clear error messages
  - Auto-login after registration
  - Enter key support

### Main Application
- **Features:**
  - Username displayed in header
  - "🚪 Logout" button in header
  - All finance tracking features
  - User-specific data storage

## 🔐 Security Features

1. **Password Hashing:** All passwords are hashed using SHA-256
2. **User-Specific Data:** Each user has their own finance data file
3. **Secure Storage:** User credentials stored in `users.json`
4. **Session Management:** Current user tracked throughout session

## 📁 Data Files

- `users.json` - Stores all user accounts (hashed passwords)
- `finance_data_username.json` - User-specific finance data
- `app_settings.json` - Application settings (theme preference)

## ✅ Registration Validation

The system validates:
- ✅ Username is not empty
- ✅ Password is not empty
- ✅ Password is at least 4 characters
- ✅ Confirm password matches
- ✅ Username is unique (not already taken)

## 🎯 Complete Flow Verification

1. **Registration Works:**
   - User enters details → Account created → Auto-login → Main app opens

2. **Login Works:**
   - User enters credentials → Authenticated → Main app opens

3. **Logout Works:**
   - User clicks logout → Confirmed → Returns to landing page

4. **Navigation Works:**
   - All pages can navigate back to landing page
   - All pages are properly connected

## 🚀 How to Test

1. **Test Registration:**
   - Start app → Click "Sign Up" → Enter details → Click "CREATE ACCOUNT"
   - Should see success message → Auto-login → Main app opens

2. **Test Login:**
   - Start app → Click "Login" → Enter credentials → Click "LOGIN"
   - Should authenticate → Main app opens

3. **Test Logout:**
   - In main app → Click "🚪 Logout" → Confirm
   - Should return to landing page

All pages are now fully functional and connected! 🎉


