from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, FadeTransition # Added FadeTransition
from kivy.properties import StringProperty
from kivy.lang import Builder
from kivy.core.window import Window # To potentially set background color
from kivy.metrics import dp # If needed globally, though often used in kv
from database import init_db # Assumes database.py is in the root
import os

# Import screens (make sure __init__.py exists in folders)
from screens.login_screen import LoginScreen
from screens.main_screen import MainScreen
from screens.analysis_screen import AnalysisScreen
# Import widgets (needed for kv rules if not explicitly used in py)
from widgets.transaction_item import TransactionItem
from widgets.add_transaction_popup import AddTransactionPopup

# Set a default window background color (optional)
# Window.clearcolor = (1, 1, 1, 1) # Light theme default

class MoneyTrackerApp(App):
    theme = StringProperty("light")  # Default theme: "light" or "dark"

    def build(self):
        init_db() # Initialize the database on startup
        # Load the main kv file that sets up the ScreenManager
        # Builder.load_file("moneytracker.kv") # Can be loaded automatically if named correctly
        # Load other kv files for screens/widgets explicitly
        try:
            Builder.load_file("screens/login_screen.kv")
            Builder.load_file("screens/main_screen.kv")
            Builder.load_file("screens/analysis_screen.kv")
            Builder.load_file("widgets/transaction_item.kv")
            Builder.load_file("widgets/add_transaction_popup.kv")
            print("KV files loaded successfully.")
        except Exception as e:
            print(f"Error loading KV files: {e}")
            # Handle error appropriately, maybe exit or show an error popup

        sm = ScreenManager(transition=FadeTransition(duration=0.2)) # Use a transition
        sm.add_widget(LoginScreen(name='login'))
        sm.add_widget(MainScreen(name='main'))
        sm.add_widget(AnalysisScreen(name='analysis'))
        # Set initial screen
        sm.current = 'login'
        return sm

    def toggle_theme(self):
        self.theme = "dark" if self.theme == "light" else "light"
        print(f"Theme toggled to: {self.theme}")
        # Update window background if desired
        # from utils.theme import get_color
        # Window.clearcolor = get_color(self.theme, "bg_color")
        # Force redraw of widgets if kv bindings aren't sufficient (less common)
        # self.root.canvas.ask_update()


if __name__ == '__main__':
    # Create assets directory if it doesn't exist
    if not os.path.exists("assets"):
        try:
            os.makedirs("assets")
            print("Created assets directory.")
        except Exception as e:
            print(f"Error creating assets directory: {e}")


    # Import CoreImage specifically for creation inside this block
    try:
        from kivy.core.image import Image as CoreImage

        # Add placeholder icons if they don't exist (replace with real icons)
        placeholder_icon = "assets/delete_icon.png"
        if not os.path.exists(placeholder_icon):
             # Create a simple red square as a placeholder
             img = CoreImage.create(size=(64, 64), color=(1, 0, 0, 1)) # Use CoreImage.create
             img.save(placeholder_icon)
             print(f"Created placeholder icon: {placeholder_icon}")

        # Add theme icon placeholder
        theme_icon = "assets/theme_icon.png"
        if not os.path.exists(theme_icon):
             img = CoreImage.create(size=(64, 64), color=(0.5, 0.5, 0.5, 1)) # Use CoreImage.create
             img.save(theme_icon)
             print(f"Created placeholder icon: {theme_icon}")

    except ImportError:
        print("Kivy core image not found, cannot create placeholder icons.")
    except Exception as e:
        print(f"Error creating placeholder icons: {e}")


    MoneyTrackerApp().run()