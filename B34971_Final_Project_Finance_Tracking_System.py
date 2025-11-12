"""
PERSONAL FINANCE TRACKER - OOP PROJECT
Author: Irene COMFORT AKONGO (S25M19/001 - B34971)
MSc. Data Science & Analytics
Uganda Christian University
Date: 12th October 2025
"""

import json
import os
from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Dict, Optional, Any
import matplotlib.pyplot as plt

# =======================================================================================
# 1. PREDEFINED CATEGORIES
# =======================================================================================
CATEGORIES = ["Food", "Transport", "Entertainment", "Rent", "Salary", "Other"]

# ====================================================================================
# 2. DATE PARSER (SAFE)
# ====================================================================================
def parse_date(date_input: Optional[str]) -> str:
    """Safely convert input to 'YYYY-MM-DD' format. Accepts DD/MM/YYYY or YYYY-MM-DD."""
    if date_input is None or not isinstance(date_input, str):
        return datetime.now().strftime("%Y-%m-%d")
    date_str = date_input.strip()
    if not date_str:
        return datetime.now().strftime("%Y-%m-%d")
    try:
        if "/" in date_str:
            d = datetime.strptime(date_str, "%d/%m/%Y")
        else:
            d = datetime.strptime(date_str, "%Y-%m-%d")
        return d.strftime("%Y-%m-%d")
    except ValueError:
        print("  [Warning] Invalid date. Using today.")
        return datetime.now().strftime("%Y-%m-%d")

# ==============================
# 3. ABSTRACT TRANSACTION
# ==============================
class Transaction(ABC):
    def __init__(self, amount: float, category: str, description: str, date: Optional[str] = None):
        if amount < 0:
            raise ValueError("Amount cannot be negative.")
        self.amount = amount
        self.category = self._normalize_category(category)
        self.description = str(description).strip() if description else ""
        self.date = parse_date(date)
        self.id = self._generate_id()

    def _normalize_category(self, cat: str) -> str:
        if not isinstance(cat, str):
            return "Other"
        cat = cat.strip().title()
        return cat if cat in CATEGORIES else "Other"

    def _generate_id(self) -> str:
        return f"{self.__class__.__name__.lower()}_{int(datetime.now().timestamp())}_{hash(self.amount)}"

    @abstractmethod
    def get_type(self) -> str:
        pass

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "amount": self.amount,
            "category": self.category,
            "description": self.description,
            "date": self.date,
            "type": self.get_type()
        }

    @classmethod
    def from_dict(cls, data: dict):
        raise NotImplementedError


# ==============================
# 4. INCOME & EXPENSE
# ==============================
class Income(Transaction):
    def get_type(self) -> str:
        return "income"

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            amount=data.get("amount", 0.0),
            category=data.get("category", "Other"),
            description=data.get("description", ""),
            date=data.get("date")
        )


class Expense(Transaction):
    def get_type(self) -> str:
        return "expense"

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            amount=data.get("amount", 0.0),
            category=data.get("category", "Other"),
            description=data.get("description", ""),
            date=data.get("date")
        )


# ==============================
# 5. CATEGORY & GOAL
# ==============================
class Category:
    def __init__(self, name: str, budget: float = 0.0):
        self.name = str(name).title() if name else "Other"
        self.budget = max(0.0, float(budget))

    def to_dict(self) -> dict:
        return {"name": self.name, "budget": self.budget}

    @classmethod
    def from_dict(cls, data: dict):
        return cls(data.get("name", "Other"), data.get("budget", 0.0))


class Goal:
    def __init__(self, name: str, target: float, current: float = 0.0, deadline: Optional[str] = None):
        self.name = str(name).strip().title() if name else "Unnamed Goal"
        self.target_amount = max(0.0, float(target))
        self.current_amount = max(0.0, float(current))
        self.deadline = parse_date(deadline) if deadline else None

    def progress(self) -> float:
        return (self.current_amount / self.target_amount) * 100 if self.target_amount > 0 else 0

    def is_achieved(self) -> bool:
        return self.current_amount >= self.target_amount

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "target_amount": self.target_amount,
            "current_amount": self.current_amount,
            "deadline": self.deadline
        }

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            name=data.get("name", "Goal"),
            target=data.get("target_amount", 0.0),
            current=data.get("current_amount", 0.0),
            deadline=data.get("deadline")
        )


# ==============================
# 6. STORAGE (SAFE)
# ==============================
DATA_FILE = "data/finances.json"

def ensure_data_dir():
    os.makedirs("data", exist_ok=True)

def save_data(data: Dict[str, Any]):
    ensure_data_dir()
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)

def load_data() -> Dict[str, Any]:
    ensure_data_dir()
    default = {
        "transactions": [],
        "categories": [{"name": c, "budget": 0.0} for c in CATEGORIES],
        "goals": []
    }
    if not os.path.exists(DATA_FILE):
        save_data(default)
        return default
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            loaded = json.load(f)
        # Ensure structure
        return {
            "transactions": loaded.get("transactions", []),
            "categories": loaded.get("categories", default["categories"]),
            "goals": loaded.get("goals", [])
        }
    except Exception as e:
        print(f"  [Warning] Data corrupted. Starting fresh. ({e})")
        save_data(default)
        return default


