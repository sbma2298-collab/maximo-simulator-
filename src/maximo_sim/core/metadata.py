from __future__ import annotations

"""Metadata describing a simplified Maximo business object."""

# Dataclass creates a small immutable-style data holder with less boilerplate.
from dataclasses import dataclass
# FrozenSet expresses a collection that callers should not modify.
from typing import FrozenSet


# frozen=True prevents accidental replacement of metadata values after creation.
@dataclass(frozen=True)
class ObjectMetadata:
    # object_name stores the Maximo object name, such as WORKORDER.
    object_name: str
    # module_name groups the object under a learning-level Maximo module.
    module_name: str
    # key_attribute identifies the field used as the local record identifier.
    key_attribute: str
    # attributes lists fields that this simulator permits on the object.
    attributes: FrozenSet[str]


# WORKORDER_METADATA is the single shared definition for our first object.
WORKORDER_METADATA = ObjectMetadata(
    # WORKORDER is the core object used by the Work Order Tracking application.
    object_name="WORKORDER",
    # This learning project groups WORKORDER under Work Management.
    module_name="WORK_MANAGEMENT",
    # WONUM acts as the readable key in this simplified model.
    key_attribute="WONUM",
    # Only fields needed by the starter lessons are allowed initially.
    attributes=frozenset({"WONUM", "DESCRIPTION", "WORKTYPE", "STATUS", "ACTFINISH"}),
)

# A deliberately small child object for relationship practice.
WOACTIVITY_METADATA = ObjectMetadata(
    object_name="WOACTIVITY",
    module_name="WORK_MANAGEMENT",
    key_attribute="TASKID",
    attributes=frozenset(
        {"TASKID", "WONUM", "DESCRIPTION", "STATUS"}
    ),
)
