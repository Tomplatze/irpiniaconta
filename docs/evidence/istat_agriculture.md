# ISTAT agriculture census: verified municipal ingestion

Verified on 12 October 2026. **Ready: 236 actual observations, 118 municipalities, reference year 2020.**

## Official source and license

- Release: https://www.istat.it/notizia/censimento-agricoltura-2020-online-i-principali-dati/
- The release links https://esploradati.istat.it/databrowser/#/it/censimentoagricoltura and explicitly describes municipal detail.
- Publisher: ISTAT. Default license: CC-BY-4.0 unless otherwise indicated, per https://www.istat.it/note-legali/. No contrary license was found on the release. Actual license-page HTML is retained under `data/raw/istat_license.html*`.
- Node `2`, code `CENSIMENTOAGRICOLTURA`, is exposed by the official browser's public metadata service. Its verified catalog includes 2020 and previous censuses. A 2024 multipurpose agriculture survey is separate and is not silently substituted for the census.
- Catalog: https://esploradati.istat.it/databrowserhub/api/core/nodes/2/catalog
- Verified flow: `IT1,DF_DCAT_CENSAGRIC2020_SURF_ALL,1.0`, title **Farms and areas**.
- Structure: https://esploradati.istat.it/databrowserhub/api/core/nodes/2/datasets/IT1,DF_DCAT_CENSAGRIC2020_SURF_ALL,1.0/structure
- Export: https://esploradati.istat.it/databrowserhub/api/core/nodes/2/datasets/IT1,DF_DCAT_CENSAGRIC2020_SURF_ALL,1.0/data

## Actual access and request contract

Public metadata GET requests returned HTTP 200 without authentication. The data endpoint requires a **read-only POST**; a GET returned HTTP 405. The following JSON body works, with `REF_AREA.filterValues` containing the exact 118 codes from the official register:

```json
[
  {"id":"FREQ","filterValues":["A"],"type":"CodeValues"},
  {"id":"REF_AREA","filterValues":["064001","... all 118 actual official codes ..."],"type":"CodeValues"},
  {"id":"DATA_TYPE","filterValues":["HO","ARU"],"type":"CodeValues"},
  {"id":"TIME_PERIOD","type":"TimeRange","from":"2020-01-01","to":"2020-12-31"}
]
```

The abbreviated code list above is explanatory only; the **complete request body** is retained in `data/raw/istat_agriculture_2020_avellino.json.acquisition.json`, and the adapter generates it from the actual register. The shared acquisition context checks URL, method, request body and response checksum in offline replay.

Actual response: HTTP 200, `application/json`, **386,261 bytes**. SHA-256 `33ef9f2f4505328fac7faf90ce3c56efbf91f839e4115f75fdb050bad8b2befb`. Request SHA-256 `a77d3cbcf1e7d314e4a026f060d1a82593ab3415b29dfb330bad9c30b1449920`. The original JSON-stat response is retained, not regenerated from manually seeded values.

An important verified failure mode: supplying `TIME_PERIOD` as `CodeValues` returned HTTP 200 and an **empty dataset**. This was a request-contract issue, resolved by `TimeRange`, not evidence that agriculture data were absent. The earlier national control probe remains in `istat_agriculture_national_probe.json*`; the successful query-to-SDMX URL is retained in `istat_agriculture_query_url_2020.json*`. Two broad direct SDMX catalog requests timed out after 90 seconds; those failures do not prevent the verified browser export route.

## Schema, measures and geography

The actual JSON-stat 2.0 dataset has ordered dimension IDs `FREQ`, `REF_AREA`, `DATA_TYPE`, `TIME_PERIOD`, sizes `[1,118,2,1]`, frequency `A`, and period `2020`. `DATA_TYPE` category order in the response is **ARU, HO**, even though the request lists **HO, ARU**. The municipal category order also differs from numeric sorting. The parser uses source indexes to decode row-major cell positions; it does not assume request order or alphabetical order.

- `HO`: source label `number of farms`; integer holding count, normalized as `agricultural_holdings`.
- `ARU`: source label `utilised agricultural area - hectares`; hectares, normalized as `utilised_agricultural_area`.
- The original source contains all 236 cells as nonnegative finite numeric values. `HO` cells are integers.
- All 118 `REF_AREA` values match the current registry, including Montoro `064121`. Source `NOTE_ISTAT_TERR_OFFICIAL_CODE` indexes match the selected municipal codes.
- No active `UNIT_MULT` indexes or active observation-status indexes occur in this response. The parser checks any active nonzero multiplier and rejects unreviewed observation-attribute index changes. Global status/unit **codelists** in the response are definitions, not flags applied to every cell. For example, a global `NOTE_DS` definition labelled `TEST` is not applied: its active dataset index is empty.

The source geography is **the municipality of the holding headquarters**. The land operated by that holding may be outside that municipality. Cultivation reference is agricultural year **2019/2020**; livestock reference in other tables is **1 December 2020**. The retrieved table has no livestock indicator. The official catalog separately exposes land-location and livestock-location flows; these are not mixed with headquarters data.

The municipal sums are **16,992 holdings** and **119,718.12 hectares assigned to holding headquarters in Avellino province**. Fontanarosa `064033` has **175 holdings** and **563.23 hectares**. These are verification results calculated/read from the downloaded file and are not substitutes for direct source attribution or land-cover measurements.

## Validation and update limits

The adapter checks JSON-stat version/class, exact dimension order and sizes, frequency/year, distinct category indexes, full official-code reconciliation, selected measure labels/units, source territorial attributes, multipliers, finite nonnegative values, integer holding counts and supported status representation. Missing cells become null/missing; standard JSON-stat confidentiality flag `c` becomes null/suppressed. Unknown flags or source-attribute formats fail ingestion instead of guessing. No missing or suppressed value is converted to zero.

The export API is a public backend of the official browser, rather than a separately guaranteed API service contract. Schema assertions deliberately make future changes visible. Production acquisition should additionally validate this route against a directly reproducible SDMX query and implement the official service's rate limits; ISTAT documents a five-query-per-minute SDMX limit at https://www.istat.it/classificazioni-e-strumenti/web-services-sdmx/. No further broad SDMX attempts were made after the bounded discovery failures.
