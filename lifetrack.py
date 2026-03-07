import json
import sys
import os
import requests
import atexit

# --- 1. COLOR & LOGO CONFIG ---
G = '\033[92m'  # Green
Y = '\033[93m'  # Yellow
C = '\033[96m'  # Cyan
R = '\033[91m'  # Red
W = '\033[0m'   # White (Reset)

LOGO = f"""
{C}  _      _  __        _______             _    
 | |    (_)/ _|      |__   __|           | |   
 | |     _| |_ ___      | | _ __ __ _  __| | __
 | |    | |  _/ _ \     | || '__/ _` |/ _` |/ /
 | |____| | ||  __/     | || | | (_| | (_|   < 
 |______|_|_| \___|     |_||_|  \__,_|\__,_|\_\\{W}
      {Y}>> COMMAND CENTRE v1.0 <<{W}
"""

# --- DATA FILE ---
DATA_FILE = "data.json"

# --- AUTO CLEAR DATA WHEN PROGRAM EXITS ---
def clear_data_on_exit():
    if os.path.exists(DATA_FILE):
        os.remove(DATA_FILE)

atexit.register(clear_data_on_exit)

# --- 2. DATA STORAGE ---
all_habits = [] 
all_expenses = [] 

# --- 3. CORE LOGIC ---
class Expense:
    def __init__(self, name, amount, category):
        self.name = name
        self.amount = float(amount)
        self.category = category

class Habit:
    def __init__(self, name, target_days):
        self.name = name
        self.target_days = int(target_days) 
        self.completed_days = 0

    def log_progress(self):
        if self.completed_days < self.target_days:
            self.completed_days += 1
            print(f"{G}[SUCCESS]{W} Progress updated!")
        else:
            print(f"{Y}[GOAL REACHED]{W} Stay consistent!")

# --- 4. HELPERS ---

def get_valid_number(prompt):
    while True:
        try:
            value = float(input(prompt))
            return value
        except ValueError:
            print(f"{R}Invalid number. Please enter a valid amount.{W}")

def get_valid_integer(prompt):
    while True:
        try:
            value = int(input(prompt))
            return value
        except ValueError:
            print(f"{R}Invalid entry. Please enter a number.{W}")

def get_quote():
    try:
        res = requests.get("https://zenquotes.io/api/random", timeout=3)
        data = res.json()
        return f"{C}\"{data[0]['q']}\"{W} - {data[0]['a']}"
    except:
        return f"{Y}Success is the sum of small efforts repeated day-in and day-out.{W}"

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def save_data():
    data = {
        "habits": [{"name": h.name, "target_days": h.target_days, "completed_days": h.completed_days} for h in all_habits],
        "expenses": [{"name": e.name, "amount": e.amount, "category": e.category} for e in all_expenses]
    }
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

def load_data():
    global all_habits, all_expenses
    try:
        with open(DATA_FILE, "r") as f:
            full_data = json.load(f)
            if not isinstance(full_data, dict): return
            all_habits = [Habit(i['name'], i['target_days']) for i in full_data.get("habits", [])]
            for i, h in enumerate(all_habits):
                h.completed_days = full_data["habits"][i]['completed_days']
            all_expenses = [Expense(e['name'], e['amount'], e['category']) for e in full_data.get("expenses", [])]
    except:
        pass

# --- RESET DEMO DATA ---
def reset_demo_data():
    global all_habits, all_expenses
    all_habits = []
    all_expenses = []
    if os.path.exists(DATA_FILE):
        os.remove(DATA_FILE)
    print(f"{G}Demo data cleared successfully!{W}")
    input(f"{C}Press Enter to continue...{W}")

# --- 5. THE DASHBOARD ---
def show_dashboard():
    clear_screen()
    print(LOGO)
    print(f" {get_quote()}")
    print(f"{C}{'='*45}{W}")
    
    total_spent = sum(e.amount for e in all_expenses)
    print(f" 💸 {Y}Total Spending:{W}  R{total_spent:.2f}")
    
    if all_habits:
        top_habit = max(all_habits, key=lambda h: h.completed_days)
        print(f" 🔥 {G}Top Habit:{W}       {top_habit.name} ({top_habit.completed_days}/{top_habit.target_days})")
    print(f"{C}{'='*45}{W}")

# --- 6. MENUS ---
def finance_menu():
    while True:
        print(f"\n{Y}--- FINANCE MODULE ---{W}")
        print("1. ➔ Add Expense\n2. ➔ View All\n3. ➔ Back")
        choice = input(f"\n{C}Select:{W} ")
        if choice == '1':
            name = input("Item: ")
            amount = get_valid_number("Amount: R")
            category = input("Category: ")
            all_expenses.append(Expense(name, amount, category))
            save_data()
        elif choice == '2':
            for e in all_expenses: print(f" • {e.name}: {Y}R{e.amount:.2f}{W}")
            input(f"\n{C}Press Enter to continue...{W}")
        elif choice == '3': break

def habit_menu():
    while True:
        print(f"\n{G}--- HABIT TRACKER ---{W}")
        print("1. ➔ Add Habit\n2. ➔ View Progress\n3. ➔ Check-in\n4. ➔ Back")
        choice = input(f"\n{C}Select:{W} ")
        if choice == '1':
            name = input("Name: ")
            goal_days = get_valid_integer("Goal Days: ")
            all_habits.append(Habit(name, goal_days))
            save_data()
        elif choice == '2':
            for h in all_habits: print(f" • {h.name}: {G}{h.completed_days}/{h.target_days}{W}")
            input(f"\n{C}Press Enter to continue...{W}")
        elif choice == '3':
            if not all_habits: continue
            for i, h in enumerate(all_habits): print(f"{i+1}. {h.name}")
            try:
                idx = get_valid_integer("Number: ") - 1
                all_habits[idx].log_progress()
                save_data()
            except:
                print(f"{R}Invalid entry.{W}")
        elif choice == '4': break

# --- 7. MAIN ---
def main_menu():
    load_data()
    while True:
        show_dashboard()
        print(f"{C}1.{W} Manage Finances")
        print(f"{C}2.{W} Manage Habits")
        print(f"{C}3.{W} Reset Demo Data")
        print(f"{C}4.{W} Exit")
        choice = input(f"\n{C}Select Option:{W} ")
        if choice == '1': finance_menu()
        elif choice == '2': habit_menu()
        elif choice == '3': reset_demo_data()
        elif choice == '4': sys.exit()

if __name__ == "__main__":
    main_menu()