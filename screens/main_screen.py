from kivy.uix.screenmanager import Screen
from kivy.properties import ListProperty, StringProperty, NumericProperty
from kivy.clock import Clock
from database import get_transactions, delete_transaction, add_transaction, get_unique_tags
from widgets.add_transaction_popup import AddTransactionPopup
from utils.analysis import convert_to_base_currency, BASE_CURRENCY_ANALYSIS # Import conversion utilities
import os

LOG_FILE = "transaction_logs.txt"

class MainScreen(Screen):
    transactions_data = ListProperty([])
    total_balance = NumericProperty(0.0) # This will now be in BASE_CURRENCY_ANALYSIS
    available_tags = ListProperty([])
    current_tag_filter = StringProperty("All Tags") # Default filter

    def on_enter(self, *args):
        print("Entering Main Screen, scheduling transaction and tag load...")
        Clock.schedule_once(self.load_tags_for_filter, 0.05) # Load tags first
        Clock.schedule_once(lambda dt: self.load_transactions(tag_filter=self.current_tag_filter), 0.1)


    def load_tags_for_filter(self, dt=0):
        print("Loading unique tags for filter...")
        unique_tags = get_unique_tags()
        self.available_tags = ["All Tags"] + sorted(list(set(unique_tags))) # Ensure "All Tags" is an option
        if self.current_tag_filter not in self.available_tags and self.current_tag_filter != "All Tags":
            self.current_tag_filter = "All Tags"
        
        if hasattr(self.ids, 'tag_filter_spinner') and self.ids.tag_filter_spinner.text != self.current_tag_filter:
             self.ids.tag_filter_spinner.text = self.current_tag_filter
        print(f"Available tags for filter: {self.available_tags}")


    def load_transactions(self, dt=0, tag_filter=None):
        print(f"Executing scheduled load_transactions... Filter: {tag_filter}")
        if tag_filter is None:
            tag_filter = self.current_tag_filter

        try:
            all_transactions = get_transactions() # Fetches (id, amount, desc, currency, type, date, tag)
            temp_data = []
            balance_in_base_currency = 0.0

            # Calculate overall balance in base currency
            for _, original_amount, _, currency, t_type, _, _ in all_transactions:
                amount_in_base = convert_to_base_currency(float(original_amount), currency)
                if t_type == 'credit':
                    balance_in_base_currency += amount_in_base
                elif t_type == 'debit':
                    balance_in_base_currency -= amount_in_base
            
            self.total_balance = balance_in_base_currency # total_balance is now in INR

            # Now filter for display
            filtered_transactions_for_display = []
            if tag_filter == "All Tags" or not tag_filter:
                filtered_transactions_for_display = all_transactions
            else:
                for t in all_transactions:
                    if t[6] == tag_filter: # index 6 is tag
                        filtered_transactions_for_display.append(t)
            
            # Prepare data for RecycleView (amounts are kept in their original currency for display in the list)
            for t_id, amount, desc, curr, t_type, date, tag_val in reversed(filtered_transactions_for_display):
                temp_data.append({
                    "transaction_id": t_id,
                    "amount": f"{float(amount):.2f}", # Display original amount
                    "description": desc,
                    "currency": curr, # Display original currency
                    "transaction_type": t_type.capitalize(),
                    "date": date,
                    "tag": tag_val if tag_val else "Uncategorized",
                    "delete_callback": self.delete_transaction_callback
                })

            self.transactions_data = temp_data
            print(f"Loaded {len(self.transactions_data)} transactions for display. Overall Balance (in {BASE_CURRENCY_ANALYSIS}): {self.total_balance:.2f}")
        except Exception as e:
            print(f"Error loading transactions: {e}")
            self.transactions_data = []


    def delete_transaction_callback(self, transaction_id):
        print(f"Callback triggered: Deleting transaction id={transaction_id}")
        try:
            delete_transaction(transaction_id)
            self.load_tags_for_filter() 
            self.load_transactions(tag_filter=self.current_tag_filter) 
        except Exception as e:
            print(f"Error deleting transaction: {e}")

    def add_transaction_callback(self, amount, description, currency, transaction_type, date, tag):
        print(f"Callback triggered: Adding transaction with tag '{tag}'...")
        try:
            add_transaction(amount, description, currency, transaction_type, date, tag)
            self.log_transaction(amount, description, currency, transaction_type, date, tag)
            self.load_tags_for_filter() 
            self.load_transactions(tag_filter=self.current_tag_filter)
        except Exception as e:
            print(f"Error adding transaction: {e}")

    def log_transaction(self, amount, description, currency, transaction_type, date, tag):
         try:
             with open(LOG_FILE, "a") as log_file:
                 log_file.write(f"{date} - {transaction_type.capitalize()}: {amount} {currency} - {description} [Tag: {tag if tag else 'Uncategorized'}]\n")
         except Exception as e:
             print(f"Error writing to log file: {e}")

    def open_add_popup(self):
        popup = AddTransactionPopup(add_callback=self.add_transaction_callback)
        popup.open()

    def go_to_analysis(self):
        if self.manager:
            self.manager.current = 'analysis'

    def on_tag_filter_change(self, spinner_text):
        print(f"Tag filter changed to: {spinner_text}")
        self.current_tag_filter = spinner_text
        self.load_transactions(tag_filter=self.current_tag_filter)