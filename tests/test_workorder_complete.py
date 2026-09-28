"""Tests for the starter WORKORDER object launch point."""

# datetime supplies a fixed timestamp so the test never depends on wall-clock time.
from datetime import datetime, timezone
# AutomationDispatcher registers the rule under test.
from maximo_sim.automation.dispatcher import AutomationDispatcher
# Import the completion rule under test.
from maximo_sim.automation.workorder_complete import set_actual_finish_for_completed_pm
# Event specifies the before-save launch point.
from maximo_sim.core.events import Event
# Service accepts the fixed test clock.
from maximo_sim.core.service import Service
# Factory builds readable work-order test data.
from maximo_sim.modules.work_management import new_work_order
# In-memory persistence keeps the test isolated and fast.
from maximo_sim.persistence.repository import InMemoryRepository
# SavePipeline exercises the complete local processing flow.
from maximo_sim.processing.save_pipeline import SavePipeline


# This test proves a changed PM status of COMP receives ACTFINISH.
def test_completed_pm_gets_actual_finish():
    # Fixed time makes the expected output exact and repeatable.
    fixed_time = datetime(2026, 9, 28, 7, 0, tzinfo=timezone.utc)
    # Create the dispatcher used by this isolated test.
    dispatcher = AutomationDispatcher()
    # Register the rule exactly as the application would.
    dispatcher.register("WORKORDER", Event.BEFORE_SAVE, set_actual_finish_for_completed_pm)
    # Create a clean repository for this test only.
    repository = InMemoryRepository()
    # Inject a clock function that always returns fixed_time.
    service = Service(clock=lambda: fixed_time)
    # Assemble the save pipeline under test.
    pipeline = SavePipeline(dispatcher, repository, service)
    # Create a PM work order with no actual finish.
    work_order = new_work_order("1001", "Inspect pump P-100", worktype="PM")
    # Change STATUS so is_modified("STATUS") becomes True.
    work_order.set_value("STATUS", "COMP")
    # Execute launch-point processing and persistence.
    pipeline.save(work_order)
    # Reload the saved dictionary from the repository.
    saved = repository.get("WORKORDER", "1001")
    # The repository must contain the injected completion timestamp.
    assert saved is not None
    # ACTFINISH should exactly match the runtime service date.
    assert saved["ACTFINISH"] == fixed_time
    # Saving accepted changes, so STATUS is no longer marked modified.
    assert work_order.is_modified("STATUS") is False


# This test proves corrective work does not use the PM-only rule.
def test_completed_non_pm_does_not_get_actual_finish():
    # Build the same processing components used by the positive test.
    dispatcher = AutomationDispatcher()
    # Register the work-order completion rule.
    dispatcher.register("WORKORDER", Event.BEFORE_SAVE, set_actual_finish_for_completed_pm)
    # Use clean in-memory persistence.
    repository = InMemoryRepository()
    # Use the default service because its date should never be requested here.
    service = Service()
    # Assemble the save pipeline.
    pipeline = SavePipeline(dispatcher, repository, service)
    # Create a corrective-maintenance work order rather than a PM work order.
    work_order = new_work_order("1002", "Repair leaking valve", worktype="CM")
    # Change the corrective work order to completed.
    work_order.set_value("STATUS", "COMP")
    # Save the record through the complete pipeline.
    pipeline.save(work_order)
    # Read the persisted snapshot.
    saved = repository.get("WORKORDER", "1002")
    # Ensure the repository returned the expected record.
    assert saved is not None
    # ACTFINISH stays empty because WORKTYPE was not PM.
    assert saved["ACTFINISH"] is None
