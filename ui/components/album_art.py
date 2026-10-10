from pathlib import Path

import customtkinter as ctk
from PIL import Image, ImageOps

from ui.theme import colors, typography


class AlbumArt(ctk.CTkFrame):
    """Artwork tile that keeps a reference to its CTkImage for Tk lifetime safety."""

    def __init__(self, parent, size=280):
        self.size = int(size)
        super().__init__(
            parent,
            width=self.size,
            height=self.size,
            fg_color=colors.SURFACE_2,
            corner_radius=16,
            border_width=1,
            border_color=colors.BORDER,
        )
        self.pack_propagate(False)
        self.image = None
        self.artwork_label = None
        self.create_placeholder()

    def create_placeholder(self):
        self.placeholder = ctk.CTkLabel(
            self,
            text="♫",
            text_color=colors.ACCENT,
            font=(typography.FONT_FAMILY, max(24, self.size // 3), "bold"),
        )
        self.placeholder.place(relx=0.5, rely=0.5, anchor="center")

    def set_artwork(self, artwork_path):
        path = Path(artwork_path) if artwork_path else None
        if path is None or not path.is_file():
            self.clear_artwork()
            return

        try:
            with Image.open(path) as source:
                image = ImageOps.fit(source.convert("RGB"), (self.size, self.size))
            self.image = ctk.CTkImage(light_image=image, dark_image=image, size=(self.size, self.size))
            self.placeholder.place_forget()
            if self.artwork_label is None or not self.artwork_label.winfo_exists():
                self.artwork_label = ctk.CTkLabel(self, text="", image=self.image)
                self.artwork_label.place(relx=0.5, rely=0.5, anchor="center")
            else:
                self.artwork_label.configure(image=self.image)
        except (OSError, ValueError):
            self.clear_artwork()

    def clear_artwork(self):
        if self.artwork_label is not None and self.artwork_label.winfo_exists():
            self.artwork_label.destroy()
        self.artwork_label = None
        self.image = None
        self.placeholder.place(relx=0.5, rely=0.5, anchor="center")
