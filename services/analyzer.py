"""Library statistics and grouping helpers."""
from collections import Counter


class LibraryAnalyzer:
    def __init__(self, tracks=None):
        self.tracks = list(tracks or [])

    def analyze(self, tracks=None):
        items = list(self.tracks if tracks is None else tracks)
        artists = set()
        albums = set()
        genres = Counter()
        total_seconds = 0
        for track in items:
            artist = (getattr(track, "artist", "") or "").strip()
            album = (getattr(track, "album", "") or "").strip()
            genre = (getattr(track, "genre", "") or "").strip()
            if artist:
                artists.add(artist.casefold())
            if album:
                albums.add((artist.casefold(), album.casefold()))
            if genre:
                genres[genre] += 1
            try:
                total_seconds += max(0, int(getattr(track, "duration", 0) or 0))
            except (TypeError, ValueError):
                pass
        return {
            "track_count": len(items),
            "artist_count": len(artists),
            "album_count": len(albums),
            "total_duration": total_seconds,
            "genre_counts": dict(genres),
        }

    @staticmethod
    def group_by_artist(tracks):
        groups = {}
        for track in tracks:
            name = (getattr(track, "artist", "") or "Unknown artist").strip()
            groups.setdefault(name, []).append(track)
        return dict(sorted(groups.items(), key=lambda item: item[0].casefold()))

    @staticmethod
    def group_by_album(tracks):
        groups = {}
        for track in tracks:
            album = (getattr(track, "album", "") or "Unknown album").strip()
            artist = (getattr(track, "artist", "") or "Unknown artist").strip()
            groups.setdefault((artist, album), []).append(track)
        return dict(sorted(groups.items(), key=lambda item: (item[0][0].casefold(), item[0][1].casefold())))
