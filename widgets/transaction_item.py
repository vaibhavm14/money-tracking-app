from kivy.uix.boxlayout import BoxLayout
from kivy.properties import NumericProperty, StringProperty, ObjectProperty

class TransactionItem(BoxLayout):
    transaction_id = NumericProperty()
    amount = StringProperty()
    description = StringProperty()
    currency = StringProperty()
    transaction_type = StringProperty()
    date = StringProperty()
    tag = StringProperty("Uncategorized") # New property for tag
    delete_callback = ObjectProperty(None)

    def trigger_delete(self):
        if self.delete_callback:
            self.delete_callback(self.transaction_id)