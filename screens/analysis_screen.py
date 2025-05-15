from kivy.uix.screenmanager import Screen
from kivy.properties import StringProperty, DictProperty, BooleanProperty
from kivy.clock import Clock
from utils.analysis import generate_analysis_plot
import os

class AnalysisScreen(Screen):
    plot_source = StringProperty("")
    # Allow stats to be None, and default to None
    stats = DictProperty(None, allownone=True)
    is_loading = BooleanProperty(False)

    def on_enter(self, *args):
        print("Entering Analysis Screen...")
        self.is_loading = True
        self.plot_source = ""  # Clear previous plot
        self.stats = None      # Clear previous stats
        # Use Clock to avoid blocking UI thread if generation is slow
        Clock.schedule_once(self.update_analysis, 0.1) # Small delay

    def update_analysis(self, dt=0):
        print("Updating analysis data and plot...")
        plot_path, stats_data = generate_analysis_plot()

        if plot_path and os.path.exists(plot_path):
            # Set plot_source to the actual file path.
            # The "?timestamp=" was causing issues for local file loading.
            self.plot_source = plot_path 
            print(f"Plot source set to: {self.plot_source}")

            # Ensure the image widget reloads the image from disk,
            # as the content of the file at plot_path has been updated.
            if hasattr(self.ids, 'analysis_image') and self.ids.analysis_image:
                # The Image widget's source is bound to root.plot_source in KV.
                # Changing root.plot_source should trigger an update.
                # Calling reload() explicitly ensures the new content is loaded.
                self.ids.analysis_image.reload()
                print("Requested analysis image reload.")
        else:
            self.plot_source = "" # Clear if no plot generated or path invalid
            print("No plot generated or path invalid.")

        self.stats = stats_data # This can be None if generate_analysis_plot returns None for stats
        
        self.is_loading = False
        print(f"Stats updated: {self.stats}")
        print(f"Is Loading: {self.is_loading}")


    def go_back(self):
        if self.manager:
            self.manager.current = 'main'