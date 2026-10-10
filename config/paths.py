"""Paths for bundled resources and writable per-user application data."""
import os
import sys
from pathlib import Path


def resource_dir():
    """Return read-only resource root in development and PyInstaller builds."""
    if getattr(sys, "_MEIPASS", None):
        return Path(sys._MEIPASS)
    return Path(__file__).resolve().parents[1]


def app_data_dir():
    """Return a writable per-user directory (safe under Program Files)."""
    if os.name == "nt":
        base = os.environ.get("LOCALAPPDATA") or os.environ.get("APPDATA")
        if base:
            root = Path(base)
        else:
            root = Path.home() / "AppData" / "Local"
    elif sys.platform == "darwin":
        root = Path.home() / "Library" / "Application Support"
    else:
        root = Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local" / "share"))
    result = root / "Velora"
    result.mkdir(parents=True, exist_ok=True)
    return result


def default_music_dir():
    """Prefer the user's Music folder in packaged builds, bundled demo in dev."""
    user_music = Path.home() / "Music"
    if getattr(sys, "frozen", False) and user_music.is_dir():
        return user_music
    bundled_demo = resource_dir() / "data" / "music"
    return bundled_demo if bundled_demo.is_dir() else user_music
