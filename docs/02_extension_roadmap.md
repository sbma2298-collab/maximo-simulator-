# 02. Extension Roadmap

## Phase 1: Current starter

- MBO and MboSet basics.
- Object metadata.
- Before-save launch point.
- Work-order completion rule.
- In-memory persistence.
- Unit testing.

## Phase 2: Local database

Implement `SQLiteRepository` using Python's `sqlite3` module while preserving the repository methods:

- `save(object_name, record_id, data)`
- `get(object_name, record_id)`
- `all(object_name)`

Suggested tables: `workorder`, `asset`, `location`, and `person`. Start with WORKORDER, then add foreign-key-like fields such as ASSETNUM and LOCATION.

## Phase 3: Relationships

Add metadata-driven relationships such as:

- WORKORDER → ASSET through `ASSETNUM`
- WORKORDER → LOCATIONS through `LOCATION`
- WORKORDER → child WORKORDER through `PARENT`

## Phase 4: Processing

Add:

- status-transition rules,
- validation errors,
- actions,
- escalations,
- cron-style batch jobs,
- transaction boundaries,
- optimistic locking.

## Phase 5: Integrations

Implement an API adapter behind `IntegrationGateway`. Keep credentials in environment variables, never in source code. Add request/response DTOs, retry policy, timeouts, structured logging, and mocked tests before calling a real endpoint.

## Phase 6: Real Maximo deployment

Move only the relevant business rule into a Maximo automation script. Configure the correct launch point in Maximo, test in a non-production environment, and use your organization's migration/deployment process.
