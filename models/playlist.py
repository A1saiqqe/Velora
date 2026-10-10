from dataclasses import dataclass, field


@dataclass
class Playlist:
    name: str
    tracks: list = field(default_factory=list)
    playlist_id: int = None
    created_at: str = ""

    @property
    def track_count(self):
        return len(self.tracks)

    @property
    def duration(self):
        return sum(max(0, int(getattr(track, "duration", 0) or 0)) for track in self.tracks)

    def add_track(self, track):
        path = getattr(track, "file_path", None)
        if path and any(getattr(item, "file_path", None) == path for item in self.tracks):
            return False
        self.tracks.append(track)
        return True

    def remove_track(self, track):
        path = getattr(track, "file_path", None)
        for index, item in enumerate(self.tracks):
            if item is track or (path and getattr(item, "file_path", None) == path):
                del self.tracks[index]
                return True
        return False
