import tkinter as tk
import sys
import os

# Make sure imports work when running from /src
sys.path.insert(0, os.path.dirname(__file__))

import database as db
from user_interface import UserInterface


def center_window(root):
    """Centers the window on the screen before showing it."""
    root.update_idletasks()
    width  = root.winfo_width()
    height = root.winfo_height()
    screen_w = root.winfo_screenwidth()
    screen_h = root.winfo_screenheight()
    x = (screen_w - width) // 2
    y = (screen_h - height) // 2
    root.geometry(f"{width}x{height}+{x}+{y}")


if __name__ == "__main__":
    # Initialize the database and creates tables if they don't exist
    db.init_db()

    root = tk.Tk()

    assets_dir = os.path.join(os.path.dirname(__file__), '..', 'assets')
    icon_path  = os.path.join(assets_dir, 'comedor.ico')
    if os.path.exists(icon_path):
        root.iconbitmap(icon_path)

    app = UserInterface(root)

    # Maximize window (works on Windows; on Linux use 'zoomed' or geometry)
    try:
        root.state("zoomed")
    except tk.TclError:
        root.attributes('-zoomed', True)

    center_window(root)
    root.mainloop()
