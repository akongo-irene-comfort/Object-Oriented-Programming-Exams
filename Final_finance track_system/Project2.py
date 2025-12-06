import tkinter as tk
from tkinter import ttk, messagebox
import json
import datetime
import os
import hashlib
from typing import List, Dict

try:
    from tkcalendar import DateEntry
    CALENDAR_AVAILABLE = True
except ImportError:
    CALENDAR_AVAILABLE = False
    print("Warning: tkcalendar not available. Install with: pip install tkcalendar")

try:
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    from matplotlib.figure import Figure
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    print("Warning: matplotlib not available. Install with: pip install matplotlib")

# Transaction Base Class
class Transaction:
    def __init__(self, amount, date, category, description):
        self.__amount = amount
        self.__date = date
        self.__category = category
        self.__description = description

    def get_amount(self): 
        return self.__amount
    
    def get_date(self): 
        return self.__date
    
    def get_category(self): 
        return self.__category
    
    def get_description(self): 
        return self.__description

    def to_dict(self):
        return {
            "amount": self.__amount,
            "date": self.__date,
            "category": self.__category,
            "description": self.__description,
            "type": "income" if self.__amount > 0 else "expense"
        }

# Income Subclass
class Income(Transaction):
    def __init__(self, amount, date, category, description):
        super().__init__(abs(amount), date, category, description)

# Expense Subclass
class Expense(Transaction):
    def __init__(self, amount, date, category, description):
        super().__init__(-abs(amount), date, category, description)

# Category Class
class Category:
    def __init__(self):
        self.__categories = ["Food", "Transport", "Entertainment", "Bills", "Shopping", "Healthcare", "Education", "Other"]

    def get_categories(self):
        return self.__categories

    def add_category(self, category):
        if category not in self.__categories:
            self.__categories.append(category)
            return True
        return False

# Goal Class
class Goal:
    def __init__(self, target_amount, description):
        self.__target_amount = target_amount
        self.__description = description
        self.__current_amount = 0

    def get_target(self):
        return self.__target_amount
    
    def get_description(self):
        return self.__description
    
    def get_current(self):
        return self.__current_amount

    def add_amount(self, amount):
        self.__current_amount += amount
        if self.__current_amount > self.__target_amount:
            self.__current_amount = self.__target_amount

    def get_progress(self):
        if self.__target_amount == 0:
            return 0
        return min((self.__current_amount / self.__target_amount) * 100, 100)
    
    def set_current(self, amount):
        self.__current_amount = amount
    
    def to_dict(self):
        return {
            "target": self.__target_amount,
            "description": self.__description,
            "current": self.__current_amount
        }

