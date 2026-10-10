from dataclasses import dataclass, field


@dataclass
class Artist:
    name: str
    tracks: list = field(default_factory=list)

    @property
    def track_count(self):
        return len(self.tracks)

    @property
    def albums(self):
        return sorted(set((getattr(track, "album", "") or "").strip() for track in self.tracks if getattr(track, "album", "").strip()), key=str.casefold)
