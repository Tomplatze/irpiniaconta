# MEF municipal IRPEF verification

Verified on 12 October 2026 against the publisher, with actual downloads. No third-party implementation or repository code was used.

## Source and availability

- Publisher: MEF — Dipartimento delle Finanze.
- [Official municipal catalog](https://www1.finanze.gov.it/finanze/analisi_stat/public/index.php?opendata=yes&search_class%5B0%5D=cCOMUNE).
- [Verified CSV ZIP](https://www1.finanze.gov.it/finanze/analisi_stat/public/v_4_0_0/contenuti/Redditi_e_principali_variabili_IRPEF_su_base_comunale_CSV_2024.zip?d=1615465800).
- [Verified RDF ZIP](https://www1.finanze.gov.it/finanze/analisi_stat/public/v_4_0_0/contenuti/Redditi_e_principali_variabili_IRPEF_su_base_comunale_RDF_2024.zip?d=1615465800).

The catalog's most recent municipal listing is declaration year **2025**, tax year **2024**, published **23 April 2026**. The tax year, rather than the download or declaration year, is stored as the observation period. This is a pinned, verified release; the adapter does not promise automatic discovery of future releases.

The ZIP returned HTTP 200, content type `application/zip`, and 1,028,668 bytes. It contains one CSV, 2,313,404 uncompressed bytes, UTF-8, semicolon-delimited, with CRLF records. This is a complete payload, not an HTML login page. The browser research tool could not display ZIP content; the independent download verified it successfully.

## Licence and attribution

The publisher's actual landing HTML links [CC BY 3.0 Italy](https://creativecommons.org/licenses/by/3.0/it/). The downloaded RDF describes its licence with the generic `http://creativecommons.org/licenses/by/3.0/deed.it` URI. These licence identifiers differ; the catalog records the explicit landing-page designation and this discrepancy remains visible. The prototype's attribution is **MEF — Dipartimento delle Finanze**, with source and licence links; normalization and the derived mean are identified as prototype processing.

Do not replace the publisher's licence with the licence attached to a municipal mirror or assume CC BY 4.0. Source data licensing is separate from software licensing.

## Verified schema and normalization

The 52 substantive source columns contain municipality identifiers, frequencies, euro amounts, and income brackets. A trailing blank header is ignored. The adapter validates named columns, a single archive CSV member, UTF-8 decoding, the tax year, provincial abbreviation, exact six-digit codes and duplicate municipality rows.

| Normalized indicator | Exact source field | Unit |
| --- | --- | --- |
| `irpef_taxpayers` | `Numero contribuenti` | persons |
| `irpef_income_declarants` | `Reddito complessivo - Frequenza` | persons |
| `irpef_income_total` | `Reddito complessivo - Ammontare in euro` | EUR |
| `irpef_income_mean` | Total income divided by its frequency | EUR/person |

The derived mean uses people reporting overall income, not all taxpayers and not resident population. It is annual nominal declared income, not household income, disposable income, median income, or purchasing power. Blank numeric fields remain `null/missing`; explicit zeros remain observed zeros. Explicit suppression tokens remain `null/suppressed`. The selected release has no blanks in the three imported source measures for Avellino. Other source columns do contain blanks, so omitted bracket totals must not be reconstructed or assumed to be zero.

## Measured result and reproducibility

- National source rows: **7,897** (including a non-attributed row).
- Rows and unique codes with prefix `064` and province `AV`: **118**.
- Selected source measures: **354 observed values**, no missing values.
- Derived means: **118 observed values**.
- Total normalized observations: **472**, tax year 2024.

For code `064008` (Avellino), the source contains 36,096 taxpayers, 34,999 overall-income declarants and EUR 955,347,567 overall income. The derived mean is EUR 27,296.424669276264 before UI rounding. This exact check makes the denominator and formula auditable. Reconciliation against the separately acquired official municipality register occurs in the core pipeline; this adapter does not invent a municipality register from tax data.

Acquisition files are under `data/raw/`, each with a `.acquisition.json` sidecar recording URL, resolved URL, UTC retrieval time, HTTP status, byte count and SHA-256. The verified CSV ZIP SHA-256 is `75cecc95d72b76cda545666154e95ab414df1983f8a0eeef72915862ef4e8cb7`. Retrieved at `2026-10-12T14:02:13.331664+00:00`.

An offline adapter replay returned 472 observations and 118 distinct municipal codes. Source retrieval in this environment required network permission; offline replay uses the checked local snapshots. Unexpected archive, schema, year, code, licence or numeric changes fail explicitly and must be reviewed before importing a new release.
