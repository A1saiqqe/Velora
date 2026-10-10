import customtkinter as ctk
from ui.theme import colors, typography, spacing

class PlaceholderPage(ctk.CTkFrame):
    def __init__(self, parent, title):
        super().__init__(parent, fg_color=colors.BACKGROUND)
        self.title_label = ctk.CTkLabel(
            self,
            text=title,
            font=(typography.FONT_FAMILY, 28, "bold"),
            text_color=colors.TEXT_PRIMARY
        )
        self.title_label.pack(anchor="w", padx=spacing.XL, pady=spacing.XL)