from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, FadeTransition
from kivy.properties import StringProperty
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.metrics import dp
from database import init_db, get_transactions # Import get_transactions
import os

# Import screens
from screens.login_screen import LoginScreen
from screens.main_screen import MainScreen
from screens.analysis_screen import AnalysisScreen
# Import widgets
from widgets.transaction_item import TransactionItem
from widgets.add_transaction_popup import AddTransactionPopup

class MoneyTrackerApp(App):
    theme = StringProperty("light")  # Default theme: "light" or "dark"

    def build(self):
        init_db() # Initialize the database on startup
        try:
            Builder.load_file("screens/login_screen.kv")
            Builder.load_file("screens/main_screen.kv")
            Builder.load_file("screens/analysis_screen.kv")
            Builder.load_file("widgets/transaction_item.kv")
            Builder.load_file("widgets/add_transaction_popup.kv")
            print("KV files loaded successfully.")
        except Exception as e:
            print(f"Error loading KV files: {e}")
            # Consider more robust error handling or app exit

        sm = ScreenManager(transition=FadeTransition(duration=0.2))
        sm.add_widget(LoginScreen(name='login'))
        sm.add_widget(MainScreen(name='main'))
        sm.add_widget(AnalysisScreen(name='analysis'))
        sm.current = 'login'
        return sm

    def get_currency_symbol(self):
        """
        Returns the symbol for the base currency used in analysis.
        Currently, analysis is done in INR.
        """
        # Since all analysis is converted to INR (as per utils/analysis.py),
        # always return the INR symbol here for the analysis screen.
        return "₹"

    def toggle_theme(self):
        self.theme = "dark" if self.theme == "light" else "light"
        print(f"Theme toggled to: {self.theme}")
        # Optional: Update window background color based on theme
        # from utils.theme import get_color
        # Window.clearcolor = get_color(self.theme, "bg_color")
        # If widgets don't update automatically, you might need to trigger a redraw:
        # if self.root:
        #     for screen in self.root.screens:
        #         # You might need a more specific way to trigger updates if simple property changes aren't enough
        #         screen.canvas.ask_update()


if __name__ == '__main__':
    # Create assets directory if it doesn't exist
    assets_dir = "assets"
    if not os.path.exists(assets_dir):
        try:
            os.makedirs(assets_dir)
            print(f"Created directory: {assets_dir}")
        except Exception as e:
            print(f"Error creating directory {assets_dir}: {e}")

    # Placeholder icon creation (ensure Kivy core image is available)
    try:
        from kivy.core.image import Image as CoreImage

        icon_paths = {
            "delete_icon.png": (1, 0, 0, 1),  # Red
            "theme_icon.png": (0.5, 0.5, 0.5, 1) # Grey
            # Add other icons here if needed
        }

        for icon_name, color in icon_paths.items():
            icon_path = os.path.join(assets_dir, icon_name)
            if not os.path.exists(icon_path):
                try:
                    img = CoreImage.create(size=(64, 64), color=color)
                    img.save(icon_path)
                    print(f"Created placeholder icon: {icon_path}")
                except Exception as e:
                    print(f"Error creating placeholder icon {icon_path}: {e}")
    
    except ImportError:
        print("Kivy CoreImage module not found. Cannot create placeholder icons.")
    except Exception as e: # Catch any other unexpected errors during icon creation
        print(f"An unexpected error occurred during placeholder icon setup: {e}")

    MoneyTrackerApp().run()