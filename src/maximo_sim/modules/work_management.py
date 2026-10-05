from __future__ import annotations

"""Factories for the Work Management learning module."""

# Mbo is the runtime record implementation.
from maximo_sim.core.mbo import Mbo
# WORKORDER_METADATA defines valid fields and the key attribute.
from maximo_sim.core.metadata import WORKORDER_METADATA


# new_work_order creates a WORKORDER record with understandable defaults.
def new_work_order(wonum: str, description: str, worktype: str = "CM") -> Mbo:
    # Construct the MBO from metadata and its initial loaded values.
    return Mbo(
        # Supply WORKORDER object metadata.
        WORKORDER_METADATA,
        # Initial values act like a record loaded from or prepared for a database.
        {
            # WONUM identifies the work order in this learning model.
            "WONUM": wonum,
            # DESCRIPTION tells a human what work is required.
            "DESCRIPTION": description,
            # WORKTYPE distinguishes PM from corrective or other work.
            "WORKTYPE": worktype,
            # WAPPR is a common starting status for an unapproved work order.
            "STATUS": "WAPPR",
            # ACTFINISH starts empty because work is not complete.
            "ACTFINISH": None,
        },
    )

