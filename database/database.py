import sqlite3
from pathlib import Path
from config.paths import app_data_dir

class Database():
    def __init__(self, db_path=None):
        self.db_path = Path(db_path) if db_path else app_data_dir() / "velora.db"
        self.connection = None

    def connect(self):
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.connection = sqlite3.connect(self.db_path)
        self.connection.row_factory = sqlite3.Row
        self.connection.execute("PRAGMA foreign_keys = ON")
        return self.connection

    def create_tables(self):
        if self.connection is None:
            self.connect()
        with self.connection:
            self.connection.execute("""
                CREATE TABLE IF NOT EXISTS tracks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    artist TEXT NOT NULL DEFAULT '',
                    album TEXT NOT NULL DEFAULT '',
                    duration INTEGER NOT NULL DEFAULT 0,
                    file_path TEXT NOT NULL UNIQUE,
                    artwork_path TEXT NOT NULL DEFAULT '',
                    genre TEXT NOT NULL DEFAULT '',
                    year INTEGER NOT NULL DEFAULT 0
                )
            """)

            self.connection.execute("""
                CREATE TABLE IF NOT EXISTS favorites (
                    track_id INTEGER PRIMARY KEY,
                    FOREIGN KEY (track_id)
                        REFERENCES tracks(id) ON DELETE CASCADE
                )
            """)

            self.connection.execute("""
                CREATE TABLE IF NOT EXISTS playlists (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            self.connection.execute("""
                CREATE TABLE IF NOT EXISTS playlist_tracks (
                    playlist_id INTEGER NOT NULL,
                    track_id INTEGER NOT NULL,
                    position INTEGER NOT NULL DEFAULT 0,
                    PRIMARY KEY (playlist_id, track_id),
                    FOREIGN KEY (playlist_id) REFERENCES playlists(id) ON DELETE CASCADE,
                    FOREIGN KEY (track_id) REFERENCES tracks(id) ON DELETE CASCADE
                )
            """)


    def close(self):
        if self.connection is not None:
            self.connection.close()
            self.connection = None

