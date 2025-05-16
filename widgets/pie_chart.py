from kivy.uix.widget import Widget
from kivy.properties import ListProperty, NumericProperty, StringProperty, ListProperty
from kivy.graphics import Color, Ellipse, Line, Rectangle
from kivy.metrics import dp
from math import pi, cos, sin
from kivy.app import App
from utils.theme import get_color
from kivy.graphics import PushMatrix, PopMatrix, Translate, Scale
from kivy.core.text import Label as CoreLabel

class PieChart(Widget):
    data_values = ListProperty([])  # Values to chart (e.g., [100, 200])
    data_labels = ListProperty([])  # Labels for segments (e.g., ["Income", "Expenses"])
    data_colors = ListProperty([])  # Colors for segments
    inner_radius_ratio = NumericProperty(0.0)  # For donut chart if > 0
    title = StringProperty('')
    
    def __init__(self, **kwargs):
        super(PieChart, self).__init__(**kwargs)
        self.bind(
            pos=self.update_chart,
            size=self.update_chart,
            data_values=self.update_chart,
            data_colors=self.update_chart
        )
    
    def update_chart(self, *args):
        self.canvas.clear()
        
        if not self.data_values or sum(self.data_values) == 0:
            # Draw empty state or message
            with self.canvas:
                Color(0.7, 0.7, 0.7, 1)
                Rectangle(pos=self.pos, size=self.size)
                Color(0.3, 0.3, 0.3, 1)
                Line(rectangle=(self.x, self.y, self.width, self.height), width=1)
            return

        # Calculate chart dimensions
        center_x = self.center_x
        center_y = self.center_y
        radius = min(self.width, self.height) / 2.5
        inner_radius = radius * self.inner_radius_ratio
        
        # Calculate total for percentages
        total = sum(self.data_values)
        
        # Draw pie segments
        start_angle = 0
        for i, value in enumerate(self.data_values):
            if value <= 0:
                continue
                
            # Calculate angles
            angle = 360 * (value / total)
            end_angle = start_angle + angle
            
            # Draw segment
            with self.canvas:
                # Use provided color or default
                if i < len(self.data_colors):
                    Color(*self.data_colors[i])
                else:
                    # Default color cycle
                    Color(
                        (i * 0.5 + 0.2) % 1.0, 
                        (i * 0.3 + 0.7) % 1.0, 
                        (i * 0.8 + 0.4) % 1.0, 
                        1
                    )
                
                # Draw segment
                Ellipse(
                    pos=(center_x - radius, center_y - radius),
                    size=(radius * 2, radius * 2),
                    angle_start=start_angle,
                    angle_end=end_angle
                )
                
                # Draw inner circle for donut if needed
                if self.inner_radius_ratio > 0:
                    Color(1, 1, 1, 1)  # Inner circle color
                    Ellipse(
                        pos=(center_x - inner_radius, center_y - inner_radius),
                        size=(inner_radius * 2, inner_radius * 2)
                    )
            
            # Add percentage text at middle of segment
            mid_angle = start_angle + angle / 2
            text_radius = radius * 0.7
            text_x = center_x + text_radius * cos(mid_angle * pi / 180)
            text_y = center_y + text_radius * sin(mid_angle * pi / 180)
            
            # Update angle for next segment
            start_angle = end_angle
            
        # Draw legends if labels are provided
        if self.data_labels:
            legend_y = self.y + self.height - dp(20)
            square_size = dp(15)
            
            for i, label in enumerate(self.data_labels):
                if i >= len(self.data_values) or self.data_values[i] <= 0:
                    continue
                    
                with self.canvas:
                    # Legend color box
                    if i < len(self.data_colors):
                        Color(*self.data_colors[i])
                    else:
                        Color((i * 0.5 + 0.2) % 1.0, (i * 0.3 + 0.7) % 1.0, (i * 0.8 + 0.4) % 1.0, 1)
                        
                    Rectangle(
                        pos=(self.x + dp(10), legend_y - square_size),
                        size=(square_size, square_size)
                    )
                    
                    # Calculate percentage for label
                    percentage = 100 * self.data_values[i] / total
                    
                    # Add label with percentage - Theme aware text color
                    label_text = f"{label}: {percentage:.1f}%"
                    label = CoreLabel(text=label_text, font_size=dp(14))
                    label.refresh()
                    texture = label.texture
                    
                    # Use theme-aware text color instead of fixed black
                    try:
                        app = App.get_running_app()
                        if app and hasattr(app, 'theme'):
                            text_color = get_color(app.theme, "text_color")
                            Color(*text_color)
                        else:
                            # Fallback if app or theme not available
                            Color(0.9, 0.9, 0.9, 1) if self._is_dark_background() else Color(0.1, 0.1, 0.1, 1)
                    except Exception as e:
                        # Final fallback
                        print(f"Error getting theme color: {e}")
                        Color(0.9, 0.9, 0.9, 1)
                    
                    Rectangle(
                        pos=(self.x + dp(10) + square_size + dp(5), legend_y - square_size + (square_size - texture.height) / 2),
                        size=texture.size,
                        texture=texture
                    )
                
                # Move to next legend item position
                legend_y -= square_size + dp(10)
    
    def _is_dark_background(self):
        """Try to detect if we're on a dark background to decide text color"""
        try:
            app = App.get_running_app()
            if app and hasattr(app, 'theme'):
                bg_color = get_color(app.theme, "bg_color")
                # Simple luminance check
                luminance = 0.299 * bg_color[0] + 0.587 * bg_color[1] + 0.114 * bg_color[2]
                return luminance < 0.5
        except:
            pass
        return False
        
    def add_title(self):
        """Add title to the chart if set"""
        if not self.title:
            return
            
        with self.canvas:
            # Use theme-aware text color
            try:
                app = App.get_running_app()
                if app and hasattr(app, 'theme'):
                    text_color = get_color(app.theme, "text_color")
                    Color(*text_color)
                else:
                    # Fallback if app or theme not available
                    Color(0.9, 0.9, 0.9, 1) if self._is_dark_background() else Color(0.1, 0.1, 0.1, 1)
            except:
                # Final fallback
                Color(0.1, 0.1, 0.1, 1)
                
            title_label = CoreLabel(text=self.title, font_size=dp(16))
            title_label.refresh()
            title_texture = title_label.texture
            
            Rectangle(
                pos=(self.center_x - title_texture.width / 2, self.y + self.height - dp(30)),
                size=title_texture.size,
                texture=title_texture
            )