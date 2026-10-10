from pathlib import Path
import hashlib
from mutagen.id3 import ID3, APIC
from mutagen.flac import FLAC

class ArtworkService():
    def __init__(self, cache_dir):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def extract_artwork(self, audio_path):
        audio_path = Path(audio_path)

        if not audio_path.exists():
            return None

        cached_path = self.get_cached_path(audio_path)
        if cached_path.exists():
            return str(cached_path)

        try:
            if audio_path.suffix.lower() == ".mp3":
                return self.extract_from_mp3(audio_path)

            if audio_path.suffix.lower() == ".flac":
                return self.extract_from_flac(audio_path)

        except Exception as error:
            print(f"Could not extract artwork: {audio_path.name} — {error}")

        return None

    def extract_from_mp3(self, audio_path):
        audio = ID3(str(audio_path))

        for tag in audio.values():
            if isinstance(tag, APIC):
                return self.save_artwork(audio_path, tag.mime, tag.data)
        return None

    def extract_from_flac(self, audio_path):
        audio = FLAC(str(audio_path))

        if not audio.pictures:
            return None

        picture = audio.pictures[0]
        return self.save_artwork(audio_path, picture.mime, picture.data)

    def save_artwork(self, audio_path, mime, data):
        extension = self.get_extension(mime)
        output_path = self.get_cached_path(audio_path, extension)

        with open(output_path, "wb") as file:
            file.write(data)
        return str(output_path)

    def get_cached_path(self, audio_path, extension=None):
        audio_path = Path(audio_path)
        file_hash = hashlib.md5(str(audio_path.resolve()).encode("utf-8")).hexdigest()

        if extension is None:
            extensions = [".jpg", ".jpeg", ".png", ".webp", ".gif"]
            for possible_extension in extensions:
                cached_path = self.cache_dir / f"{file_hash}{possible_extension}"
                if cached_path.exists():
                    return cached_path
            return self.cache_dir / f"{file_hash}.jpg"

        return self.cache_dir / f"{file_hash}{extension}"

    def get_extension(self, mime):
        extensions = {
            "image/jpeg": ".jpg",
            "image/png": ".png",
            "image/webp": ".webp",
            "image/gif": ".gif"
        }

        return extensions.get(mime, ".jpg")