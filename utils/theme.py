# Define color palettes for light and dark themes
light_theme = {
    "bg_color": [1, 1, 1, 1],
    "text_color": [0, 0, 0, 1],
    "secondary_text": [0.3, 0.3, 0.3, 1], # Added: Darker grey for light theme
    "primary_color": [0.2, 0.6, 0.8, 1], # Blueish
    "secondary_color": [0.95, 0.95, 0.95, 1], # Light grey
    "accent_color": [0.2, 0.8, 0.6, 1], # Greenish
    "error_color": [0.8, 0.2, 0.2, 1], # Reddish
    "list_item_bg": [1, 1, 1, 1],
    "button_text": [1, 1, 1, 1],
}

dark_theme = {
    "bg_color": [0.1, 0.1, 0.1, 1],
    "text_color": [1, 1, 1, 1],
    "secondary_text": [0.7, 0.7, 0.7, 1], # Added: Lighter grey for dark theme
    "primary_color": [0.2, 0.6, 0.8, 1], # Keep primary same or adjust
    "secondary_color": [0.2, 0.2, 0.2, 1], # Dark grey
    "accent_color": [0.2, 0.8, 0.6, 1], # Keep accent same or adjust
    "error_color": [0.8, 0.2, 0.2, 1], # Keep error same or adjust
    "list_item_bg": [0.15, 0.15, 0.15, 1],
    "button_text": [1, 1, 1, 1],
}

def get_color(theme, key):
    """Helper function to get color based on theme"""
    if theme == "light":
        # Return secondary_text if key is missing, otherwise default to black
        return light_theme.get(key, light_theme.get("secondary_text", [0,0,0,1]))
    else:
        # Return secondary_text if key is missing, otherwise default to white
        return dark_theme.get(key, dark_theme.get("secondary_text", [1,1,1,1]))
