# Object launch point: WORKORDER, before save.
# Purpose: set ACTFINISH when a PM work order changes to COMP.
# Note: this file is a learning example; configure and test it in your own environment.

# Read WORKTYPE from the current Maximo business object supplied as implicit variable mbo.
work_type = mbo.getString("WORKTYPE")
# Ask the MBO whether STATUS changed in the current transaction.
status_changed = mbo.isModified("STATUS")
# Read the current status after any user or process change.
current_status = mbo.getString("STATUS")

# Run the rule only for preventive-maintenance work orders.
if work_type == "PM":
    # Avoid resetting ACTFINISH when STATUS was not part of the current change.
    if status_changed:
        # Apply the finish time only when the new status is COMP.
        if current_status == "COMP":
            # Use Maximo's script service to obtain the runtime date.
            mbo.setValue("ACTFINISH", service.date())
