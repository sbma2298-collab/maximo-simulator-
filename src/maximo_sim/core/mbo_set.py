from __future__ import annotations

"""A small collection type for working with multiple MBO records."""

# Iterator gives precise typing for iteration over records.
from collections.abc import Iterator
# Mbo is the record type stored by this collection.
from maximo_sim.core.mbo import Mbo


# MboSet represents a collection of records for one business object.
class MboSet:
    # Constructor starts with an optional list of records.
    def __init__(self, records: list[Mbo] | None = None):
        # Copy the list so callers do not control internal collection state.
        self._records = list(records or [])

    # add appends one MBO and returns it for fluent lesson code.
    def add(self, mbo: Mbo) -> Mbo:
        # Store the supplied record at the end of this collection.
        self._records.append(mbo)
        # Return the same record, similar to APIs that create and return a new MBO.
        return mbo

    # count reports how many MBOs currently belong to the set.
    def count(self) -> int:
        # len is sufficient because records are held in a Python list.
        return len(self._records)

    # __iter__ allows `for mbo in mbo_set` syntax.
    def __iter__(self) -> Iterator[Mbo]:
        # Return an iterator rather than exposing the private list itself.
        return iter(self._records)

