from kivy.uix.modalview import ModalView
from kivy.properties import ObjectProperty, StringProperty
from datetime import datetime

class AddTransactionPopup(ModalView):
    add_callback = ObjectProperty(None) # Callback function
    error_message = StringProperty("")

    def submit_transaction(self):
        amount_str = self.ids.amount_input.text.strip()
        description = self.ids.description_input.text.strip()
        currency = self.ids.currency_spinner.text
        transaction_type = self.ids.type_spinner.text
        tag = self.ids.tag_input.text.strip() # Get tag input

        # Basic Validation
        if not amount_str:
            self.error_message = "Amount is required."
            return
        if not description:
            self.error_message = "Note is required."
            return
        
        try:
            amount = float(amount_str)
            if amount <= 0:
                 self.error_message = "Amount must be positive."
                 return
        except ValueError:
            self.error_message = "Amount must be a valid number."
            return

        if transaction_type.lower() not in ['credit', 'debit']:
             self.error_message = "Invalid transaction type selected."
             return

        date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.error_message = "" # Clear error on success

        if self.add_callback:
            # Pass data to the callback provided by MainScreen
            self.add_callback(amount, description, currency, transaction_type.lower(), date, tag)
        self.dismiss() # Close the popup