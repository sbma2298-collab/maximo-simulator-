# Real Maximo Script Examples

`WORKORDER_PM_COMPLETE.py` is the Maximo-facing form of the starter rule.

Suggested configuration to validate in your environment:

- Script language supported by your Maximo/MAS Manage version.
- Object launch point on `WORKORDER`.
- Before-save event.
- Correct status synonym/internal value.
- Attribute access and security.
- Whether ACTFINISH should be set automatically by existing status processing.
- Behavior for status reversal, cancellation, integrations, and batch updates.

Do not deploy directly to production. Test through your organization's development, migration, and review process.
