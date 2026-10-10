from dataclasses import dataclass, field


@dataclass
class Album:
    title: str
    artist: str = "Unknown artist"
    year: int = 0
    artwork_path: str = ""
    tracks: list = field(default_factory=list)

    @property
    def track_count(self):
        return len(self.tracks)

    @property
    def duration(self):
        return sum(max(0, int(getattr(track, "duration", 0) or 0)) for track in self.tracks)
