# Local data workspace

Only this guide belongs in Git. Acquisitions, publications, collection staging,
history, SQLite migration sources and backups stay local. Never delete them as
part of dependency or build cleanup.

The application reads PostgreSQL. A clean checkout can install dependencies,
build the application and apply the schema without data. Restoring the current
publication also requires a separately transferred, verified data bundle:

```sh
# On the existing, validated workspace:
npm run data:pack -- /absolute/path/irpiniaconta-data.tar.gz

# Transfer both the archive and its .sha256 sidecar outside Git.
# On a checkout with the same configuration and Python dependencies installed:
npm run data:unpack -- /absolute/path/irpiniaconta-data.tar.gz
npm run db:up
npm run db:migrate
npm run db:reader
npm run db:seed
npm run data:validate
```

The bundle contains verified core and selected snapshots, archived snapshot
history, all collection artifacts declared by the inventory, the collection
manifest, boundary geometry and available verification reports. It does not
contain credentials, PostgreSQL files, SQLite files, backups or national raw
archives. It restores publications and selected-metric transformations; it is
not a PostgreSQL backup and cannot replay every acquisition without raw bytes.

Export checks the source hashes and configuration. Import verifies the archive,
configuration and each file before writing; it accepts missing or identical
files and refuses conflicting files or symlinks. It never modifies PostgreSQL.
Keep an independent backup of PostgreSQL and original raw evidence.

For source acquisition, updates and adding/disabling integrations, see the
[data workflow guide](../docs/DATA_WORKFLOW.md). The data bundle is a transfer
mechanism; it is independent of the update pipeline.
