import customtkinter as ctk
from tkinter import messagebox

from ui.theme import colors, spacing
from ui.theme.fonts import register_fonts
from ui.theme.theme import setup_theme

from ui.components.sidebar import Sidebar
from ui.components.search_bar import SearchBar
from ui.components.now_playing import NowPlaying
from ui.components.queue import Queue
from ui.components.lyrics_panel import LyricsPanel

from core.player import Player
from pathlib import Path
from core.scanner import MusicScanner

from ui.pages.placeholder_page import PlaceholderPage
from ui.pages.library import LibraryPage
from ui.pages.favorites import FavoritesPage
from ui.pages.albums import AlbumsPage
from ui.pages.artists import ArtistsPage
from ui.pages.genres import GenresPage
from ui.pages.folders import FoldersPage
from ui.pages.playlists import PlaylistsPage
from ui.pages.settings import SettingsPage
from config.config import AppConfig
from config.paths import default_music_dir

from database.database import Database
from database.repositories import TrackRepository

from models.track import Track

setup_theme()
register_fonts()

class VeloraApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.player = Player()
        self.config = AppConfig()
        self.config.load()
        music_dir = Path(self.config.get("music_directory") or default_music_dir())
        self.database = Database()
        self.database.connect()
        self.database.create_tables()
        self.track_repository = TrackRepository(self.database)
        self.scanner = MusicScanner(track_repository=self.track_repository)
        self.scanner.scan(music_dir)
        self.player.set_volume(self.config.get("volume", 0.7))

        self.tracks = [
            Track(
                title=item["title"],
                artist=item["artist"],
                album=item["album"],
                duration=item["duration"],
                file_path=item["file_path"],
                artwork_path=item["artwork_path"],
                genre=item["genre"],
                year=item["year"])
            for item in self.track_repository.get_all_tracks()]

        self.title("Velora — Music Player")
        self.geometry("1536x960")
        self.minsize(1180, 780)
        self.configure(fg_color=colors.BACKGROUND)

        self.sidebar = Sidebar(self, on_page_change=self.change_page)
        self.sidebar.pack(side="left", fill="y")

        self.main_area = ctk.CTkFrame(self, fg_color=colors.BACKGROUND)
        self.main_area.pack(side="left", fill="both", expand=True)

        self.search_query = ""
        self.current_page = "home"
        self.search_bar = SearchBar(self.main_area, on_search=self.search_tracks)
        self.search_bar.pack(fill="x")

        self.content_area = ctk.CTkFrame(self.main_area, fg_color=colors.BACKGROUND)
        self.content_area.pack(fill="both", expand=True)

        self.home_layout = ctk.CTkFrame(self.content_area, fg_color="transparent")
        self.home_layout.pack(fill="both", expand=True, padx=spacing.MD, pady=(0, spacing.MD))

        self.home_left = ctk.CTkFrame(self.home_layout, fg_color="transparent")
        self.home_left.pack(side="left", fill="both", expand=True, padx=(0, spacing.MD))

        self.home_right = ctk.CTkFrame(self.home_layout, width=390, fg_color="transparent")
        self.home_right.pack(side="right", fill="y")
        self.home_right.pack_propagate(False)

        self.now_playing = NowPlaying(
            self.home_left, tracks=self.tracks, on_track_play=self.play_track,
            on_play_pause=self.toggle_playback, on_seek=self.seek,
            on_next=self.manual_next_track, on_shuffle=self.toggle_shuffle,
            on_previous=self.previous_track, on_volume_change=self.change_volume,
            on_repeat=self.toggle_repeat)
        self.now_playing.pack(fill="both", expand=True)
        self.now_playing.volume_control.set_volume(self.config.get("volume", 0.7))

        self.lyrics_panel = LyricsPanel(
            self.home_right, on_favorite_toggle=self.toggle_track_favorite,
            is_favorite=self.is_track_favorite)
        self.lyrics_panel.configure(height=255)
        self.lyrics_panel.pack(side="bottom", fill="x", pady=(spacing.MD, 0))
        self.lyrics_panel.pack_propagate(False)

        self.queue = Queue(self.home_right, on_track_selected=self.select_track,
            on_current_track_removed=self.current_track_removed, tracks=self.tracks)
        self.queue.pack(side="top", fill="both", expand=True)

        self.protocol("WM_DELETE_WINDOW", self.on_close)
        self.update_progress()

    def on_close(self):
        try:
            self.player.shutdown()
        except Exception as error:
            print("Error while shutting down audio player:", error)
        try:
            self.database.close()
        except Exception as error:
            print("Error while closing the database:", error)
        self.destroy()

    def select_track(self, track):
        if hasattr(self, "queue"):
            self.queue.focus_track(track, fallback_tracks=self.tracks)
        try:
            self.player.load(track)
        except (OSError, RuntimeError, ValueError) as error:
            self.player.clear()
            self.now_playing.set_track("", "", 0, "")
            self.now_playing.update_progress(0, 0)
            self.now_playing.player_controls.set_playing(False)
            self.lyrics_panel.set_track(None)
            messagebox.showerror("Could not open track", str(error), parent=self)
            return False
        self.now_playing.set_track(
            track.title, track.artist, track.duration, track.artwork_path,
            album=track.album, year=track.year, genre=track.genre)
        self.now_playing.add_recent(track)
        self.lyrics_panel.set_track(track)
        return True

    def play_track(self, track):
        if hasattr(self, "queue"):
            self.queue.focus_track(track, fallback_tracks=self.tracks)
        if self.player.current_track is not track and not self.select_track(track):
            return
        try:
            self.player.toggle_playback()
        except (OSError, RuntimeError, ValueError) as error:
            messagebox.showerror("Playback error", str(error), parent=self)
            self.now_playing.player_controls.set_playing(False)
            return
        self.now_playing.player_controls.set_playing(self.player.is_playing)

    def toggle_playback(self):
        try:
            self.player.toggle_playback()
        except (OSError, RuntimeError, ValueError) as error:
            messagebox.showerror("Playback error", str(error), parent=self)
            self.now_playing.player_controls.set_playing(False)
            return
        self.now_playing.player_controls.set_playing(self.player.is_playing)

    def next_track(self):
        track = self.queue.next_track()
        if track is None:
            self.player.stop()
            self.now_playing.set_track("", "", 0, "")
            self.now_playing.update_progress(0, 0)
            self.now_playing.player_controls.set_playing(False)
            self.lyrics_panel.set_track(None)
            return
        if self.player.current_track is not track:
            return
        try:
            self.player.play()
        except (OSError, RuntimeError, ValueError) as error:
            messagebox.showerror("Playback error", str(error), parent=self)
            return
        self.now_playing.player_controls.set_playing(True)

    def manual_next_track(self):
        track = self.queue.next_track(manual=True)
        if track is None:
            self.player.stop()
            self.now_playing.set_track("", "", 0, "")
            self.now_playing.update_progress(0, 0)
            self.now_playing.player_controls.set_playing(False)
            self.lyrics_panel.set_track(None)
            return
        if self.player.current_track is not track:
            return
        try:
            self.player.play()
        except (OSError, RuntimeError, ValueError) as error:
            messagebox.showerror("Playback error", str(error), parent=self)
            return
        self.now_playing.player_controls.set_playing(True)

    def previous_track(self):
        self.queue.previous_track()
        if self.player.current_track:
            try:
                self.player.play()
            except (OSError, RuntimeError, ValueError) as error:
                messagebox.showerror("Playback error", str(error), parent=self)
                return
            self.now_playing.player_controls.set_playing(True)

    def update_progress(self):
        if self.player.current_track and self.player.is_playing:
            if self.player.is_track_finished():
                self.next_track()
            else:
                current = self.player.get_position()
                total = self.player.current_track.duration
                self.now_playing.update_progress(current, total)

        if hasattr(self, "library_page"):
            self.library_page.update_play_buttons(
                self.player.current_track,
                self.player.is_playing)
            
        self.after(250, self.update_progress)

    def seek(self, position):
        try:
            self.player.seek(position)
        except (OSError, RuntimeError, ValueError) as error:
            messagebox.showerror("Seeking", str(error), parent=self)

    def change_volume(self, volume):
        try:
            self.player.set_volume(volume)
        except (OSError, RuntimeError, ValueError) as error:
            messagebox.showerror("Volume", str(error), parent=self)

    def current_track_removed(self, track):
        if track is None:
            self.player.clear()
            self.now_playing.set_track("", "", 0, "")
            self.now_playing.update_progress(0, 0)
            self.now_playing.player_controls.set_playing(False)
            self.lyrics_panel.set_track(None)
            return
        try:
            self.player.stop()
            self.player.load(track)
            self.now_playing.set_track(track.title, track.artist, track.duration, track.artwork_path,
                                       album=track.album, year=track.year, genre=track.genre)
            self.now_playing.add_recent(track)
            self.lyrics_panel.set_track(track)
            self.player.play()
        except (OSError, RuntimeError, ValueError) as error:
            self.player.clear()
            self.now_playing.player_controls.set_playing(False)
            messagebox.showerror("Could not play track", str(error), parent=self)
            return
        self.now_playing.player_controls.set_playing(True)

    def toggle_shuffle(self):
        enabled = self.queue.queue_manager.toggle_shuffle()
        if enabled:
            self.queue.queue_manager.history.clear()
        return enabled

    def toggle_repeat(self):
        mode = self.queue.queue_manager.cycle_repeat_mode()
        return mode

    def change_page(self, page):
        self.current_page = page
        for widget in self.content_area.winfo_children():
            widget.pack_forget()
        if hasattr(self, "placeholder_page"):
            self.placeholder_page.destroy()
            del self.placeholder_page
        if hasattr(self, "library_page"):
            self.library_page.destroy()
            del self.library_page
        if hasattr(self, "favorites_page"):
            self.favorites_page.destroy()
            del self.favorites_page
        for page_attr in ("albums_page", "artists_page", "genres_page", "folders_page", "playlists_page", "settings_page"):
            if hasattr(self, page_attr):
                getattr(self, page_attr).destroy()
                delattr(self, page_attr)
        if page == "home":
            self.home_layout.pack(fill="both", expand=True, padx=spacing.MD, pady=(0, spacing.MD))
            return
        if page == "library":
            self.library_page = LibraryPage(
                self.content_area, tracks=self.tracks,
                on_track_selected=self.select_track,
                on_track_play=self.play_track,
                on_favorite_toggle=self.toggle_track_favorite,
                is_favorite=self.is_track_favorite)
            self.library_page.pack(fill="both", expand=True)
            if self.search_query:
                self.library_page.filter_tracks(self.search_query)
            return
        if page == "favorites":
            favorite_tracks = [
                Track(
                    title=item["title"],
                    artist=item["artist"],
                    album=item["album"],
                    duration=item["duration"],
                    file_path=item["file_path"],
                    artwork_path=item["artwork_path"],
                    genre=item["genre"],
                    year=item["year"]
                )
                for item in self.track_repository.get_favorite_tracks()
            ]
            self.favorites_page = FavoritesPage(
                self.content_area,
                tracks=favorite_tracks,
                on_track_selected=self.select_track,
                on_track_play=self.play_track,
                on_favorite_toggle=self.toggle_track_favorite,
                is_favorite=self.is_track_favorite
            )
            self.favorites_page.pack(fill="both", expand=True)
            return

        if page == "albums":
            self.albums_page = AlbumsPage(self.content_area, tracks=self.tracks, on_play=self.play_track_group)
            self.albums_page.pack(fill="both", expand=True)
            return
        if page == "artists":
            self.artists_page = ArtistsPage(self.content_area, tracks=self.tracks, on_play=self.play_track_group)
            self.artists_page.pack(fill="both", expand=True)
            return
        if page == "genres":
            self.genres_page = GenresPage(self.content_area, tracks=self.tracks, on_play=self.play_track_group)
            self.genres_page.pack(fill="both", expand=True)
            return
        if page == "folders":
            self.folders_page = FoldersPage(self.content_area, tracks=self.tracks, on_play=self.play_track_group)
            self.folders_page.pack(fill="both", expand=True)
            return
        if page == "playlists":
            self.playlists_page = PlaylistsPage(self.content_area, repository=self.track_repository, tracks=self.tracks, on_play=self.play_playlist_tracks)
            self.playlists_page.pack(fill="both", expand=True)
            return
        if page == "settings":
            self.settings_page = SettingsPage(self.content_area, config=self.config, on_music_directory_change=self.scan_music_directory, on_volume_change=self.change_volume)
            self.settings_page.pack(fill="both", expand=True)
            return

        titles = {
            "albums": "Albums",
            "artists": "Artists",
            "playlists": "Playlists",
            "favorites": "Favorites",
            "settings": "Settings"
        }

        if page in titles:
            self.placeholder_page = PlaceholderPage(self.content_area, titles[page])
            self.placeholder_page.pack(fill="both", expand=True)
        
    def play_track_group(self, tracks):
        """Play a grouped collection (album, artist, genre or folder) as its own queue."""
        if not tracks:
            return
        self.queue.set_tracks(list(tracks))
        self.play_track(tracks[0])

    def play_playlist_tracks(self, tracks):
        self.play_track_group(tracks)

    def scan_music_directory(self, directory):
        scanned = self.scanner.scan(directory)
        self.tracks = [
            Track(title=item["title"], artist=item["artist"], album=item["album"],
                  duration=item["duration"], file_path=item["file_path"],
                  artwork_path=item["artwork_path"], genre=item["genre"], year=item["year"])
            for item in self.track_repository.get_all_tracks()
        ]
        if hasattr(self, "library_page"):
            self.library_page.destroy()
            del self.library_page
        if hasattr(self, "playlists_page"):
            self.playlists_page.tracks = list(self.tracks)
        self.queue.set_tracks(self.tracks)
        self.now_playing.set_tracks(self.tracks)
        if self.search_query and hasattr(self, "library_page"):
            self.library_page.filter_tracks(self.search_query)
        if self.scanner.errors:
            print("Errors occurred while scanning ({}):".format(len(self.scanner.errors)))
            for file_path, error in self.scanner.errors[:20]:
                print("  {}: {}".format(file_path, error))
        return len(scanned)

    def search_tracks(self, query):
        self.search_query = query
        if query.strip() and self.current_page != "library":
            self.sidebar.set_active("library")
            return
        if hasattr(self, "library_page"):
            self.library_page.filter_tracks(query)

    def is_track_favorite(self, track):
        return self.track_repository.is_favorite(track.file_path)

    def toggle_track_favorite(self, track):
        if self.track_repository.is_favorite(track.file_path):
            self.track_repository.remove_favorite(track.file_path)
            favorite = False
        else:
            self.track_repository.add_favorite(track.file_path)
            favorite = True
        return favorite
    
if __name__ == "__main__":
    app = VeloraApp()
    app.mainloop()