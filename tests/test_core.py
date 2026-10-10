import tempfile
import unittest
from pathlib import Path

from core.queue import QueueManager
from database.database import Database
from database.repositories import TrackRepository
from models.track import Track
from config.config import AppConfig
from core.scanner import MusicScanner


class QueueManagerTests(unittest.TestCase):
    def setUp(self):
        self.tracks = [Track(str(i), "artist", file_path="track{}.mp3".format(i)) for i in range(3)]
        self.queue = QueueManager()
        for track in self.tracks:
            self.queue.add(track)

    def test_next_and_repeat_all(self):
        self.assertIs(self.queue.next(), self.tracks[1])
        self.assertIs(self.queue.next(), self.tracks[2])
        self.assertIsNone(self.queue.next())
        self.queue.set_repeat_mode("all")
        self.assertIs(self.queue.next(), self.tracks[0])

    def test_repeat_one_only_applies_to_automatic_advance(self):
        self.queue.set_repeat_mode("one")
        self.assertIs(self.queue.next(), self.tracks[0])
        self.assertIs(self.queue.next(manual=True), self.tracks[1])

    def test_remove_before_current_keeps_current_track(self):
        self.queue.set_current(2)
        self.queue.remove(0)
        self.assertIs(self.queue.get_current(), self.tracks[2])

    def test_empty_queue_is_safe(self):
        self.queue.clear()
        self.assertIsNone(self.queue.next())
        self.assertIsNone(self.queue.previous())

    def test_set_current_track_matches_by_path_not_object_identity(self):
        duplicate_instance = Track("renamed", "artist", file_path="track2.mp3")
        selected = self.queue.set_current_track(duplicate_instance)
        self.assertIs(selected, self.tracks[2])
        self.assertEqual(self.queue.current_index, 2)

    def test_set_current_track_returns_none_when_not_queued(self):
        missing = Track("missing", "artist", file_path="missing.mp3")
        self.assertIsNone(self.queue.set_current_track(missing))
        self.assertEqual(self.queue.current_index, 0)


    def test_shuffle_visits_each_track_once_before_stopping(self):
        self.queue.set_shuffle(True)
        visited = [self.queue.get_current()]
        while True:
            track = self.queue.next()
            if track is None:
                break
            visited.append(track)
        self.assertEqual(len(visited), len(self.tracks))
        self.assertEqual({track.file_path for track in visited},
                         {track.file_path for track in self.tracks})
        self.assertIsNone(self.queue.next())

    def test_shuffle_repeat_all_starts_a_new_cycle(self):
        self.queue.set_shuffle(True)
        self.queue.set_repeat_mode("all")
        first_cycle = [self.queue.get_current()]
        for _ in range(len(self.tracks) - 1):
            first_cycle.append(self.queue.next())
        self.assertEqual(len({track.file_path for track in first_cycle}), len(self.tracks))
        next_track = self.queue.next()
        self.assertIsNotNone(next_track)
        self.assertIsNot(next_track, first_cycle[-1])

    def test_shuffle_single_track_stops_unless_repeat_all(self):
        self.queue.clear()
        self.queue.add(self.tracks[0])
        self.queue.set_shuffle(True)
        self.assertIsNone(self.queue.next())
        self.queue.set_repeat_mode("all")
        self.assertIs(self.queue.next(), self.tracks[0])


class ScannerTests(unittest.TestCase):
    def test_missing_music_directory_returns_empty_and_refreshes_errors(self):
        scanner = MusicScanner()
        scanner.errors = [("old-file.mp3", "old error")]
        with tempfile.TemporaryDirectory() as temp:
            missing = Path(temp) / "does-not-exist"
            self.assertEqual(scanner.scan(missing), [])
        self.assertEqual(len(scanner.errors), 1)
        self.assertIn("does not exist", scanner.errors[0][1].lower())


class RepositoryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        root = Path(self.temp.name)
        self.db = Database(root / "test.db")
        self.db.connect()
        self.db.create_tables()
        self.repo = TrackRepository(self.db)
        self.track_path = root / "song.mp3"
        self.track_path.write_bytes(b"test")
        self.track = Track("Song", "Artist", "Album", 123, str(self.track_path))

    def tearDown(self):
        self.db.close()
        self.temp.cleanup()

    def test_upsert_does_not_duplicate_track(self):
        self.repo.add_track(self.track)
        self.track.title = "Updated"
        self.repo.add_track(self.track)
        rows = self.repo.get_all_tracks()
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["title"], "Updated")

    def test_favorite_and_playlist_round_trip(self):
        self.repo.add_track(self.track)
        self.repo.add_favorite(str(self.track_path))
        self.assertTrue(self.repo.is_favorite(str(self.track_path)))
        playlist_id = self.repo.create_playlist("Road trip")
        self.assertEqual(self.repo.add_tracks_to_playlist(playlist_id, [self.track]), 1)
        self.assertEqual(len(self.repo.get_playlist_tracks(playlist_id)), 1)
        self.repo.delete_playlist(playlist_id)
        self.assertEqual(self.repo.get_playlists(), [])

    def test_duplicate_playlist_name_is_clear_error(self):
        self.repo.create_playlist("Mix")
        with self.assertRaises(ValueError):
            self.repo.create_playlist("Mix")


class ConfigTests(unittest.TestCase):
    def test_config_round_trip_and_volume_validation(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "config.json"
            config = AppConfig(path)
            config.set("volume", 2)
            config.save()
            loaded = AppConfig(path)
            loaded.load()
            self.assertEqual(loaded.get("volume"), 1.0)


if __name__ == "__main__":
    unittest.main()
