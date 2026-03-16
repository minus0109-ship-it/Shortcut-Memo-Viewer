import os
import json

SETTINGS_FILE = "settings.json"
DEFAULT_SETTINGS = {
    "base_color": "#f0f0f0",
    "press_color": "#ff7675",
    "saved_color": "#74b9ff",
    "multi_color": "#fdcb6e"
}

def load_settings():
    if not os.path.exists(SETTINGS_FILE):
        save_settings(DEFAULT_SETTINGS)
        return DEFAULT_SETTINGS
    with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_settings(settings):
    with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
        json.dump(settings, f, indent=4)