from __future__ import annotations

"""One business-object record and a small Maximo-style practice API."""

from typing import TYPE_CHECKING, Any

from maximo_sim.core.metadata import ObjectMetadata

if TYPE_CHECKING:
    from maximo_sim.core.mbo_set import MboSet


class Mbo:
    def __init__(
        self,
        metadata: ObjectMetadata,
        initial_values: dict[str, Any] | None = None,
    ):
        self.metadata = metadata
        self._values: dict[str, Any] = {}
        self._modified_fields: set[str] = set()
        self._relationships: dict[str, MboSet] = {}

        # Initial values represent a loaded record. They are not modifications.
        for attribute, value in (initial_values or {}).items():
            name = attribute.upper()
            self._require_attribute(name)
            self._values[name] = value

    def _require_attribute(self, attribute: str) -> None:
        if attribute.upper() not in self.metadata.attributes:
            raise KeyError(
                f"{attribute} is not defined on {self.metadata.object_name}"
            )

    # ----- Existing Python-style API -----

    def get_value(self, attribute: str) -> Any:
        name = attribute.upper()
        self._require_attribute(name)
        return self._values.get(name)

    def get_string(self, attribute: str) -> str:
        value = self.get_value(attribute)
        return "" if value is None else str(value)

    def set_value(self, attribute: str, value: Any) -> None:
        name = attribute.upper()
        self._require_attribute(name)

        if self._values.get(name) != value:
            self._values[name] = value
            self._modified_fields.add(name)

    def is_modified(self, attribute: str) -> bool:
        name = attribute.upper()
        self._require_attribute(name)
        return name in self._modified_fields

    def to_dict(self) -> dict[str, Any]:
        return dict(self._values)

    def accept_changes(self) -> None:
        self._modified_fields.clear()

    # ----- Maximo-style names for practice scripts -----

    def getString(self, attribute: str) -> str:
        return self.get_string(attribute)

    def getInt(self, attribute: str) -> int:
        value = self.get_value(attribute)
        return 0 if value is None else int(value)

    def getDouble(self, attribute: str) -> float:
        value = self.get_value(attribute)
        return 0.0 if value is None else float(value)

    def isNull(self, attribute: str) -> bool:
        return self.get_value(attribute) is None

    def setValue(self, attribute: str, value: Any) -> None:
        self.set_value(attribute, value)

    def setValueNull(self, attribute: str) -> None:
        self.set_value(attribute, None)

    def isModified(self, attribute: str) -> bool:
        return self.is_modified(attribute)

    # ----- Explicitly configured relationships -----

    def add_relationship(self, name: str, mbo_set: MboSet) -> None:
        """Connect a named child set to this record for a lesson."""
        self._relationships[name.upper()] = mbo_set

    def getMboSet(self, relationship: str) -> MboSet:
        """Return a configured relationship; fail clearly if it is missing."""
        name = relationship.upper()

        if name not in self._relationships:
            raise KeyError(
                f"Relationship {name} is not configured on "
                f"{self.metadata.object_name}"
            )

        return self._relationships[name]