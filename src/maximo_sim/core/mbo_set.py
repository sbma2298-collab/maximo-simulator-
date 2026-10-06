from __future__ import annotations

"""A small collection of MBO records."""

from collections.abc import Iterator

from maximo_sim.core.mbo import Mbo
from maximo_sim.core.metadata import ObjectMetadata


class MboSet:
    def __init__(
        self,
        records: list[Mbo] | None = None,
        metadata: ObjectMetadata | None = None,
    ):
        self._records = list(records or [])
        self.metadata = metadata

    def add(self, mbo: Mbo | None = None) -> Mbo:
        """
        add(existing_mbo): preserve the original simulator behavior.
        add(): create a record when this set has object metadata.
        """
        if mbo is None:
            if self.metadata is None:
                raise ValueError(
                    "This MboSet needs metadata before add() can create a record"
                )
            mbo = Mbo(self.metadata)

        self._records.append(mbo)
        return mbo

    def getMbo(self, index: int) -> Mbo | None:
        if index < 0 or index >= len(self._records):
            return None
        return self._records[index]

    def count(self) -> int:
        return len(self._records)

    def isEmpty(self) -> bool:
        return not self._records

    def __iter__(self) -> Iterator[Mbo]:
        return iter(self._records)