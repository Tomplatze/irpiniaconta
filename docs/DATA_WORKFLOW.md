# Data acquisition and publication

The data pipeline runs independently of Nuxt. The frontend consumes typed HTTP
responses; Nitro queries PostgreSQL with a SELECT-only login. Python acquires,
normalizes, validates and publishes source evidence. SQL migrations remain an
explicit schema operation and never run implicitly during an update.

## Daily commands

```sh
# Preview work without network requests, a database connection or publication.
npm run data:plan -- --sources DEM-02

# Acquire a selected source and its dependencies, then publish a complete revision.
npm run data:update -- --sources DEM-02

# Replay verified raw source bytes instead of downloading them.
npm run data:update -- --sources DEM-02 --offline

# Inspect the candidate before publication.
npm run data:prepare -- --sources DEM-02 --offline
npm run data:publish -- --run RUN_ID

# Rebuild all selected indicators from existing normalized/staged evidence.
npm run data:rebuild

# Update every enabled source, or only sources due under their configured cadence.
npm run data:update
npm run data:check
```

`RUN_ID` is printed after successful preparation. Detailed attempts, timestamps,
selected source/job IDs and errors live in `.local/runs/RUN_ID/run.json`, outside
Git. Targeted updates acquire only the selected sources and their dependencies;
selected metrics are rebuilt as a complete coherent publication. Full updates
can download large national archives. No scheduler is installed or enabled.

`data:import` and `data:refresh` delegate to `data:update`. `data:offline` delegates
to the same workflow with `--offline`. Direct `python -m etl.workflow ...` works
with the virtual environment, without installing or starting Node/Nuxt.

## Responsibilities

| Module or directory | Responsibility |
| --- | --- |
| `etl/models.py` | Data contracts without network or database operations. |
| `etl/acquisition.py` | Original response bytes, request provenance, hashes and offline replay. |
| `etl/adapters/` | Source-specific interpretation and normalization. |
| `etl/collect.py`, `collection_profiles.py`, `collection_spatial.py` | Original-field collection and explicit geographic association. |
| `etl/quality.py`, `sections.py`, `section_normalization.py` | Measurement validation and selected indicator transformations. |
| `etl/registry.py` | Central registry validation and dependency ordering. |
| `etl/workflow.py` | Plan, prepare and publish orchestration. |
| `etl/workspaces.py` | File locks, isolated preparation, reports and recoverable file promotion. |
| `etl/publication.py`, `database.py`, `publication_assets.py` | Complete publication transaction and database persistence. |
| `database/migrations/` | Ordered, checksummed schema changes. |
| `server/` | Read APIs; no acquisition, Python execution or ingestion triggers. |
| `app/` | Interface and presentation logic. |

## Publication guarantees and recovery

1. Validate the registry and resolve source/job dependencies before acquisition.
2. Copy publication inputs into a private workspace. Raw bytes remain in the
   independent local acquisition cache; multi-gigabyte archives are not copied.
3. Acquire and normalize requested sources. Rebuild the inventory, selected
   metrics and map in the workspace. Verify identities, periods, null semantics,
   hashes and publication lineage before writing PostgreSQL.
4. Acquire the database publication lock and reject a candidate if another
   supported publisher changed the database since preparation. Commit core
   tables, selected metrics, documents, original evidence and import traces in
   one transaction. API requests observe a consistent revision.
5. Promote normalized files after the commit, using atomic replacements per
   file. Delete the redundant successful workspace; retain the run report.

Unexpected source errors or invalid transformed data fail preparation and leave
the published database and normalized local files unchanged. Original acquired
bytes and the failure report remain available. Known unavailable/restricted
catalogue items retain explicit blockers and do not produce invented data.
Individual maintenance commands still retain last-valid source data on failure.

