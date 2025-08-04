# main.py


import tkinter as tk
from wallpaper_gui import WallpaperApp

if __name__ == "__main__":
    app = tk.Tk()
    app.geometry("420x520")
    WallpaperApp(app)
    app.mainloop()
