# ISTAT municipality register verification

Verified on 12 October 2026. This prototype contains original adapter code; the register is attributed source data.

- Publisher: ISTAT.
- Landing page: https://www.istat.it/classificazione/codici-dei-comuni-delle-province-e-delle-regioni/
- Download: https://www.istat.it/storage/codici-unita-amministrative/Elenco-comuni-italiani.xlsx
- Landing page describes this permanent XLSX URL and an update to 21 February 2026.
- Actual retrieval: HTTP 200, XLSX content type, 1,229,843 bytes. SHA-256: `83842076860450f7e482daecea6b7a769f5f93d0bf5b0d48802b44896d7a26d5`.
- Evidence: `data/raw/istat_registry_2026.xlsx.acquisition.json`; the original workbook is retained.

## Schema and reconciliation

The first worksheet has `Codice Regione` (A), historical province code (C), `Codice Comune formato alfanumerico` (E), and `Denominazione in italiano` (G). The adapter validates header identity before accepting records. It filters province `064`, asserts region `15`, and returns **118 distinct municipality codes**. Codes are preserved as six-character strings, including the leading zero. Fontanarosa is `064033`; Avellino is `064008`.

This is a current-register reconciliation, not historical boundary harmonization. Future mergers or changes require explicitly versioned registers/crosswalks. It is incorrect to assume that the numeric municipality suffixes form an uninterrupted 1–118 sequence; the scope includes Zungoli `064120` and Montoro `064121` and excludes historical suppressed codes.

## License

https://www.istat.it/note-legali/ explicitly applies Creative Commons Attribution 4.0 to website contents unless otherwise indicated, permitting modification and commercial reuse with attribution, a license link and disclosure of transformations. The registry page does not identify a contrary license. License-page HTML and acquisition evidence are retained as `istat_license.html*`. The prototype attributes ISTAT and records the geographic filtering as a transformation. This attribution does not imply ISTAT endorsement and does not grant logo rights.

## Validation

The offline parser returned 118 records. It rejects incorrect headers, malformed six-digit codes, duplicate codes, missing names, geography outside Campania and any unexpected record count. Replaying the source requires a matching checksum; checksum verification is provided by the shared download context.
