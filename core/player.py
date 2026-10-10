from pathlib import Path

from models.track import Track
from services.audio import AudioService
from services.artwork import ArtworkService
from services.metadata import MetadataService
from config.paths import app_data_dir

class Player:
    def __init__(self):
        self.audio = AudioService()
        self.current_track = None
        self.is_playing = False
        self.is_paused = False
        self.position_offset = 0

        cache_dir = app_data_dir() / "cache" / "artwork"

        self.artwork_service = ArtworkService(cache_dir)
        self.metadata_service = MetadataService()

    def load(self, track):
        if not isinstance(track, Track):
            raise TypeError("Player.load() expects a Track object.")

        if not track.file_path:
            raise ValueError("The track has no audio file path.")

        self.audio.stop()
        self.audio.load(track.file_path)

        metadata = self.metadata_service.read_metadata(track.file_path)

        if metadata:
            track.title = metadata.get("title") or track.title
            track.artist = metadata.get("artist") or track.artist
            track.album = metadata.get("album") or track.album
            track.genre = metadata.get("genre") or track.genre
            track.year = metadata.get("year") or track.year

        artwork_path = self.artwork_service.extract_artwork(
            track.file_path
        )

        if artwork_path:
            track.artwork_path = artwork_path

        self.current_track = track
        self.is_playing = False
        self.is_paused = False
        self.position_offset = 0

    def play(self):
        if self.current_track is None:
            return

        if self.is_paused:
            self.resume()
            return

        self.position_offset = 0
        self.audio.play()
        self.is_playing = True
        self.is_paused = False

    def pause(self):
        if not self.is_playing:
            return

        self.audio.pause()
        self.is_playing = False
        self.is_paused = True

    def resume(self):
        if not self.is_paused:
            return

        self.audio.resume()
        self.is_playing = True
        self.is_paused = False

    def toggle_playback(self):
        if self.current_track is None:
            return

        if self.is_playing:
            self.pause()
        elif self.is_paused:
            self.resume()
        else:
            self.play()

    def stop(self):
        self.audio.stop()
        self.is_playing = False
        self.is_paused = False
        self.position_offset = 0
    
    def clear(self):
        self.stop()
        self.current_track = None
        self.position_offset = 0

    def seek(self, position):
        if self.current_track is None:
            return

        if not self.current_track.file_path:
            return

        duration = self.current_track.duration

        if duration <= 0:
            return

        position = max(0, min(position, duration))
        self.audio.seek(position)
        self.position_offset = position

    def set_volume(self, volume):
        self.audio.set_volume(volume)

    def get_volume(self):
        return self.audio.get_volume()

    def get_position(self):
        position = self.position_offset + self.audio.get_position()

        if self.current_track:
            position = min(position, self.current_track.duration)

        return position

    def is_audio_playing(self):
        return self.audio.is_playing()

    def is_track_finished(self):
        if self.current_track is None:
            return False

        if not self.is_playing:
            return False

        return not self.audio.is_playing()

    def shutdown(self):
        self.stop()
        self.audio.shutdown()