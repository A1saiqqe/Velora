"""Audio backend wrapper around pygame.mixer with graceful device handling."""
from pathlib import Path

import pygame


class AudioService:
    def __init__(self):
        self.initialized = False
        self.last_error = None
        self.initialize()

    def initialize(self):
        if self.initialized:
            return True
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init()
            self.initialized = True
            self.last_error = None
            return True
        except pygame.error as exc:
            # Keep the application usable when Windows has no available output
            # device (e.g. a disconnected headset or Remote Desktop session).
            self.initialized = False
            self.last_error = exc
            return False

    def _require_mixer(self):
        if not self.initialized and not self.initialize():
            raise RuntimeError(
                "Could not initialize the audio device. "
                "Check your Windows output device and try again."
            ) from self.last_error

    def load(self, file_path):
        self._require_mixer()
        path = Path(file_path)
        if not path.is_file():
            raise FileNotFoundError("Audio file not found: {}".format(path))
        try:
            pygame.mixer.music.load(str(path))
        except (pygame.error, OSError) as exc:
            raise RuntimeError("Could not open audio file '{}': {}".format(path.name, exc)) from exc

    def play(self):
        self._require_mixer()
        try:
            pygame.mixer.music.play()
        except pygame.error as exc:
            raise RuntimeError("Could not start playback: {}".format(exc)) from exc

    def pause(self):
        if self.initialized:
            try:
                pygame.mixer.music.pause()
            except pygame.error as exc:
                raise RuntimeError("Could not pause playback: {}".format(exc)) from exc

    def resume(self):
        if self.initialized:
            try:
                pygame.mixer.music.unpause()
            except pygame.error as exc:
                raise RuntimeError("Could not resume playback: {}".format(exc)) from exc

    def stop(self):
        if self.initialized:
            pygame.mixer.music.stop()

    def seek(self, position):
        self._require_mixer()
        position = max(0.0, float(position))
        try:
            was_playing = pygame.mixer.music.get_busy()
            pygame.mixer.music.play(start=position)
            if not was_playing:
                pygame.mixer.music.pause()
        except pygame.error as exc:
            raise RuntimeError("Could not seek in track: {}".format(exc)) from exc

    def set_volume(self, volume):
        volume = max(0.0, min(1.0, float(volume)))
        if not self.initialized and not self.initialize():
            return
        try:
            pygame.mixer.music.set_volume(volume)
        except pygame.error as exc:
            raise RuntimeError("Could not change volume: {}".format(exc)) from exc

    def get_volume(self):
        if not self.initialized:
            return 0.0
        return pygame.mixer.music.get_volume()

    def get_position(self):
        if not self.initialized:
            return 0
        position = pygame.mixer.music.get_pos()
        return 0 if position < 0 else position // 1000

    def is_playing(self):
        return bool(self.initialized and pygame.mixer.music.get_busy())

    def shutdown(self):
        if not self.initialized:
            return
        try:
            pygame.mixer.music.stop()
        finally:
            pygame.mixer.quit()
            self.initialized = False
