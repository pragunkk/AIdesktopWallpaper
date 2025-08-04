import os
import sys
import json
import time
import random
import threading
from datetime import datetime

import tkinter as tk
from tkinter import ttk


from PIL import Image


from wallpaper_utils import (
    get_screen_resolution, url_builder, download_image, set_wallpaper,
    load_settings, save_settings, update_next_refresh_file
)

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
    Otherwise, returns path to resource in install dir (for static files like prompts.json).
    """
    if user_data:
        return os.path.join(get_appdata_dir(), filename)
    if hasattr(sys, '_MEIPASS'):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, filename)

class WallpaperApp:
    def __init__(self, root):
        self.root = root
        self.root.title("AI Wallpaper Generator")
        self.auto_refresh_enabled = False

        # SET WINDOW SIZE
        self.root.geometry("600x580")
        self.root.minsize(500, 500)



        # FONT SETTING
        self.font_family = "Segoe UI Variable Text"

        # STYLES AND DESCRIPTORS
        self.styles = ["Random", "neon", "synthwave", "dreamy", "fantasy", "cyberpunk", "lowpoly", 
        "oil painting", "sketch", "vaporwave", "retrofuturism", "dark fantasy", "anime-style", 
        "pixel art", "photorealistic", "watercolor", "line art", "glitchcore", "minimalist", 
        "steampunk", "gothic", "concept art", "dreamcore", "hyperrealism", "mosaic"
    ]
        self.descriptors = ["Random", "dusk", "sunset", "fog", "crystals", "city", "galaxy", "alien landscape", 
        "northern lights", "celestial", "rainy streets", "underwater world", "volcanic eruption", 
        "frozen tundra", "overgrown ruins", "infinite void", "parallel universe", "bioluminescence", 
        "mystic forest", "lunar surface", "haunted valley", "utopia", "dystopia", "time-lapse sky", 
        "electric storm", "floating islands", "neon jungle", "mirror dimension", "sacred temple"
        ]

        self.selected_style = tk.StringVar()
        self.selected_descriptor = tk.StringVar()
        self.status_var = tk.StringVar(value="Ready")
        self.interval_var = tk.IntVar(value=30)
        self.selected_category = tk.StringVar()
        self.prompt_entry = ttk.Entry(root, width=50)
        self.prompts_data = self.load_prompts()

        self.category_list = ["Random"] + sorted(list(self.prompts_data.keys()))
        if self.category_list:
            self.selected_category.set(self.category_list[0])

        self.load_previous_settings()
        self.setup_gui()
        self.show_window_flag = False
        self.root.after(500, self.check_show_window_flag)
        self.root.protocol("WM_DELETE_WINDOW", self.hide_window)
        # self.root.withdraw()  # Only withdraw if running from tray, not on direct launch
        self.check_and_refresh_on_launch()
        if self.auto_refresh_enabled:
            self.status_var.set("Auto-refresh resumed.")
            threading.Thread(target=self.auto_refresh_loop, daemon=True).start()

    def check_show_window_flag(self):
        if self.show_window_flag:
            self.root.deiconify()
            self.show_window_flag = False
        self.root.after(500, self.check_show_window_flag)

    def load_prompts(self):
        try:
            with open(get_resource_path("prompts.json"), "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            self.status_var.set(f"Failed to load prompts.json: {e}")
            return {}

    def load_previous_settings(self):
        settings = self.load_settings()
        self.selected_style.set(settings.get("selected_style", self.styles[0]))
        self.selected_descriptor.set(settings.get("selected_descriptor", self.descriptors[0]))
        self.selected_category.set(settings.get("selected_category", self.category_list[0]))
        self.interval_var.set(settings.get("interval_minutes", 30))
        self.auto_refresh_enabled = settings.get("auto_refresh_enabled", False)

    def save_current_settings(self):
        settings = self.load_settings()
        settings.update({
            "selected_style": self.selected_style.get(),
            "selected_descriptor": self.selected_descriptor.get(),
            "selected_category": self.selected_category.get(),
            "interval_minutes": self.interval_var.get(),
            "auto_refresh_enabled": self.auto_refresh_enabled
        })
        self.save_settings(settings)

    def load_settings(self):
        try:
            settings_path = get_resource_path("settings.json", user_data=True)
            if os.path.exists(settings_path):
                with open(settings_path, "r") as f:
                    return json.load(f)
        except Exception as e:
            self.status_var.set(f"Error loading settings: {e}")
        return {}

    def save_settings(self, data):
        try:
            settings_path = get_resource_path("settings.json", user_data=True)
            with open(settings_path, "w") as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            self.status_var.set(f"Error saving settings: {e}")

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
        style = ttk.Style()
        style.configure("TLabel", font=(self.font_family, 12), padding=5)
        style.configure("TEntry", padding=5)
        style.configure("TButton", font=(self.font_family, 11), padding=6)
        style.configure("TCombobox", padding=5)
        style.configure("TFrame")

        frame = ttk.Frame(self.root, padding=20)
        frame.pack(fill="both", expand=True)

        ttk.Label(frame, text="Prompt (leave blank for random):").pack(pady=(5, 2))
        self.prompt_entry = ttk.Entry(frame, font=(self.font_family, 11), width=50)
        self.prompt_entry.pack(pady=(0, 10))

        ttk.Label(frame, text="Category (used if prompt is blank):").pack(pady=(5, 2))
        self.category_dropdown = ttk.Combobox(frame, textvariable=self.selected_category, values=self.category_list, font=(self.font_family, 11))
        self.category_dropdown.pack(pady=(0, 10))

        ttk.Label(frame, text="Style:").pack(pady=(5, 2))
        ttk.Combobox(frame, textvariable=self.selected_style, values=self.styles, font=(self.font_family, 11)).pack(pady=(0, 10))

        ttk.Label(frame, text="Descriptor:").pack(pady=(5, 2))
        ttk.Combobox(frame, textvariable=self.selected_descriptor, values=self.descriptors, font=(self.font_family, 11)).pack(pady=(0, 10))

        ttk.Label(frame, text="Auto Refresh Interval (min):").pack(pady=(5, 2))
        ttk.Entry(frame, textvariable=self.interval_var, font=(self.font_family, 11), width=10).pack(pady=(0, 10))

        ttk.Button(frame, text="Generate Wallpaper", command=self.run).pack(pady=5)
        ttk.Button(frame, text="Toggle Auto-Refresh", command=self.toggle_auto_refresh).pack(pady=5)

        self.status_label = ttk.Label(frame, textvariable=self.status_var, font=(self.font_family, 10))
        self.status_label.pack(pady=15)

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



if __name__ == "__main__":
    import tkinter as tk
    app = tk.Tk()
    WallpaperApp(app)
    app.mainloop()