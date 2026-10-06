from __future__ import annotations

"""Run a trusted practice script through this repo's existing save pipeline."""

import runpy
import sys
from pathlib import Path

from maximo_sim.automation.dispatcher import AutomationDispatcher
from maximo_sim.core.events import Event
from maximo_sim.core.mbo_set import MboSet
from maximo_sim.core.metadata import WOACTIVITY_METADATA
from maximo_sim.core.service import Service
from maximo_sim.modules.work_management import new_work_order
from maximo_sim.persistence.repository import InMemoryRepository
from maximo_sim.processing.save_pipeline import SavePipeline


ROOT = Path(__file__).resolve().parent
DEFAULT_SCRIPT = ROOT / "maximo_scripts" / "WORKORDER_PM_COMPLETE.py"


def main() -> None:
    script_path = (
        Path(sys.argv[1]).resolve()
        if len(sys.argv) > 1
        else DEFAULT_SCRIPT
    )

    if not script_path.is_file():
        raise SystemExit(f"Script not found: {script_path}")

    # This record is the implicit "mbo" inside the practice script.
    work_order = new_work_order(
        "1001",
        "Inspect pump P-100",
        worktype="PM",
    )

    # Configure one relationship for scripts that practice getMboSet().
    tasks = MboSet(metadata=WOACTIVITY_METADATA)
    work_order.add_relationship("WOTASK", tasks)

    dispatcher = AutomationDispatcher()
    repository = InMemoryRepository()
    service = Service()

    def run_script(mbo, runtime_service) -> None:
        # runpy executes the file with these names already available.
        # Only run scripts you wrote or trust.
        runpy.run_path(
            str(script_path),
            init_globals={
                "mbo": mbo,
                "service": runtime_service,
            },
        )

    dispatcher.register(
        "WORKORDER",
        Event.BEFORE_SAVE,
        run_script,
    )

    pipeline = SavePipeline(dispatcher, repository, service)

    print("Before status change:", work_order.to_dict())

    # Simulate a user changing the work order before clicking Save.
    work_order.set_value("STATUS", "COMP")

    print("Before save:", work_order.to_dict())
    print("STATUS modified:", work_order.is_modified("STATUS"))

    # This calls your existing dispatcher, script, and repository.
    pipeline.save(work_order)

    print("Saved work order:", repository.get("WORKORDER", "1001"))
    print("Child tasks:", [task.to_dict() for task in tasks])
    print("STATUS modified after save:", work_order.is_modified("STATUS"))


if __name__ == "__main__":
    main()