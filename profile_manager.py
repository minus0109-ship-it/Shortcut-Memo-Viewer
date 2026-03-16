import os
import json
import shutil

PROFILE_DIR = "profiles"

def get_profiles():
    if not os.path.exists(PROFILE_DIR):
        os.makedirs(PROFILE_DIR)
    return [f for f in os.listdir(PROFILE_DIR) if f.endswith('.json')]

def create_profile(name):
    filepath = os.path.join(PROFILE_DIR, f"{name}.json")
    if not os.path.exists(filepath):
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump({"metadata": {"app_name": name}, "shortcuts": []}, f, indent=4)
        return True
    return False

def delete_profile(name):
    filepath = os.path.join(PROFILE_DIR, f"{name}.json")
    if os.path.exists(filepath):
        os.remove(filepath)
        return True
    return False

def export_profile(name, dest_path):
    src = os.path.join(PROFILE_DIR, f"{name}.json")
    if os.path.exists(src):
        shutil.copy(src, dest_path)
        return True
    return False