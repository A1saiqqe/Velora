from pathlib import Path

class TrackRepository():
    def __init__(self, database):
        self.database = database

    def add_track(self, track):
        connection = self.database.connection
        if connection is None:
            raise RuntimeError("Database is not connected")

        track_path = Path(track.file_path).resolve()
        track.file_path = str(track_path)
        values = (
            track.title, track.artist, track.album, int(track.duration or 0),
            str(track_path), track.artwork_path or "", track.genre or "", int(track.year or 0)
        )
        with connection:
            # Fast path for the common case; avoids a full-table scan for every
            # discovered file. NOCASE matches Windows path semantics better.
            row = connection.execute(
                "SELECT id FROM tracks WHERE file_path = ? COLLATE NOCASE LIMIT 1",
                (str(track_path),),
            ).fetchone()
            if row is not None:
                connection.execute("""
                    UPDATE tracks SET title=?, artist=?, album=?, duration=?, file_path=?,
                        artwork_path=?, genre=?, year=? WHERE id=?
                """, (*values[:4], values[4], values[5], values[6], values[7], row["id"]))
                return

            # Migrate legacy relative paths only when the indexed exact lookup misses.
            legacy_rows = connection.execute(
                "SELECT id, file_path FROM tracks WHERE file_path NOT LIKE ?",
                (str(track_path.parent) + "%",),
            ).fetchall()
            for legacy in legacy_rows:
                stored = Path(legacy["file_path"])
                if not stored.is_absolute():
                    stored = (Path(__file__).resolve().parent.parent / stored).resolve()
                if str(stored).casefold() == str(track_path).casefold():
                    connection.execute("""
                        UPDATE tracks SET title=?, artist=?, album=?, duration=?, file_path=?,
                            artwork_path=?, genre=?, year=? WHERE id=?
                    """, (*values, legacy["id"]))
                    return
            connection.execute("""
                INSERT INTO tracks (title, artist, album, duration, file_path, artwork_path, genre, year)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, values)

    def get_all_tracks(self):
        connection = self.database.connection
        if connection is None:
            raise RuntimeError("Database is not connected")

        rows = connection.execute(
            "SELECT * FROM tracks ORDER BY title COLLATE NOCASE"
        ).fetchall()
        return [dict(row) for row in rows]

    def delete_track(self, file_path):
        connection = self.database.connection
        if connection is None:
            raise RuntimeError("Database is not connected")

        with connection:
            connection.execute(
                "DELETE FROM tracks WHERE file_path = ?",
                (str(file_path),))

    def remove_duplicate_tracks(self):
        connection = self.database.connection
        if connection is None:
            raise RuntimeError("Database is not connected")

        tracks = self.get_all_tracks()
        seen = set()
        removed = 0

        with connection:
            for track in tracks:
                path = Path(track["file_path"])
                if not path.is_absolute():
                    path = (Path(__file__).resolve().parent.parent / path).resolve()
                else:
                    path = path.resolve()

                key = str(path).casefold()
                if key in seen:
                    connection.execute(
                        "DELETE FROM tracks WHERE id = ?",
                        (track["id"],)
                    )
                    removed += 1
                else:
                    seen.add(key)
        return removed

    def add_favorite(self, file_path):
        connection = self.database.connection
        if connection is None:
            raise RuntimeError("Database is not connected")
        track_path = str(Path(file_path).resolve())
        with connection:
            row = connection.execute(
                "SELECT id FROM tracks WHERE file_path = ?", (track_path,)
            ).fetchone()
            if row is None:
                raise ValueError("Track was not found in the library")
            connection.execute(
                "INSERT OR IGNORE INTO favorites (track_id) VALUES (?)",
                (row["id"],)
            )

    def remove_favorite(self, file_path):
        connection = self.database.connection
        if connection is None:
            raise RuntimeError("Database is not connected")
        track_path = str(Path(file_path).resolve())
        with connection:
            connection.execute("""
                DELETE FROM favorites
                WHERE track_id = (SELECT id FROM tracks WHERE file_path = ?)
            """, (track_path,))

    def is_favorite(self, file_path):
        connection = self.database.connection
        if connection is None:
            raise RuntimeError("Database is not connected")
        track_path = str(Path(file_path).resolve())
        row = connection.execute("""
            SELECT 1
            FROM favorites
            JOIN tracks ON tracks.id = favorites.track_id
            WHERE tracks.file_path = ?
        """, (track_path,)).fetchone()
        return row is not None

    def get_favorite_tracks(self):
        connection = self.database.connection
        if connection is None:
            raise RuntimeError("Database is not connected")
        rows = connection.execute("""
            SELECT tracks.*
            FROM tracks
            JOIN favorites ON favorites.track_id = tracks.id
            ORDER BY tracks.title COLLATE NOCASE
        """).fetchall()
        return [dict(row) for row in rows]
    def get_playlists(self):
        connection = self.database.connection
        if connection is None:
            raise RuntimeError("Database is not connected")
        rows = connection.execute("""
            SELECT p.id, p.name, p.created_at, COUNT(pt.track_id) AS track_count
            FROM playlists p LEFT JOIN playlist_tracks pt ON pt.playlist_id = p.id
            GROUP BY p.id, p.name, p.created_at ORDER BY p.name COLLATE NOCASE
        """).fetchall()
        return [dict(row) for row in rows]

    def create_playlist(self, name):
        name = (name or "").strip()
        if not name:
            raise ValueError("Playlist name cannot be empty")
        connection = self.database.connection
        if connection is None:
            raise RuntimeError("Database is not connected")
        try:
            with connection:
                cursor = connection.execute("INSERT INTO playlists (name) VALUES (?)", (name,))
                return cursor.lastrowid
        except Exception as exc:
            if "UNIQUE" in str(exc).upper():
                raise ValueError("A playlist with this name already exists") from exc
            raise

    def delete_playlist(self, playlist_id):
        connection = self.database.connection
        if connection is None:
            raise RuntimeError("Database is not connected")
        with connection:
            connection.execute("DELETE FROM playlists WHERE id = ?", (int(playlist_id),))

    def add_tracks_to_playlist(self, playlist_id, tracks):
        connection = self.database.connection
        if connection is None:
            raise RuntimeError("Database is not connected")
        added = 0
        with connection:
            for track in tracks:
                row = connection.execute("SELECT id FROM tracks WHERE file_path = ?", (str(Path(track.file_path).resolve()),)).fetchone()
                if row is None:
                    continue
                cursor = connection.execute("INSERT OR IGNORE INTO playlist_tracks (playlist_id, track_id, position) VALUES (?, ?, COALESCE((SELECT MAX(position)+1 FROM playlist_tracks WHERE playlist_id = ?), 0))", (int(playlist_id), row["id"], int(playlist_id)))
                added += cursor.rowcount
        return added

    def get_playlist_tracks(self, playlist_id):
        connection = self.database.connection
        if connection is None:
            raise RuntimeError("Database is not connected")
        rows = connection.execute("""
            SELECT t.* FROM tracks t JOIN playlist_tracks pt ON pt.track_id = t.id
            WHERE pt.playlist_id = ? ORDER BY pt.position, t.title COLLATE NOCASE
        """, (int(playlist_id),)).fetchall()
        from models.track import Track
        return [Track(title=row["title"], artist=row["artist"], album=row["album"], duration=row["duration"], file_path=row["file_path"], artwork_path=row["artwork_path"], genre=row["genre"], year=row["year"]) for row in rows]
