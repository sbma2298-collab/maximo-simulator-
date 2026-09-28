"""Repository contracts and an in-memory implementation."""

# Any permits mixed field types in a business-object snapshot.
from typing import Any, Protocol


# Repository defines what persistence implementations must provide.
class Repository(Protocol):
    # save inserts or replaces one object snapshot.
    def save(self, object_name: str, record_id: str, data: dict[str, Any]) -> None: ...
    # get returns one snapshot or None when the identifier is unknown.
    def get(self, object_name: str, record_id: str) -> dict[str, Any] | None: ...
    # all returns every saved snapshot for one object.
    def all(self, object_name: str) -> list[dict[str, Any]]: ...


# InMemoryRepository supports lessons and unit tests without database setup.
class InMemoryRepository:
    # Constructor creates an empty nested object-name and record-id dictionary.
    def __init__(self):
        # Each object name maps to a dictionary of record identifiers and snapshots.
        self._database: dict[str, dict[str, dict[str, Any]]] = {}

    # save writes one detached snapshot into the local dictionary.
    def save(self, object_name: str, record_id: str, data: dict[str, Any]) -> None:
        # Normalize the Maximo object name for consistent storage.
        normalized_object = object_name.upper()
        # Create the object bucket if this is its first saved record.
        object_bucket = self._database.setdefault(normalized_object, {})
        # Copy the data so later MBO changes do not mutate the saved snapshot.
        object_bucket[record_id] = dict(data)

    # get reads one record and returns a safe copy.
    def get(self, object_name: str, record_id: str) -> dict[str, Any] | None:
        # Locate the object bucket, falling back to an empty dictionary.
        data = self._database.get(object_name.upper(), {}).get(record_id)
        # Preserve a missing result as None; otherwise return a defensive copy.
        return None if data is None else dict(data)

    # all reads every record for one object as detached copies.
    def all(self, object_name: str) -> list[dict[str, Any]]:
        # Read all snapshots from the requested normalized object bucket.
        records = self._database.get(object_name.upper(), {}).values()
        # Return new dictionaries to protect repository state from callers.
        return [dict(record) for record in records]
