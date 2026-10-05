from __future__ import annotations

"""Object-launch-point rule for completing preventive-maintenance work orders."""

# Mbo represents the current WORKORDER record.
from maximo_sim.core.mbo import Mbo
# Service supplies the current date in a testable way.
from maximo_sim.core.service import Service


# set_actual_finish_for_completed_pm is our local automation script function.
def set_actual_finish_for_completed_pm(mbo: Mbo, service: Service) -> None:
    # First confirm that the current record is a preventive-maintenance work order.
    if mbo.get_string("WORKTYPE") == "PM":
        # Then confirm STATUS changed during the current unit of work.
        if mbo.is_modified("STATUS"):
            # Finally confirm the changed status is the completed status.
            if mbo.get_string("STATUS") == "COMP":
                # Set ACTFINISH before persistence by using the runtime date service.
                mbo.set_value("ACTFINISH", service.date())

