import customtkinter as ctk

from ui.theme import colors, spacing, typography
from ui.components.icon import load_icon


class Sidebar(ctk.CTkFrame):
    def __init__(self, parent, on_page_change=None):
        super().__init__(parent, width=280, fg_color=colors.SURFACE, corner_radius=0)
        self.pack_propagate(False)
        self.on_page_change = on_page_change
        self.active_page = "home"
        self.buttons = {}
        self.create_brand()
        self.create_buttons()

    def create_brand(self):
        brand = ctk.CTkFrame(self, fg_color="transparent")
        brand.pack(fill="x", padx=spacing.LG, pady=(spacing.XL, spacing.LG))
        mark = ctk.CTkLabel(
            brand, text="V", width=38, height=38,
            fg_color=colors.ACCENT, corner_radius=12,
            text_color="#FFFFFF", font=(typography.FONT_FAMILY, 22, "bold"),
        )
        mark.pack(side="left", padx=(0, spacing.SM))
        text = ctk.CTkFrame(brand, fg_color="transparent")
        text.pack(side="left", fill="x", expand=True)
        ctk.CTkLabel(
            text, text="Velora", anchor="w", text_color=colors.TEXT_PRIMARY,
            font=(typography.FONT_FAMILY, 21, "bold"),
        ).pack(fill="x")
        ctk.CTkLabel(
            text, text="MUSIC PLAYER", anchor="w", text_color=colors.TEXT_MUTED,
            font=(typography.FONT_FAMILY, 9, "bold"),
        ).pack(fill="x", pady=(1, 0))

    def create_buttons(self):
        self.buttons["home"] = self.create_button("Home", "home", "home")
        self.buttons["library"] = self.create_button("Library", "library", "library")

        ctk.CTkLabel(
            self, text="COLLECTION", anchor="w", text_color=colors.TEXT_MUTED,
            font=(typography.FONT_FAMILY, 10, "bold"),
        ).pack(fill="x", padx=spacing.XL, pady=(spacing.LG, spacing.XS))
        self.buttons["playlists"] = self.create_button("Playlists", "playlists", "playlist")
        self.buttons["albums"] = self.create_button("Albums", "albums", "album")
        self.buttons["artists"] = self.create_button("Artists", "artists", "artist")
        self.buttons["genres"] = self.create_button("Genres", "genres", "album")
        self.buttons["folders"] = self.create_button("Folders", "folders", "folder")
        self.buttons["favorites"] = self.create_button("Favorites", "favorites", "heart")

        ctk.CTkFrame(self, height=1, fg_color=colors.BORDER).pack(fill="x", padx=spacing.LG, pady=spacing.LG)
        self.buttons["settings"] = self.create_button("Settings", "settings", "settings", bottom=True)

    def create_button(self, text, page, icon_name, bottom=False):
        button = ctk.CTkButton(
            self, text=text, image=load_icon(icon_name, 20), compound="left", anchor="w",
            width=244, height=44, fg_color=colors.ACCENT_SOFT if page == "home" else "transparent",
            hover_color=colors.SURFACE_HOVER,
            text_color=colors.TEXT_PRIMARY if page == "home" else colors.TEXT_SECONDARY,
            corner_radius=12, font=(typography.FONT_FAMILY, typography.BODY_SIZE),
            command=lambda: self.set_active(page),
        )
        button.pack(side="bottom" if bottom else "top", padx=spacing.MD,
                    pady=(spacing.LG, spacing.MD) if bottom else spacing.XS, fill="x")
        return button

    def set_active(self, page):
        if page not in self.buttons:
            return
        self.active_page = page
        for name, button in self.buttons.items():
            active = name == page
            button.configure(
                fg_color=colors.ACCENT_SOFT if active else "transparent",
                text_color=colors.TEXT_PRIMARY if active else colors.TEXT_SECONDARY,
            )
        if self.on_page_change:
            self.on_page_change(page)
