"""Event names used by the local launch-point dispatcher."""

# Enum prevents spelling differences in event names across the project.
from enum import Enum


# Each member represents one simplified point in an MBO save lifecycle.
class Event(str, Enum):
    # BEFORE_SAVE runs after field changes and before repository persistence.
    BEFORE_SAVE = "before_save"
    # AFTER_SAVE runs after repository persistence has completed.
    AFTER_SAVE = "after_save"
