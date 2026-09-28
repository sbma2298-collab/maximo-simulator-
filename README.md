# Maximo Learning Lab

A local, hierarchical learning project that simulates core IBM Maximo concepts without requiring a Maximo server.

## What you will learn

1. How an MBO represents a Maximo business object record.
2. How an MboSet represents a collection of records.
3. How object launch points execute business rules.
4. How the WORKORDER object belongs to a module and uses attributes such as WORKTYPE, STATUS, and ACTFINISH.
5. How save-time processing, validation, actions, cron-style processing, persistence, and integrations fit together.
6. How to replace the in-memory repository with SQLite or another local database later.
7. How to add REST API adapters without mixing integration code into business rules.

## Seed Maximo requirement

The first example is based on this automation-script rule:

```python
# Object launch point on WORKORDER, before save.
if mbo.getString("WORKTYPE") == "PM" and mbo.isModified("STATUS"):
    if mbo.getString("STATUS") == "COMP":
        mbo.setValue("ACTFINISH", service.date())
```

In plain English: when a preventive-maintenance work order changes to `COMP`, set its actual finish time before saving.

## Repository map

```text
maximo-learning-lab/
├── src/maximo_sim/
│   ├── core/          # MBO, MboSet, metadata, service, events
│   ├── modules/       # Work Management and future Maximo modules
│   ├── automation/    # Launch points and scripts
│   ├── persistence/   # In-memory repository; SQLite extension point
│   ├── processing/    # Save pipeline and cron-style processing
│   └── integrations/  # API gateway interfaces and examples
├── maximo_scripts/    # Jython-style scripts for real Maximo
├── examples/          # Small runnable lessons
├── tests/             # Automated tests
├── docs/              # Concepts and learning path
└── .vscode/           # VS Code configuration
```

## Open in VS Code

```bash
unzip maximo-learning-lab.zip
cd maximo-learning-lab
code .
```

## Set up Python

```bash
python -m venv .venv
```

Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
python -m pip install -r requirements-dev.txt
```

macOS/Linux:

```bash
source .venv/bin/activate
python -m pip install -r requirements-dev.txt
```

## Run the first lesson

```bash
python examples/01_complete_pm_workorder.py
```

## Run tests

```bash
pytest -q
```

## Important boundary

This is a learning simulator, not IBM Maximo code and not a replacement for a Maximo test environment. Files under `maximo_scripts/` demonstrate the shape of deployable Jython-style automation scripts. Verify object names, attributes, launch-point event, security, and version-specific behavior in your own Maximo/MAS environment before deployment.

## Recommended learning order

1. `docs/01_architecture.md`
2. `src/maximo_sim/core/mbo.py`
3. `src/maximo_sim/processing/save_pipeline.py`
4. `src/maximo_sim/automation/workorder_complete.py`
5. `examples/01_complete_pm_workorder.py`
6. `tests/test_workorder_complete.py`
7. `docs/02_extension_roadmap.md`
