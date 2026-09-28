"""Lesson 01: change a PM work order to COMP and observe before-save processing."""

# AutomationDispatcher is the local launch-point registry.
from maximo_sim.automation.dispatcher import AutomationDispatcher
# Import the business rule that sets ACTFINISH.
from maximo_sim.automation.workorder_complete import set_actual_finish_for_completed_pm
# Event tells the dispatcher when the rule should run.
from maximo_sim.core.events import Event
# Service supplies the current date to the script.
from maximo_sim.core.service import Service
# Factory creates a valid WORKORDER MBO.
from maximo_sim.modules.work_management import new_work_order
# InMemoryRepository stores results without a database server.
from maximo_sim.persistence.repository import InMemoryRepository
# SavePipeline coordinates scripts and persistence.
from maximo_sim.processing.save_pipeline import SavePipeline

# Create an empty launch-point registry.
dispatcher = AutomationDispatcher()
# Register the script against WORKORDER's before-save event.
dispatcher.register("WORKORDER", Event.BEFORE_SAVE, set_actual_finish_for_completed_pm)
# Create local persistence for this lesson run.
repository = InMemoryRepository()
# Create the runtime service with the real current UTC clock.
service = Service()
# Assemble all save-processing dependencies.
pipeline = SavePipeline(dispatcher, repository, service)
# Create a preventive-maintenance work order.
work_order = new_work_order("1001", "Inspect pump P-100", worktype="PM")
# Simulate a user or process changing the status to completed.
work_order.set_value("STATUS", "COMP")
# Save runs the before-save script, which sets ACTFINISH, and then persists.
pipeline.save(work_order)
# Read the saved snapshot to prove the value was persisted.
saved_work_order = repository.get("WORKORDER", "1001")
# Print the result for inspection in the VS Code terminal.
print(saved_work_order)
