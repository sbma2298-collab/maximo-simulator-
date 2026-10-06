# WORKORDER before-save practice rule.
# The test runner supplies "mbo" and "service".

work_type = mbo.getString("WORKTYPE")
status = mbo.getString("STATUS")
status_changed = mbo.isModified("STATUS")

if work_type == "PM" and status == "COMP" and status_changed:
    original_description = mbo.getString("DESCRIPTION")
    clean_description = original_description.strip()

    if not clean_description:
        raise ValueError(
            "A PM work order needs a DESCRIPTION before completion"
        )

    if clean_description != original_description:
        mbo.setValue("DESCRIPTION", clean_description)

    if not mbo.getString("ACTFINISH"):
        mbo.setValue("ACTFINISH", service.date())
