from datetime import datetime, timezone
from pathlib import Path
import runpy
import sys

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

from maximo_sim.automation.dispatcher import AutomationDispatcher
from maximo_sim.core.events import Event
from maximo_sim.core.service import Service
from maximo_sim.modules.work_management import new_work_order
from maximo_sim.persistence.repository import InMemoryRepository
from maximo_sim.processing.save_pipeline import SavePipeline

# Reuse the adapter in your working runner.
from run_mbo_script import MaximoStyleMbo


SCRIPT = ROOT / "maximo_scripts" / "WORKORDER_PM_RULES.py"
FIXED_TIME = datetime(2026, 10, 5, 12, 0, tzinfo=timezone.utc)
EXISTING_TIME = datetime(2026, 10, 4, 12, 0, tzinfo=timezone.utc)


def make_pipeline():
    """Build a fresh simulator for one independent scenario."""
    dispatcher = AutomationDispatcher()
    repository = InMemoryRepository()
    service = Service(clock=lambda: FIXED_TIME)

    def run_script(local_mbo, runtime_service):
        runpy.run_path(
            str(SCRIPT),
            init_globals={
                "mbo": MaximoStyleMbo(local_mbo),
                "service": runtime_service,
            },
        )

    dispatcher.register("WORKORDER", Event.BEFORE_SAVE, run_script)
    pipeline = SavePipeline(dispatcher, repository, service)

    return pipeline, repository


def saved_record(repository, wonum):
    """Read a record and fail clearly if it was not saved."""
    record = repository.get("WORKORDER", wonum)
    assert record is not None, f"Work order {wonum} was not saved"
    return record


def scenario_1_pm_completion():
    pipeline, repository = make_pipeline()
    wo = new_work_order("1001", "Inspect pump", worktype="PM")

    wo.set_value("STATUS", "COMP")
    pipeline.save(wo)

    saved = saved_record(repository, "1001")
    assert saved["ACTFINISH"] == FIXED_TIME
    assert saved["STATUS"] == "COMP"
    print("PASS 1: PM completion sets ACTFINISH")


def scenario_2_trim_description():
    pipeline, repository = make_pipeline()
    wo = new_work_order("1002", "  Inspect pump  ", worktype="PM")

    wo.set_value("STATUS", "COMP")
    pipeline.save(wo)

    saved = saved_record(repository, "1002")
    assert saved["DESCRIPTION"] == "Inspect pump"
    assert saved["ACTFINISH"] == FIXED_TIME
    print("PASS 2: Completion trims DESCRIPTION")


def scenario_3_reject_blank_description():
    pipeline, repository = make_pipeline()
    wo = new_work_order("1003", "   ", worktype="PM")

    wo.set_value("STATUS", "COMP")

    try:
        pipeline.save(wo)
    except ValueError as error:
        assert "DESCRIPTION" in str(error)
    else:
        raise AssertionError("Expected a validation error")

    assert repository.get("WORKORDER", "1003") is None
    print("PASS 3: Blank DESCRIPTION blocks the save")


def scenario_4_ignore_non_pm():
    pipeline, repository = make_pipeline()
    wo = new_work_order("1004", "Repair valve", worktype="CM")

    wo.set_value("STATUS", "COMP")
    pipeline.save(wo)

    saved = saved_record(repository, "1004")
    assert saved["ACTFINISH"] is None
    print("PASS 4: CM work order is unaffected")


def scenario_5_ignore_other_status():
    pipeline, repository = make_pipeline()
    wo = new_work_order("1005", "Inspect pump", worktype="PM")

    wo.set_value("STATUS", "APPR")
    pipeline.save(wo)

    saved = saved_record(repository, "1005")
    assert saved["ACTFINISH"] is None
    print("PASS 5: PM approval does not set ACTFINISH")


def scenario_6_preserve_existing_finish():
    pipeline, repository = make_pipeline()
    wo = new_work_order("1006", "Inspect pump", worktype="PM")

    wo.set_value("ACTFINISH", EXISTING_TIME)
    wo.set_value("STATUS", "COMP")
    pipeline.save(wo)

    saved = saved_record(repository, "1006")
    assert saved["ACTFINISH"] == EXISTING_TIME
    print("PASS 6: Existing ACTFINISH is preserved")


def scenario_7_unchanged_status():
    pipeline, repository = make_pipeline()
    wo = new_work_order("1007", "Inspect pump", worktype="PM")

    # Simulate loading an already-completed record:
    # its STATUS is COMP, but it was not changed in this save.
    wo.set_value("STATUS", "COMP")
    wo.accept_changes()

    pipeline.save(wo)

    saved = saved_record(repository, "1007")
    assert saved["ACTFINISH"] is None
    print("PASS 7: Unchanged COMP status does not set ACTFINISH")


if __name__ == "__main__":
    if not SCRIPT.is_file():
        raise FileNotFoundError(f"Create the practice script first: {SCRIPT}")

    scenario_1_pm_completion()
    scenario_2_trim_description()
    scenario_3_reject_blank_description()
    scenario_4_ignore_non_pm()
    scenario_5_ignore_other_status()
    scenario_6_preserve_existing_finish()
    scenario_7_unchanged_status()

    print("\nALL 7 SCENARIOS PASSED")