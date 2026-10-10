import customtkinter as ctk
from ui.pages.library import LibraryPage
from ui.theme import colors


class FavoritesPage(LibraryPage):
    """Library-style view that removes tracks immediately when un-favorited."""

    def __init__(self, parent, tracks=None, on_track_selected=None, on_track_play=None,
                 on_favorite_toggle=None, is_favorite=None):
        super().__init__(
            parent,
            tracks=tracks,
            on_track_selected=on_track_selected,
            on_track_play=on_track_play,
            on_favorite_toggle=on_favorite_toggle,
            is_favorite=is_favorite,
        )
        self.header.winfo_children()[0].configure(text="Favorites")
        self.refresh_title()

    def refresh_title(self):
        self.count_label.configure(text=f"{len(self.tracks)} tracks")

    def toggle_favorite(self, track):
        was_favorite = self.is_favorite(track)
        super().toggle_favorite(track)
        # In the Favorites page, turning a favorite off should remove the row
        # immediately instead of leaving a stale entry visible until navigation.
        if was_favorite and not self.is_favorite(track):
            self.all_tracks = [item for item in self.all_tracks if item.file_path != track.file_path]
            self.tracks = [item for item in self.tracks if item.file_path != track.file_path]
            if self.selected_track is not None and self.selected_track.file_path == track.file_path:
                self.selected_track = None
                self.selected_index = None
            self.list_frame.destroy()
            self.track_rows = {}
            self.play_buttons = {}
            self.favorite_buttons = {}
            self.create_list()
            self.refresh_title()
