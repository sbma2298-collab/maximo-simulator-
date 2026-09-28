"""Coordinates launch-point execution and persistence."""

# AutomationDispatcher runs scripts registered for save events.
from maximo_sim.automation.dispatcher import AutomationDispatcher
# Event identifies BEFORE_SAVE and AFTER_SAVE stages.
from maximo_sim.core.events import Event
# Mbo is the record flowing through the save pipeline.
from maximo_sim.core.mbo import Mbo
# Service supplies runtime functions to automation scripts.
from maximo_sim.core.service import Service
# Repository permits memory, SQLite, or another later persistence implementation.
from maximo_sim.persistence.repository import Repository


# SavePipeline makes save-time processing visible and testable.
class SavePipeline:
    # Constructor receives dependencies instead of creating hard-coded global objects.
    def __init__(self, dispatcher: AutomationDispatcher, repository: Repository, service: Service):
        # Save the launch-point dispatcher used during processing.
        self._dispatcher = dispatcher
        # Save the selected persistence implementation.
        self._repository = repository
        # Save the runtime service passed to scripts.
        self._service = service

    # save processes one MBO from before-save logic through after-save logic.
    def save(self, mbo: Mbo) -> None:
        # Run object launch points before creating the persistence snapshot.
        self._dispatcher.dispatch(mbo, Event.BEFORE_SAVE, self._service)
        # Find the metadata-defined key field for this object.
        key_attribute = mbo.metadata.key_attribute
        # Convert the key to string for repository indexing.
        record_id = mbo.get_string(key_attribute)
        # Reject records without a key because they cannot be retrieved predictably.
        if not record_id:
            # ValueError shows this is invalid record state, not a repository failure.
            raise ValueError(f"{key_attribute} must have a value before save")
        # Persist a detached snapshot after all before-save scripts have finished.
        self._repository.save(mbo.metadata.object_name, record_id, mbo.to_dict())
        # Mark the current values as the saved baseline.
        mbo.accept_changes()
        # Run after-save scripts only after persistence succeeds.
        self._dispatcher.dispatch(mbo, Event.AFTER_SAVE, self._service)
