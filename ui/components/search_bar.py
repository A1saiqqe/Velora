import customtkinter as ctk

from ui.theme import colors, spacing, typography
from ui.components.icon import load_icon


class SearchBar(ctk.CTkFrame):
    def __init__(self, parent, on_search=None):
        super().__init__(parent, fg_color="transparent")
        self.on_search = on_search
        self.create_search()

    def create_search(self):
        self.search_surface = ctk.CTkFrame(
            self, fg_color=colors.SURFACE_2, corner_radius=22,
            border_width=1, border_color=colors.BORDER, height=44,
        )
        self.search_surface.pack(fill="x", expand=True, padx=spacing.LG, pady=spacing.MD)
        self.search_surface.pack_propagate(False)
        icon = load_icon("search", 18)
        self.search_icon = ctk.CTkLabel(
            self.search_surface, text="" if icon else "⌕", image=icon,
            text_color=colors.TEXT_SECONDARY, width=34,
        )
        self.search_icon.pack(side="left", padx=(spacing.SM, 0), pady=spacing.XS)
        self.search_entry = ctk.CTkEntry(
            self.search_surface, height=38,
            placeholder_text="Search music, artists, albums...",
            fg_color="transparent", border_width=0,
            text_color=colors.TEXT_PRIMARY, placeholder_text_color=colors.TEXT_MUTED,
            corner_radius=18, font=(typography.FONT_FAMILY, typography.BODY_SIZE),
        )
        self.search_entry.pack(side="left", fill="both", expand=True, padx=(spacing.XS, spacing.MD), pady=2)
        self.search_entry._entry.bind("<KeyRelease>", self.text_key)
        self.search_entry._entry.bind("<Return>", self.submit_search)

    def text_key(self, _event=None):
        if self.on_search:
            self.on_search(self.search_entry.get())

    def submit_search(self, _event=None):
        self.text_key()
        return "break"
