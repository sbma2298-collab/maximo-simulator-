from __future__ import annotations

"""Services normally supplied by the Maximo automation-script runtime."""

# datetime is the value type returned by our date service.
from datetime import datetime, timezone
# Callable lets tests inject a predictable clock.
from collections.abc import Callable


# Service provides runtime helpers to local automation scripts.
class Service:
    # Constructor permits a fake clock while defaulting to current UTC time.
    def __init__(self, clock: Callable[[], datetime] | None = None):
        # Save either the supplied test clock or a timezone-aware production clock.
        self._clock = clock or (lambda: datetime.now(timezone.utc))

    # date mirrors the purpose of service.date() in a Maximo automation script.
    def date(self) -> datetime:
        # Ask the configured clock for the current time.
        return self._clock()

    # log prints a message in the starter; later replace it with structured logging.
    def log(self, message: str) -> None:
        # Prefix output so simulator logs are easy to recognize in a terminal.
        print(f"[maximo-sim] {message}")

