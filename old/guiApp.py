import os
import random
import urllib.parse
import ctypes
import requests
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import StringVar

# === Prompt Variants ===
styles = [
    "Random", "in the style of vaporwave", "neon futuristic", "cyberpunk vibes",
    "hyper-realistic 8K", "oil painting style", "digital matte painting",
    "sci-fi scene", "dreamy surreal"
]

descriptors = [
    "Random", "sunset", "stormy", "night time", "in winter", "with aurora",
    "during sunrise", "under starry sky", "on an alien planet"
]

def get_screen_resolution():
    user32 = ctypes.windll.user32
    user32.SetProcessDPIAware()
    width = user32.GetSystemMetrics(0)
    height = user32.GetSystemMetrics(1)
    return width, height

def generate_unique_prompt(theme, descriptor, style):
    desc = random.choice(descriptors[1:]) if descriptor == "Random" else descriptor
    styl = random.choice(styles[1:]) if style == "Random" else style
    return f"{theme}, {desc}, {styl}"

def url_encode(text):
    return urllib.parse.quote(text)

def urlBuilder(prompt, width, height):
    return (
        "https://image.pollinations.ai/prompt/"
        + url_encode(prompt)
        + "%2C%20style%20realistic%2C%20aspect%20ratio%2016%3A9"
        + "?width="
        + str(width)
        + "&height="
        + str(height)
        + "&seed="
        + str(random.randrange(10000, 99999))
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
        return None

def set_wallpaper(image_path):
    result = ctypes.windll.user32.SystemParametersInfoW(20, 0, image_path, 3)
    return result

# === GUI APP ===
class WallpaperApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Dynamic AI Wallpaper Generator")
        self.root.geometry("650x380")
        self.theme_var = StringVar()
        self.style_var = StringVar(value="Random")
        self.desc_var = StringVar(value="Random")
        self.status_var = StringVar(value="Enter a theme and click Generate")

        ttk.Label(root, text="Wallpaper Theme:", font=("Segoe UI", 14)).pack(pady=(10, 5))
        ttk.Entry(root, textvariable=self.theme_var, font=("Segoe UI", 12), width=45).pack(pady=5)

        # Descriptor dropdown
        ttk.Label(root, text="Choose Mood/Time (Descriptor):", font=("Segoe UI", 12)).pack(pady=(10, 2))
        self.desc_menu = ttk.Combobox(root, values=descriptors, textvariable=self.desc_var, font=("Segoe UI", 10), width=40)
        self.desc_menu.pack()

        # Style dropdown
        ttk.Label(root, text="Choose Art Style:", font=("Segoe UI", 12)).pack(pady=(10, 2))
        self.style_menu = ttk.Combobox(root, values=styles, textvariable=self.style_var, font=("Segoe UI", 10), width=40)
        self.style_menu.pack()

        # Button
        ttk.Button(root, text="Generate & Set Wallpaper", bootstyle=SUCCESS, command=self.run).pack(pady=20)

        # Status
        ttk.Label(root, textvariable=self.status_var, font=("Segoe UI", 10)).pack(pady=10)

    def run(self):
        theme = self.theme_var.get().strip()
        if not theme:
            self.status_var.set("Please enter a theme first.")
            return

        desc = self.desc_var.get()
        style = self.style_var.get()
        prompt = generate_unique_prompt(theme, desc, style)
        width, height = get_screen_resolution()

        self.status_var.set("Generating image...")
        self.root.update()

        url = urlBuilder(prompt, width, height)
        path = download_image(url)
        if path:
            if set_wallpaper(path):
                self.status_var.set(f"Wallpaper set! Prompt: {prompt}")
            else:
                self.status_var.set("Failed to set wallpaper.")
        else:
            self.status_var.set("Failed to download image.")

# === Start GUI ===
if __name__ == "__main__":
    app = ttk.Window(themename="cyborg")  # Try: solar, superhero, darkly, morph
    WallpaperApp(app)
    app.mainloop()
