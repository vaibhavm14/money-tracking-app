from kivy.uix.boxlayout import BoxLayout
from kivy.properties import NumericProperty, StringProperty, ObjectProperty

class TransactionItem(BoxLayout):
    transaction_id = NumericProperty()
    amount = StringProperty()
    description = StringProperty()
    currency = StringProperty()
    transaction_type = StringProperty() # Expecting "Credit" or "Debit" (capitalized)
    date = StringProperty()
    delete_callback = ObjectProperty(None) # Callback function

    def trigger_delete(self):
        if self.delete_callback:
            self.delete_callback(self.transaction_id)