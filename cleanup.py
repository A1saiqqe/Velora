from database.database import Database
from database.repositories import TrackRepository

db = Database()
db.connect()
repository = TrackRepository(db)

try:
    print("Before cleanup:", len(repository.get_all_tracks()))
    removed = repository.remove_duplicate_tracks()
    print("Removed:", removed)
    print("After cleanup:", len(repository.get_all_tracks()))
finally:
    db.close()