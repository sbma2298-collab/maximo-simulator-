from maximo_sim.automation.dispatcher import AutomationDispatcher
from maximo_sim.automation.workorder_complete import set_actual_finish_for_completed_pm
from maximo_sim.core.events import Event
from maximo_sim.core.service import Service
from maximo_sim.modules.work_management import new_work_order
from maximo_sim.persistence.repository import InMemoryRepository
from maximo_sim.processing.save_pipeline import SavePipeline

dispatcher = AutomationDispatcher()
dispatcher.register(
    "WORKORDER",
    Event.BEFORE_SAVE,
    set_actual_finish_for_completed_pm
)

repository = InMemoryRepository()
service = Service()
pipeline = SavePipeline(dispatcher, repository, service)

wo = new_work_order(
    "2001",
    "Monthly Pump Inspection",
    worktype="PM"
)

print("Before Completion")
print(wo)

wo.set_value("STATUS", "COMP")

pipeline.save(wo)

saved = repository.get("WORKORDER", "2001")

print("After Completion")
print(saved)