import os
import requests
import random
import urllib.parse
import ctypes

# ====== NEW CONFIG SECTION ======
user_theme = "pizza slice on a china dish"  # This can be taken from user input (CLI, GUI, etc.)
styles = [
    "in the style of vaporwave",
    "neon futuristic",
    "cyberpunk vibes",
    "hyper-realistic 8K",
    "oil painting style",
    "digital matte painting",
    "sci-fi scene",
    "dreamy surreal"
]
descriptors = [
    "sunset", "stormy", "night time", "in winter", "with aurora",
    "during sunrise", "under starry sky", "on an alien planet"
]

def generate_unique_prompt(theme):
    return f"{theme}, {random.choice(descriptors)}, {random.choice(styles)}"
# =================================

def get_screen_resolution():
    user32 = ctypes.windll.user32
    user32.SetProcessDPIAware()
    width = user32.GetSystemMetrics(0)
    height = user32.GetSystemMetrics(1)
    return width, height

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

        print(f"Image saved as '{filename}' in {os.getcwd()}")
    except Exception as e:
        print(f"Failed to download image: {e}")

def set_wallpaper(image_path):
    image_path = os.path.abspath(image_path)
    result = ctypes.windll.user32.SystemParametersInfoW(20, 0, image_path, 3)
    if result:
        print(f"Wallpaper set successfully to: {image_path}")
    else:
        print("Failed to set wallpaper.")

# ==== MAIN LOGIC ====
width, height = get_screen_resolution()
prompt = generate_unique_prompt(user_theme)
print(f"Generated Prompt: {prompt}")
image_url = urlBuilder(prompt, width, height)
download_image(image_url)
set_wallpaper("../downloaded_image.jpg")