# ==============================
# 7. BUDGET MANAGER
# ==============================
class BudgetManager:
    def __init__(self):
        self.transactions: List[Transaction] = []
        self.categories: List[Category] = []
        self.goals: List[Goal] = []
        self._load_all()

    def _load_all(self):
        data = load_data()
        self._load_transactions(data.get("transactions", []))
        self._load_categories(data.get("categories", []))
        self._load_goals(data.get("goals", []))

    def _load_transactions(self, trans_data: List[Dict]):
        for t in trans_data:
            try:
                if t.get("type") == "income":
                    self.transactions.append(Income.from_dict(t))
                elif t.get("type") == "expense":
                    self.transactions.append(Expense.from_dict(t))
            except:
                continue  # Skip invalid

    def _load_categories(self, cat_data: List[Dict]):
        loaded_names = set()
        for c in cat_data:
            try:
                cat = Category.from_dict(c)
                self.categories.append(cat)
                loaded_names.add(cat.name)
            except:
                continue
        # Add missing defaults
        for name in CATEGORIES:
            if name not in loaded_names:
                self.categories.append(Category(name))

    def _load_goals(self, goal_data: List[Dict]):
        for g in goal_data:
            try:
                self.goals.append(Goal.from_dict(g))
            except:
                continue

    def save(self):
        data = {
            "transactions": [t.to_dict() for t in self.transactions],
            "categories": [c.to_dict() for c in self.categories],
            "goals": [g.to_dict() for g in self.goals]
        }
        save_data(data)

    def add_income(self, amount: float, category: str, description: str, date: str = None):
        income = Income(amount, category, description, date)
        self.transactions.append(income)
        self.save()

    def add_expense(self, amount: float, category: str, description: str, date: str = None):
        expense = Expense(amount, category, description, date)
        self.transactions.append(expense)
        self.save()

    def get_category_summary(self) -> Dict[str, Dict[str, float]]:
        summary = {cat.name: {"income": 0.0, "expense": 0.0, "balance": 0.0} for cat in self.categories}
        for t in self.transactions:
            cat = t.category
            if cat in summary:
                if isinstance(t, Income):
                    summary[cat]["income"] += t.amount
                elif isinstance(t, Expense):
                    summary[cat]["expense"] += t.amount
                summary[cat]["balance"] = summary[cat]["income"] - summary[cat]["expense"]
        return summary

    def get_total_balance(self) -> float:
        income = sum(t.amount for t in self.transactions if isinstance(t, Income))
        expense = sum(t.amount for t in self.transactions if isinstance(t, Expense))
        return income - expense

    def add_goal(self, name: str, target: float, current: float = 0.0, deadline: str = None):
        goal = Goal(name, target, current, deadline)
        self.goals.append(goal)
        self.save()

    def contribute_to_goal(self, name: str, amount: float):
        for goal in self.goals:
            if goal.name.lower() == name.lower():
                goal.current_amount += max(0.0, amount)
                self.save()
                return
        print("  [Error] Goal not found.")

    def plot_expense_pie(self):
        expenses = {}
        for t in self.transactions:
            if isinstance(t, Expense):
                expenses[t.category] = expenses.get(t.category, 0) + t.amount
        if not expenses:
            print("  [Info] No expenses to display.")
            return
        plt.figure(figsize=(8, 6))
        plt.pie(expenses.values(), labels=expenses.keys(), autopct='%1.1f%%', startangle=90)
        plt.title("Expenses by Category")
        plt.axis('equal')
        plt.show()

    def plot_income_vs_expense_bar(self):
        summary = self.get_category_summary()
        cats = [c.name for c in self.categories]
        income = [summary[c]["income"] for c in cats]
        expense = [summary[c]["expense"] for c in cats]

        x = range(len(cats))
        width = 0.35

        plt.figure(figsize=(10, 6))
        plt.bar([i - width/2 for i in x], income, width, label='Income', color='#4CAF50')
        plt.bar([i + width/2 for i in x], expense, width, label='Expense', color='#F44336')
        plt.xlabel('Category')
        plt.ylabel('Amount (UGX)')
        plt.title('Income vs Expense by Category')
        plt.xticks(x, cats, rotation=45)
        plt.legend()
        plt.tight_layout()
        plt.show()


# ==============================
# 8. USER INTERFACE
# ==============================
def print_header():
    print("\n" + "="*70)
    print("    PERSONAL FINANCE TRACKER")
    print("    Irene COMFORT AKONGO - S25M19/001 (B34971)")
    print("    FACUALTY OF ENGINEERING DESIGN AND TECHNOLOGY")
    print("    DEPARTMENT OF COMPUTING")
    print("    UGANDA CHRISTIAN UNIVERSITY")
    print("="*70)

