from kivy.uix.screenmanager import Screen
from kivy.properties import StringProperty, BooleanProperty
from kivy.app import App
from kivy.metrics import dp
from kivy.clock import Clock
import os
import json

# File to store password
USER_DATA_FILE = "user_data.json"

class LoginScreen(Screen):
    error_message = StringProperty("")
    login_mode = BooleanProperty(True)  # True for login, False for register
    show_register_option = BooleanProperty(False)  # Whether to show the register option
    
    def __init__(self, **kwargs):
        super(LoginScreen, self).__init__(**kwargs)
        # Check if a password already exists
        user_data = self.load_user_data()
        if not user_data or "master_password" not in user_data:
            # No password exists yet, switch to registration mode
            self.login_mode = False
            self.show_register_option = False  # No option needed on first run
        else:
            # Password exists, stay in login mode
            self.login_mode = True
            self.show_register_option = False  # Hide register option when password exists
    
    def toggle_login_mode(self):
        """Switch between login and register mode"""
        self.login_mode = not self.login_mode
        self.error_message = ""  # Clear error message
        self.ids.password_input.text = ""  # Clear password
        if not self.login_mode and hasattr(self.ids, 'confirm_password_input'):
            self.ids.confirm_password_input.text = ""  # Clear confirm password

    def login(self):
        """Handle login process"""
        password = self.ids.password_input.text.strip()
        
        if not password:
            self.error_message = "Please enter your password"
            return
            
        user_data = self.load_user_data()
        
        if not user_data or "master_password" not in user_data:
            self.error_message = "No password set. Please create a password first."
            self.login_mode = False  # Switch to register mode
            return
            
        # Check if the password is correct
        if password == user_data["master_password"]:
            self.error_message = ""
            App.get_running_app().root.current = 'main'  # Switch to main screen
            self.ids.password_input.text = ""  # Clear password
        else:
            self.error_message = "Invalid password"
            self.ids.password_input.text = ""  # Clear password

    def register_user(self):
        """Handle new user registration"""
        password = self.ids.password_input.text.strip()
        confirm_password = self.ids.confirm_password_input.text.strip()
        
        # Basic validation
        if not password:
            self.error_message = "Please enter a password"
            return
            
        if password != confirm_password:
            self.error_message = "Passwords do not match"
            return
            
        # Save the master password
        user_data = {"master_password": password}
        self.save_user_data(user_data)
        
        # Success feedback
        self.error_message = "Password created successfully!"
        # Automatically switch to login mode
        Clock.schedule_once(lambda dt: self.auto_login_after_register(), 1.5)

    def auto_login_after_register(self):
        """Automatically login after successful registration"""
        self.login_mode = True  # Switch back to login mode
        self.show_register_option = False  # Hide register option after password is set
        self.error_message = "You can now log in"

    def load_user_data(self):
        """Load user data from file"""
        try:
            if os.path.exists(USER_DATA_FILE):
                with open(USER_DATA_FILE, 'r') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            print(f"Error loading user data: {e}")
            return {}
            
    def save_user_data(self, data):
        """Save user data to file"""
        try:
            with open(USER_DATA_FILE, 'w') as f:
                json.dump(data, f)
        except Exception as e:
            print(f"Error saving user data: {e}")