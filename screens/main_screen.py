#filepath: /home/vaibhavm14/code/PROJECT/Money-tracker/screens/main_screen.py
from kivy.uix.screenmanager import Screen
from kivy.properties import ListProperty, StringProperty, NumericProperty
from kivy.clock import Clock
from database import get_transactions, delete_transaction, add_transaction
from widgets.add_transaction_popup import AddTransactionPopup
import os

LOG_FILE = "transaction_logs.txt" # Consider moving to config/utils

class MainScreen(Screen):
    # transactions_data holds dictionaries for RecycleView
    transactions_data = ListProperty([])
    total_balance = NumericProperty(0.0)

    def on_enter(self, *args):
        # Schedule loading transactions slightly after entering the screen
        # This can sometimes help ensure the UI is ready.
        print("Entering Main Screen, scheduling transaction load...")
        Clock.schedule_once(self.load_transactions, 0.1) # Schedule with a small delay (0.1 seconds)

    def load_transactions(self, dt=0): # Add dt argument for Clock schedule
        print("Executing scheduled load_transactions...")
        try:
            transactions = get_transactions()
            temp_data = []
            balance = 0
            # Process transactions in reverse for newest first display if desired
            for t_id, amount, desc, curr, t_type, date in reversed(transactions):
                temp_data.append({
                    "transaction_id": t_id,
                    "amount": f"{amount:.2f}", # Format amount string
                    "description": desc,
                    "currency": curr,
                    "transaction_type": t_type.capitalize(), # Capitalize for display
                    "date": date,
                    "delete_callback": self.delete_transaction_callback # Pass method reference
                })
                # Calculate balance based on original data
                if t_type == 'credit':
                    balance += amount
                elif t_type == 'debit':
                    balance -= amount

            self.transactions_data = temp_data # Update RecycleView data
            self.total_balance = balance
            print(f"Loaded {len(self.transactions_data)} transactions. Balance: {self.total_balance}")
            # Optional: Force refresh RecycleView if data update doesn't trigger it (usually not needed)
            # if hasattr(self.ids, 'rv'):
            #     self.ids.rv.refresh_from_data()
        except Exception as e:
            print(f"Error loading transactions: {e}")
            # Ensure data is cleared on error to avoid showing stale data
            self.transactions_data = []
            self.total_balance = 0

    def delete_transaction_callback(self, transaction_id):
        print(f"Callback triggered: Deleting transaction id={transaction_id}")
        try:
            delete_transaction(transaction_id)
            self.load_transactions() # Reload list after deleting
        except Exception as e:
            print(f"Error deleting transaction: {e}")

    def add_transaction_callback(self, amount, description, currency, transaction_type, date):
        print(f"Callback triggered: Adding transaction...")
        try:
            add_transaction(amount, description, currency, transaction_type, date)
            self.log_transaction(amount, description, currency, transaction_type, date)
            self.load_transactions() # Reload list after adding
        except Exception as e:
            print(f"Error adding transaction: {e}")

    def log_transaction(self, amount, description, currency, transaction_type, date):
         try:
             with open(LOG_FILE, "a") as log_file:
                 log_file.write(f"{date} - {transaction_type.capitalize()}: {amount} {currency} - {description}\n")
         except Exception as e:
             print(f"Error writing to log file: {e}")

    def open_add_popup(self):
        # Pass the callback method to the popup
        popup = AddTransactionPopup(add_callback=self.add_transaction_callback)
        popup.open()

    def go_to_analysis(self):
        # Use self.manager to access the ScreenManager
        if self.manager:
            self.manager.current = 'analysis'