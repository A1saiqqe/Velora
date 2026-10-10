"""Queue state and playback-order management."""
import random
import os
from pathlib import Path


class QueueManager:
    def __init__(self):
        self.tracks = []
        self.current_index = -1
        self.shuffle = False
        self.repeat_mode = "off"
        self.history = []
        # Shuffle is a shuffled bag of indexes: each queued track is visited
        # once per cycle, instead of randomly repeating tracks indefinitely.
        self._shuffle_remaining = []

    def add(self, track):
        self.tracks.append(track)
        new_index = len(self.tracks) - 1
        if self.current_index == -1:
            self.current_index = 0
        elif self.shuffle:
            self._shuffle_remaining.append(new_index)
            random.shuffle(self._shuffle_remaining)

    def remove(self, index):
        if index < 0 or index >= len(self.tracks):
            return
        removed_current = index == self.current_index
        self.tracks.pop(index)
        self.history = [i for i in self.history if i != index]
        self.history = [i - 1 if i > index else i for i in self.history]
        self._shuffle_remaining = [i for i in self._shuffle_remaining if i != index]
        self._shuffle_remaining = [i - 1 if i > index else i for i in self._shuffle_remaining]
        if not self.tracks:
            self.current_index = -1
            self.history.clear()
            self._shuffle_remaining.clear()
            return
        if index < self.current_index:
            self.current_index -= 1
        elif removed_current:
            self.current_index = min(self.current_index, len(self.tracks) - 1)
            if self.shuffle:
                self._shuffle_remaining = [i for i in self._shuffle_remaining if i != self.current_index]

    def clear(self):
        self.tracks.clear()
        self.current_index = -1
        self.history.clear()
        self._shuffle_remaining.clear()

    def get_current(self):
        if self.current_index < 0 or self.current_index >= len(self.tracks):
            return None
        return self.tracks[self.current_index]

    def next(self, manual=False):
        if not self.tracks:
            return None
        if self.repeat_mode == "one" and not manual:
            return self.get_current()
        if self.shuffle:
            return self.next_shuffle()
        if self.current_index < len(self.tracks) - 1:
            self.current_index += 1
            return self.get_current()
        if self.repeat_mode == "all":
            self.current_index = 0
            return self.get_current()
        return None

    def previous(self):
        if not self.tracks:
            return None
        if self.shuffle and self.history:
            old_index = self.current_index
            self.current_index = self.history.pop()
            if old_index != self.current_index and old_index not in self._shuffle_remaining:
                self._shuffle_remaining.append(old_index)
                random.shuffle(self._shuffle_remaining)
            self._shuffle_remaining = [i for i in self._shuffle_remaining if i != self.current_index]
            return self.get_current()
        if self.current_index > 0:
            self.current_index -= 1
        elif self.repeat_mode == "all":
            self.current_index = len(self.tracks) - 1
        if self.shuffle:
            self._shuffle_remaining = [i for i in self._shuffle_remaining if i != self.current_index]
        return self.get_current()

    def next_shuffle(self):
        if not self.tracks:
            return None
        if not self._shuffle_remaining:
            if self.repeat_mode != "all":
                return None
            self._shuffle_remaining = [i for i in range(len(self.tracks)) if i != self.current_index]
            random.shuffle(self._shuffle_remaining)
            if not self._shuffle_remaining:  # A one-track queue repeats itself.
                return self.get_current()
        next_index = self._shuffle_remaining.pop()
        if self.current_index != -1:
            self.history.append(self.current_index)
        self.current_index = next_index
        return self.get_current()

    def set_current(self, index):
        if index < 0 or index >= len(self.tracks):
            return None
        if self.shuffle and self.current_index != -1 and index != self.current_index:
            self.history.append(self.current_index)
            self._shuffle_remaining = [i for i in self._shuffle_remaining if i != index]
        self.current_index = index
        return self.get_current()

    def set_current_track(self, track):
        """Select a queued track by path, not by object identity."""
        if track is None:
            return None
        target_path = self._path_key(getattr(track, "file_path", ""))
        if not target_path:
            return None
        for index, queued_track in enumerate(self.tracks):
            if self._path_key(getattr(queued_track, "file_path", "")) == target_path:
                return self.set_current(index)
        return None

    @staticmethod
    def _path_key(file_path):
        if not file_path:
            return ""
        try:
            return os.path.normcase(str(Path(file_path).resolve()))
        except (OSError, RuntimeError, TypeError, ValueError):
            return os.path.normcase(str(file_path))

    def set_shuffle(self, enabled):
        enabled = bool(enabled)
        if enabled == self.shuffle:
            return
        self.shuffle = enabled
        self.history.clear()
        if enabled:
            self._shuffle_remaining = [i for i in range(len(self.tracks)) if i != self.current_index]
            random.shuffle(self._shuffle_remaining)
        else:
            self._shuffle_remaining.clear()

    def toggle_shuffle(self):
        self.set_shuffle(not self.shuffle)
        return self.shuffle

    def is_shuffle_enabled(self):
        return self.shuffle

    def set_repeat_mode(self, mode):
        if mode in ("off", "all", "one"):
            self.repeat_mode = mode

    def cycle_repeat_mode(self):
        modes = ("off", "all", "one")
        self.repeat_mode = modes[(modes.index(self.repeat_mode) + 1) % len(modes)]
        return self.repeat_mode

    def get_repeat_mode(self):
        return self.repeat_mode

    def get_all(self):
        return self.tracks.copy()

    def get_count(self):
        return len(self.tracks)
