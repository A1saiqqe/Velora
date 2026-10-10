import customtkinter as ctk
from ui.theme import colors, spacing, typography
from models.track import Track
from ui.components.icon import load_icon

class LibraryPage(ctk.CTkFrame):
    def __init__(self, parent, tracks=None, on_track_selected=None, on_track_play=None, on_favorite_toggle=None, is_favorite=None):
        super().__init__(parent, fg_color=colors.BACKGROUND)
        self.all_tracks = list(tracks or [])
        self.tracks = list(self.all_tracks)
        self.on_track_selected = on_track_selected
        self.on_track_play = on_track_play
        self.on_favorite_toggle = on_favorite_toggle
        self.is_favorite = is_favorite or (lambda track: False)
        self.favorite_buttons = {}
        self.selected_track = None
        self.selected_index = None
        self.track_rows = {}
        self.play_buttons = {}
        self.create_header()
        self.create_list()

    def create_header(self):
        self.header = ctk.CTkFrame(self, fg_color="transparent")
        self.header.pack(fill="x", padx=spacing.XL, pady=spacing.XL)
        ctk.CTkLabel(
            self.header, text="Library",
            font=(typography.FONT_FAMILY, 28, "bold"),
            text_color=colors.TEXT_PRIMARY).pack(anchor="w")
        self.count_label = ctk.CTkLabel(
            self.header, text=f"{len(self.tracks)} tracks",
            font=(typography.FONT_FAMILY, typography.BODY_SIZE),
            text_color=colors.TEXT_MUTED)
        self.count_label.pack(anchor="w", pady=(spacing.XS, spacing.LG))

    def create_list(self):
        self.list_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.list_frame.pack(fill="both", expand=True, padx=spacing.XL, pady=(0, spacing.LG))
        self.list_frame.grid_columnconfigure(1, weight=5)
        self.list_frame.grid_columnconfigure(2, weight=3)
        self.list_frame.grid_columnconfigure(3, weight=1)
        self.list_frame.grid_columnconfigure(4, weight=0)

        headers = [
            ("№", 0, 45),
            ("Title", 1, 250),
            ("Artist", 2, 180),
            ("Duration", 3, 90),
            ("♡", 4, 44)
        ]

        for text, column, width in headers:
            ctk.CTkLabel(
                self.list_frame, text=text,
                width=width, anchor="w", text_color=colors.TEXT_MUTED,
                font=(typography.FONT_FAMILY, typography.BODY_SIZE)).grid(row=0, column=column, padx=spacing.SM, pady=(spacing.SM, spacing.LG), sticky="ew")

        if not self.tracks:
            ctk.CTkLabel(
                self.list_frame,
                text="No matches found" if self.all_tracks else "No music found yet", text_color=colors.TEXT_MUTED,
                font=(typography.FONT_FAMILY, typography.BODY_SIZE)).grid(row=1, column=0, columnspan=4, padx=spacing.SM, pady=spacing.LG, sticky="w")
            return

        for index, track in enumerate(self.tracks, start=1):
            self.create_track_row(index, track)

    def create_track_row(self, index, track):
        row = ctk.CTkFrame(self.list_frame, fg_color=colors.SURFACE, corner_radius=10)
        self.track_rows[index] = row
        row.grid(row=index, column=0, columnspan=5, sticky="ew", pady=3)
        row.grid_columnconfigure(1, weight=5)
        row.grid_columnconfigure(2, weight=3)
        row.grid_columnconfigure(3, weight=1)

        play_button = ctk.CTkButton(
            row,
            text="",
            width=45,
            height=44,
            fg_color="transparent",
            hover_color=colors.SURFACE_HOVER,
            text_color=colors.ACCENT,
            font=(typography.FONT_FAMILY, typography.BODY_SIZE),
            command=lambda item=track: self.play_track(item)
        )
        play_button.grid(row=0, column=0, padx=spacing.XS, sticky="ew")
        self.play_buttons[index] = play_button

        duration = getattr(track, "duration", 0) or 0
        try:
            duration = int(duration)
            duration_text = f"{duration // 60}:{duration % 60:02d}"
        except (TypeError, ValueError):
            duration_text = "—"

        values = [
            (track.title, 1, 250, colors.TEXT_PRIMARY),
            (track.artist, 2, 180, colors.TEXT_SECONDARY),
            (duration_text, 3, 90, colors.TEXT_MUTED)
        ]

        for text, column, width, color in values:
            ctk.CTkButton(
                row,
                text=text,
                width=width,
                height=44,
                anchor="w",
                fg_color="transparent",
                hover_color=colors.SURFACE_HOVER,
                text_color=color,
                font=(typography.FONT_FAMILY, typography.BODY_SIZE),
                command=lambda item=track, idx=index: self.select_track(item, idx)
            ).grid(row=0, column=column, padx=spacing.XS, sticky="ew")

        favorite_button = ctk.CTkButton(
            row,
            text="♥" if self.is_favorite(track) else "♡",
            width=44,
            height=44,
            fg_color="transparent",
            hover_color=colors.SURFACE_HOVER,
            text_color=colors.ACCENT if self.is_favorite(track) else colors.TEXT_MUTED,
            command=lambda item=track: self.toggle_favorite(item)
        )
        favorite_button.grid(row=0, column=4, padx=spacing.XS, sticky="ew")
        self.favorite_buttons[index] = favorite_button

    def select_track(self, track, index):
        self.selected_track = track
        self.selected_index = index
        self.update_track_highlight()
        if self.on_track_selected:
            self.on_track_selected(track)

    def update_track_highlight(self):
        for index, row in self.track_rows.items():
            row.configure(fg_color=colors.ACCENT_SOFT if index == self.selected_index else colors.SURFACE)

    def play_track(self, track):
        index = self.tracks.index(track) + 1
        self.selected_track = track
        self.selected_index = index
        self.update_track_highlight()
        if self.on_track_play:
            self.on_track_play(track)

    def update_play_buttons(self, current_track, is_playing):
        for index, button in self.play_buttons.items():
            track = self.tracks[index - 1]
            button.configure(image=load_icon("pause" if is_playing and track is current_track else "play", 18))

    def filter_tracks(self, query):
        query = (query or "").strip().casefold()
        self.tracks = [
            track for track in self.all_tracks
            if query in f"{track.title} {track.artist} {getattr(track, 'album', '')}".casefold()
        ]
        self.count_label.configure(
            text=f"{len(self.tracks)} of {len(self.all_tracks)} tracks"
            if query else f"{len(self.all_tracks)} tracks")
        if self.selected_track in self.tracks:
            self.selected_index = self.tracks.index(self.selected_track) + 1
        else:
            self.selected_track = None
            self.selected_index = None
        self.list_frame.destroy()
        self.track_rows = {}
        self.play_buttons = {}
        self.create_list()
        self.update_track_highlight()
        self.refresh_favorites()

    def toggle_favorite(self, track):
        if self.on_favorite_toggle:
            is_favorite = self.on_favorite_toggle(track)
            for index, item in enumerate(self.tracks, start=1):
                if item is track:
                    button = self.favorite_buttons.get(index)
                    if button:
                        button.configure(
                            text="♥" if is_favorite else "♡",
                            text_color=colors.ACCENT if is_favorite else colors.TEXT_MUTED
                        )
                    break

    def refresh_favorites(self):
        for index, track in enumerate(self.tracks, start=1):
            button = self.favorite_buttons.get(index)
            if button:
                is_favorite = self.is_favorite(track)
                button.configure(
                    text="♥" if is_favorite else "♡",
                    text_color=colors.ACCENT if is_favorite else colors.TEXT_MUTED
                )