PostgreSQL and the filesystem are separate systems: their writes are not one
cross-system transaction. If file promotion is interrupted after the database
commit, run `data:publish -- --run RUN_ID` again. A marker committed with the
publication prevents duplicate database imports; file promotion is repeatable.
New preparations are blocked until a committed run finishes file promotion.
Recovery refuses to promote an older committed run over a newer database import.
Keep the workspace until recovery succeeds. Configuration changes or edits to
prepared files invalidate the candidate. Restore the original configuration to
recover that run, or prepare a fresh revision after resolving the mismatch.

Supported writers serialize through advisory locks and import traces. Manual
out-of-band SQL edits are outside the optimistic revision check; do not edit
publication tables directly. A prepared candidate is not a database backup.

## Add or modify a source

`config/sources.json` is the central source/schedule index. Each source declares
its ID, category, publisher, adapter, dataset ID, cadence, temporal semantics and
options. Keep explicit blockers for unavailable integrations. Update the category
`expected_items` count when intentionally changing scope.

For a new source format, implement a small adapter under `etl/adapters/` returning
`AdapterResult`. Use `Context` from `etl.acquisition` for downloads and offline
replay. Do not write PostgreSQL or import frontend code from an adapter. Add a
regression fixture and test actual source columns, periods, units and disclosure
flags. A changed URL or supported option usually needs only configuration;
changed source semantics require adapter review and regression validation.

For original-row collection, add a job to `config/collection.json` and link it to
central source IDs with `scope_ids`. Declare `depends_on` for required collection
jobs and `reference_requests` for ancillary remote files. Geographic jobs declare
their boundary dependency. Crosswalk fields must declare the corresponding job
dependency; unknown, cyclic, duplicated and disabled required dependencies fail
before any requests. Do not rely on list order or pre-existing exploratory files.

Indicator definitions and transformations belong to `config/sections.json`;
editorial choices belong to `config/editorial.json`. A source that fits existing
data/API/chart contracts needs no frontend change. New response shapes or visual
types require their own application work. Schema changes require a new migration;
never edit an already applied SQL file.

Run `data:plan`, a targeted offline preparation when evidence is available, then
`data:update` or publish the inspected candidate. Run `data:validate` afterward.
`--rebuild` uses existing normalized evidence and does not refresh source data.
Unchanged map geometry is reused through its boundary SHA-256. Geographic source
jobs or changed geometry require `pip install -r requirements-collection.txt`;
the workflow checks selected geographic-job prerequisites before acquisition.

## Disable a source

Set `enabled: false` on the central source to stop scheduled/targeted acquisition.
Use the same flag on a collection job to stop a particular distribution. Retain
definitions and prior evidence. Disabled jobs with previously collected data
remain in the inventory. A job shared by several scopes can still be needed by
another enabled scope; use its own flag to disable that physical job.

An enabled definition cannot depend on a disabled one. Remove or replace those
dependencies deliberately. `data:rebuild` can publish configuration changes from
existing evidence without acquisition. Deleting published source definitions or
removing published evidence is rejected; data retirement is a separate reviewed
operation, not an implicit side effect of disabling updates.

## Separate database credentials

```sh
npm run db:up
npm run db:migrate
npm run db:reader
```

`DATABASE_URL` is private writer access for migrations and ingestion.
`db:reader` provisions a separate local login, grants SELECT on the publication
schemas and saves `DATABASE_READ_URL` privately in `.env`. Nitro uses only the
reader URL. Restart Nuxt after changing credentials. Reader provisioning does
not alter observations or reset the Docker volume. Run it after adding schema
objects owned by a different migration user. Automatic provisioning supports
the local Docker database only; remote role management is separate.

## Reproducibility

Live acquisition can rebuild data that upstream sources still distribute. Exact
historical reproduction requires the retained original bytes, request provenance
and matching transformation/configuration versions. Current upstream files may
contain revisions or different periods. `data:pack`/`data:unpack` transfer a
verified publication separately from Git; PostgreSQL backups and original raw
archive backups remain independent responsibilities.
