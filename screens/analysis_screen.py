from kivy.uix.screenmanager import Screen
from kivy.properties import StringProperty, DictProperty, BooleanProperty, ObjectProperty
from kivy.clock import Clock
from utils.analysis import generate_analysis_plot
import os

class AnalysisScreen(Screen):
    plot_source = StringProperty("")
    stats = DictProperty(None, allownone=True)
    is_loading = BooleanProperty(False)
    chart_data = DictProperty(None, allownone=True)  # New property for chart data

    def on_enter(self, *args):
        print("Entering Analysis Screen...")
        self.is_loading = True
        self.plot_source = ""
        self.stats = None
        self.chart_data = None  # Reset chart data
        Clock.schedule_once(self.update_analysis, 0.1)

    def update_analysis(self, dt=0):
        print("Updating analysis data and plot...")
        plot_path, stats_data, chart_data = generate_analysis_plot()  # Now returns chart_data too

        if plot_path:
            self.plot_source = plot_path
            print(f"Plot source set to: {self.plot_source}")
        else:
            self.plot_source = ""
            print("No plot path available.")

        self.stats = stats_data
        self.chart_data = chart_data  # Store the chart data
        
        self.is_loading = False
        print(f"Stats updated: {self.stats}")
        print(f"Chart data: {self.chart_data}")
        print(f"Is Loading: {self.is_loading}")

    def go_back(self):
        if self.manager:
            self.manager.current = 'main'