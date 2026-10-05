from __future__ import annotations

"""A deliberately small, heavily commented simulation of a Maximo MBO."""

# Any allows attributes to hold strings, datetimes, numbers, or None.
from typing import Any
# ObjectMetadata tells the MBO which fields are valid.
from maximo_sim.core.metadata import ObjectMetadata


# Mbo models one current business-object record.
class Mbo:
    # Constructor receives metadata and optional initial database-style values.
    def __init__(self, metadata: ObjectMetadata, initial_values: dict[str, Any] | None = None):
        # Store object metadata so field names can be checked on every access.
        self.metadata = metadata
        # Copy input values so external callers cannot mutate internal state indirectly.
        self._values = dict(initial_values or {})
        # An empty set means no fields have been changed since load or last save.
        self._modified_fields: set[str] = set()
        # Validate every supplied field immediately to expose mistakes early.
        for attribute in self._values:
            # Reuse one validation method instead of duplicating the rule.
            self._require_attribute(attribute)

    # This private method rejects attributes not defined in object metadata.
    def _require_attribute(self, attribute: str) -> None:
        # Maximo object and attribute names are commonly treated in uppercase.
        if attribute.upper() not in self.metadata.attributes:
            # KeyError clearly identifies a metadata or spelling problem.
            raise KeyError(f"{attribute} is not defined on {self.metadata.object_name}")

    # get_string mirrors the intent of Maximo's mbo.getString("FIELD").
    def get_string(self, attribute: str) -> str:
        # Normalize the requested name for predictable lookup.
        normalized_attribute = attribute.upper()
        # Ensure the requested field exists on this business object.
        self._require_attribute(normalized_attribute)
        # Read the current field value, returning None when it was never assigned.
        value = self._values.get(normalized_attribute)
        # Represent a missing field as an empty string, similar to common MBO usage.
        return "" if value is None else str(value)

    # get_value returns the original Python type, useful for datetime assertions.
    def get_value(self, attribute: str) -> Any:
        # Normalize field names for consistent internal storage.
        normalized_attribute = attribute.upper()
        # Reject invalid fields before returning data.
        self._require_attribute(normalized_attribute)
        # Return the current raw value without converting it to text.
        return self._values.get(normalized_attribute)

    # set_value mirrors the intent of Maximo's mbo.setValue("FIELD", value).
    def set_value(self, attribute: str, value: Any) -> None:
        # Normalize the name once so later operations use the same key.
        normalized_attribute = attribute.upper()
        # Verify the field belongs to the current object.
        self._require_attribute(normalized_attribute)
        # Compare old and new values so unchanged assignments are not marked modified.
        if self._values.get(normalized_attribute) != value:
            # Store the new in-memory value.
            self._values[normalized_attribute] = value
            # Record the field change for launch-point conditions such as STATUS changed.
            self._modified_fields.add(normalized_attribute)

    # is_modified mirrors the intent of Maximo's mbo.isModified("FIELD").
    def is_modified(self, attribute: str) -> bool:
        # Normalize the caller's field name before membership testing.
        normalized_attribute = attribute.upper()
        # Validate field names even when only checking modification state.
        self._require_attribute(normalized_attribute)
        # Return True only when set_value changed that field since the last accept.
        return normalized_attribute in self._modified_fields

    # to_dict produces a safe persistence or display snapshot.
    def to_dict(self) -> dict[str, Any]:
        # Return a copy so callers cannot bypass set_value and modification tracking.
        return dict(self._values)

    # accept_changes marks the current snapshot as the new saved baseline.
    def accept_changes(self) -> None:
        # Clear all field-change markers after successful persistence.
        self._modified_fields.clear()

