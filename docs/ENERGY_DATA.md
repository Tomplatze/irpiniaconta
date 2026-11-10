# Provincial electricity statistics

The homepage's environment chapter uses the Campania chapter of Terna's annual *Statistiche regionali* reports. Source AMB-11 in `config/sources.json` pins the official URLs, SHA-256 digests and one-based PDF pages.

- Table 5 gives total gross and net generation and plant auxiliary electricity use. Net generation and provincial consumption are compared as annual volumes. The difference does not measure the province’s grid exchanges or renewable consumption share.
- Table 6 gives gross renewable electricity generation for Avellino in GWh, including the published total and five source categories. A dash is kept as null.
- Table 7 gives electricity consumption for Avellino in GWh, including agriculture, industry, services, domestic use and the published total. Rail traction reported separately for Campania is excluded. The 2018 edition's *Terziario* is shown for that year separately from the 2019 onward *Servizi* trend.
- All figures come from the provincial row or column. No municipal allocation, interpolation or estimation of self-sufficiency is performed. Totals can differ from the rounded component values. Monthly reports and national or regional summaries use other geographic levels.
- The reviewed series covers 2018–2024. The general source catalogue lists this provincial source separately from the municipality-oriented inventory, with links to the three latest tables and Terna’s terms. Before adding another edition, review the provincial scope, table layout and sector definitions, then pin the new PDF in the registry.

## Local reproduction

1. Save the pinned PDFs in an ignored local directory, keeping the URL filenames as stored by `curl -O` (including literal `%20`).
2. Install PyMuPDF in the local ETL environment (`python -m pip install 'PyMuPDF==2.1'`, the version used for extraction). The standard ETL does not need this optional dependency.
3. Run `.venv/bin/python -m etl.energy_publication --pdf-dir PATH --check` to validate and inspect the extracted values.
4. Run `npm run db:up` and `npm run db:migrate`, then rerun the energy command without `--check` to import. If the existing API reader lacks SELECT access, run `npm run db:reader`. Run Nuxt with `NUXT_PUBLICATION_MODE=database`.
5. To test the private snapshot read path, copy the full local v2 snapshot to a fresh directory and run `.venv/bin/python -m etl.energy_publication --snapshot-dir PATH`. Start Nuxt with `NUXT_PUBLICATION_MODE=snapshot`, `ATLAS_SNAPSHOT_DIRECTORY=PATH`, and `NUXT_ENERGY_PUBLICATION_READY=true`. Compare the energy API with the database response. Staging writes only local files.

The publication command appends a complete revision under the same PostgreSQL publication lock as the other datasets. Repeating an unchanged import leaves the previous revision in place. A failed parse or validation leaves the active revision intact.

## Publication scope and rights

The site presents a limited factual extract from three public tables for one province and seven years, with original charts and attribution. It links to the Terna reports and keeps the source documents out of the publication and repository. The project treats this as reuse of a non-substantial extract under [Article 102-ter of Italian Law 633/1941](https://www.normattiva.it/atto/caricaDettaglioAtto?atto.codiceRedazionale=012G0043&atto.dataPubblicazioneGazzetta=2012-03-23&qId=&tipoDettaglio=originario). The source registry leaves the licence field unset. Any wider extract should be reviewed separately.

Production reads the immutable private Netlify Blobs snapshot. Stage the compressed objects and verify their SHA-256 values before changing the selected version. The public CDN policy is `max-age=2592000` (30 days), applied only to successful GET responses. Netlify's production deploy invalidates the preceding deploy's cached responses. Neon is maintained as a backup and is outside the public read path.
