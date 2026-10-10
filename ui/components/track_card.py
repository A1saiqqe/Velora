import customtkinter as ctk
from ui.theme import colors, spacing, typography

class TrackCard(ctk.CTkFrame):
    def __init__(self, parent, title="Track title", artist="Artist", duration="0:00", active=False, command=None):
        self.active = active
        self.command = command

        super().__init__(parent, height=64, fg_color=(colors.ACCENT_SOFT if active else "transparent"), corner_radius=12)

        self.pack_propagate(False)
        self.title_text = title
        self.artist_text = artist
        self.duration_text = duration
        self.create_card()
        self.bind_click()

    def create_card(self):
        self.artwork = ctk.CTkFrame(self, width=44, height=44, fg_color=colors.SURFACE_2, corner_radius=8)
        self.artwork.pack_propagate(False)
        self.artwork.pack(side="left", padx=(spacing.SM, spacing.MD), pady=spacing.SM)
        self.artwork_label = ctk.CTkLabel(self.artwork, text="♪", text_color=colors.TEXT_MUTED, font=(typography.FONT_FAMILY, 16))
        self.artwork_label.place(relx=0.5, rely=0.5, anchor="center")

        self.info = ctk.CTkFrame(self, fg_color="transparent")
        self.info.pack(side="left", fill="both", expand=True, pady=spacing.SM)

        self.title_label = ctk.CTkLabel(self.info, text=self.title_text, text_color=colors.TEXT_PRIMARY, font=(typography.FONT_FAMILY, typography.BODY_SIZE), anchor="w")
        self.title_label.pack(fill="x")

        self.artist_label = ctk.CTkLabel(self.info,text=self.artist_text, text_color=colors.TEXT_SECONDARY, font=(typography.FONT_FAMILY, typography.SMALL_SIZE), anchor="w")
        self.artist_label.pack(fill="x")

        self.duration_label = ctk.CTkLabel(self, text=self.duration_text, text_color=colors.TEXT_MUTED, font=(typography.FONT_FAMILY, typography.SMALL_SIZE))
        self.duration_label.pack(side="right", padx=spacing.MD)

    def bind_click(self):
        widgets = [
            self,
            self.artwork,
            self.artwork_label,
            self.info,
            self.title_label,
            self.artist_label,
            self.duration_label
        ]

        for widget in widgets:
            widget.bind("<Button-1>", self.on_click)

    def on_click(self, event=None):
        if self.command:
            self.command(self.title_text, self.artist_text)