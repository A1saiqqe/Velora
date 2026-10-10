"""Small, dependency-free configuration helper compatible with older Python versions."""
import json
from pathlib import Path

from config import defaults
from config.paths import app_data_dir, default_music_dir


class AppConfig:
    def __init__(self, path=None):
        self.path = Path(path) if path else app_data_dir() / "config.json"
        self.values = {
            "volume": defaults.DEFAULT_VOLUME,
            "music_directory": str(default_music_dir()),
            "theme": "dark",
        }

    def load(self):
        try:
            with self.path.open("r", encoding="utf-8") as stream:
                saved = json.load(stream)
            if isinstance(saved, dict):
                self.values.update(saved)
        except (IOError, ValueError, TypeError):
            pass
        self._validate()
        return dict(self.values)

    def save(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temporary = self.path.with_suffix(self.path.suffix + ".tmp")
        with temporary.open("w", encoding="utf-8") as stream:
            json.dump(self.values, stream, ensure_ascii=False, indent=2)
        temporary.replace(self.path)

    def get(self, key, default=None):
        return self.values.get(key, default)

    def set(self, key, value):
        self.values[key] = value
        self._validate()

    def _validate(self):
        try:
            volume = float(self.values.get("volume", defaults.DEFAULT_VOLUME))
        except (TypeError, ValueError):
            volume = defaults.DEFAULT_VOLUME
        self.values["volume"] = max(0.0, min(1.0, volume))
        if self.values.get("theme") not in ("dark", "light", "system"):
            self.values["theme"] = "dark"
        self.values["music_directory"] = str(self.values.get("music_directory") or "")
