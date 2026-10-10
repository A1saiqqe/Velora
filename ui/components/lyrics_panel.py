from pathlib import Path
import re

import customtkinter as ctk
from PIL import Image, ImageOps

from ui.theme import colors, spacing, typography


class LyricsPanel(ctk.CTkFrame):
    """Compact right-column now-playing card with artwork and honest lyrics state."""

    def __init__(self, parent, on_favorite_toggle=None, is_favorite=None):
        super().__init__(
            parent, fg_color=colors.SURFACE, corner_radius=18,
            border_width=1, border_color=colors.BORDER,
        )
        self.on_favorite_toggle = on_favorite_toggle
        self.is_favorite = is_favorite
        self.current_track = None
        self.artwork_image = None
        self._build()

    def _build(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=spacing.MD, pady=(spacing.MD, spacing.SM))
        ctk.CTkLabel(
            header, text="Now playing", text_color=colors.TEXT_PRIMARY,
            font=(typography.FONT_FAMILY, typography.SUBTITLE_SIZE, "bold"),
        ).pack(side="left")
        ctk.CTkLabel(header, text="⌃", text_color=colors.TEXT_MUTED, font=(typography.FONT_FAMILY, 18)).pack(side="right")

        self.track_row = ctk.CTkFrame(self, fg_color=colors.SURFACE_2, corner_radius=12)
        self.track_row.pack(fill="x", padx=spacing.SM, pady=(0, spacing.MD))
        self.artwork = ctk.CTkLabel(
            self.track_row, text="♫", width=42, height=42,
            fg_color=colors.ACCENT_SOFT, corner_radius=8,
            text_color=colors.ACCENT, font=(typography.FONT_FAMILY, 18, "bold"),
        )
        self.artwork.pack(side="left", padx=spacing.SM, pady=spacing.SM)
        info = ctk.CTkFrame(self.track_row, fg_color="transparent")
        info.pack(side="left", fill="x", expand=True, pady=spacing.SM)
        self.title_label = ctk.CTkLabel(
            info, text="Nothing playing", anchor="w", text_color=colors.TEXT_PRIMARY,
            font=(typography.FONT_FAMILY, typography.BODY_SIZE, "bold"), wraplength=180,
        )
        self.title_label.pack(fill="x")
        self.artist_label = ctk.CTkLabel(
            info, text="Choose a track from your library", anchor="w", text_color=colors.TEXT_SECONDARY,
            font=(typography.FONT_FAMILY, typography.SMALL_SIZE),
        )
        self.artist_label.pack(fill="x")
        self.favorite_button = ctk.CTkButton(
            self.track_row, text="♡", width=34, height=34,
            fg_color="transparent", hover_color=colors.SURFACE_HOVER,
            text_color=colors.TEXT_SECONDARY, font=(typography.FONT_FAMILY, 22),
            command=self.toggle_favorite,
        )
        self.favorite_button.pack(side="right", padx=spacing.XS)

        self.lyrics_heading = ctk.CTkLabel(
            self, text="LYRICS", text_color=colors.TEXT_MUTED,
            font=(typography.FONT_FAMILY, 10, "bold"), anchor="w",
        )
        self.lyrics_heading.pack(fill="x", padx=spacing.MD, pady=(spacing.XS, spacing.SM))
        self.lyrics = ctk.CTkLabel(
            self, text="No lyrics found for this track.",
            text_color=colors.TEXT_SECONDARY, justify="left", anchor="nw",
            wraplength=270, font=(typography.FONT_FAMILY, typography.BODY_SIZE),
        )
        self.lyrics.pack(fill="both", expand=True, padx=spacing.MD, pady=(0, spacing.MD))
        self.waveform = ctk.CTkCanvas(
            self, height=36, bg=colors.SURFACE, highlightthickness=0, borderwidth=0,
        )
        self.waveform.pack(fill="x", padx=spacing.MD, pady=(0, spacing.MD))
        self.waveform.bind("<Configure>", lambda _event: self._draw_waveform())
        self._draw_waveform()
        self._lyrics_widgets = [self.lyrics_heading, self.lyrics, self.waveform]

    def _show_lyrics_widgets(self, visible):
        for widget in getattr(self, "_lyrics_widgets", []):
            if visible:
                widget.pack(fill="x" if widget is not self.lyrics else "both",
                            expand=widget is self.lyrics,
                            padx=spacing.MD,
                            pady=(spacing.XS, spacing.SM) if widget is self.lyrics_heading
                            else ((0, spacing.MD) if widget is self.waveform else (0, spacing.MD)))
            else:
                widget.pack_forget()

    @staticmethod
    def _read_lyrics(track):
        audio = Path(getattr(track, "file_path", "") or "")
        if not audio:
            return ""
        candidates = [audio.with_suffix(".lrc"), audio.with_suffix(".txt")]
        for candidate in candidates:
            if candidate.is_file():
                try:
                    text = candidate.read_text(encoding="utf-8-sig").strip()
                    if candidate.suffix.lower() == ".lrc":
                        text = re.sub(r"\[\d{2}:\d{2}(?:\.\d+)?\]", "", text)
                    if text:
                        return text
                except (OSError, UnicodeError):
                    pass
        return ""

    def set_track(self, track, favorite=None):
        self.current_track = track
        if track is None:
            self.title_label.configure(text="Nothing playing")
            self.artist_label.configure(text="Choose a track from your library")
            self.lyrics.configure(text="")
            self._show_lyrics_widgets(False)
            self.artwork.configure(image=None, text="♫", fg_color=colors.ACCENT_SOFT)
            self.artwork_image = None
            self.favorite_button.configure(text="♡", state="disabled")
            return

        self.title_label.configure(text=getattr(track, "title", "Untitled"))
        self.artist_label.configure(text=getattr(track, "artist", "Unknown artist"))
        lyrics_text = self._read_lyrics(track)
        if lyrics_text:
            self.lyrics.configure(text=lyrics_text)
            self._show_lyrics_widgets(True)
        else:
            self._show_lyrics_widgets(False)
        self.favorite_button.configure(state="normal")
        self._set_artwork(getattr(track, "artwork_path", ""))
        if favorite is None and self.is_favorite:
            try:
                favorite = bool(self.is_favorite(track))
            except Exception:
                favorite = False
        self.favorite_button.configure(
            text="♥" if favorite else "♡",
            text_color=colors.ACCENT if favorite else colors.TEXT_SECONDARY,
        )

    def toggle_favorite(self):
        if self.current_track is None or not self.on_favorite_toggle:
            return
        try:
            favorite = bool(self.on_favorite_toggle(self.current_track))
        except Exception:
            return
        self.favorite_button.configure(
            text="♥" if favorite else "♡",
            text_color=colors.ACCENT if favorite else colors.TEXT_SECONDARY,
        )

    def _set_artwork(self, artwork_path):
        path = Path(artwork_path) if artwork_path else None
        if path is None or not path.is_file():
            self.artwork_image = None
            self.artwork.configure(image=None, text="♫", fg_color=colors.ACCENT_SOFT)
            return
        try:
            with Image.open(path) as source:
                image = ImageOps.fit(source.convert("RGB"), (42, 42))
            self.artwork_image = ctk.CTkImage(light_image=image, dark_image=image, size=(42, 42))
            self.artwork.configure(image=self.artwork_image, text="", fg_color="transparent")
        except (OSError, ValueError):
            self.artwork_image = None
            self.artwork.configure(image=None, text="♫", fg_color=colors.ACCENT_SOFT)

    def _draw_waveform(self):
        if not self.waveform.winfo_exists():
            return
        self.waveform.delete("all")
        width = max(1, self.waveform.winfo_width())
        height = max(1, self.waveform.winfo_height())
        bars = 37
        gap = 4
        bar_width = max(2, (width - (bars - 1) * gap) / bars)
        levels = [4, 5, 4, 7, 5, 8, 4, 6, 11, 7, 14, 8, 18, 11, 24, 15, 29, 18, 22, 12, 17, 9, 12, 7, 10, 5, 7, 4, 6, 4, 5, 3, 4, 3, 4, 2, 3]
        for index, level in enumerate(levels):
            x = index * (bar_width + gap) + bar_width / 2
            bar_height = min(height - 2, level)
            self.waveform.create_line(x, (height - bar_height) / 2, x, (height + bar_height) / 2,
                                      fill=colors.ACCENT if index in (13, 14, 15, 16, 17, 18, 19) else colors.ACCENT_SOFT,
                                      width=max(2, int(bar_width)), capstyle="round")
