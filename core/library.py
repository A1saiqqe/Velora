"""Application-level operations for the music library."""
from pathlib import Path

from core.scanner import MusicScanner
from models.track import Track


class MusicLibrary:
    def __init__(self, repository, scanner=None):
        self.repository = repository
        self.scanner = scanner or MusicScanner(track_repository=repository)

    def scan(self, directory):
        return self.scanner.scan(directory)

    def get_tracks(self):
        return [self._to_track(row) for row in self.repository.get_all_tracks()]

    def search(self, query):
        query = (query or "").strip().casefold()
        tracks = self.get_tracks()
        if not query:
            return tracks
        return [track for track in tracks if query in " ".join((track.title, track.artist, track.album, track.genre)).casefold()]

    def remove_missing(self):
        """Remove database entries whose files no longer exist; return removal count."""
        removed = 0
        for track in self.repository.get_all_tracks():
            if not Path(track["file_path"]).is_file():
                self.repository.delete_track(track["file_path"])
                removed += 1
        return removed

    @staticmethod
    def _to_track(row):
        return Track(
            title=row.get("title") or Path(row.get("file_path", "")).stem,
            artist=row.get("artist") or "Unknown artist",
            album=row.get("album") or "",
            duration=int(row.get("duration") or 0),
            file_path=row.get("file_path") or "",
            artwork_path=row.get("artwork_path") or "",
            genre=row.get("genre") or "",
            year=int(row.get("year") or 0),
        )
