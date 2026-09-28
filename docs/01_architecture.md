# 01. Architecture

## Hierarchy

```text
Application/module
  └── Business object (MBO)
      ├── Attributes
      ├── Relationships
      ├── Validation and actions
      └── Persistence through an MboSet/repository

Event
  └── Launch point
      └── Automation script
          └── Reads or changes the current MBO
```

## Practical mapping

- **Module:** Work Management.
- **Object:** WORKORDER.
- **Current record:** `mbo` in an object launch-point script.
- **Collection:** `MboSet` in this simulator, similar in concept to a Maximo MboSet.
- **Service:** supplies time and logging functions.
- **Before-save event:** runs after the user changes values but before persistence.
- **Repository:** stores the final record. The starter implementation uses memory.

## Save lifecycle used by this project

1. Create or load an MBO.
2. Call `set_value` to change attributes.
3. The MBO records which attributes were modified.
4. The save pipeline dispatches `BEFORE_SAVE` scripts.
5. Scripts validate or modify the MBO.
6. The repository saves a plain snapshot.
7. The MBO accepts the changes and clears its modified-field set.
8. The save pipeline dispatches `AFTER_SAVE` scripts.

This intentionally simplifies Maximo internals so each concept can be inspected and tested locally.
