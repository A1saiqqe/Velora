import customtkinter as ctk

from ui.theme import colors, spacing, typography


class TrackInfo(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        self.create_info()

    def create_info(self):
        self.title_label = ctk.CTkLabel(
            self, text="Nothing playing", text_color=colors.TEXT_PRIMARY,
            font=(typography.FONT_FAMILY, typography.TRACK_TITLE_SIZE, "bold"),
            anchor="w", justify="left", wraplength=360,
        )
        self.title_label.pack(fill="x")
        self.artist_label = ctk.CTkLabel(
            self, text="Choose a track from your library", text_color=colors.TEXT_SECONDARY,
            font=(typography.FONT_FAMILY, typography.TRACK_ARTIST_SIZE),
            anchor="w", justify="left", wraplength=360,
        )
        self.artist_label.pack(fill="x", pady=(spacing.XS, 0))

    def set_track(self, title, artist):
        self.title_label.configure(text=title or "")
        self.artist_label.configure(text=artist or "")
