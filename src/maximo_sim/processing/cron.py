"""A tiny cron-style batch processor for later scheduled-processing lessons."""

# Callable describes a unit of scheduled work.
from collections.abc import Callable


# CronProcessor runs registered jobs once when requested by a lesson or test.
class CronProcessor:
    # Constructor starts with an empty job registry.
    def __init__(self):
        # Store jobs by readable name rather than by an actual time schedule.
        self._jobs: dict[str, Callable[[], None]] = {}

    # register adds or replaces a named scheduled job.
    def register(self, name: str, job: Callable[[], None]) -> None:
        # Normalize the name to make lookup case-insensitive.
        self._jobs[name.upper()] = job

    # run_once executes one named job immediately.
    def run_once(self, name: str) -> None:
        # Retrieve the requested job or raise KeyError when it was not registered.
        job = self._jobs[name.upper()]
        # Invoke the job exactly once; real scheduling can be added later.
        job()
