from pathlib import Path
import customtkinter as ctk
from config.paths import resource_dir

FONT_DIR = resource_dir() / "assets" / "fonts"

FR_PRIVATE = 0x10

def register_fonts():
    fonts = [
        "Manrope-Regular.ttf",
        "Manrope-Medium.ttf",
        "Manrope-SemiBold.ttf",
        "Manrope-Bold.ttf"
    ]
    
    for font_name in fonts:
        font_path = FONT_DIR / font_name

        if not font_path.exists():
            print(f'Font not found: {font_path}')
            continue
        
        loaded = ctk.FontManager.load_font(str(font_path))

        if loaded:
            print(f"Font loaded: {font_name}")
        else:
            print(f"Could not load: {font_name}")