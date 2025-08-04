import subprocess
from PIL import Image
import pystray
import threading
import sys
import os
import random
import urllib.parse
import ctypes
import requests
import json
from datetime import datetime, timedelta

# --- Resource path logic for data files ---
def get_appdata_dir():
    # Use %APPDATA%/AI Wallpaper App for user data
    if os.name == 'nt':
        base = os.environ.get('APPDATA', os.path.expanduser('~'))
    else:
        base = os.path.expanduser('~')
    appdata_dir = os.path.join(base, 'AI Wallpaper App')
    if not os.path.exists(appdata_dir):
        os.makedirs(appdata_dir, exist_ok=True)
    return appdata_dir

def get_resource_path(filename, user_data=False):
    """
    If user_data=True, returns path in user-writable appdata dir.
    Otherwise, returns path to resource in install dir (for static files like icon.ico).
    """
    if user_data:
        return os.path.join(get_appdata_dir(), filename)
    if hasattr(sys, '_MEIPASS'):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, filename)

SETTINGS_FILE = "settings.json"

def start_tray_icon(on_show, on_exit):
    """
    Starts the system tray icon.
    :param on_show: Function to call when 'Show' is clicked.
    :param on_exit: Function to call when 'Exit' is clicked.
    """
    def _on_exit(icon, item):
        on_exit()
        icon.stop()
        sys.exit()

    def _on_show(icon, item):
        on_show()

    # image = Image.new("RGB", (64, 64), (40, 40, 40))
    image = Image.open(get_resource_path("icon.ico"))
    menu = pystray.Menu(
        pystray.MenuItem("Show", _on_show),
        pystray.MenuItem("Exit", _on_exit)
    )
    tray_icon = pystray.Icon("AI Wallpaper", image, "Wallpaper AI", menu)
    threading.Thread(target=tray_icon.run, daemon=True).start()
    return tray_icon


# wallpaper_utils.py

import os
import random
import urllib.parse
import ctypes
import requests
import json
from datetime import datetime, timedelta
from time import sleep

# --- Resource path logic for data files ---
def get_appdata_dir():
    # Use %APPDATA%/AI Wallpaper App for user data
    if os.name == 'nt':
        base = os.environ.get('APPDATA', os.path.expanduser('~'))
    else:
        base = os.path.expanduser('~')
    appdata_dir = os.path.join(base, 'AI Wallpaper App')
    if not os.path.exists(appdata_dir):
        os.makedirs(appdata_dir, exist_ok=True)
    return appdata_dir

def get_resource_path(filename, user_data=False):
    """
    If user_data=True, returns path in user-writable appdata dir.
    Otherwise, returns path to resource in install dir (for static files like icon.ico).
    """
    if user_data:
        return os.path.join(get_appdata_dir(), filename)
    if hasattr(sys, '_MEIPASS'):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, filename)

SETTINGS_FILE = "settings.json"

def get_screen_resolution():
    user32 = ctypes.windll.user32
    user32.SetProcessDPIAware()
    return user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)

def url_encode(text):
    return urllib.parse.quote(text)

def url_builder(prompt, width, height):
    base_prompt = f"{prompt}, style realistic, aspect ratio 16:9"
    return (
        "https://image.pollinations.ai/prompt/"
        + url_encode(base_prompt)
        + f"?width={width}&height={height}"
        + f"&seed={random.randint(10000,99999)}"
        + "&model=flux&nologo=true&private=false&enhance=false&safe=true"
    )

def download_image(url, filename="downloaded_image.jpg"):
    try:
        # Always save downloaded images to user-writable appdata dir
        out_path = get_resource_path(filename, user_data=True)
        response = requests.get(url, stream=True)
        response.raise_for_status()
        with open(out_path, "wb") as f:
            for chunk in response.iter_content(1024):
                f.write(chunk)
        return out_path
    except Exception as e:
        raise Exception(f"Image download failed: {e}")

def set_wallpaper(image_path):
    image_path = os.path.abspath(image_path)
    result = ctypes.windll.user32.SystemParametersInfoW(20, 0, image_path, 3)
    if not result:
        raise Exception("Failed to set wallpaper")

def load_settings():
    try:
        settings_path = get_resource_path(SETTINGS_FILE, user_data=True)
        if os.path.exists(settings_path):
            with open(settings_path, "r") as f:
                return json.load(f)
    except Exception as e:
        print(f"Error loading settings: {e}")
    return {}

def save_settings(data):
    try:
        settings_path = get_resource_path(SETTINGS_FILE, user_data=True)
        with open(settings_path, "w") as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        print(f"Error saving settings: {e}")

