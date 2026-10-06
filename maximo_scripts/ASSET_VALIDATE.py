# ASSET before-save practice script.
# asset_lab.py supplies the current asset as "mbo".

assetnum = mbo.getString("ASSETNUM").strip()
description = mbo.getString("DESCRIPTION").strip()
siteid = mbo.getString("SITEID").strip()
location = mbo.getString("LOCATION").strip()
asset_type = mbo.getString("ASSETTYPE").strip()
serialnum = mbo.getString("SERIALNUM").strip()
status = mbo.getString("STATUS").strip()

# Required fields
if not assetnum:
    raise ValueError("ASSETNUM is required")

if not description:
    raise ValueError(
        "DESCRIPTION is required for asset {}".format(assetnum)
    )

if not siteid:
    raise ValueError(
        "SITEID is required for asset {}".format(assetnum)
    )

if not location:
    raise ValueError(
        "LOCATION is required for asset {}".format(assetnum)
    )

# Clean surrounding spaces from the description.
if description != mbo.getString("DESCRIPTION"):
    mbo.setValue("DESCRIPTION", description)

# Give an asset with no status a default status.
if not status:
    mbo.setValue("STATUS", "OPERATING")
    status = "OPERATING"

allowed_statuses = {"OPERATING", "NOT READY", "DECOMMISSIONED"}

if status not in allowed_statuses:
    raise ValueError(
        "Invalid STATUS {!r} for asset {}".format(status, assetnum)
    )

# Extra practice rule: motors must have a serial number.
if asset_type == "MOTOR" and not serialnum:
    raise ValueError(
        "SERIALNUM is required for motor {}".format(assetnum)
    )
