"""Registers scripts against object events and dispatches them."""

# Callable describes an automation script function.
from collections.abc import Callable
# Event identifies the simulated launch-point event.
from maximo_sim.core.events import Event
# Mbo is the current record supplied to an object launch point.
from maximo_sim.core.mbo import Mbo
# Service supplies runtime functions such as date and logging.
from maximo_sim.core.service import Service

# ScriptFunction documents the expected signature for local scripts.
ScriptFunction = Callable[[Mbo, Service], None]


# AutomationDispatcher is a simplified launch-point registry.
class AutomationDispatcher:
    # Constructor initializes an empty mapping of event keys to scripts.
    def __init__(self):
        # The key combines object name and event; the value is an ordered script list.
        self._scripts: dict[tuple[str, Event], list[ScriptFunction]] = {}

    # register attaches one script to one object event.
    def register(self, object_name: str, event: Event, script: ScriptFunction) -> None:
        # Normalize object name so registration and dispatch use identical keys.
        key = (object_name.upper(), event)
        # Create the list when needed, then append the script in registration order.
        self._scripts.setdefault(key, []).append(script)

    # dispatch runs every script attached to the current object event.
    def dispatch(self, mbo: Mbo, event: Event, service: Service) -> None:
        # Build the same normalized key used during registration.
        key = (mbo.metadata.object_name.upper(), event)
        # Iterate over an empty list when no script is registered.
        for script in self._scripts.get(key, []):
            # Supply the current MBO and runtime service to the script.
            script(mbo, service)
