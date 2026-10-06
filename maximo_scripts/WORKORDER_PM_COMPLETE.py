"""
Maximo-style automation script for PM work-order completion.

Launch point simulation:
Object: WORKORDER
Event: Before Save
"""

work_type = mbo.getString("WORKTYPE")
status = mbo.getString("STATUS")
description = mbo.getString("DESCRIPTION")

# Apply these rules only to PM work orders being completed.
if work_type == "PM" and status == "COMP":

    # A completed PM work order must have a description.
    if not description or not description.strip():
        service.error(
            "workorder",
            "PM work order description is required before completion"
        )

    # Remove unnecessary spaces from the description.
    cleaned_description = description.strip()

    if cleaned_description != description:
        mbo.setValue("DESCRIPTION", cleaned_description)