# Budget Manager Class
class BudgetManager:
    def __init__(self, username=None):
        self.transactions: List[Transaction] = []
        self.goals: List[Goal] = []
        self.category_mgr = Category()
        # Use user-specific data file if username provided
        if username:
            self.filename = f"finance_data_{username}.json"
        else:
            self.filename = "finance_data.json"

    def add_transaction(self, trans):
        self.transactions.append(trans)
        self.save_data()
    
    def remove_transaction(self, trans):
        """Remove a transaction from the list"""
        if trans in self.transactions:
            self.transactions.remove(trans)
            self.save_data()
            return True
        return False
    
    def clear_all_transactions(self):
        """Clear all transactions from the list"""
        self.transactions.clear()
        self.save_data()
        return True

    def add_goal(self, goal):
        self.goals.append(goal)
        self.save_data()

    def get_total_income(self):
        return sum(t.get_amount() for t in self.transactions if t.get_amount() > 0)

    def get_total_expenses(self):
        return abs(sum(t.get_amount() for t in self.transactions if t.get_amount() < 0))

    def get_balance(self):
        return self.get_total_income() - self.get_total_expenses()

    def get_transactions_by_category(self):
        category_totals = {}
        for trans in self.transactions:
            cat = trans.get_category()
            if cat not in category_totals:
                category_totals[cat] = {"income": 0, "expense": 0}
            if trans.get_amount() > 0:
                category_totals[cat]["income"] += trans.get_amount()
            else:
                category_totals[cat]["expense"] += abs(trans.get_amount())
        return category_totals

    def save_data(self):
        """Save transactions and goals to file"""
        try:
            data = {
                "transactions": [t.to_dict() for t in self.transactions],
                "goals": [g.to_dict() for g in self.goals]
            }
            with open(self.filename, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving data to {self.filename}: {e}")
            raise

    def load_data(self):
        if os.path.exists(self.filename):
            try:
                with open(self.filename, 'r') as f:
                    data = json.load(f)
                    self.transactions = []
                    for t in data.get("transactions", []):
                        if t.get("type") == "income" or t.get("amount", 0) > 0:
                            self.transactions.append(Income(
                                t["amount"], t["date"], t["category"], t["description"]
                            ))
                        else:
                            self.transactions.append(Expense(
                                abs(t["amount"]), t["date"], t["category"], t["description"]
                            ))
                    
                    self.goals = []
                    for g in data.get("goals", []):
                        goal = Goal(g["target"], g["desc"] if "desc" in g else g.get("description", ""))
                        goal.set_current(g.get("current", 0))
                        self.goals.append(goal)
            except Exception as e:
                print(f"Error loading data: {e}")

# User Authentication System
class UserManager:
    def __init__(self):
        self.users_file = "users.json"
        self.current_user = None
    
    def hash_password(self, password):
        """Hash password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def load_users(self):
        """Load users from file"""
        if os.path.exists(self.users_file):
            try:
                with open(self.users_file, 'r') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def save_users(self, users):
        """Save users to file"""
        try:
            with open(self.users_file, 'w') as f:
                json.dump(users, f, indent=2)
        except Exception as e:
            print(f"Error saving users: {e}")
            raise
    
    def register_user(self, username, password):
        """Register a new user"""
        try:
            users = self.load_users()
            if username in users:
                return False, "Username already exists!"
            
            if len(password) < 4:
                return False, "Password must be at least 4 characters!"
            
            if not username.strip():
                return False, "Username cannot be empty!"
            
            users[username] = {
                "password_hash": self.hash_password(password),
                "created_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            self.save_users(users)
            return True, "User registered successfully!"
        except Exception as e:
            return False, f"Registration failed: {str(e)}"
    
    def authenticate(self, username, password):
        """Authenticate user with proper validation and strict access control"""
        # CRITICAL: Clear any existing session FIRST before authentication
        self.current_user = None
        
        # STRICT VALIDATION: Check username
        if not username or not isinstance(username, str):
            return False, "Please enter a valid username!"
        
        username = username.strip()
        if not username:
            return False, "Username cannot be empty!"
        
        # STRICT VALIDATION: Check password
        if not password or not isinstance(password, str):
            return False, "Please enter a valid password!"
        
        if not password:
            return False, "Password cannot be empty!"
        
        # Load users database
        users = self.load_users()
        
        # ACCESS CONTROL: Check if username exists in database
        if username not in users:
            self.current_user = None  # Ensure no user is set
            return False, "Invalid username or password!"
        
        # ACCESS CONTROL: Verify password with strict comparison
        password_hash = self.hash_password(password)
        stored_hash = users[username].get("password_hash")
        
        if not stored_hash:
            self.current_user = None
            return False, "Invalid user account! Please contact administrator."
        
        # STRICT PASSWORD VERIFICATION: Compare hashes exactly
        if stored_hash == password_hash:
            # CRITICAL: Set current user ONLY after successful authentication
            self.current_user = username
            
            # VERIFICATION: Double-check user is set correctly
            if self.current_user != username:
                self.current_user = None
                return False, "Authentication error! Please try again."
            
            return True, "Login successful!"
        else:
            # ACCESS CONTROL: Wrong password - clear session
            self.current_user = None
            return False, "Invalid username or password!"
    
    def logout(self):
        """Logout current user and clear session completely"""
        # CRITICAL: Clear user session completely
        old_user = self.current_user
        self.current_user = None
        
        # Force garbage collection of any cached data
        import gc
        gc.collect()
        
        # Verify logout was successful
        if self.current_user is not None:
            self.current_user = None  # Force clear again

# Unified App Controller - Manages all navigation in a single window
class AppController:
    def __init__(self, root):
        self.root = root
        self.user_manager = UserManager()
        self.root.title("Personal Finance Tracker")
        self.root.geometry("1000x750")
        self.root.resizable(True, True)
        
        # Center the window
        self.center_window()
        
        # Container frame for all pages
        self.container = tk.Frame(root)
        self.container.pack(fill='both', expand=True)
        
        # Store page references
        self.pages = {}
        
        # Start with landing page
        self.show_landing_page()
    
    def center_window(self):
        """Center the window on screen"""
        self.root.update_idletasks()
        width = 1000
        height = 750
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def hide_all_pages(self):
        """Hide all pages"""
        for page in self.pages.values():
            if page:
                page.pack_forget()
    
    def show_landing_page(self):
        """Show landing page"""
        self.hide_all_pages()
        if 'landing' not in self.pages or not self.pages['landing']:
            self.pages['landing'] = LandingPage(self.container, self.user_manager, self)
        self.pages['landing'].pack(fill='both', expand=True)
        self.root.title("Personal Finance Tracker - Welcome")
    
    def show_login_page(self):
        """Show login page"""
        self.hide_all_pages()
        if 'login' not in self.pages or not self.pages['login']:
            self.pages['login'] = LoginWindow(self.container, self.user_manager, self)
        self.pages['login'].pack(fill='both', expand=True)
        self.root.title("Personal Finance Tracker - Login")
    
    def show_signup_page(self):
        """Show signup page"""
        self.hide_all_pages()
        if 'signup' not in self.pages or not self.pages['signup']:
            self.pages['signup'] = SignUpWindow(self.container, self.user_manager, self)
        self.pages['signup'].pack(fill='both', expand=True)
        self.root.title("Personal Finance Tracker - Sign Up")
    
    def show_main_app(self):
        """Show main finance tracker application - WITH STRICT ACCESS CONTROL"""
        # STRICT ACCESS CONTROL: Verify user manager exists
        if not self.user_manager:
            messagebox.showerror("Access Denied", "Authentication system error!\n\nPlease restart the application.")
            return
        
        # STRICT ACCESS CONTROL: Verify user is authenticated
        if not self.user_manager.current_user:
            messagebox.showerror("Access Denied", "You must be logged in to access the application!\n\nPlease login first.")
            self.show_login_page()
            return
        
        # Get current username and validate
        username = self.user_manager.current_user.strip()
        if not username:
            messagebox.showerror("Access Denied", "Invalid user session!\n\nPlease login again.")
            self.user_manager.logout()
            self.show_login_page()
            return
        
        # CRITICAL: Always destroy old main app to prevent data mixing between users
        self.hide_all_pages()
        if 'main' in self.pages:
            try:
                # Destroy the frame and all its widgets
                if hasattr(self.pages['main'], 'frame'):
                    self.pages['main'].frame.destroy()
                # Clear budget manager data
                if hasattr(self.pages['main'], 'budget_mgr'):
                    self.pages['main'].budget_mgr = None
            except Exception as e:
                print(f"Error destroying old main app: {e}")
            finally:
                del self.pages['main']
        
        # Create NEW instance with current user's data - ensures fresh data for each user
        try:
            self.pages['main'] = FinanceTrackerGUI(self.container, self.user_manager, self)
            self.pages['main'].pack(fill='both', expand=True)
            self.root.title(f"💰 Personal Finance Tracker - {username}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load application for user {username}!\n\n{str(e)}")
            self.user_manager.logout()
            self.show_login_page()

# Modern Landing Page (now a Frame)
class LandingPage:
    def __init__(self, parent, user_manager, app_controller):
        self.parent = parent
        self.user_manager = user_manager
        self.app_controller = app_controller
        
        # Modern color scheme
        self.colors = {
            'bg': '#0f172a',  # Dark blue background
            'card': '#1e293b',
            'primary': '#6366f1',  # Indigo
            'primary_hover': '#818cf8',
            'secondary': '#8b5cf6',  # Purple
            'success': '#10b981',  # Green
            'text': '#f1f5f9',
            'text_muted': '#94a3b8',
            'accent': '#06b6d4'  # Cyan
        }
        
        self.frame = tk.Frame(parent, bg=self.colors['bg'])
        self.setup_landing_ui()
    
    def pack(self, **kwargs):
        """Pack method for frame compatibility"""
        self.frame.pack(**kwargs)
    
    def pack_forget(self):
        """Pack forget for frame compatibility"""
        self.frame.pack_forget()
    
    def setup_landing_ui(self):
        """Setup modern landing page interface"""
        # Main container
        main_frame = self.frame
        
        main_frame.pack(fill='both', expand=True)
        
        # Top decorative element
        top_decoration = tk.Frame(main_frame, bg=self.colors['primary'], height=5)
        top_decoration.pack(fill='x')
        
        # Content container
        content_frame = tk.Frame(main_frame, bg=self.colors['bg'])
        content_frame.pack(fill='both', expand=True, padx=50, pady=40)
        
        # Logo and Title Section
        logo_frame = tk.Frame(content_frame, bg=self.colors['bg'])
        logo_frame.pack(pady=(20, 40))
        
        # Large emoji logo
        logo_label = tk.Label(
            logo_frame,
            text="💰",
            font=('Segoe UI', 80),
            bg=self.colors['bg'],
            fg=self.colors['primary']
        )
        logo_label.pack()
        
        # Main title
        title_label = tk.Label(
            logo_frame,
            text="Personal Finance Tracker",
            font=('Segoe UI', 36, 'bold'),
            bg=self.colors['bg'],
            fg=self.colors['text']
        )
        title_label.pack(pady=(15, 10))
        
        # Subtitle
        subtitle_label = tk.Label(
            logo_frame,
            text="Take control of your finances with ease",
            font=('Segoe UI', 16),
            bg=self.colors['bg'],
            fg=self.colors['text_muted']
        )
        subtitle_label.pack()
        
        # Features section
        features_frame = tk.Frame(content_frame, bg=self.colors['bg'])
        features_frame.pack(pady=(30, 40))
        
        features = [
            ("📊", "Track Income & Expenses"),
            ("🎯", "Set Savings Goals"),
            ("📈", "View Analytics"),
            ("💾", "Secure Data Storage")
        ]
        
        for icon, text in features:
            feature_frame = tk.Frame(features_frame, bg=self.colors['bg'])
            feature_frame.pack(side='left', padx=20)
            
            icon_label = tk.Label(
                feature_frame,
                text=icon,
                font=('Segoe UI', 24),
                bg=self.colors['bg'],
                fg=self.colors['primary']
            )
            icon_label.pack()
            
            text_label = tk.Label(
                feature_frame,
                text=text,
                font=('Segoe UI', 11),
                bg=self.colors['bg'],
                fg=self.colors['text_muted']
            )
            text_label.pack(pady=(5, 0))
        
        # Action buttons section
        buttons_frame = tk.Frame(content_frame, bg=self.colors['bg'])
        buttons_frame.pack(pady=(40, 20))
        
        # Login button - Larger and more visible
        login_btn = tk.Button(
            buttons_frame,
            text="🔐 Login",
            font=('Segoe UI', 20, 'bold'),
            bg=self.colors['primary'],
            fg='white',
            relief='flat',
            bd=0,
            padx=60,
            pady=25,
            cursor='hand2',
            command=self.show_login,
            activebackground=self.colors['primary_hover']
        )
        login_btn.pack(side='left', padx=15)
        
        # Sign Up button - Larger and more visible
        signup_btn = tk.Button(
            buttons_frame,
            text="✨ Sign Up",
            font=('Segoe UI', 20, 'bold'),
            bg=self.colors['secondary'],
            fg='white',
            relief='flat',
            bd=0,
            padx=60,
            pady=25,
            cursor='hand2',
            command=self.show_signup,
            activebackground='#a78bfa'
        )
        signup_btn.pack(side='left', padx=15)
        
        # Footer
        footer_label = tk.Label(
            content_frame,
            text="Secure • Private • Easy to Use",
            font=('Segoe UI', 12),
            bg=self.colors['bg'],
            fg=self.colors['text_muted']
        )
        footer_label.pack(pady=(30, 0))
    
    def show_login(self):
        """Show login page"""
        self.app_controller.show_login_page()
    
    def show_signup(self):
        """Show signup page"""
        self.app_controller.show_signup_page()

# Sign Up Window (now a Frame)
class SignUpWindow:
    def __init__(self, parent, user_manager, app_controller):
        self.parent = parent
        self.user_manager = user_manager
        self.app_controller = app_controller
        
        # Color scheme
        self.colors = {
            'bg': '#f5f7fa',
            'card': '#ffffff',
            'primary': '#6366f1',
            'success': '#10b981',
            'danger': '#ef4444',
            'text': '#1f2937',
            'text_muted': '#6b7280',
            'border': '#e5e7eb'
        }
        
        self.frame = tk.Frame(parent, bg=self.colors['bg'])
        self.setup_signup_ui()
    
    def pack(self, **kwargs):
        """Pack method for frame compatibility"""
        self.frame.pack(**kwargs)
    
    def pack_forget(self):
        """Pack forget for frame compatibility"""
        self.frame.pack_forget()
    
    def setup_signup_ui(self):
        """Setup signup interface - Professional and Clear with ALL fields visible"""
        # Main container - simple and clean
        main_frame = self.frame
        
        # Header section
        header_frame = tk.Frame(main_frame, bg=self.colors['bg'])
        header_frame.pack(pady=(20, 10))
        
        logo_label = tk.Label(
            header_frame,
            text="💰",
            font=('Segoe UI', 48),
            bg=self.colors['bg'],
            fg=self.colors['primary']
        )
        logo_label.pack()
        
        signup_title = tk.Label(
            header_frame,
            text="SIGN UP",
            font=('Segoe UI', 32, 'bold'),
            bg=self.colors['bg'],
            fg=self.colors['success']
        )
        signup_title.pack(pady=(10, 5))
        
        title_label = tk.Label(
            header_frame,
            text="Create Your Account",
            font=('Segoe UI', 16),
            bg=self.colors['bg'],
            fg=self.colors['text_muted']
        )
        title_label.pack()
        
        # Signup form card
        signup_card = tk.Frame(
            main_frame,
            bg=self.colors['card'],
            relief='flat',
            bd=2,
            highlightbackground=self.colors['border'],
            highlightthickness=1
        )
        signup_card.pack(fill='both', expand=True, padx=50, pady=20)
        
        form_frame = tk.Frame(signup_card, bg=self.colors['card'])
        form_frame.pack(fill='both', expand=True, padx=50, pady=40)
        
        # Username field - clearer label
        username_section = tk.Frame(form_frame, bg=self.colors['card'])
        username_section.pack(fill='x', pady=(0, 20))
        
        tk.Label(
            username_section,
            text="Username",
            font=('Segoe UI', 13, 'bold'),
            bg=self.colors['card'],
            fg=self.colors['text'],
            anchor='w'
        ).pack(fill='x', pady=(0, 10))
        
        self.username_entry = tk.Entry(
            username_section,
            font=('Segoe UI', 14),
            bg='white',
            fg=self.colors['text'],
            relief='solid',
            bd=2,
            highlightthickness=2,
            highlightbackground=self.colors['border'],
            highlightcolor=self.colors['primary'],
            insertbackground=self.colors['text']
        )
        self.username_entry.pack(fill='x', pady=(0, 20), ipady=12)
        self.username_entry.focus()
        self.username_entry.bind('<Return>', lambda e: self.password_entry.focus())
        
        # Password field - clearer label
        password_section = tk.Frame(form_frame, bg=self.colors['card'])
        password_section.pack(fill='x', pady=(0, 20))
        
        tk.Label(
            password_section,
            text="Password (minimum 4 characters)",
            font=('Segoe UI', 13, 'bold'),
            bg=self.colors['card'],
            fg=self.colors['text'],
            anchor='w'
        ).pack(fill='x', pady=(0, 10))
        
        self.password_entry = tk.Entry(
            password_section,
            font=('Segoe UI', 14),
            bg='white',
            fg=self.colors['text'],
            relief='solid',
            bd=2,
            show='•',
            highlightthickness=2,
            highlightbackground=self.colors['border'],
            highlightcolor=self.colors['primary'],
            insertbackground=self.colors['text']
        )
        self.password_entry.pack(fill='x', ipady=12)
        self.password_entry.bind('<Return>', lambda e: self.confirm_entry.focus())
        
        # Confirm Password field - MUST BE VISIBLE AND PROMINENT
        confirm_section = tk.Frame(form_frame, bg=self.colors['card'])
        confirm_section.pack(fill='x', pady=(10, 25), padx=0)
        
        confirm_label = tk.Label(
            confirm_section,
            text="Confirm Password *",
            font=('Segoe UI', 14, 'bold'),
            bg=self.colors['card'],
            fg=self.colors['text'],
            anchor='w'
        )
        confirm_label.pack(fill='x', pady=(0, 10))
        
        self.confirm_entry = tk.Entry(
            confirm_section,
            font=('Segoe UI', 14),
            bg='white',
            fg=self.colors['text'],
            relief='solid',
            bd=2,
            show='•',
            highlightthickness=2,
            highlightbackground=self.colors['border'],
            highlightcolor=self.colors['primary'],
            insertbackground=self.colors['text']
        )
        self.confirm_entry.pack(fill='x', ipady=12, pady=(0, 0))
        self.confirm_entry.bind('<Return>', lambda e: self.register())
        
        # Status label - MUST BE VISIBLE (placed before button)
        status_frame = tk.Frame(form_frame, bg=self.colors['card'])
        status_frame.pack(fill='x', pady=(15, 20))
        
        self.status_label = tk.Label(
            status_frame,
            text="",
            font=('Segoe UI', 12, 'bold'),
            bg=self.colors['card'],
            fg=self.colors['danger'],
            wraplength=480,
            justify='center',
            height=2
        )
        self.status_label.pack(fill='x')
        
        # Large, clear CREATE ACCOUNT button - VERY VISIBLE AND PROMINENT
        button_container = tk.Frame(form_frame, bg=self.colors['card'])
        button_container.pack(fill='x', pady=(10, 20))
        
        signup_btn = tk.Button(
            button_container,
            text="CREATE ACCOUNT",
            font=('Segoe UI', 18, 'bold'),
            bg=self.colors['success'],
            fg='white',
            relief='flat',
            bd=0,
            padx=40,
            pady=22,
            cursor='hand2',
            command=self.register,
            activebackground='#34d399'
        )
        signup_btn.pack(fill='x')
        
        # Divider for visual separation
        divider = tk.Frame(form_frame, bg=self.colors['border'], height=1)
        divider.pack(fill='x', pady=(15, 15))
        
        # Navigation buttons frame - PROMINENT BACK TO LOGIN BUTTON
        nav_frame = tk.Frame(form_frame, bg=self.colors['card'])
        nav_frame.pack(fill='x', pady=(10, 10))
        
        # Back to Login button - LARGE AND VERY VISIBLE
        back_login_btn = tk.Button(
            nav_frame,
            text="🔐 Back to Login",
            font=('Segoe UI', 14, 'bold'),
            bg=self.colors['primary'],
            fg='white',
            relief='flat',
            bd=0,
            padx=30,
            pady=12,
            cursor='hand2',
            command=self.back_to_login,
            activebackground='#818cf8'
        )
        back_login_btn.pack(fill='x', pady=(0, 10))
        
        # Back to Home button
        back_home_btn = tk.Button(
            nav_frame,
            text="🏠 Back to Home",
            font=('Segoe UI', 12),
            bg=self.colors['card'],
            fg=self.colors['primary'],
            relief='flat',
            bd=1,
            highlightbackground=self.colors['primary'],
            highlightthickness=1,
            padx=20,
            pady=8,
            cursor='hand2',
            command=self.back_to_landing,
            activebackground='#f0f0f0'
        )
        back_home_btn.pack(fill='x', pady=(0, 0))
    
    def register(self):
        """Handle registration with clear validation"""
        # Ensure all fields exist
        if not hasattr(self, 'username_entry') or not hasattr(self, 'password_entry') or not hasattr(self, 'confirm_entry'):
            print("ERROR: Entry fields not initialized!")
            return
        
        username = self.username_entry.get().strip()
        password = self.password_entry.get()
        confirm = self.confirm_entry.get()
        
        # Clear previous status
        if hasattr(self, 'status_label'):
            self.status_label.config(text="", fg=self.colors['danger'])
        
        # Validation with clear messages
        if not username:
            self.status_label.config(text="⚠️ Please enter a username", fg=self.colors['danger'])
            self.username_entry.focus()
            return
        
        if not password:
            self.status_label.config(text="⚠️ Please enter a password", fg=self.colors['danger'])
            self.password_entry.focus()
            return
        
        if len(password) < 4:
            self.status_label.config(text="⚠️ Password must be at least 4 characters", fg=self.colors['danger'])
            self.password_entry.focus()
            return
        
        if not confirm:
            self.status_label.config(text="⚠️ Please confirm your password", fg=self.colors['danger'])
            self.confirm_entry.focus()
            return
        
        if password != confirm:
            self.status_label.config(text="✗ Passwords do not match! Please try again", fg=self.colors['danger'])
            self.password_entry.delete(0, tk.END)
            self.confirm_entry.delete(0, tk.END)
            self.password_entry.focus()
            return
        
        # Attempt registration with error handling
        try:
            success, message = self.user_manager.register_user(username, password)
            
            if success:
                self.status_label.config(text=f"✓ {message} Logging you in...", fg=self.colors['success'])
                self.frame.update_idletasks()
                # Auto login after successful registration
                self.frame.after(1500, self.auto_login, username, password)
            else:
                self.status_label.config(text=f"✗ {message}", fg=self.colors['danger'])
                self.username_entry.focus()
                self.frame.update_idletasks()
        except Exception as e:
            error_msg = f"Registration error: {str(e)}"
            self.status_label.config(text=f"✗ {error_msg}", fg=self.colors['danger'])
            self.frame.update_idletasks()
            self.username_entry.focus()
    
    def auto_login(self, username, password):
        """Auto login after registration and launch main app"""
        success, message = self.user_manager.authenticate(username, password)
        if success:
            self.status_label.config(text="✓ Login successful! Opening application...", fg=self.colors['success'])
            self.frame.update_idletasks()
            self.frame.after(500, self.launch_main_app)
        else:
            self.status_label.config(text=f"✗ Auto-login failed: {message}", fg=self.colors['danger'])
            self.frame.update_idletasks()
    
    def launch_main_app(self):
        """Launch the main finance tracker application"""
        self.app_controller.show_main_app()
    
    def back_to_landing(self):
        """Return to landing page"""
        self.app_controller.show_landing_page()
    
    def back_to_login(self):
        """Return to login page"""
        self.app_controller.show_login_page()
    
# Login Window (now a Frame)
class LoginWindow:
    def __init__(self, parent, user_manager, app_controller):
        self.parent = parent
        self.user_manager = user_manager
        self.app_controller = app_controller
        
        # Color scheme (light theme for login)
        self.colors = {
            'bg': '#f5f7fa',
            'card': '#ffffff',
            'primary': '#4f46e5',
            'primary_hover': '#6366f1',
            'success': '#059669',
            'danger': '#dc2626',
            'text': '#1f2937',
            'text_muted': '#6b7280',
            'border': '#e5e7eb'
        }
        
        self.frame = tk.Frame(parent, bg=self.colors['bg'])
        self.setup_login_ui()
    
    def pack(self, **kwargs):
        """Pack method for frame compatibility"""
        self.frame.pack(**kwargs)
    
    def pack_forget(self):
        """Pack forget for frame compatibility"""
        self.frame.pack_forget()
    
    def setup_login_ui(self):
        """Setup login interface - Professional and Clear"""
        # Main container with proper padding
        main_frame = self.frame
        main_frame.pack(fill='both', expand=True, padx=40, pady=40)
        
        # Header Section
        header_frame = tk.Frame(main_frame, bg=self.colors['bg'])
        header_frame.pack(fill='x', pady=(0, 30))
        
        # Logo
        logo_label = tk.Label(
            header_frame,
            text="💰",
            font=('Segoe UI', 56),
            bg=self.colors['bg'],
            fg=self.colors['primary']
        )
        logo_label.pack(pady=(0, 15))
        
        # Large, clear LOGIN title
        login_title = tk.Label(
            header_frame,
            text="LOGIN",
            font=('Segoe UI', 36, 'bold'),
            bg=self.colors['bg'],
            fg=self.colors['primary']
        )
        login_title.pack(pady=(0, 8))
        
        # Subtitle
        subtitle_label = tk.Label(
            header_frame,
            text="Welcome to Personal Finance Tracker",
            font=('Segoe UI', 14),
            bg=self.colors['bg'],
            fg=self.colors['text_muted']
        )
        subtitle_label.pack()
        
        # Login Card with shadow effect
        login_card = tk.Frame(
            main_frame,
            bg=self.colors['card'],
            relief='flat',
            bd=2,
            highlightbackground=self.colors['border'],
            highlightthickness=1
        )
        login_card.pack(fill='both', expand=True, pady=(0, 20))
        
        # Form container with proper padding
        form_frame = tk.Frame(login_card, bg=self.colors['card'])
        form_frame.pack(fill='both', expand=True, padx=40, pady=40)
        
        # Username Section
        username_section = tk.Frame(form_frame, bg=self.colors['card'])
        username_section.pack(fill='x', pady=(0, 20))
        
        username_label = tk.Label(
            username_section,
            text="Username",
            font=('Segoe UI', 13, 'bold'),
            bg=self.colors['card'],
            fg=self.colors['text'],
            anchor='w'
        )
        username_label.pack(fill='x', pady=(0, 10))
        
        self.username_entry = tk.Entry(
            username_section,
            font=('Segoe UI', 14),
            bg='white',
            fg=self.colors['text'],
            relief='solid',
            bd=2,
            highlightthickness=2,
            highlightbackground=self.colors['border'],
            highlightcolor=self.colors['primary'],
            insertbackground=self.colors['text']
        )
        self.username_entry.pack(fill='x', ipady=12)
        self.username_entry.focus()
        self.username_entry.bind('<Return>', lambda e: self.password_entry.focus())
        
        # Password Section
        password_section = tk.Frame(form_frame, bg=self.colors['card'])
        password_section.pack(fill='x', pady=(0, 25))
        
        password_label = tk.Label(
            password_section,
            text="Password",
            font=('Segoe UI', 13, 'bold'),
            bg=self.colors['card'],
            fg=self.colors['text'],
            anchor='w'
        )
        password_label.pack(fill='x', pady=(0, 10))
        
        self.password_entry = tk.Entry(
            password_section,
            font=('Segoe UI', 14),
            bg='white',
            fg=self.colors['text'],
            relief='solid',
            bd=2,
            show='•',
            highlightthickness=2,
            highlightbackground=self.colors['border'],
            highlightcolor=self.colors['primary'],
            insertbackground=self.colors['text']
        )
        self.password_entry.pack(fill='x', ipady=12)
        self.password_entry.bind('<Return>', lambda e: self.login())
        
        # Status Message Area
        self.status_label = tk.Label(
            form_frame,
            text="",
            font=('Segoe UI', 11),
            bg=self.colors['card'],
            fg=self.colors['danger'],
            wraplength=400,
            justify='center'
        )
        self.status_label.pack(fill='x', pady=(0, 20))
        
        # LOGIN Button - Large and Clear
        login_btn = tk.Button(
            form_frame,
            text="LOGIN",
            font=('Segoe UI', 16, 'bold'),
            bg=self.colors['primary'],
            fg='white',
            relief='flat',
            bd=0,
            padx=30,
            pady=18,
            cursor='hand2',
            command=self.login,
            activebackground=self.colors['primary_hover']
        )
        login_btn.pack(fill='x', pady=(0, 20))
        
        # Divider
        divider = tk.Frame(form_frame, bg=self.colors['border'], height=1)
        divider.pack(fill='x', pady=(0, 20))
        
        # Sign Up Section
        signup_section = tk.Frame(form_frame, bg=self.colors['card'])
        signup_section.pack(fill='x', pady=(0, 15))
        
        signup_text = tk.Label(
            signup_section,
            text="Don't have an account?",
            font=('Segoe UI', 12),
            bg=self.colors['card'],
            fg=self.colors['text_muted']
        )
        signup_text.pack(pady=(0, 10))
        
        signup_btn = tk.Button(
            signup_section,
            text="SIGN UP NOW",
            font=('Segoe UI', 13, 'bold'),
            bg=self.colors['card'],
            fg=self.colors['primary'],
            relief='flat',
            bd=1,
            highlightbackground=self.colors['primary'],
            highlightthickness=1,
            padx=20,
            pady=10,
            cursor='hand2',
            command=self.show_signup,
            activebackground='#f0f0f0'
        )
        signup_btn.pack()
        
        # Back to Home Button
        back_btn = tk.Button(
            form_frame,
            text="← Back to Home",
            font=('Segoe UI', 11),
            bg=self.colors['card'],
            fg=self.colors['text_muted'],
            relief='flat',
            bd=0,
            cursor='hand2',
            command=self.back_to_landing,
            activebackground=self.colors['card']
        )
        back_btn.pack(pady=(10, 0))
    
    def login(self):
        """Handle login with strict validation and access control"""
        username = self.username_entry.get().strip()
        password = self.password_entry.get()
        
        # Clear previous status
        self.status_label.config(text="", fg=self.colors['danger'])
        
        # STRICT VALIDATION: Check username
        if not username:
            self.status_label.config(text="⚠️ Please enter your username", fg=self.colors['danger'])
            self.username_entry.focus()
            return
        
        # STRICT VALIDATION: Check password
        if not password:
            self.status_label.config(text="⚠️ Please enter your password", fg=self.colors['danger'])
            self.password_entry.focus()
            return
        
        # CRITICAL: Clear any existing session before authentication
        self.user_manager.logout()
        
        # ACCESS CONTROL: Attempt authentication with strict validation
        success, message = self.user_manager.authenticate(username, password)
        
        if success:
            # VERIFY: Check user is actually set after authentication
            if not self.user_manager.current_user:
                self.status_label.config(text="✗ Authentication failed! Please try again.", fg=self.colors['danger'])
                self.user_manager.logout()
                self.password_entry.delete(0, tk.END)
                self.password_entry.focus()
                return
            
            # VERIFY: Check logged-in user matches the username entered (case-sensitive)
            logged_in_user = self.user_manager.current_user.strip()
            entered_username = username.strip()
            if logged_in_user != entered_username:
                self.status_label.config(text="✗ Authentication error! Username mismatch.", fg=self.colors['danger'])
                self.user_manager.logout()
                self.password_entry.delete(0, tk.END)
                self.password_entry.focus()
                return
            
            # SUCCESS: User authenticated correctly
            self.status_label.config(text=f"✓ Login successful! Welcome {logged_in_user}...", fg=self.colors['success'])
            self.frame.update()
            self.frame.after(500, self.launch_main_app)
        else:
            # ACCESS CONTROL: Failed login - ensure session is cleared
            self.user_manager.logout()
            self.status_label.config(text=f"✗ {message}", fg=self.colors['danger'])
            self.password_entry.delete(0, tk.END)
            self.password_entry.focus()
    
    def launch_main_app(self):
        """Launch the main finance tracker application"""
        self.app_controller.show_main_app()
    
    def show_signup(self):
        """Show signup page"""
        self.app_controller.show_signup_page()
    
    def back_to_landing(self):
        """Return to landing page"""
        self.app_controller.show_landing_page()

# Modern GUI Application with Cool Colors (now a Frame)
class FinanceTrackerGUI:
    def __init__(self, parent, user_manager=None, app_controller=None):
        self.parent = parent
        self.user_manager = user_manager
        self.app_controller = app_controller
        
        # Color Palettes
        self.light_colors = {
            'bg_dark': '#f5f7fa',      # Light gray background
            'bg_card': '#ffffff',      # White cards
            'bg_hover': '#e8ecf1',     # Light hover effect
            'primary': '#4f46e5',      # Bright Indigo
            'primary_hover': '#6366f1',
            'success': '#059669',      # Vibrant Green
            'danger': '#dc2626',        # Bright Red
            'warning': '#d97706',       # Warm Amber
            'info': '#0891b2',          # Bright Cyan
            'text_light': '#1f2937',    # Dark text for light background
            'text_muted': '#6b7280',    # Muted dark text
            'accent_purple': '#9333ea', # Bright Purple
            'accent_blue': '#2563eb',   # Bright Blue
            'border': '#e5e7eb'         # Light border
        }
        
        self.dark_colors = {
            'bg_dark': '#0a0e27',      # Dark navy background
            'bg_card': '#1a1f3a',      # Dark blue-gray cards
            'bg_hover': '#252b4a',     # Dark hover effect
            'primary': '#6366f1',      # Indigo
            'primary_hover': '#818cf8',
            'success': '#10b981',      # Green
            'danger': '#ef4444',       # Red
            'warning': '#f59e0b',       # Amber
            'info': '#06b6d4',         # Cyan
            'text_light': '#e5e7eb',    # Light text for dark background
            'text_muted': '#9ca3af',    # Muted light text
            'accent_purple': '#a855f7', # Purple
            'accent_blue': '#3b82f6',   # Blue
            'border': '#374151'         # Dark border
        }
        
        # Load theme preference
        self.theme_mode = self.load_theme_preference()  # 'light' or 'dark'
        self.colors = self.light_colors if self.theme_mode == 'light' else self.dark_colors
        
        # Create main frame
        self.frame = tk.Frame(parent, bg=self.colors['bg_dark'])
        
        # Configure style
        self.setup_styles()
        
        # ACCESS CONTROL: Strict validation - user MUST be authenticated
        if not self.user_manager:
            raise ValueError("UserManager not provided! Access denied.")
        
        if not self.user_manager.current_user:
            raise ValueError("User must be authenticated to access the finance tracker! Access denied.")
        
        # Get username and validate it's not empty
        username = self.user_manager.current_user.strip()
        if not username:
            raise ValueError("Invalid user session! Access denied.")
        
        # Create user-specific budget manager - CRITICAL for data separation
        self.budget_mgr = BudgetManager(username)
        self.budget_mgr.load_data()
        
        # CRITICAL: Verify we're using the correct user-specific file
        expected_filename = f"finance_data_{username}.json"
        if self.budget_mgr.filename != expected_filename:
            error_msg = f"SECURITY ERROR: File mismatch! Expected {expected_filename}, got {self.budget_mgr.filename}"
            print(error_msg)
            raise ValueError(error_msg)
        
        # Additional verification: ensure username matches exactly
        if self.budget_mgr.filename != f"finance_data_{username}.json":
            raise ValueError(f"Data file mismatch for user {username}! Access denied.")

        # Store widget references for theme switching
        self.theme_widgets = []

        # Main container with padding
        main_container = tk.Frame(self.frame, bg=self.colors['bg_dark'])
        main_container.pack(fill='both', expand=True, padx=10, pady=10)

        # Header
        self.create_header(main_container)

        # Tabs with modern styling
        self.notebook = ttk.Notebook(main_container, style='Modern.TNotebook')
        self.notebook.pack(fill='both', expand=True, pady=(10, 0))

        # Create tabs
        self.transaction_frame = self.create_frame_with_bg()
        self.summary_frame = self.create_frame_with_bg()
        self.goal_frame = self.create_frame_with_bg()
        self.transactions_view_frame = self.create_frame_with_bg()

        self.notebook.add(self.transaction_frame, text="➕ Add Transaction")
        self.notebook.add(self.transactions_view_frame, text="📋 View Transactions")
        self.notebook.add(self.summary_frame, text="📊 Summary & Analytics")
        self.notebook.add(self.goal_frame, text="🎯 Savings Goals")

        # Setup each tab
        self.setup_transaction_tab()
        self.setup_transactions_view_tab()
        self.setup_summary_tab()
        self.setup_goal_tab()

        # Initial update
        self.update_all_displays()

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        
        # Notebook style
        style.configure('Modern.TNotebook', background=self.colors['bg_dark'], borderwidth=0)
        style.configure('Modern.TNotebook.Tab', 
                       background=self.colors['bg_hover'],
                       foreground=self.colors['text_light'],
                       padding=[20, 10],
                       font=('Segoe UI', 10, 'bold'),
                       borderwidth=1,
                       relief='flat')
        style.map('Modern.TNotebook.Tab',
                 background=[('selected', self.colors['primary']),
                           ('active', self.colors['bg_card'])],
                 foreground=[('selected', 'white')],
                 expand=[('selected', [1, 1, 1, 0])])

        # Button styles
        style.configure('Primary.TButton',
                       background=self.colors['primary'],
                       foreground='white',
                       borderwidth=0,
                       focuscolor='none',
                       font=('Segoe UI', 10, 'bold'),
                       padding=10)
        style.map('Primary.TButton',
                 background=[('active', self.colors['primary_hover']),
                            ('pressed', self.colors['primary'])])

        style.configure('Success.TButton',
                       background=self.colors['success'],
                       foreground='white',
                       borderwidth=0,
                       focuscolor='none',
                       font=('Segoe UI', 10, 'bold'),
                       padding=10)
        style.map('Success.TButton',
                 background=[('active', '#34d399')])

        style.configure('Danger.TButton',
                       background=self.colors['danger'],
                       foreground='white',
                       borderwidth=0,
                       focuscolor='none',
                       font=('Segoe UI', 10, 'bold'),
                       padding=10)
        style.map('Danger.TButton',
                 background=[('active', '#f87171')])
        
        # Combobox style
        style.configure('TCombobox',
                       fieldbackground='white' if self.theme_mode == 'light' else self.colors['bg_hover'],
                       background='white' if self.theme_mode == 'light' else self.colors['bg_hover'],
                       foreground=self.colors['text_light'],
                       borderwidth=1,
                       relief='solid')
        style.map('TCombobox',
                 fieldbackground=[('readonly', 'white' if self.theme_mode == 'light' else self.colors['bg_hover'])],
                 background=[('readonly', 'white' if self.theme_mode == 'light' else self.colors['bg_hover'])])

    def create_frame_with_bg(self):
        frame = tk.Frame(self.notebook, bg=self.colors['bg_dark'])
        return frame

    def load_theme_preference(self):
        """Load theme preference from settings file"""
        settings_file = "app_settings.json"
        if os.path.exists(settings_file):
            try:
                with open(settings_file, 'r') as f:
                    settings = json.load(f)
                    return settings.get('theme', 'light')
            except:
                return 'light'
        return 'light'
    
    def save_theme_preference(self):
        """Save theme preference to settings file"""
        settings_file = "app_settings.json"
        settings = {'theme': self.theme_mode}
        with open(settings_file, 'w') as f:
            json.dump(settings, f, indent=2)
    
    def toggle_theme(self):
        """Switch between light and dark mode"""
        self.theme_mode = 'dark' if self.theme_mode == 'light' else 'light'
        self.colors = self.light_colors if self.theme_mode == 'light' else self.dark_colors
        self.save_theme_preference()
        self.apply_theme()
    
    def apply_theme(self):
        """Apply current theme to all UI elements"""
        # Update frame
        self.frame.configure(bg=self.colors['bg_dark'])
        
        # Update styles
        self.setup_styles()
        
        # Update header
        if hasattr(self, 'header_frame'):
            self.header_frame.configure(bg=self.colors['bg_card'], highlightbackground=self.colors['border'])
            if hasattr(self, 'title_label'):
                self.title_label.configure(bg=self.colors['bg_card'], fg=self.colors['text_light'])
            if hasattr(self, 'header_balance'):
                balance = self.budget_mgr.get_balance()
                balance_color = self.colors['success'] if balance >= 0 else self.colors['danger']
                self.header_balance.configure(bg=self.colors['bg_card'], fg=balance_color)
            if hasattr(self, 'theme_toggle_btn'):
                icon = "🌙" if self.theme_mode == 'light' else "☀️"
                self.theme_toggle_btn.configure(text=icon)
        
        # Update all frames
        self.update_frame_colors(self.transaction_frame)
        self.update_frame_colors(self.summary_frame)
        self.update_frame_colors(self.goal_frame)
        self.update_frame_colors(self.transactions_view_frame)
        
        # Update entry fields
        entry_fields = [
            self.amount_entry, self.desc_entry,
            self.goal_amount_entry, self.goal_desc_entry
        ]
        for entry in entry_fields:
            if entry:
                entry.configure(
                    bg='white' if self.theme_mode == 'light' else self.colors['bg_hover'],
                    fg=self.colors['text_light'],
                    insertbackground=self.colors['text_light'],
                    highlightbackground=self.colors['border'],
                    highlightcolor=self.colors['primary']
                )
        
        # Update date entry (calendar or regular entry)
        if hasattr(self, 'date_entry'):
            if CALENDAR_AVAILABLE and isinstance(self.date_entry, DateEntry):
                entry_bg = 'white' if self.theme_mode == 'light' else self.colors['bg_hover']
                text_color = self.colors['text_light']
                try:
                    self.date_entry.configure(
                        background=entry_bg,
                        foreground=text_color,
                        selectbackground=self.colors['primary'],
                        selectforeground='white',
                        normalbackground=entry_bg,
                        normalforeground=text_color,
                        headersbackground=self.colors['bg_hover'],
                        headersforeground=text_color,
                        weekendbackground=entry_bg,
                        weekendforeground=text_color,
                        othermonthbackground=entry_bg,
                        othermonthforeground=self.colors['text_muted']
                    )
                except:
                    # Fallback if some options not supported
                    self.date_entry.configure(
                        background=entry_bg,
                        foreground=text_color
                    )
            else:
                self.date_entry.configure(
                    bg='white' if self.theme_mode == 'light' else self.colors['bg_hover'],
                    fg=self.colors['text_light'],
                    insertbackground=self.colors['text_light'],
                    highlightbackground=self.colors['border'],
                    highlightcolor=self.colors['primary']
                )
        
        # Update Combobox
        if hasattr(self, 'category_dropdown'):
            self.category_dropdown.configure(
                style='TCombobox'
            )
        
        # Refresh all displays
        self.update_all_displays()
    
    def update_frame_colors(self, frame):
        """Recursively update colors of all widgets in a frame"""
        try:
            frame.configure(bg=self.colors['bg_dark'])
            for widget in frame.winfo_children():
                widget_type = widget.winfo_class()
                if widget_type == 'Frame' or widget_type == 'TFrame':
                    self.update_frame_colors(widget)
                elif widget_type == 'Label' or widget_type == 'TLabel':
                    # Only update if it's not a special label (like balance)
                    if not hasattr(widget, '_no_theme_update'):
                        widget.configure(bg=self.colors.get('bg_dark', self.colors['bg_card']), 
                                       fg=self.colors['text_light'])
        except:
            pass
    
    def create_header(self, parent):
        self.header_frame = tk.Frame(parent, bg=self.colors['bg_card'], relief='flat', bd=1, highlightbackground=self.colors['border'], highlightthickness=1)
        self.header_frame.pack(fill='x', pady=(0, 10))
        
        self.title_label = tk.Label(
            self.header_frame,
            text="💰 Personal Finance Tracker",
            font=('Segoe UI', 24, 'bold'),
            bg=self.colors['bg_card'],
            fg=self.colors['text_light']
        )
        self.title_label.pack(side='left', padx=20, pady=15)
        
        # Right side container for buttons and info
        right_container = tk.Frame(self.header_frame, bg=self.colors['bg_card'])
        right_container.pack(side='right', padx=20, pady=15)
        
        # Username display (if logged in)
        if self.user_manager and self.user_manager.current_user:
            username_label = tk.Label(
                right_container,
                text=f"👤 {self.user_manager.current_user}",
                font=('Segoe UI', 11),
                bg=self.colors['bg_card'],
                fg=self.colors['text_muted']
            )
            username_label.pack(side='right', padx=(0, 15))
        
        # Logout button (if logged in)
        if self.user_manager and self.user_manager.current_user:
            logout_btn = tk.Button(
                right_container,
                text="🚪 Logout",
                font=('Segoe UI', 10, 'bold'),
                bg=self.colors['danger'],
                fg='white',
                relief='flat',
                bd=0,
                padx=12,
                pady=5,
                cursor='hand2',
                command=self.logout
            )
            logout_btn.pack(side='right', padx=(0, 10))
        
        # Theme toggle button
        theme_icon = "🌙" if self.theme_mode == 'light' else "☀️"
        self.theme_toggle_btn = tk.Button(
            right_container,
            text=theme_icon,
            font=('Segoe UI', 16),
            bg=self.colors['primary'],
            fg='white',
            relief='flat',
            bd=0,
            padx=15,
            pady=5,
            cursor='hand2',
            command=self.toggle_theme
        )
        self.theme_toggle_btn.pack(side='right', padx=(0, 10))
        
        # Balance display in header
        self.header_balance = tk.Label(
            right_container,
            text="Balance: UGX 0.00",
            font=('Segoe UI', 16, 'bold'),
            bg=self.colors['bg_card'],
            fg=self.colors['success']
        )
        self.header_balance.pack(side='right', padx=(0, 10))
    
    def pack(self, **kwargs):
        """Pack method for frame compatibility"""
        self.frame.pack(**kwargs)
    
    def pack_forget(self):
        """Pack forget for frame compatibility"""
        self.frame.pack_forget()
    
    def logout(self):
        """Handle logout with complete session clearing"""
        if messagebox.askyesno("Logout", "Are you sure you want to logout?"):
            # Get username before logout for confirmation
            username = None
            if self.user_manager and self.user_manager.current_user:
                username = self.user_manager.current_user
            
            # CRITICAL: Clear user session completely
            if self.user_manager:
                self.user_manager.logout()
            
            # VERIFY: Ensure logout was successful
            if self.user_manager and self.user_manager.current_user is not None:
                # Force clear if logout didn't work
                self.user_manager.current_user = None
            
            # Clear any cached data
            if hasattr(self, 'budget_mgr'):
                self.budget_mgr = None
            
            # Return to landing page
            if self.app_controller:
                self.app_controller.show_landing_page()

    def create_card(self, parent, row, column, columnspan=1, padx=10, pady=10):
        card = tk.Frame(
            parent,
            bg=self.colors['bg_card'],
            relief='flat',
            bd=1,
            highlightbackground=self.colors['border'],
            highlightthickness=1
        )
        card.grid(row=row, column=column, columnspan=columnspan, padx=padx, pady=pady, sticky='nsew')
        return card

    def setup_transaction_tab(self):
        # Main container with grid
        self.transaction_frame.grid_columnconfigure(0, weight=1)
        self.transaction_frame.grid_columnconfigure(1, weight=1)
        
        # Left column - Input form
        left_card = self.create_card(self.transaction_frame, 0, 0, padx=15, pady=15)
        
        form_title = tk.Label(
            left_card,
            text="Add New Transaction",
            font=('Segoe UI', 18, 'bold'),
            bg=self.colors['bg_card'],
            fg=self.colors['text_light']
        )
        form_title.pack(pady=(15, 25))
        
        # Amount field
        amount_frame = tk.Frame(left_card, bg=self.colors['bg_card'])
        amount_frame.pack(fill='x', padx=20, pady=10)
        tk.Label(
            amount_frame,
            text="Amount (UGX)",
            font=('Segoe UI', 11),
            bg=self.colors['bg_card'],
            fg=self.colors['text_light']
        ).pack(anchor='w')
        entry_bg = 'white' if self.theme_mode == 'light' else self.colors['bg_hover']
        self.amount_entry = tk.Entry(
            amount_frame,
            font=('Segoe UI', 12),
            bg=entry_bg,
            fg=self.colors['text_light'],
            insertbackground=self.colors['text_light'],
            relief='solid',
            bd=1,
            highlightthickness=1,
            highlightbackground=self.colors['border'],
            highlightcolor=self.colors['primary']
        )
        self.amount_entry.pack(fill='x', pady=(5, 0), ipady=8)
        
        # Date field with calendar picker
        date_frame = tk.Frame(left_card, bg=self.colors['bg_card'])
        date_frame.pack(fill='x', padx=20, pady=10)
        tk.Label(
            date_frame,
            text="Date",
            font=('Segoe UI', 11),
            bg=self.colors['bg_card'],
            fg=self.colors['text_light']
        ).pack(anchor='w')
        
        if CALENDAR_AVAILABLE:
            # Use DateEntry calendar widget
            entry_bg = 'white' if self.theme_mode == 'light' else self.colors['bg_hover']
            text_color = self.colors['text_light']
            self.date_entry = DateEntry(
                date_frame,
                width=12,
                background=entry_bg,
                foreground=text_color,
                borderwidth=1,
                relief='solid',
                font=('Segoe UI', 12),
                date_pattern='yyyy-mm-dd',
                locale='en_US',
                selectbackground=self.colors['primary'],
                selectforeground='white',
                normalbackground=entry_bg,
                normalforeground=text_color,
                headersbackground=self.colors['bg_hover'],
                headersforeground=text_color,
                weekendbackground=entry_bg,
                weekendforeground=text_color,
                othermonthbackground=entry_bg,
                othermonthforeground=self.colors['text_muted']
            )
            self.date_entry.pack(fill='x', pady=(5, 0))
            # Set today's date
            self.date_entry.set_date(datetime.datetime.now())
        else:
            # Fallback to regular entry if tkcalendar not available
            entry_bg = 'white' if self.theme_mode == 'light' else self.colors['bg_hover']
            self.date_entry = tk.Entry(
                date_frame,
                font=('Segoe UI', 12),
                bg=entry_bg,
                fg=self.colors['text_light'],
                insertbackground=self.colors['text_light'],
                relief='solid',
                bd=1,
                highlightthickness=1,
                highlightbackground=self.colors['border'],
                highlightcolor=self.colors['primary']
            )
            self.date_entry.pack(fill='x', pady=(5, 0), ipady=8)
        self.date_entry.insert(0, datetime.datetime.now().strftime("%Y-%m-%d"))

        # Category field - Only for expenses
        self.category_frame = tk.Frame(left_card, bg=self.colors['bg_card'])
        self.category_frame.pack(fill='x', padx=20, pady=10)
        self.category_label = tk.Label(
            self.category_frame,
            text="Category (Required for Expenses)",
            font=('Segoe UI', 11),
            bg=self.colors['bg_card'],
            fg=self.colors['text_light']
        )
        self.category_label.pack(anchor='w')
        self.category_var = tk.StringVar()
        categories = self.budget_mgr.category_mgr.get_categories()
        self.category_dropdown = ttk.Combobox(
            self.category_frame,
            textvariable=self.category_var,
            values=categories,
            font=('Segoe UI', 12),
            state='readonly'
        )
        self.category_dropdown.pack(fill='x', pady=(5, 0))
        if categories:
            self.category_dropdown.current(0)
            self.category_var.set(categories[0])  # Explicitly set the value
        
        # Initially show category (default to expense mode)
        self.show_category_field(True)
        
        # Description field
        desc_frame = tk.Frame(left_card, bg=self.colors['bg_card'])
        desc_frame.pack(fill='x', padx=20, pady=10)
        tk.Label(
            desc_frame,
            text="Description",
            font=('Segoe UI', 11),
            bg=self.colors['bg_card'],
            fg=self.colors['text_light']
        ).pack(anchor='w')
        entry_bg = 'white' if self.theme_mode == 'light' else self.colors['bg_hover']
        self.desc_entry = tk.Entry(
            desc_frame,
            font=('Segoe UI', 12),
            bg=entry_bg,
            fg=self.colors['text_light'],
            insertbackground=self.colors['text_light'],
            relief='solid',
            bd=1,
            highlightthickness=1,
            highlightbackground=self.colors['border'],
            highlightcolor=self.colors['primary']
        )
        self.desc_entry.pack(fill='x', pady=(5, 0), ipady=8)
        
        # Buttons
        button_frame = tk.Frame(left_card, bg=self.colors['bg_card'])
        button_frame.pack(fill='x', padx=20, pady=20)
        
        income_btn = ttk.Button(
            button_frame,
            text="➕ Add Income",
            command=lambda: [self.show_category_field(False), self.add_income()],
            style='Success.TButton'
        )
        income_btn.pack(side='left', fill='x', expand=True, padx=(0, 10))
        
        expense_btn = ttk.Button(
            button_frame,
            text="➖ Add Expense",
            command=lambda: [self.show_category_field(True), self.add_expense()],
            style='Danger.TButton'
        )
        expense_btn.pack(side='left', fill='x', expand=True, padx=(10, 0))
        
        # Update income button to hide category
        income_btn.config(command=lambda: [self.show_category_field(False), self.add_income()])
        
        # Right column - Quick stats
        right_card = self.create_card(self.transaction_frame, 0, 1, padx=15, pady=15)
        
        stats_title = tk.Label(
            right_card,
            text="Quick Overview",
            font=('Segoe UI', 18, 'bold'),
            bg=self.colors['bg_card'],
            fg=self.colors['text_light']
        )
        stats_title.pack(pady=(15, 25))
        
        self.quick_stats_frame = tk.Frame(right_card, bg=self.colors['bg_card'])
        self.quick_stats_frame.pack(fill='both', expand=True, padx=20, pady=10)

    def setup_transactions_view_tab(self):
        # Header with Clear All button
        header_frame = tk.Frame(self.transactions_view_frame, bg=self.colors['bg_dark'])
        header_frame.pack(fill='x', padx=20, pady=(10, 0))
        
        # Clear All button
        clear_all_btn = tk.Button(
            header_frame,
            text="🗑️ Clear All Transactions",
            font=('Segoe UI', 11, 'bold'),
            bg=self.colors['danger'],
            fg='white',
            relief='flat',
            bd=0,
            padx=15,
            pady=8,
            cursor='hand2',
            command=self.clear_all_transactions
        )
        clear_all_btn.pack(side='right')
        
        # Scrollable frame for transactions
        canvas = tk.Canvas(
            self.transactions_view_frame,
            bg=self.colors['bg_dark'],
            highlightthickness=0
        )
        scrollbar = ttk.Scrollbar(
            self.transactions_view_frame,
            orient="vertical",
            command=canvas.yview
        )
        self.transactions_scroll_frame = tk.Frame(canvas, bg=self.colors['bg_dark'])
        
        self.transactions_scroll_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.transactions_scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def setup_summary_tab(self):
        self.summary_frame.grid_columnconfigure(0, weight=1)
        self.summary_frame.grid_columnconfigure(1, weight=1)
        self.summary_frame.grid_rowconfigure(2, weight=1)
        self.summary_frame.grid_rowconfigure(3, weight=1)
        
        # Summary cards
        self.summary_income_card = self.create_card(self.summary_frame, 0, 0, padx=15, pady=15)
        self.summary_expense_card = self.create_card(self.summary_frame, 0, 1, padx=15, pady=15)
        self.summary_balance_card = self.create_card(self.summary_frame, 1, 0, columnspan=2, padx=15, pady=15)
        self.summary_category_card = self.create_card(self.summary_frame, 2, 0, columnspan=2, padx=15, pady=15)
        
        # Chart cards
        self.bar_chart_card = self.create_card(self.summary_frame, 3, 0, padx=15, pady=15)
        self.pie_chart_card = self.create_card(self.summary_frame, 3, 1, padx=15, pady=15)

    def setup_goal_tab(self):
        # Goals input section
        input_card = self.create_card(self.goal_frame, 0, 0, padx=15, pady=15)
        
        goal_title = tk.Label(
            input_card,
            text="Create New Savings Goal",
            font=('Segoe UI', 18, 'bold'),
            bg=self.colors['bg_card'],
            fg=self.colors['text_light']
        )
        goal_title.pack(pady=(15, 25))
        
        # Target amount
        target_frame = tk.Frame(input_card, bg=self.colors['bg_card'])
        target_frame.pack(fill='x', padx=20, pady=10)
        tk.Label(
            target_frame,
            text="Target Amount (UGX)",
            font=('Segoe UI', 11),
            bg=self.colors['bg_card'],
            fg=self.colors['text_light']
        ).pack(anchor='w')
        entry_bg = 'white' if self.theme_mode == 'light' else self.colors['bg_hover']
        self.goal_amount_entry = tk.Entry(
            target_frame,
            font=('Segoe UI', 12),
            bg=entry_bg,
            fg=self.colors['text_light'],
            insertbackground=self.colors['text_light'],
            relief='solid',
            bd=1,
            highlightthickness=1,
            highlightbackground=self.colors['border'],
            highlightcolor=self.colors['primary']
        )
        self.goal_amount_entry.pack(fill='x', pady=(5, 0), ipady=8)
        
        # Description
        goal_desc_frame = tk.Frame(input_card, bg=self.colors['bg_card'])
        goal_desc_frame.pack(fill='x', padx=20, pady=10)
        tk.Label(
            goal_desc_frame,
            text="Goal Description",
            font=('Segoe UI', 11),
            bg=self.colors['bg_card'],
            fg=self.colors['text_light']
        ).pack(anchor='w')
        entry_bg = 'white' if self.theme_mode == 'light' else self.colors['bg_hover']
        self.goal_desc_entry = tk.Entry(
            goal_desc_frame,
            font=('Segoe UI', 12),
            bg=entry_bg,
            fg=self.colors['text_light'],
            insertbackground=self.colors['text_light'],
            relief='solid',
            bd=1,
            highlightthickness=1,
            highlightbackground=self.colors['border'],
            highlightcolor=self.colors['primary']
        )
        self.goal_desc_entry.pack(fill='x', pady=(5, 0), ipady=8)
        
        # Add goal button
        add_goal_btn = ttk.Button(
            input_card,
            text="🎯 Add Savings Goal",
            command=self.add_goal,
            style='Primary.TButton'
        )
        add_goal_btn.pack(padx=20, pady=20, fill='x')
        
        # Goals display section
        self.goals_display_frame = tk.Frame(self.goal_frame, bg=self.colors['bg_dark'])
        self.goals_display_frame.grid(row=1, column=0, sticky='nsew', padx=15, pady=15)
        self.goal_frame.grid_rowconfigure(1, weight=1)

    def show_category_field(self, show):
        """Show or hide category field based on transaction type"""
        if show:
            self.category_frame.pack(fill='x', padx=20, pady=10)
            self.category_label.config(text="Category (Required for Expenses)")
        else:
            self.category_frame.pack_forget()

    def add_income(self):
        try:
            amount = float(self.amount_entry.get())
            # Get date from calendar or entry field
            if CALENDAR_AVAILABLE and isinstance(self.date_entry, DateEntry):
                date = self.date_entry.get_date().strftime("%Y-%m-%d")
            else:
                date = self.date_entry.get()
            # Income doesn't need category - use "Income" as default
            category = "Income"
            desc = self.desc_entry.get()
            
            if amount <= 0:
                messagebox.showerror("Error", "Income amount must be positive!")
                return
            
            # Create and add income transaction
            trans = Income(amount, date, category, desc)
            self.budget_mgr.add_transaction(trans)
            messagebox.showinfo("Success", f"Income of UGX {amount:,.2f} added successfully! 💰")
            self.clear_transaction_form()
            self.update_all_displays()
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid amount!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add income: {str(e)}")
            print(f"Error adding income: {e}")

    def add_expense(self):
        try:
            amount = float(self.amount_entry.get())
            # Get date from calendar or entry field
            if CALENDAR_AVAILABLE and isinstance(self.date_entry, DateEntry):
                date = self.date_entry.get_date().strftime("%Y-%m-%d")
            else:
                date = self.date_entry.get()
            category = self.category_var.get().strip() if self.category_var.get() else ""
            desc = self.desc_entry.get()
            
            if amount <= 0:
                messagebox.showerror("Error", "Expense amount must be positive!")
                return
            
            if not category or category == "":
                messagebox.showerror("Error", "Please select a category!")
                return
            
            # Create and add expense transaction
            trans = Expense(amount, date, category, desc)
            self.budget_mgr.add_transaction(trans)
            messagebox.showinfo("Success", f"Expense of UGX {amount:,.2f} recorded successfully! 💸")
            self.clear_transaction_form()
            self.update_all_displays()
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid amount!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add expense: {str(e)}")
            print(f"Error adding expense: {e}")
    
    def delete_transaction(self, trans):
        """Delete a transaction after confirmation"""
        trans_type = "Income" if trans.get_amount() > 0 else "Expense"
        amount = abs(trans.get_amount())
        
        if messagebox.askyesno(
            "Delete Transaction",
            f"Are you sure you want to delete this {trans_type.lower()}?\n\n"
            f"Amount: UGX {amount:,.2f}\n"
            f"Description: {trans.get_description()}\n"
            f"Date: {trans.get_date()}"
        ):
            if self.budget_mgr.remove_transaction(trans):
                messagebox.showinfo("Success", f"{trans_type} deleted successfully!")
                self.update_all_displays()
            else:
                messagebox.showerror("Error", "Failed to delete transaction!")
    
    def clear_all_transactions(self):
        """Clear all transactions with confirmation"""
        total_income = self.budget_mgr.get_total_income()
        total_expenses = self.budget_mgr.get_total_expenses()
        transaction_count = len(self.budget_mgr.transactions)
        
        if transaction_count == 0:
            messagebox.showinfo("Info", "No transactions to clear!")
            return
        
        # Show detailed confirmation
        confirm_msg = (
            f"⚠️ WARNING: This will delete ALL transactions!\n\n"
            f"Total Income: UGX {total_income:,.2f}\n"
            f"Total Expenses: UGX {total_expenses:,.2f}\n"
            f"Number of Transactions: {transaction_count}\n\n"
            f"This action cannot be undone!\n\n"
            f"Are you sure you want to clear all transactions?"
        )
        
        if messagebox.askyesno("Clear All Transactions", confirm_msg, icon='warning'):
            if self.budget_mgr.clear_all_transactions():
                messagebox.showinfo(
                    "Success", 
                    f"All {transaction_count} transactions have been cleared!\n\n"
                    f"Income and Expenses reset to zero."
                )
                self.update_all_displays()
            else:
                messagebox.showerror("Error", "Failed to clear transactions!")

    def clear_transaction_form(self):
        self.amount_entry.delete(0, tk.END)
        # Reset date entry (calendar or regular entry)
        if CALENDAR_AVAILABLE and isinstance(self.date_entry, DateEntry):
            self.date_entry.set_date(datetime.datetime.now())
        else:
            self.date_entry.delete(0, tk.END)
            self.date_entry.insert(0, datetime.datetime.now().strftime("%Y-%m-%d"))
        if hasattr(self, 'category_dropdown') and self.category_dropdown.winfo_viewable():
            categories = self.budget_mgr.category_mgr.get_categories()
            if categories:
                self.category_dropdown.current(0)
        self.desc_entry.delete(0, tk.END)
        # Show category field by default (for expenses)
        self.show_category_field(True)

    def add_goal(self):
        try:
            amount = float(self.goal_amount_entry.get())
            desc = self.goal_desc_entry.get()
            
            if amount <= 0:
                messagebox.showerror("Error", "Target amount must be positive!")
                return
            
            if not desc:
                messagebox.showerror("Error", "Please enter a goal description!")
                return
            
                goal = Goal(amount, desc)
                self.budget_mgr.add_goal(goal)
            messagebox.showinfo("Success", f"Savings goal '{desc}' created! 🎯")
            self.goal_amount_entry.delete(0, tk.END)
            self.goal_desc_entry.delete(0, tk.END)
            self.update_all_displays()
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid target amount!")

    def update_all_displays(self):
        self.update_header_balance()
        self.update_quick_stats()
        self.update_transactions_view()
        self.update_summary_tab()
        self.update_goals_display()

    def update_header_balance(self):
        balance = self.budget_mgr.get_balance()
        color = self.colors['success'] if balance >= 0 else self.colors['danger']
        if hasattr(self, 'header_balance'):
            self.header_balance.config(
                text=f"Balance: UGX {balance:,.2f}",
                fg=color,
                bg=self.colors['bg_card']
            )

    def update_quick_stats(self):
        # Clear existing widgets
        for widget in self.quick_stats_frame.winfo_children():
            widget.destroy()
        
        income = self.budget_mgr.get_total_income()
        expenses = self.budget_mgr.get_total_expenses()
        balance = self.budget_mgr.get_balance()
        
        # Income stat
        income_frame = tk.Frame(self.quick_stats_frame, bg=self.colors['bg_hover'], relief='flat', bd=1, highlightbackground=self.colors['border'], highlightthickness=1)
        income_frame.pack(fill='x', pady=10, padx=10)
        tk.Label(
            income_frame,
            text="Total Income",
            font=('Segoe UI', 10),
            bg=self.colors['bg_hover'],
            fg=self.colors['text_muted']
        ).pack(anchor='w', padx=15, pady=(10, 5))
        tk.Label(
            income_frame,
            text=f"UGX {income:,.2f}",
            font=('Segoe UI', 20, 'bold'),
            bg=self.colors['bg_hover'],
            fg=self.colors['success']
        ).pack(anchor='w', padx=15, pady=(0, 10))
        
        # Expense stat
        expense_frame = tk.Frame(self.quick_stats_frame, bg=self.colors['bg_hover'], relief='flat', bd=1, highlightbackground=self.colors['border'], highlightthickness=1)
        expense_frame.pack(fill='x', pady=10, padx=10)
        tk.Label(
            expense_frame,
            text="Total Expenses",
            font=('Segoe UI', 10),
            bg=self.colors['bg_hover'],
            fg=self.colors['text_muted']
        ).pack(anchor='w', padx=15, pady=(10, 5))
        tk.Label(
            expense_frame,
            text=f"UGX {expenses:,.2f}",
            font=('Segoe UI', 20, 'bold'),
            bg=self.colors['bg_hover'],
            fg=self.colors['danger']
        ).pack(anchor='w', padx=15, pady=(0, 10))
        
        # Balance stat
        balance_frame = tk.Frame(self.quick_stats_frame, bg=self.colors['bg_hover'], relief='flat', bd=1, highlightbackground=self.colors['border'], highlightthickness=1)
        balance_frame.pack(fill='x', pady=10, padx=10)
        tk.Label(
            balance_frame,
            text="Current Balance",
            font=('Segoe UI', 10),
            bg=self.colors['bg_hover'],
            fg=self.colors['text_muted']
        ).pack(anchor='w', padx=15, pady=(10, 5))
        balance_color = self.colors['success'] if balance >= 0 else self.colors['danger']
        tk.Label(
            balance_frame,
            text=f"UGX {balance:,.2f}",
            font=('Segoe UI', 20, 'bold'),
            bg=self.colors['bg_hover'],
            fg=balance_color
        ).pack(anchor='w', padx=15, pady=(0, 10))

    def update_transactions_view(self):
        # Clear existing widgets
        for widget in self.transactions_scroll_frame.winfo_children():
            widget.destroy()
        
        if not self.budget_mgr.transactions:
            no_trans_label = tk.Label(
                self.transactions_scroll_frame,
                text="No transactions yet. Add your first transaction!",
                font=('Segoe UI', 14),
                bg=self.colors['bg_dark'],
                fg=self.colors['text_muted']
            )
            no_trans_label.pack(pady=50)
            return
        
        # Header
        header = tk.Label(
            self.transactions_scroll_frame,
            text="All Transactions",
            font=('Segoe UI', 18, 'bold'),
            bg=self.colors['bg_dark'],
            fg=self.colors['text_light']
        )
        header.pack(pady=(10, 20))
        
        # Display transactions (most recent first)
        for trans in reversed(self.budget_mgr.transactions):
            self.create_transaction_card(trans)

    def create_transaction_card(self, trans):
        card = tk.Frame(
            self.transactions_scroll_frame,
            bg=self.colors['bg_card'],
            relief='flat',
            bd=1,
            highlightbackground=self.colors['border'],
            highlightthickness=1
        )
        card.pack(fill='x', padx=20, pady=8)
        
        # Transaction type and amount
        amount = trans.get_amount()
        is_income = amount > 0
        color = self.colors['success'] if is_income else self.colors['danger']
        symbol = "💰" if is_income else "💸"
        
        main_frame = tk.Frame(card, bg=self.colors['bg_card'])
        main_frame.pack(fill='x', padx=15, pady=12)
        
        # Left side - Info
        info_frame = tk.Frame(main_frame, bg=self.colors['bg_card'])
        info_frame.pack(side='left', fill='both', expand=True)
        
        tk.Label(
            info_frame,
            text=f"{symbol} {trans.get_description()}",
            font=('Segoe UI', 12, 'bold'),
            bg=self.colors['bg_card'],
            fg=self.colors['text_light']
        ).pack(anchor='w')
        
        # Show category only for expenses
        category_text = f"📁 {trans.get_category()} | " if not is_income else ""
        tk.Label(
            info_frame,
            text=f"{category_text}📅 {trans.get_date()}",
            font=('Segoe UI', 10),
            bg=self.colors['bg_card'],
            fg=self.colors['text_muted']
        ).pack(anchor='w', pady=(5, 0))
        
        # Right side - Amount and Delete button
        right_frame = tk.Frame(main_frame, bg=self.colors['bg_card'])
        right_frame.pack(side='right', padx=(10, 0))
        
        tk.Label(
            right_frame,
            text=f"UGX {abs(amount):,.2f}",
            font=('Segoe UI', 14, 'bold'),
            bg=self.colors['bg_card'],
            fg=color
        ).pack(side='right', padx=(0, 10))
        
        # Delete button
        delete_btn = tk.Button(
            right_frame,
            text="🗑️ Delete",
            font=('Segoe UI', 10, 'bold'),
            bg=self.colors['danger'],
            fg='white',
            relief='flat',
            bd=0,
            padx=10,
            pady=5,
            cursor='hand2',
            command=lambda t=trans: self.delete_transaction(t)
        )
        delete_btn.pack(side='right')

    def update_summary_tab(self):
        # Clear existing widgets
        for widget in self.summary_income_card.winfo_children():
            widget.destroy()
        for widget in self.summary_expense_card.winfo_children():
            widget.destroy()
        for widget in self.summary_balance_card.winfo_children():
            widget.destroy()
        for widget in self.summary_category_card.winfo_children():
            widget.destroy()
        for widget in self.bar_chart_card.winfo_children():
            widget.destroy()
        for widget in self.pie_chart_card.winfo_children():
            widget.destroy()
        
        income = self.budget_mgr.get_total_income()
        expenses = self.budget_mgr.get_total_expenses()
        balance = self.budget_mgr.get_balance()
        
        # Income card
        tk.Label(
            self.summary_income_card,
            text="💰 Total Income",
            font=('Segoe UI', 14, 'bold'),
            bg=self.colors['bg_card'],
            fg=self.colors['text_light']
        ).pack(pady=(15, 10))
        tk.Label(
            self.summary_income_card,
            text=f"UGX {income:,.2f}",
            font=('Segoe UI', 24, 'bold'),
            bg=self.colors['bg_card'],
            fg=self.colors['success']
        ).pack(pady=(0, 15))
        
        # Expense card
        tk.Label(
            self.summary_expense_card,
            text="💸 Total Expenses",
            font=('Segoe UI', 14, 'bold'),
            bg=self.colors['bg_card'],
            fg=self.colors['text_light']
        ).pack(pady=(15, 10))
        tk.Label(
            self.summary_expense_card,
            text=f"UGX {expenses:,.2f}",
            font=('Segoe UI', 24, 'bold'),
            bg=self.colors['bg_card'],
            fg=self.colors['danger']
        ).pack(pady=(0, 15))
        
        # Balance card
        tk.Label(
            self.summary_balance_card,
            text="💵 Current Balance",
            font=('Segoe UI', 16, 'bold'),
            bg=self.colors['bg_card'],
            fg=self.colors['text_light']
        ).pack(pady=(15, 10))
        balance_color = self.colors['success'] if balance >= 0 else self.colors['danger']
        tk.Label(
            self.summary_balance_card,
            text=f"UGX {balance:,.2f}",
            font=('Segoe UI', 32, 'bold'),
            bg=self.colors['bg_card'],
            fg=balance_color
        ).pack(pady=(0, 15))
        
        # Category breakdown
        tk.Label(
            self.summary_category_card,
            text="📊 Category Breakdown",
            font=('Segoe UI', 16, 'bold'),
            bg=self.colors['bg_card'],
            fg=self.colors['text_light']
        ).pack(pady=(15, 20))
        
        category_totals = self.budget_mgr.get_transactions_by_category()
        if category_totals:
            for category, totals in category_totals.items():
                cat_frame = tk.Frame(self.summary_category_card, bg=self.colors['bg_hover'], relief='flat', bd=1, highlightbackground=self.colors['border'], highlightthickness=1)
                cat_frame.pack(fill='x', padx=20, pady=5)
                
                tk.Label(
                    cat_frame,
                    text=f"📁 {category}",
                    font=('Segoe UI', 11, 'bold'),
                    bg=self.colors['bg_hover'],
                    fg=self.colors['text_light']
                ).pack(side='left', padx=15, pady=10)
                
                info_text = f"Income: UGX {totals['income']:,.2f} | Expenses: UGX {totals['expense']:,.2f}"
                tk.Label(
                    cat_frame,
                    text=info_text,
                    font=('Segoe UI', 10),
                    bg=self.colors['bg_hover'],
                    fg=self.colors['text_muted']
                ).pack(side='right', padx=15, pady=10)
        
        # Create charts if matplotlib is available
        if MATPLOTLIB_AVAILABLE:
            self.create_bar_chart()
            self.create_pie_chart()
        else:
            # Show message if matplotlib not available
            tk.Label(
                self.bar_chart_card,
                text="📊 Bar Chart\n\nInstall matplotlib to view charts:\npip install matplotlib",
                font=('Segoe UI', 12),
                bg=self.colors['bg_card'],
                fg=self.colors['text_muted'],
                justify='center'
            ).pack(expand=True, fill='both', pady=20)
            
            tk.Label(
                self.pie_chart_card,
                text="🥧 Pie Chart\n\nInstall matplotlib to view charts:\npip install matplotlib",
                font=('Segoe UI', 12),
                bg=self.colors['bg_card'],
                fg=self.colors['text_muted'],
                justify='center'
            ).pack(expand=True, fill='both', pady=20)
    
    def create_bar_chart(self):
        """Create a bar chart showing expenses by category"""
        category_totals = self.budget_mgr.get_transactions_by_category()
        
        # Prepare data for bar chart (expenses by category)
        categories = []
        expenses = []
        
        for category, totals in category_totals.items():
            if totals['expense'] > 0:  # Only show categories with expenses
                categories.append(category)
                expenses.append(totals['expense'])
        
        if not categories:
            tk.Label(
                self.bar_chart_card,
                text="📊 Expenses by Category\n\nNo expense data available",
                font=('Segoe UI', 12),
                bg=self.colors['bg_card'],
                fg=self.colors['text_muted'],
                justify='center'
            ).pack(expand=True, fill='both', pady=20)
            return
        
        # Create figure with larger size for better visibility
        fig = Figure(figsize=(6.5, 5), dpi=100, facecolor=self.colors['bg_card'])
        ax = fig.add_subplot(111)
        
        # Set theme colors
        if self.theme_mode == 'dark':
            fig.patch.set_facecolor(self.colors['bg_card'])
            ax.set_facecolor(self.colors['bg_card'])
            ax.tick_params(colors=self.colors['text_light'], labelsize=12)
            ax.spines['bottom'].set_color(self.colors['text_light'])
            ax.spines['top'].set_color(self.colors['text_light'])
            ax.spines['right'].set_color(self.colors['text_light'])
            ax.spines['left'].set_color(self.colors['text_light'])
            ax.xaxis.label.set_color(self.colors['text_light'])
            ax.yaxis.label.set_color(self.colors['text_light'])
            title_color = self.colors['text_light']
            label_color = self.colors['text_light']
        else:
            fig.patch.set_facecolor('white')
            ax.set_facecolor('white')
            ax.tick_params(colors=self.colors['text_light'], labelsize=12)
            title_color = self.colors['text_light']
            label_color = self.colors['text_light']
        
        # Create bar chart with better visibility
        bars = ax.bar(categories, expenses, color=self.colors['danger'], alpha=0.8, edgecolor=self.colors['border'], linewidth=2)
        
        # Customize chart with larger, clearer fonts
        ax.set_title('Expenses by Category', fontsize=18, fontweight='bold', color=title_color, pad=20)
        ax.set_xlabel('Category', fontsize=14, fontweight='bold', color=label_color, labelpad=10)
        ax.set_ylabel('Amount (UGX)', fontsize=14, fontweight='bold', color=label_color, labelpad=10)
        ax.grid(axis='y', alpha=0.4, color=self.colors['border'], linewidth=1)
        
        # Rotate x-axis labels for better readability with larger font
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right', fontsize=12, fontweight='bold')
        plt.setp(ax.yaxis.get_majorticklabels(), fontsize=12, fontweight='bold')
        
        # Add value labels on bars with larger, clearer text
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'UGX {height:,.0f}',
                   ha='center', va='bottom', fontsize=11, fontweight='bold', 
                   color='white', bbox=dict(boxstyle='round,pad=0.3', facecolor=self.colors['danger'], alpha=0.8))
        
        # Adjust layout with more padding
        fig.tight_layout(pad=3.0)
        
        # Embed in tkinter with better positioning
        canvas = FigureCanvasTkAgg(fig, self.bar_chart_card)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True, padx=15, pady=15)
    
    def create_pie_chart(self):
        """Create a pie chart showing income vs expenses"""
        income = self.budget_mgr.get_total_income()
        expenses = self.budget_mgr.get_total_expenses()
        
        if income == 0 and expenses == 0:
            tk.Label(
                self.pie_chart_card,
                text="🥧 Income vs Expenses\n\nNo transaction data available",
                font=('Segoe UI', 12),
                bg=self.colors['bg_card'],
                fg=self.colors['text_muted'],
                justify='center'
            ).pack(expand=True, fill='both', pady=20)
            return
        
        # Create figure with larger size for better visibility
        fig = Figure(figsize=(6.5, 5), dpi=100, facecolor=self.colors['bg_card'])
        ax = fig.add_subplot(111)
        
        # Set theme colors
        if self.theme_mode == 'dark':
            fig.patch.set_facecolor(self.colors['bg_card'])
            ax.set_facecolor(self.colors['bg_card'])
            text_color = self.colors['text_light']
        else:
            fig.patch.set_facecolor('white')
            ax.set_facecolor('white')
            text_color = self.colors['text_light']
        
        # Prepare data
        labels = ['Income', 'Expenses']
        sizes = [income, expenses]
        colors_list = [self.colors['success'], self.colors['danger']]
        explode = (0.05, 0.05)  # Slight separation
        
        # Create pie chart with larger, clearer text
        wedges, texts, autotexts = ax.pie(
            sizes, 
            explode=explode, 
            labels=labels, 
            colors=colors_list,
            autopct='%1.1f%%',
            shadow=True,
            startangle=90,
            textprops={'fontsize': 14, 'fontweight': 'bold', 'color': text_color}
        )
        
        # Customize percentage text - larger and more visible
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
            autotext.set_fontsize(16)
        
        # Customize label text - make it larger and more visible
        for text in texts:
            text.set_fontsize(15)
            text.set_fontweight('bold')
            text.set_color(text_color)
        
        # Set title with larger, clearer font
        ax.set_title('Income vs Expenses', fontsize=18, fontweight='bold', color=text_color, pad=20)
        
        # Add legend with values - larger and clearer
        legend_labels = [f'{labels[i]}: UGX {sizes[i]:,.2f}' for i in range(len(labels))]
        legend = ax.legend(wedges, legend_labels, loc="center left", bbox_to_anchor=(1, 0, 0.5, 1), 
                 facecolor=self.colors['bg_card'], edgecolor=self.colors['border'],
                 labelcolor=text_color, fontsize=13, framealpha=0.9, prop={'weight': 'bold'})
        
        # Make legend frame more visible
        legend.get_frame().set_linewidth(2)
        
        # Adjust layout with more padding
        fig.tight_layout(pad=3.0)
        
        # Embed in tkinter with better positioning
        canvas = FigureCanvasTkAgg(fig, self.pie_chart_card)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True, padx=15, pady=15)

    def update_goals_display(self):
        # Clear existing widgets
        for widget in self.goals_display_frame.winfo_children():
            widget.destroy()
        
        if not self.budget_mgr.goals:
            no_goals_label = tk.Label(
                self.goals_display_frame,
                text="No savings goals yet. Create your first goal!",
                font=('Segoe UI', 14),
                bg=self.colors['bg_dark'],
                fg=self.colors['text_muted']
            )
            no_goals_label.pack(pady=50)
            return
        
        # Header
        header = tk.Label(
            self.goals_display_frame,
            text="Your Savings Goals",
            font=('Segoe UI', 18, 'bold'),
            bg=self.colors['bg_dark'],
            fg=self.colors['text_light']
        )
        header.pack(pady=(10, 20))
        
        # Display goals
        for goal in self.budget_mgr.goals:
            self.create_goal_card(goal)

    def create_goal_card(self, goal):
        card = tk.Frame(
            self.goals_display_frame,
            bg=self.colors['bg_card'],
            relief='flat',
            bd=1,
            highlightbackground=self.colors['border'],
            highlightthickness=1
        )
        card.pack(fill='x', padx=20, pady=10)
        
        # Goal info
        info_frame = tk.Frame(card, bg=self.colors['bg_card'])
        info_frame.pack(fill='x', padx=15, pady=12)
        
        tk.Label(
            info_frame,
            text=f"🎯 {goal.get_description()}",
            font=('Segoe UI', 14, 'bold'),
            bg=self.colors['bg_card'],
            fg=self.colors['text_light']
        ).pack(anchor='w')
        
        # Progress info
        current = goal.get_current()
        target = goal.get_target()
        progress = goal.get_progress()
        
        progress_text = f"UGX {current:,.2f} / UGX {target:,.2f} ({progress:.1f}%)"
        tk.Label(
            info_frame,
            text=progress_text,
            font=('Segoe UI', 11),
            bg=self.colors['bg_card'],
            fg=self.colors['text_muted']
        ).pack(anchor='w', pady=(5, 10))
        
        # Progress bar using Canvas
        progress_container = tk.Frame(card, bg=self.colors['bg_card'], relief='flat')
        progress_container.pack(fill='x', padx=15, pady=(0, 12))
        
        canvas_bg = 'white' if self.theme_mode == 'light' else self.colors['bg_hover']
        canvas = tk.Canvas(
            progress_container,
            bg=canvas_bg,
            height=30,
            highlightthickness=1,
            highlightbackground=self.colors['border'],
            relief='solid',
            bd=1
        )
        canvas.pack(fill='x', padx=5, pady=5)
        
        # Draw progress bar
        def draw_progress():
            canvas.update_idletasks()
            width = canvas.winfo_width()
            if width > 1:
                progress_percent = min(progress, 100) / 100
                bar_width = width * progress_percent
                canvas.delete("progress")
                canvas.create_rectangle(
                    0, 0, bar_width, 30,
                    fill=self.colors['primary'],
                    outline='',
                    tags="progress"
                )
                # Add percentage text
                canvas.delete("text")
                canvas.create_text(
                    width/2, 15,
                    text=f"{progress:.1f}%",
                    fill=self.colors['text_light'],
                    font=('Segoe UI', 10, 'bold'),
                    tags="text"
                )
        
        canvas.after(50, draw_progress)
        canvas.bind('<Configure>', lambda e: draw_progress())

if __name__ == "__main__":
    # Start with unified navigation system
    root = tk.Tk()
    app = AppController(root)
    root.mainloop()
