from kivy.uix.screenmanager import Screen
from kivy.properties import StringProperty, DictProperty
from kivy.clock import Clock
from utils.analysis import generate_analysis_plot
import os
# from datetime import datetime # No longer needed for timestamp

class AnalysisScreen(Screen):
    plot_source = StringProperty("")
    stats = DictProperty({})

    def on_enter(self, *args):
        # Generate plot when entering the screen
        # Use Clock to avoid blocking UI thread if generation is slow
        print("Entering Analysis Screen, scheduling update...")
        Clock.schedule_once(self.update_analysis)

    def update_analysis(self, dt=0):
        print("Updating analysis data and plot...")
        plot_path, stats_data = generate_analysis_plot()

        if plot_path and os.path.exists(plot_path):
            # Remove the nocache query string for simplicity
            # timestamp = datetime.now().timestamp() # Removed
            # self.plot_source = f"{plot_path}?nocache={timestamp}" # Removed
            self.plot_source = plot_path # Use the direct path
            print(f"Plot found: {self.plot_source}")
            # Force image reload in kv - check if id exists first
            if hasattr(self.ids, 'analysis_image') and self.ids.analysis_image:
                 # Reloading might be less effective without nocache, but try anyway
                 self.ids.analysis_image.reload()
                 print("Reloaded analysis image.")
        else:
            self.plot_source = "" # Clear if no plot generated or path invalid
            print("No plot generated or path invalid.")

        self.stats = stats_data if stats_data else {}
        print(f"Stats updated: {self.stats}")

    def go_back(self):
        # Use self.manager to access the ScreenManager
        if self.manager:
            self.manager.current = 'main'