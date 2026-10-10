from pathlib import Path
from mutagen import File

class MetadataService:
    def read_metadata(self, audio_path):
        audio_path = Path(audio_path)
        if not audio_path.exists():
            return {}
        try:
            audio = File(str(audio_path), easy=True)
            if audio is None:
                return {}
            return {
                "title": self.get_value(audio, "title"),
                "artist": self.get_value(audio, "artist"),
                "album": self.get_value(audio, "album"),
                "genre": self.get_value(audio, "genre"),
                "year": self.get_year(audio),
                "duration": self.get_duration(audio)
            }
        except Exception as error:
            print(f"Could not read metadata: {audio_path.name} — {error}")
            return {}

    def get_value(self, audio, key):
        value = audio.get(key)
        if not value:
            return ""
        if isinstance(value, list):
            return str(value[0])
        return str(value)

    def get_year(self, audio):
        year = self.get_value(audio, "date")
        if not year:
            return 0
        try:
            return int(year[:4])
        except (ValueError, TypeError):
            return 0

    def get_duration(self, audio):
        if not getattr(audio, "info", None):
            return 0
        try:
            return int(audio.info.length)
        except (AttributeError, TypeError, ValueError):
            return 0