from pathlib import Path

import customtkinter as ctk
from PIL import Image, ImageOps

from ui.theme import colors, spacing, typography
from ui.components.icon import load_icon
from core.queue import QueueManager


class Queue(ctk.CTkFrame):
    def __init__(self, parent, on_track_selected=None, on_current_track_removed=None, tracks=None):
        super().__init__(parent, width=330, fg_color=colors.SURFACE, corner_radius=18,
                         border_width=1, border_color=colors.BORDER)
        self.pack_propagate(False)
        self.on_track_selected = on_track_selected
        self.on_current_track_removed = on_current_track_removed
        self.queue_manager = QueueManager()
        self.tracks = tracks or []
        self._artwork_refs = []
        self.create_header()
        self.create_list()
        self.set_tracks(self.tracks)

    def create_header(self):
        self.header = ctk.CTkFrame(self, fg_color="transparent")
        self.header.pack(fill="x", padx=spacing.LG, pady=spacing.LG)
        self.title = ctk.CTkLabel(
            self.header, text="Queue", text_color=colors.TEXT_PRIMARY,
            font=(typography.FONT_FAMILY, typography.SUBTITLE_SIZE, "bold"),
        )
        self.title.pack(side="left")
        self.count = ctk.CTkLabel(
            self.header, text="0", width=30, height=24, corner_radius=12,
            fg_color=colors.SURFACE_2, text_color=colors.TEXT_SECONDARY,
            font=(typography.FONT_FAMILY, typography.SMALL_SIZE, "bold"),
        )
        self.count.pack(side="left", padx=spacing.SM)
        self.clear_button = ctk.CTkButton(
            self.header, text="Clear", width=66, height=28,
            fg_color="transparent", hover_color=colors.SURFACE_HOVER,
            text_color=colors.TEXT_SECONDARY, corner_radius=8,
            font=(typography.FONT_FAMILY, 10), command=self.clear_queue,
        )
        self.clear_button.pack(side="right")

    def create_list(self):
        self.list_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.list_frame.pack(fill="both", expand=True, padx=spacing.XS, pady=(0, spacing.SM))

    def set_tracks(self, tracks):
        self.tracks = list(tracks or [])
        self.queue_manager.clear()
        for track in self.tracks:
            self.queue_manager.add(track)
        self.refresh()

    def focus_track(self, track, fallback_tracks=None):
        selected = self.queue_manager.set_current_track(track)
        if selected is None and fallback_tracks is not None:
            self.set_tracks(fallback_tracks)
            selected = self.queue_manager.set_current_track(track)
        if selected is None:
            self.set_tracks([track])
            selected = track
        self.tracks = self.queue_manager.get_all()
        self.refresh()
        return selected

    @staticmethod
    def format_duration(seconds):
        seconds = max(0, int(seconds or 0))
        return f"{seconds // 60}:{seconds % 60:02d}"

    def refresh(self):
        for widget in self.list_frame.winfo_children():
            widget.destroy()
        self._artwork_refs.clear()
        self.count.configure(text=str(len(self.tracks)))
        if not self.tracks:
            self.show_empty_state()
            return
        current_index = self.queue_manager.current_index
        for index, track in enumerate(self.tracks):
            is_active = index == current_index
            item = ctk.CTkFrame(
                self.list_frame, height=68,
                fg_color=colors.ACCENT_SOFT if is_active else "transparent",
                corner_radius=12,
            )
            item.pack(fill="x", padx=spacing.XS, pady=3)
            item.pack_propagate(False)

            if is_active:
                ctk.CTkFrame(item, width=3, fg_color=colors.ACCENT, corner_radius=2).pack(side="left", fill="y")

            artwork_image = self._load_artwork(getattr(track, "artwork_path", ""))
            if artwork_image is not None:
                self._artwork_refs.append(artwork_image)
                art = ctk.CTkLabel(item, text="", image=artwork_image, width=42, height=42)
            else:
                art = ctk.CTkLabel(
                    item, text="♫", width=42, height=42, corner_radius=8,
                    fg_color=colors.SURFACE_2, text_color=colors.ACCENT,
                    font=(typography.FONT_FAMILY, 17, "bold"),
                )
            art.pack(side="left", padx=(spacing.SM, spacing.SM), pady=spacing.SM)

            info = ctk.CTkFrame(item, fg_color="transparent")
            info.pack(side="left", fill="both", expand=True, pady=spacing.SM)
            ctk.CTkLabel(
                info, text=getattr(track, "title", "Untitled"), anchor="w",
                text_color=colors.TEXT_PRIMARY, font=(typography.FONT_FAMILY, typography.SMALL_SIZE, "bold"),
            ).pack(fill="x")
            ctk.CTkLabel(
                info, text=getattr(track, "artist", "Unknown artist"), anchor="w",
                text_color=colors.TEXT_SECONDARY, font=(typography.FONT_FAMILY, 10),
            ).pack(fill="x")
            ctk.CTkLabel(
                item, text=self.format_duration(getattr(track, "duration", 0)),
                text_color=colors.TEXT_MUTED, font=(typography.FONT_FAMILY, 10),
            ).pack(side="right", padx=(spacing.XS, spacing.SM))
            remove_button = ctk.CTkButton(
                item, text="×", width=24, height=28, fg_color="transparent",
                hover_color=colors.SURFACE_HOVER, text_color=colors.TEXT_MUTED,
                font=(typography.FONT_FAMILY, 16), corner_radius=8,
                command=lambda i=index: self.remove_track(i),
            )
            remove_button.pack(side="right", padx=(0, spacing.XS))

            for widget in (item, art, info):
                widget.bind("<Button-1>", lambda _event, i=index: self.select_track(i))
            for widget in info.winfo_children():
                widget.bind("<Button-1>", lambda _event, i=index: self.select_track(i))

    def _load_artwork(self, artwork_path):
        path = Path(artwork_path) if artwork_path else None
        if path is None or not path.is_file():
            return None
        try:
            with Image.open(path) as source:
                image = ImageOps.fit(source.convert("RGB"), (42, 42))
            return ctk.CTkImage(light_image=image, dark_image=image, size=(42, 42))
        except (OSError, ValueError):
            return None

    def show_empty_state(self):
        empty_frame = ctk.CTkFrame(self.list_frame, fg_color="transparent")
        empty_frame.pack(fill="both", expand=True)
        ctk.CTkLabel(empty_frame, text="♫", text_color=colors.ACCENT,
                     font=(typography.FONT_FAMILY, 36, "bold")).pack(pady=(spacing.XXL, spacing.SM))
        ctk.CTkLabel(empty_frame, text="Queue is empty", text_color=colors.TEXT_PRIMARY,
                     font=(typography.FONT_FAMILY, typography.BODY_SIZE, "bold")).pack()
        ctk.CTkLabel(empty_frame, text="Add music to start listening",
                     text_color=colors.TEXT_MUTED, font=(typography.FONT_FAMILY, typography.SMALL_SIZE),
                     wraplength=220).pack(pady=(spacing.XS, 0))

    def select_track(self, index):
        if not self.tracks:
            return
        track = self.queue_manager.set_current(index)
        if track is None:
            return
        self.refresh()
        if self.on_track_selected:
            self.on_track_selected(track)

    def remove_track(self, index):
        if index < 0 or index >= len(self.tracks):
            return
        was_current = index == self.queue_manager.current_index
        self.queue_manager.remove(index)
        self.tracks = self.queue_manager.get_all()
        self.refresh()
        if was_current and self.on_current_track_removed:
            self.on_current_track_removed(self.queue_manager.get_current() if self.tracks else None)

    def clear_queue(self):
        self.queue_manager.clear()
        self.tracks = []
        self.refresh()
        if self.on_current_track_removed:
            self.on_current_track_removed(None)

    def next_track(self, manual=False):
        track = self.queue_manager.next(manual=manual)
        if track is None:
            return None
        self.refresh()
        if self.on_track_selected:
            self.on_track_selected(track)
        return track

    def previous_track(self):
        track = self.queue_manager.previous()
        if track is None:
            return None
        self.refresh()
        if self.on_track_selected:
            self.on_track_selected(track)
        return track