def update_next_refresh_file(minutes_ahead, base_time=None):
    try:
        if base_time is None:
            base_time = datetime.now()
        next_time = base_time + timedelta(minutes=minutes_ahead)
        settings = load_settings()
        settings["next_update_time"] = next_time.strftime("%Y-%m-%d %H:%M:%S")
        save_settings(settings)
    except:
        pass

def read_next_refresh_file():
    try:
        settings = load_settings()
        return settings.get("next_update_time", "Not yet scheduled")
    except:
        return "Not yet scheduled"

def load_prompts():
    try:
        with open(get_resource_path("prompts.json"), "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Failed to load prompts.json: {e}")
        return {}

# --- Prompt builder logic (copied from wallpaper_gui.py) ---
def build_prompt(settings, prompts_data):
    user_prompt = settings.get("last_prompt", "").strip()
    styles = [
        "Random", "neon", "synthwave", "dreamy", "fantasy", "cyberpunk", "lowpoly", 
        "oil painting", "sketch", "vaporwave", "retrofuturism", "dark fantasy", "anime-style", 
        "pixel art", "photorealistic", "watercolor", "line art", "glitchcore", "minimalist", 
        "steampunk", "gothic", "concept art", "dreamcore", "hyperrealism", "mosaic"
    ]

    descriptors = [
        "Random", "dusk", "sunset", "fog", "crystals", "city", "galaxy", "alien landscape", 
        "northern lights", "celestial", "rainy streets", "underwater world", "volcanic eruption", 
        "frozen tundra", "overgrown ruins", "infinite void", "parallel universe", "bioluminescence", 
        "mystic forest", "lunar surface", "haunted valley", "utopia", "dystopia", "time-lapse sky", 
        "electric storm", "floating islands", "neon jungle", "mirror dimension", "sacred temple"
        ]

    style = settings.get("selected_style", styles[0])
    if style == "Random":
        style = random.choice(styles[1:])
    desc = settings.get("selected_descriptor", descriptors[0])
    if desc == "Random":
        desc = random.choice(descriptors[1:])
    if user_prompt:
        return f"{user_prompt}, {desc}, {style} art"
    else:
        try:
            category = settings.get("selected_category", "Random")
            category_list = ["Random"] + sorted(list(prompts_data.keys()))
            if category == "Random":
                valid_categories = list(prompts_data.keys())
                if valid_categories:
                    category = random.choice(valid_categories)
                else:
                    return f"surreal nature, {desc}, {style} art"
            prompts = prompts_data.get(category, [])
            if prompts:
                return random.choice(prompts)
            else:
                return f"unknown dreamscape, {desc}, {style} art"
        except Exception as e:
            print(f"Prompt error: {e}")
            return f"surreal nature, {desc}, {style} art"

def auto_refresh_loop():
    prompts_data = load_prompts()
    while True:
        settings = load_settings()
        interval = settings.get("interval_minutes", 30)
        auto_refresh = settings.get("auto_refresh_enabled", False)
        if auto_refresh:
            try:
                prompt = build_prompt(settings, prompts_data)
                width, height = get_screen_resolution()
                url = url_builder(prompt, width, height)
                image_path = download_image(url)
                set_wallpaper(image_path)
                update_next_refresh_file(interval)
            except Exception as e:
                print(f"Auto-refresh error: {e}")
        # Sleep for interval minutes if enabled, else check every 60s
        sleep_time = interval * 60 if auto_refresh else 60
        for _ in range(sleep_time):
            # Allow for quick exit if process is killed
            threading.Event().wait(1)


# --- Standalone tray entry point ---
if __name__ == "__main__":
    def launch_gui():
        import os
        base_dir = os.path.dirname(os.path.abspath(__file__))
        exe_path = "../wallpaper_gui/wallpaper_gui.exe"
        py_path = os.path.join(base_dir, "wallpaper_gui.py")
        try:
            if os.path.exists(exe_path):
                print(f"Launching EXE: {exe_path}")
                subprocess.Popen([exe_path], cwd=base_dir)
            elif os.path.exists(py_path):
                print(f"Launching PY: {py_path}")
                subprocess.Popen([sys.executable, py_path], cwd=base_dir)
            else:
                print(f"Neither {exe_path} nor {py_path} found!")
        except Exception as e:
            print(f"Error launching GUI: {e}")

    def on_show():
        launch_gui()

    def on_exit():
        import os
        os._exit(0)

    # Start auto-refresh in background
    threading.Thread(target=auto_refresh_loop, daemon=True).start()
    start_tray_icon(on_show, on_exit)
    # Keep the script running so the tray icon stays alive
    threading.Event().wait()
