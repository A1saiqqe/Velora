from dataclasses import dataclass


@dataclass
class Track:
    title: str
    artist: str
    album: str = ""
    duration: int = 0
    file_path: str = ""
    artwork_path: str = ""
    genre: str = ""
    year: int = 0