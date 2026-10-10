import customtkinter as ctk
from pathlib import Path
from PIL import Image, ImageOps

from ui.theme import colors, spacing, typography
from ui.components.album_art import AlbumArt
from ui.components.track_info import TrackInfo
from ui.components.progress_bar import ProgressBar
from ui.components.player_controls import PlayerControls
from ui.components.volume_control import VolumeControl


class NowPlaying(ctk.CTkFrame):
    """Home dashboard: prominent current track, transport controls and library cards."""

    def __init__(self, parent, tracks=None, on_track_play=None, on_play_pause=None,
                 on_seek=None, on_next=None, on_previous=None,
                 on_volume_change=None, on_shuffle=None, on_repeat=None):
        super().__init__(parent, fg_color="transparent")
        self.on_play_pause = on_play_pause
        self.on_seek = on_seek
        self.on_next = on_next
        self.on_previous = on_previous
        self.on_volume_change = on_volume_change
        self.on_shuffle = on_shuffle
        self.on_repeat = on_repeat
        self.on_track_play = on_track_play
        self.tracks = list(tracks or [])
        self.recent_tracks = []
        self._card_images = []
        self.current_duration = 0
        self.create_layout()
        self.refresh_recent()

    def create_layout(self):
        self.content = ctk.CTkFrame(self, fg_color="transparent")
        self.content.pack(fill="both", expand=True, padx=spacing.MD, pady=spacing.MD)

        # Hero card uses a horizontal artwork / metadata composition like the target mockup.
        self.hero = ctk.CTkFrame(
            self.content, fg_color=colors.SURFACE, corner_radius=20,
            border_width=1, border_color=colors.BORDER,
        )
        self.hero.pack(fill="x", expand=False, pady=(0, spacing.MD))

        self.hero_top = ctk.CTkFrame(self.hero, fg_color="transparent")
        self.hero_top.pack(fill="x", expand=True, padx=spacing.LG, pady=(spacing.LG, spacing.SM))

        self.album_art = AlbumArt(self.hero_top, size=280)
        self.album_art.pack(side="left", padx=(0, spacing.LG))

        self.track_column = ctk.CTkFrame(self.hero_top, fg_color="transparent")
        self.track_column.pack(side="left", fill="both", expand=True, pady=(spacing.MD, 0))
        ctk.CTkLabel(
            self.track_column, text="NOW PLAYING", anchor="w",
            text_color=colors.ACCENT, font=(typography.FONT_FAMILY, 10, "bold"),
        ).pack(fill="x", pady=(0, spacing.SM))
        self.track_info = TrackInfo(self.track_column)
        self.track_info.pack(fill="x", anchor="w")
        self.album_label = ctk.CTkLabel(
            self.track_column, text="Choose a track from your library",
            text_color=colors.TEXT_MUTED, anchor="w",
            font=(typography.FONT_FAMILY, typography.SMALL_SIZE),
        )
        self.album_label.pack(fill="x", pady=(spacing.MD, spacing.SM))
        self.favorite_hint = ctk.CTkLabel(
            self.track_column, text="Velora · your music library",
            text_color=colors.TEXT_SECONDARY, anchor="w",
            font=(typography.FONT_FAMILY, typography.BODY_SIZE), wraplength=270,
        )
        self.favorite_hint.pack(fill="x", pady=(0, spacing.MD))

        self.progress_bar = ProgressBar(self.hero, on_seek=self.on_seek)
        self.progress_bar.pack(fill="x", padx=spacing.LG, pady=(spacing.SM, spacing.SM))

        self.player_controls = PlayerControls(
            self.hero, on_play_pause=self.on_play_pause,
            on_next=self.on_next, on_previous=self.on_previous,
            on_shuffle=self.on_shuffle, on_repeat=self.on_repeat,
        )
        self.player_controls.pack(pady=(0, spacing.SM))

        self.volume_control = VolumeControl(self.hero, on_volume_change=self.on_volume_change)
        self.volume_control.pack(pady=(0, spacing.LG))

        self.recent_section = ctk.CTkFrame(
            self.content, fg_color=colors.SURFACE, corner_radius=18,
            border_width=1, border_color=colors.BORDER,
        )
        self.recent_section.pack(fill="both", expand=True)
        header = ctk.CTkFrame(self.recent_section, fg_color="transparent")
        header.pack(fill="x", padx=spacing.LG, pady=(spacing.MD, spacing.SM))
        self.recent_title = ctk.CTkLabel(
            header, text="In your library", text_color=colors.TEXT_PRIMARY,
            font=(typography.FONT_FAMILY, typography.SUBTITLE_SIZE, "bold"), anchor="w",
        )
        self.recent_title.pack(side="left")
        ctk.CTkLabel(
            header, text="QUICK PLAY", text_color=colors.TEXT_MUTED,
            font=(typography.FONT_FAMILY, typography.SMALL_SIZE),
        ).pack(side="right")
        self.recent_cards = ctk.CTkFrame(self.recent_section, fg_color="transparent")
        self.recent_cards.pack(fill="both", expand=True, padx=spacing.MD, pady=(0, spacing.MD))

    def set_track(self, title, artist, duration, artwork_path="", album="", year=None, genre=""):
        self.track_info.set_track(title, artist)
        self.current_duration = max(0, int(duration or 0))
        self.progress_bar.update_progress(0, self.current_duration)
        self.player_controls.set_playing(False)
        self.album_art.set_artwork(artwork_path)
        details = [str(value).strip() for value in (album, year, genre)
                   if value not in (None, "", 0) and str(value).strip()]
        self.album_label.configure(text="  ·  ".join(details) if details else "Unknown album")
        self.favorite_hint.configure(
            text="Velora · your music library" if not title else "Music sounds better when it’s close by."
        )

    def update_progress(self, current, total):
        self.progress_bar.update_progress(current, total)

    def set_tracks(self, tracks):
        self.tracks = list(tracks or [])
        self.refresh_recent()

    def add_recent(self, track):
        if not track:
            return
        key = self._track_key(track)
        self.recent_tracks = [item for item in self.recent_tracks if self._track_key(item) != key]
        self.recent_tracks.insert(0, track)
        self.recent_tracks = self.recent_tracks[:5]
        self.refresh_recent()

    @staticmethod
    def _track_key(track):
        return str(getattr(track, "file_path", "") or getattr(track, "title", "")).casefold()

    @staticmethod
    def _format_duration(seconds):
        seconds = max(0, int(seconds or 0))
        return f"{seconds // 60}:{seconds % 60:02d}"

    def refresh_recent(self):
        if not hasattr(self, "recent_cards"):
            return
        for child in self.recent_cards.winfo_children():
            child.destroy()
        self._card_images.clear()
        items = self.recent_tracks or self.tracks[:5]
        self.recent_title.configure(text="Recently played" if self.recent_tracks else "In your library")
        if not items:
            ctk.CTkLabel(
                self.recent_cards, text="Add a music folder in Settings to see your tracks here.",
                text_color=colors.TEXT_MUTED, font=(typography.FONT_FAMILY, typography.BODY_SIZE),
            ).pack(anchor="w", padx=spacing.MD, pady=spacing.XL)
            return
        for track in items[:5]:
            card = ctk.CTkFrame(
                self.recent_cards, fg_color=colors.SURFACE_2, corner_radius=12,
                border_width=1, border_color=colors.BORDER,
            )
            card.pack(side="left", fill="both", expand=True, padx=spacing.XS, pady=spacing.XS)
            image = self._load_card_image(getattr(track, "artwork_path", ""))
            if image is not None:
                self._card_images.append(image)
                art = ctk.CTkLabel(card, text="", image=image)
            else:
                art = ctk.CTkLabel(card, text="♫", text_color=colors.ACCENT, font=(typography.FONT_FAMILY, 28, "bold"))
            art.pack(fill="x", padx=spacing.SM, pady=(spacing.SM, spacing.XS))
            title = ctk.CTkLabel(
                card, text=getattr(track, "title", "Untitled"),
                text_color=colors.TEXT_PRIMARY, anchor="w", justify="left",
                font=(typography.FONT_FAMILY, typography.SMALL_SIZE, "bold"), wraplength=125,
            )
            title.pack(fill="x", padx=spacing.SM)
            artist = ctk.CTkLabel(
                card, text=getattr(track, "artist", "Unknown artist"),
                text_color=colors.TEXT_SECONDARY, anchor="w",
                font=(typography.FONT_FAMILY, 10), wraplength=125,
            )
            artist.pack(fill="x", padx=spacing.SM, pady=(2, 0))
            ctk.CTkLabel(
                card, text=self._format_duration(getattr(track, "duration", 0)),
                text_color=colors.TEXT_MUTED, anchor="w", font=(typography.FONT_FAMILY, 10),
            ).pack(fill="x", padx=spacing.SM, pady=(spacing.XS, spacing.SM))
            for widget in (card, art, title, artist):
                widget.bind("<Button-1>", lambda _event, selected=track: self._play_recent(selected))

    def _load_card_image(self, artwork_path):
        path = Path(artwork_path) if artwork_path else None
        if path is None or not path.is_file():
            return None
        try:
            with Image.open(path) as source:
                image = ImageOps.fit(source.convert("RGB"), (92, 72))
            return ctk.CTkImage(light_image=image, dark_image=image, size=(92, 72))
        except (OSError, ValueError):
            return None

    def _play_recent(self, track):
        if self.on_track_play:
            self.on_track_play(track)
