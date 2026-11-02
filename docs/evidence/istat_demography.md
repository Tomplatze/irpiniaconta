# ISTAT demographic source verification

Verified on 12 October 2026.

- Publisher: ISTAT, Demography in Figures.
- Landing page: https://demo.istat.it/app/?i=POS&l=it
- Actual link in the retrieved page: https://demo.istat.it/data/posas/POSAS_2026_it_064_Avellino.zip
- Latest annual population snapshot offered by the page at retrieval: **1 January 2026, estimate**.
- Actual retrieval: HTTP 200, `application/zip`, 64,709 bytes. SHA-256: `4fba78e9e0aec2e93d393d43b10859fa8168f00fbb29f9de9db72dc0bc615a7c`.
- Evidence: original ZIP, page HTML, and their `*.acquisition.json` records under `data/raw/`.

## Availability and limitations

No authentication or paid access was needed. This is an actual downloaded municipal archive, not a search-result assumption. The original first line is `Popolazione residente per età e sesso al 1° gennaio 2026 (stima)`. ISTAT's page states that population by age/sex is estimated in line with census results and the provisional 2025 demographic balance; civil-status distribution is unavailable. This prototype uses no civil-status data and does not label estimates as final census counts.

## Schema

The ZIP contains exactly `POSAS_2026_it_064_Avellino.csv`. It is UTF-8 text with semicolon separators and quoted strings. Line 1 is a descriptive title; line 2 defines:

`Codice comune;Comune;Età;Totale maschi;Totale femmine;Totale`

There are 118 municipalities × 102 age rows = **12,036 data rows**, followed by a civil-status validation note. Ages are `0` through `100`, plus `999` for the published all-age total. The adapter checks one row per code/age, expected columns, title/period, six-character province codes, sex sums and the sum of all age rows against age `999`. The `999` row is never included in an age aggregation.

## Normalized indicators

- `population`: original all-age, both-sexes estimate (`Età = 999`), persons.
- `population_65_plus_share`: 100 × sum of both-sexes estimates for age rows 65–100 / all-age total, percent. This is a disclosed prototype calculation based on ISTAT data.

All 118 codes match the current register. The resulting 236 observations are complete. The sum of municipal all-age estimates is **393,093 persons**, computed from the archive; Fontanarosa (`064033`) is **2,832**. These verification values are not manually seeded or synthesized.

Missing and suppressed tokens produce null values with explicit statuses. Unknown textual tokens, negative/noninteger counts, incomplete age coverage, duplicate rows and inconsistent aggregates fail ingestion. A denominator of zero does not become a percentage of zero.

## License and update behavior

The page links https://www.istat.it/note-legali/, which states the default CC-BY-4.0 policy unless otherwise indicated. The source page/archive does not expose contrary terms. ISTAT attribution, source URL, estimate status, date and derivation are carried in the catalog. See `istat_license.html*` for the actual downloaded legal page.

The prototype pins the verified 2026 archive for repeatability. It does not silently relabel future data under 2026. A new annual adapter configuration must update URL, title assertion, period and source evidence together.
