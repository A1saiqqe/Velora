from pathlib import Path
import customtkinter as ctk
from config.paths import resource_dir
from PIL import Image


ICON_DIR = resource_dir() / "assets" / "icons"


def load_icon(name, size):
    icon_path = ICON_DIR / f"{name}.png"

    if not icon_path.exists():
        print(f"Icon not found: {icon_path}")
        return None

    image = Image.open(icon_path)

    return ctk.CTkImage(
        light_image=image,
        dark_image=image,
        size=(size, size)
    )