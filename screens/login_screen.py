from kivy.uix.screenmanager import Screen
from kivy.properties import StringProperty
from kivy.app import App
from kivy.metrics import dp # Import dp for density-independent pixels

# VERY Basic password check - REPLACE with a secure method (hashing, etc.)
CORRECT_PASSWORD = "password"

class LoginScreen(Screen):
    error_message = StringProperty("")

    def check_password(self):
        password = self.ids.password_input.text
        if password == CORRECT_PASSWORD:
            self.error_message = ""
            # Use App.get_running_app().root to access the ScreenManager
            App.get_running_app().root.current = 'main' # Switch screen
            self.ids.password_input.text = "" # Clear password
        else:
            self.error_message = "Incorrect Password"
            self.ids.password_input.text = "" # Clear password on failure too