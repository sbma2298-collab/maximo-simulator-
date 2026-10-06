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


class MaximoStyleMbo:
    """Connect Maximo-style method names to the existing simulator."""

    def __init__(self, local_mbo):
        self.local_mbo = local_mbo

    def getString(self, attribute):
        return self.local_mbo.get_string(attribute)

    def isModified(self, attribute):
        return self.local_mbo.is_modified(attribute)

    def setValue(self, attribute, value):
        self.local_mbo.set_value(attribute, value)


def main():
    script_path = (
    ROOT / sys.argv[1]
    if len(sys.argv) > 1
    else ROOT / "maximo_scripts" / "WORKORDER_PM_RULES.py"
)

    if not script_path.is_file():
        raise FileNotFoundError(f"Practice script not found: {script_path}")

    dispatcher = AutomationDispatcher()
    repository = InMemoryRepository()
    service = Service()

    def run_practice_script(local_mbo, runtime_service):
        runpy.run_path(
            str(script_path),
            init_globals={
                "mbo": MaximoStyleMbo(local_mbo),
                "service": runtime_service,
            },
        )

    dispatcher.register("WORKORDER", Event.BEFORE_SAVE, run_practice_script)
    pipeline = SavePipeline(dispatcher, repository, service)

    work_order = new_work_order("1001", "Inspect pump P-100", worktype="PM")
    print("Before:", work_order.to_dict())

    work_order.set_value("STATUS", "COMP")
    pipeline.save(work_order)

    print("After: ", repository.get("WORKORDER", "1001"))


if __name__ == "__main__":
    main()