def print_menu():
    print("\n" + " MAIN MENU ".center(70, "="))
    print("1. Add Income")
    print("2. Add Expense")
    print("3. View Total Balance")
    print("4. Category Summary")
    print("5. View Savings Goals")
    print("6. Add Savings Goal")
    print("7. Contribute to Goal")
    print("8. Show Expense Pie Chart")
    print("9. Show Income vs Expense Bar Chart")
    print("10. Exit")
    print("="*70)

def get_input(prompt: str, type_cast=float, allow_empty=False):
    while True:
        val = input(prompt).strip()
        if allow_empty and not val:
            return None
        if not val:
            print("  [Error] Cannot be empty.")
            continue
        try:
            return type_cast(val)
        except:
            print(f"  [Error] Please enter a valid {type_cast.__name__}.")

def select_category() -> str:
    print("\n" + " SELECT CATEGORY ".center(50, "-"))
    for i, cat in enumerate(CATEGORIES, 1):
        print(f"  {i}. {cat}")
    print("-"*50)
    while True:
        try:
            choice = int(input("  Enter number (1-6): ")) - 1
            if 0 <= choice < len(CATEGORIES):
                return CATEGORIES[choice]
            print("  [Error] Invalid choice.")
        except:
            print("  [Error] Enter a number.")

def main():
    print_header()
    print("  Initializing system...")
    manager = BudgetManager()
    print("  System ready!\n")

    while True:
        print_menu()
        choice = get_input("  Enter your choice (1-10): ", int)

        if choice == 1:
            print("\n" + " ADD INCOME ".center(50, "="))
            amt = get_input("  Amount (UGX): ", float)
            cat = select_category()
            desc = input("  Description: ").strip()
            date = input("  Date (DD/MM/YYYY or YYYY-MM-DD) [today]: ").strip()
            manager.add_income(amt, cat, desc, date or None)
            print("  Income added.")

        elif choice == 2:
            print("\n" + " ADD EXPENSE ".center(50, "="))
            amt = get_input("  Amount (UGX): ", float)
            cat = select_category()
            desc = input("  Description: ").strip()
            date = input("  Date (DD/MM/YYYY or YYYY-MM-DD) [today]: ").strip()
            manager.add_expense(amt, cat, desc, date or None)
            print("  Expense added.")

        elif choice == 3:
            print(f"\n  TOTAL BALANCE: UGX {manager.get_total_balance():,.2f}")

        elif choice == 4:
            print("\n" + " CATEGORY SUMMARY ".center(70, "="))
            print(f"{'Category':<15} {'Income':>12} {'Expense':>12} {'Balance':>12}")
            print("-" * 55)
            summary = manager.get_category_summary()
            for cat, data in summary.items():
                bal = data["balance"]
                status = "PROFIT" if bal > 0 else "LOSS" if bal < 0 else "ZERO"
                print(f"{cat:<15} {data['income']:>12,.2f} {data['expense']:>12,.2f} {bal:>12,.2f} [{status}]")
            total_inc = sum(s['income'] for s in summary.values())
            total_exp = sum(s['expense'] for s in summary.values())
            print("-" * 55)
            print(f"{'TOTAL':<15} {total_inc:>12,.2f} {total_exp:>12,.2f} {manager.get_total_balance():>12,.2f}")

        elif choice == 5:
            print("\n" + " SAVINGS GOALS ".center(60, "="))
            if not manager.goals:
                print("  No goals set.")
            for g in manager.goals:
                status = "ACHIEVED!" if g.is_achieved() else f"{g.progress():.1f}%"
                deadline = f" | By {g.deadline}" if g.deadline else ""
                print(f"  • {g.name}: UGX {g.current_amount:,.2f} / {g.target_amount:,.2f} [{status}]{deadline}")

        elif choice == 6:
            print("\n" + " ADD SAVINGS GOAL ".center(50, "="))
            name = input("  Goal name: ").strip()
            target = get_input("  Target amount: ", float)
            current = get_input("  Current saved (0): ", float)
            deadline = input("  Deadline (DD/MM/YYYY) [optional]: ").strip()
            manager.add_goal(name, target, current, deadline or None)
            print("  Goal added.")

        elif choice == 7:
            if not manager.goals:
                print("  No goals to contribute to.")
            else:
                print("\n" + " CONTRIBUTE TO GOAL ".center(50, "="))
                for g in manager.goals:
                    print(f"  - {g.name}: UGX {g.current_amount:,.2f}/{g.target_amount:,.2f}")
                name = input("  Goal name: ").strip()
                amt = get_input("  Amount to add: ", float)
                manager.contribute_to_goal(name, amt)

        elif choice == 8:
            manager.plot_expense_pie()

        elif choice == 9:
            manager.plot_income_vs_expense_bar()

        elif choice == 10:
            print("\n  Thank you for using Personal Finance Tracker!")
            print("  Goodbye, Irene!")
            break

        else:
            print("  [Error] Invalid option.")

        input("\n  Press Enter to continue...")



if __name__ == "__main__":
    main()
    