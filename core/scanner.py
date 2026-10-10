"""Filesystem scanner for supported audio formats."""
from pathlib import Path

from services.metadata import MetadataService
from services.artwork import ArtworkService
from database.repositories import TrackRepository
from models.track import Track
from config.paths import app_data_dir


class MusicScanner:
    def __init__(self, track_repository=None):
        self.metadata_service = MetadataService()
        self.supported_formats = {".mp3", ".flac", ".wav", ".ogg", ".oga", ".m4a", ".opus", ".wma", ".aiff", ".aif"}
        self.artwork_service = ArtworkService(app_data_dir() / "cache" / "artwork")
        self.track_repository = track_repository
        self.errors = []

    def scan(self, music_directory):
        # Clear diagnostics for every scan, including an invalid/missing folder.
        self.errors = []
        root = Path(music_directory).expanduser()
        if not root.exists() or not root.is_dir():
            self.errors.append((str(root), "The music folder does not exist or is inaccessible."))
            return []

        tracks = []
        try:
            candidates = root.rglob("*")
            for file_path in candidates:
                try:
                    if not file_path.is_file() or file_path.suffix.lower() not in self.supported_formats:
                        continue
                    track = self.create_track(file_path)
                    if track is None:
                        continue
                    if self.track_repository:
                        self.track_repository.add_track(track)
                    tracks.append(track)
                except (OSError, ValueError, RuntimeError) as exc:
                    self.errors.append((str(file_path), str(exc)))
                except Exception as exc:
                    # A single corrupt tag/artwork file must not abort the scan.
                    self.errors.append((str(file_path), str(exc)))
        except OSError as exc:
            self.errors.append((str(root), str(exc)))
        return tracks

    def create_track(self, file_path):
        metadata = self.metadata_service.read_metadata(file_path)
        try:
            artwork_path = self.artwork_service.extract_artwork(file_path) or ""
        except Exception as exc:
            self.errors.append((str(file_path), "Could not extract artwork: {}".format(exc)))
            artwork_path = ""
        return Track(
            title=metadata.get("title") or file_path.stem,
            artist=metadata.get("artist") or "Unknown artist",
            album=metadata.get("album") or "",
            duration=metadata.get("duration") or 0,
            file_path=str(file_path.resolve()),
            artwork_path=artwork_path,
            genre=metadata.get("genre") or "",
            year=metadata.get("year") or 0,
        )
