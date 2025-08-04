import os
import random
import threading
import time
import urllib.parse
import ctypes
import requests
import tkinter as tk
from tkinter import ttk
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from PIL import Image
import pystray
import sys
import json
from datetime import datetime, timedelta

# -------------------- Wallpaper Functions --------------------
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
        response = requests.get(url, stream=True)
        response.raise_for_status()
        with open(filename, "wb") as f:
            for chunk in response.iter_content(1024):
                f.write(chunk)
        return os.path.abspath(filename)
    except Exception as e:
        raise Exception(f"Image download failed: {e}")

def set_wallpaper(image_path):
    image_path = os.path.abspath(image_path)
    result = ctypes.windll.user32.SystemParametersInfoW(20, 0, image_path, 3)
    if not result:
        raise Exception("Failed to set wallpaper")

# -------------------- Settings File Handling --------------------
SETTINGS_FILE = "../settings.json"

def load_settings():
    try:
        if os.path.exists(SETTINGS_FILE):
            with open(SETTINGS_FILE, "r") as f:
                return json.load(f)
    except:
        pass
    return {}

def save_settings(data):
    try:
        with open(SETTINGS_FILE, "w") as f:
            json.dump(data, f, indent=4)
    except:
        pass

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

# -------------------- GUI Class --------------------
class WallpaperApp:
    def __init__(self, root):
        self.root = root
        self.root.title("AI Wallpaper Generator")
        self.auto_refresh_enabled = False

        self.styles = ["Random", "neon", "synthwave", "dreamy", "fantasy", "cyberpunk", "lowpoly", "oil painting", "sketch"]
        self.descriptors = ["Random", "dusk", "sunset", "fog", "crystals", "city", "galaxy", "alien landscape"]

        self.selected_style = tk.StringVar()
        self.selected_descriptor = tk.StringVar()
        self.status_var = tk.StringVar(value="Ready")
        self.interval_var = tk.IntVar(value=30)
        self.selected_category = tk.StringVar()
        self.prompt_entry = ttk.Entry(root, width=50)
        self.tray_icon = None
        self.prompts_data = self.load_prompts()

        self.category_list = ["Random"] + sorted(list(self.prompts_data.keys()))
        if self.category_list:
            self.selected_category.set(self.category_list[0])

        self.load_previous_settings()
        self.setup_gui()
        self.create_tray_icon()
        self.root.protocol("WM_DELETE_WINDOW", self.hide_window)

        self.root.withdraw()
        self.check_and_refresh_on_launch()

        # Start auto-refresh if it was previously enabled
        if self.auto_refresh_enabled:
            self.status_var.set("Auto-refresh resumed.")
            threading.Thread(target=self.auto_refresh_loop, daemon=True).start()

    def load_prompts(self):
        try:
            with open("../prompts.json", "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            self.status_var.set(f"Failed to load prompts.json: {e}")
            return {}

    def load_previous_settings(self):
        settings = load_settings()
        self.selected_style.set(settings.get("selected_style", self.styles[0]))
        self.selected_descriptor.set(settings.get("selected_descriptor", self.descriptors[0]))
        self.selected_category.set(settings.get("selected_category", self.category_list[0]))
        self.interval_var.set(settings.get("interval_minutes", 30))
        self.auto_refresh_enabled = settings.get("auto_refresh_enabled", False)

    def save_current_settings(self):
        settings = load_settings()
        settings.update({
            "selected_style": self.selected_style.get(),
            "selected_descriptor": self.selected_descriptor.get(),
            "selected_category": self.selected_category.get(),
            "interval_minutes": self.interval_var.get(),
            "auto_refresh_enabled": self.auto_refresh_enabled
        })
        save_settings(settings)

    def check_and_refresh_on_launch(self):
        try:
            settings = load_settings()
            next_time_str = settings.get("next_update_time")
            if next_time_str:
                next_time = datetime.strptime(next_time_str, "%Y-%m-%d %H:%M:%S")
                if datetime.now() >= next_time:
                    self.run(force_time=next_time)
                    return
            self.status_var.set(f"Ready. Next update: {next_time_str}")
        except Exception as e:
            self.status_var.set(f"Ready (Check failed): {e}")

    def setup_gui(self):
        ttk.Label(self.root, text="Prompt (leave blank for random):", font=("Segoe UI", 12)).pack(pady=(10, 2))
        self.prompt_entry.pack()

        ttk.Label(self.root, text="Category (used if prompt is blank):", font=("Segoe UI", 12)).pack(pady=(10, 2))
        self.category_dropdown = ttk.Combobox(self.root, textvariable=self.selected_category, values=self.category_list)
        self.category_dropdown.pack()

        ttk.Label(self.root, text="Style:", font=("Segoe UI", 12)).pack(pady=(10, 2))
        ttk.Combobox(self.root, textvariable=self.selected_style, values=self.styles).pack()

        ttk.Label(self.root, text="Descriptor:", font=("Segoe UI", 12)).pack(pady=(10, 2))
        ttk.Combobox(self.root, textvariable=self.selected_descriptor, values=self.descriptors).pack()

        ttk.Label(self.root, text="Auto Refresh Interval (min):", font=("Segoe UI", 12)).pack(pady=(10, 2))
        ttk.Entry(self.root, textvariable=self.interval_var, width=10).pack()

        ttk.Button(self.root, text="Generate Wallpaper", bootstyle=PRIMARY, command=self.run).pack(pady=5)
        ttk.Button(self.root, text="Toggle Auto-Refresh", bootstyle=INFO, command=self.toggle_auto_refresh).pack(pady=5)

        self.status_label = ttk.Label(self.root, textvariable=self.status_var, font=("Segoe UI", 10))
        self.status_label.pack(pady=10)

    def build_prompt(self):
        user_prompt = self.prompt_entry.get().strip()

        style = self.selected_style.get()
        if style == "Random":
            style = random.choice(self.styles[1:])

        desc = self.selected_descriptor.get()
        if desc == "Random":
            desc = random.choice(self.descriptors[1:])

        if user_prompt:
            return f"{user_prompt}, {desc}, {style} art"
        else:
            try:
                category = self.selected_category.get()
                if category == "Random":
                    valid_categories = list(self.prompts_data.keys())
                    if valid_categories:
                        category = random.choice(valid_categories)
                    else:
                        return f"surreal nature, {desc}, {style} art"
                prompts = self.prompts_data.get(category, [])
                if prompts:
                    return random.choice(prompts)
                else:
                    return f"unknown dreamscape, {desc}, {style} art"
            except Exception as e:
                self.status_var.set(f"Prompt error: {e}")
                return f"surreal nature, {desc}, {style} art"

    def run(self, force_time=None):
        try:
            self.save_current_settings()
            prompt = self.build_prompt()
            width, height = get_screen_resolution()
            url = url_builder(prompt, width, height)
            image_path = download_image(url)
            set_wallpaper(image_path)
            self.status_var.set("Wallpaper updated successfully.")
            update_next_refresh_file(self.interval_var.get(), base_time=force_time or datetime.now())
        except Exception as e:
            self.status_var.set(str(e))

    def toggle_auto_refresh(self):
        self.auto_refresh_enabled = not self.auto_refresh_enabled
        if self.auto_refresh_enabled:
            self.status_var.set("Auto-refresh started.")
            threading.Thread(target=self.auto_refresh_loop, daemon=True).start()
        else:
            self.status_var.set("Auto-refresh stopped.")
        self.save_current_settings()

    def auto_refresh_loop(self):
        while self.auto_refresh_enabled:
            self.run()
            interval_sec = self.interval_var.get() * 60
            for _ in range(interval_sec):
                if not self.auto_refresh_enabled:
                    return
                time.sleep(1)

    def hide_window(self):
        self.root.withdraw()

    def create_tray_icon(self):
        def on_exit(icon, item):
            # self.auto_refresh_enabled = False
            self.save_current_settings()
            icon.stop()
            self.root.quit()
            sys.exit()

        def show_window(icon, item):
            self.root.after(0, self.root.deiconify)

        image = Image.new("RGB", (64, 64), (40, 40, 40))
        menu = pystray.Menu(
            pystray.MenuItem("Show", show_window),
            pystray.MenuItem("Exit", on_exit)
        )
        self.tray_icon = pystray.Icon("AI Wallpaper", image, "Wallpaper AI", menu)
        threading.Thread(target=self.tray_icon.run, daemon=True).start()

# -------------------- Main --------------------
if __name__ == "__main__":
    app = tb.Window(themename="cyborg")
    app.geometry("420x520")
    WallpaperApp(app)
    app.mainloop()