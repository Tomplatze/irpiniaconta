# Data availability and collection evidence

Generated: 2026-10-13T14:11:50.128429+00:00

All 81 scope entries are assessed. 76 have imported data or locally collected source records, including explicitly labelled partial/free alternatives. 17 are integrated into the legacy product-source store. 84 staged dataset families contain 1,714,245 source rows.

This is a collection inventory, not a claim that every dataset is integrated, current, complete, or suitable for municipal comparisons. A scope entry can name a broad portal; the 81 entries are not 81 independent downloadable datasets.

The curated 0.4 section publication selects 42 impact metrics over the verified collection. See [Sections](SECTIONS.md) for published periods, measured coverage and graphical presentation. Legacy integration counts below describe the original store, not the number of current selected metrics.

## Read and reproduce

```sh
.venv/bin/python -m etl.collect --offline
.venv/bin/python -m etl.collection_report
```

Install optional geographic dependencies with `pip install -r requirements-collection.txt`. Omit `--offline` only for a deliberate manual re-acquisition. Use `--only JOB_ID` to inspect a source independently. Commands never update the product database or activate scheduling. Original bytes and request provenance live in `data/raw/collection`; reconciled original-field rows, dictionaries and metadata live in `data/collection`.

## Interpretation rules

- Coverage means at least one source record is associated with a municipality. Absence is not zero and does not demonstrate absence of a service, business, protected site or infrastructure.
- Source periods, retrieval timestamps, estimates, forecasts, registers and reanalysis are distinct. There is no invented uniform current year.
- All original variables are retained in staged rows. No automatic sums across sector hierarchies, financial totals, project phases or multiple geographic locations are published.
- Original municipal codes are retained. Exact current-code/name crosswalks are explicit; historical municipal fusions are not silently aggregated.
- Open-source application code does not change source conditions. Attribution and the known source terms are recorded; unknown terms do not prevent local technical collection.

## Important verified limits

- BDAP 2024 budget and indicator exports cover all 118 municipal authorities. The 2025 export covers 117; missing code 064105. Latest reporting year is not automatically the best common comparison year.
- ISTAT ASIA local units/employees provide a free statistical alternative to a business-register extraction. Sector aggregates are not lists of companies or legal records.
- Municipal agriculture was observed in the 2020 census. Organic crop records cover 114 municipalities and irrigation 116. Missing/suppressed combinations are retained, not reconstructed.
- ISTAT projections are a median scenario, covering 17 Irpinia municipalities in the acquired export. They are not observed present-day population.
- Open-Meteo ERA5-Land supplies 2025 daily reanalysis at one interior sample point for all 118 municipalities. History 2020–2025 was acquired for the first 10 only; wider parallel history requests received HTTP 429. Nearby municipalities may share a grid cell. These are not station observations or municipal averages.
- Air/water measurements, hospitals, cultural places and mapped transport have limited observed spatial coverage. Hospital statistics in the acquired release refer to 2022, despite later file publication.
- PNRR joins use CUP plus local project code. Project amounts must not be multiplied across locations. ANAC authority-location and contract-location relationships remain separate.
- IdroGEO live detail contains population baselines from 2011/2021 and does not encode the hazard-map vintage in every response. Earthquake events are not a forecast or a risk ranking.
- SIAT layers may be historic. Independent source counts detect truncation and error payloads, including HTTP-200 errors.

- ISTAT monthly source rows include months 1–12 plus publisher-defined summary/adjustment rows 13 and 15. These are not 14 observed calendar months and must not be added blindly.
- OpenCivitas source variable dictionaries, privacy and anomaly flags are retained. Fund calculation components are not observed cash receipts; nursery standard needs are not counts of available nursery places.

## Category coverage

| Category | Scope entries | Entries with data/explicit alternatives |
|---|---:|---:|
| Demografia e migrazioni | 9 | 9 |
| Economia e imprese | 9 | 8 |
| Amministrazione e finanza | 9 | 8 |
| Investimenti e appalti | 7 | 7 |
| Agricoltura | 8 | 7 |
| Ambiente e territorio | 10 | 10 |
| Clima | 4 | 3 |
| Patrimonio culturale | 9 | 9 |
| Istruzione e servizi | 8 | 8 |
| Mobilità e abitazioni | 8 | 7 |

## All scope entries

| ID | Original scope title | Collection state | Associated municipalities | Evidence and limits |
|---|---|---|---:|---|
| DEM-01 | Popolazione per sesso ed età | integrated | 118 | Original institutional records and statistical periods are retained. Product integration and source-level collection are separate states. |
| DEM-02 | Bilancio demografico annuale | integrated | 118 | Original institutional records and statistical periods are retained. Product integration and source-level collection are separate states. |
| DEM-03 | Bilancio demografico mensile | collected | 118 | Original institutional records and statistical periods are retained. Product integration and source-level collection are separate states. |
| DEM-04 | Stranieri residenti | collected | 118 | Original institutional records and statistical periods are retained. Product integration and source-level collection are separate states. |
| DEM-05 | Censimenti storici della popolazione | collected | 118 | Original institutional records and statistical periods are retained. Product integration and source-level collection are separate states. |
| DEM-06 | Proiezioni demografiche comunali | partial | 17 | Acquired median-scenario population projections for 2025–2050 cover 17 municipalities. This is not current observed population or coverage of all 118. |
| DEM-07 | Basi territoriali e sezioni censuarie | collected | 118 | Original institutional records and statistical periods are retained. Product integration and source-level collection are separate states. |
| DEM-08 | Migrazioni e trasferimenti | collected | 118 | Monthly/annual demographic balances include arrivals/departures and internal/foreign migration. Migrants are flows, not the stock of foreign citizens. |
| DEM-09 | Famiglie e convivenze | collected | 118 | Original institutional records and statistical periods are retained. Product integration and source-level collection are separate states. |
| ECO-01 | Unità locali e settori ATECO | alternative | 118 | ISTAT ASIA 2023 supplies municipal statistical local-unit and employee counts by NACE, not a live business-register extract. |
| ECO-02 | Movimprese | partial | 0 | Official Unioncamere annual 2025 report acquired and its Avellino provincial business-demography table extracted. No municipal or newer quarterly detail acquired. |
| ECO-03 | Redditi IRPEF comunali | integrated | 118 | Original institutional records and statistical periods are retained. Product integration and source-level collection are separate states. |
| ECO-04 | Censimenti industria e servizi | alternative | 118 | ASIA municipal local-unit/employee statistics were collected; this does not reproduce every variable of the 2011 economic census. |
| ECO-05 | Open Government camerale | alternative | 118 | The Unioncamere portal is a discovery catalog, not one dataset. Collected ASIA supplies a free institutional municipal alternative for business structure. |
| ECO-06 | Occupazione e disoccupazione | collected | 118 | Original institutional records and statistical periods are retained. Product integration and source-level collection are separate states. |
| ECO-07 | Lavoro, pensioni e retribuzioni | partial | 118 | INPS pension data acquired at regional grain only. MEF has municipal pension-income frequencies/amounts, a different measure. |
| ECO-08 | Turismo e ricettività | collected | 118 | ISTAT municipal accommodation-capacity XLSX acquired for 2002–2025. It contains establishments, beds, rooms and bathrooms by accommodation type, not arrivals or hotel occupancy. |
| ECO-09 | Registro delle imprese | not_collected | 0 | Full company-register extracts and individual legal/business records are not a verified free bulk municipal dataset. ASIA supplies aggregate statistics but cannot replace individual register records. |
| PA-01 | Bilanci armonizzati | collected | 118 | 2024 statements cover all 118 municipal authorities; 2025 covers 117. Source fiscal codes, financial taxonomy and original blanks retained. |
| PA-02 | Bilanci storici | partial | 118 | Budget and indicator records for 2024 and 2025 acquired. Earlier pre-harmonization public archives not yet acquired or reconciled. |
| PA-03 | Incassi e pagamenti SIOPE | not_collected | 0 | SIOPE consultation is a separate cash-flow system. No anonymous bulk export/API for the 118 authorities has been verified in this collection. BDAP budget payment/receipt fields are annual alternatives, not monthly SIOPE. |
| PA-04 | Fabbisogni, spesa e servizi OpenCivitas | integrated | 118 | Original institutional records and statistical periods are retained. Product integration and source-level collection are separate states. |
| PA-05 | Enti e uffici pubblici IPA | integrated | 118 | Original institutional records and statistical periods are retained. Product integration and source-level collection are separate states. |
| PA-06 | Partecipazioni pubbliche | collected | 102 | MEF 2023 participation records acquired. Municipal authority fiscal identifiers use the verified BDAP crosswalk; company seats are distinct. |
| PA-07 | Personale pubblico e conto annuale | collected | 118 | Public 2024 personnel CSV exported successfully without email/credentials; BDAP authority IDs reconciled to budget authority identities. The source page/form discovery must be repeated if the export URL changes. |
| PA-08 | Trasferimenti e certificati finanziari | partial | 118 | OpenCivitas 2026 municipal solidarity-fund component distribution acquired. These are allocation/calculation components, not cash receipts or all financial certificates. |
| PA-09 | Amministratori e mandati | collected | 118 | Original institutional records and statistical periods are retained. Product integration and source-level collection are separate states. |
| INV-01 | Politiche di coesione e progetti | collected | 118 | Original institutional records and statistical periods are retained. Product integration and source-level collection are separate states. |
| INV-02 | CIG, appalti e contratti | collected | 118 | Official 2025 ANAC CSV monthly partitions were downloaded via links in the national catalog; the catalog API returned an HTML rejection. PNRR contracts are separately collected. Distinguish authority from contract location. |
| INV-03 | Monitoraggio opere pubbliche | partial | 118 | OpenCoesione supplies cohesion-funded project records associated with municipal locations, not the complete BDAP MOP inventory. |
| INV-04 | Finanziamenti PA Digitale 2026 | integrated | 118 | Original institutional records and statistical periods are retained. Product integration and source-level collection are separate states. |
| INV-05 | PNRR e Italia Domani | collected | 118 | Original institutional records and statistical periods are retained. Product integration and source-level collection are separate states. |
| INV-06 | Anagrafe CUP | partial | 118 | OpenCUP subject records were acquired. Subject municipality is not investment location. Full national projects (1.7 GB ZIP) and localization bulk require a separate streamed join. PNRR/OpenCoesione already provide project-level alternatives. |
| INV-07 | Interventi e fondi regionali | partial | 118 | Campania cohesion projects include program/fund classifications. This is not an exhaustive record of every regional grant scheme. |
| AGR-01 | Aziende agricole e SAU | integrated | 118 | Original institutional records and statistical periods are retained. Product integration and source-level collection are separate states. |
| AGR-02 | Coltivazioni e utilizzazione dei terreni | collected | 118 | Original institutional records and statistical periods are retained. Product integration and source-level collection are separate states. |
| AGR-03 | Allevamenti e consistenza dei capi | collected | 118 | Original institutional records and statistical periods are retained. Product integration and source-level collection are separate states. |
| AGR-04 | Irrigazione | collected | 116 | Original institutional records and statistical periods are retained. Product integration and source-level collection are separate states. |
| AGR-05 | Manodopera agricola | collected | 118 | Original institutional records and statistical periods are retained. Product integration and source-level collection are separate states. |
| AGR-06 | Agricoltura biologica | collected | 114 | Organic crop source covers 114 current municipal codes in census 2020. No record for the remaining municipalities must not be interpreted as zero. |
| AGR-07 | Censimenti agricoli storici | collected | 117 | Complete official national historical archive acquired; code-only data and all dimension dictionaries are streamed for exact current municipal codes. Former municipality codes are retained in source and not silently merged. |
| AGR-08 | Produzioni e qualità DOP/IGP | not_collected | 0 | Official regional pages for Taurasi, Greco di Tufo, Fiano di Avellino and Irpinia wine specifications downloaded as reference documents. A structured annual municipal production-volume distribution is not verified. Legal production areas are not statistical production amounts. |
| AMB-01 | Consumo di suolo | integrated | 118 | Original institutional records and statistical periods are retained. Product integration and source-level collection are separate states. |
| AMB-02 | Confini amministrativi | collected | 118 | Original institutional records and statistical periods are retained. Product integration and source-level collection are separate states. |
| AMB-03 | Dissesto idrogeologico | collected | 118 | IdroGEO municipal public detail acquired for each current municipal code. Baselines and hazard-map vintages differ; no present-day risk forecasts are inferred. |
| AMB-04 | Rifiuti urbani e raccolta differenziata | collected | 118 | Original institutional records and statistical periods are retained. Product integration and source-level collection are separate states. |
| AMB-05 | Qualità dell’aria | collected | 3 | 2025 ARPAC measurement records are associated through declared station identifiers. Sentinel -9999 is retained. Monitored-town coverage is not all municipalities. |
| AMB-06 | Acque e qualità ambientale | collected | 20 | ARPAC surface-water and groundwater 2025 source partitions collected, with original censored measurements and units. The early 2026 surface-water partition contains no Avellino records. |
| AMB-07 | Aree protette e Natura 2000 | partial | 69 | Natura 2000 December 2025 sites and original geometry acquired; this does not include every other protected-area designation. |
| AMB-08 | Copertura del suolo CORINE | collected | 118 | Actual CORINE 2018 vector classes and geometries downloaded for the Irpinia bounding box with independently checked IDs/counts. Resolution is not comparable to high-resolution soil consumption. |
| AMB-09 | Cartografia e pianificazione SIAT | collected | 118 | Multiple SIAT layers acquired. Positive independent counts are required; layers with errors or truncation are rejected until complete exports are collected. |
| AMB-10 | Sismicità e pericolosità | partial | 65 | Recorded INGV earthquake epicentres for 2020–2026 are acquired. Events cannot replace seismic hazard maps or zoning. |
| CLI-01 | Serie climatiche SCIA | alternative | 118 | SCIA station export remains restricted/unverified for bulk ingestion. ERA5-Land reanalysis through Open-Meteo supplies a different free point-based historical source. |
| CLI-02 | Rianalisi ERA5-Land | alternative | 118 | The CDS workflow needs an account/token; the same ERA5-Land model is acquired through the public Open-Meteo API, with different hosting limits. |
| CLI-03 | Stazioni meteorologiche regionali | not_collected | 0 | No validated regional historical station export covering municipalities was acquired. ARPAC station metadata exists and Open-Meteo provides reanalysis for all 118, a different measurement model. |
| CLI-04 | Indicatori climatici territoriali | alternative | 118 | Daily ERA5-Land values permit later derived annual climate summaries. No ASTer climate table or climate index is claimed imported. |
| CUL-01 | Castelli | integrated | 39 | Original institutional records and statistical periods are retained. Product integration and source-level collection are separate states. |
| CUL-02 | Complessi religiosi | integrated | 13 | Original institutional records and statistical periods are retained. Product integration and source-level collection are separate states. |
| CUL-03 | Biblioteche | integrated | 87 | Original institutional records and statistical periods are retained. Product integration and source-level collection are separate states. |
| CUL-04 | Aree archeologiche | integrated | 19 | Original institutional records and statistical periods are retained. Product integration and source-level collection are separate states. |
| CUL-05 | Palazzi storici | integrated | 30 | Original institutional records and statistical periods are retained. Product integration and source-level collection are separate states. |
| CUL-06 | Beni culturali e catalogazione | partial | 2 | ArCo public SPARQL yielded 30 catalog/location relations for Avellino province. Relation roles retained; shooting/collecting locations are not current object storage. Not an exhaustive municipal inventory. |
| CUL-07 | Musei e luoghi della cultura | collected | 36 | MiC regional JSON-LD cultural-site graph acquired. 55 sites are associated with 36 current municipalities. Individual record freshness is not stated. |
| CUL-08 | Torri e strutture fortificate SIAT | collected | 70 | Complete SIAT tower/castle layer acquired; independent count verifies 74 source features. Features are not necessarily open or accessible to visitors. |
| CUL-09 | Centri storici e paesaggio | collected | 116 | SIAT historic-center/landscape layers acquired and checked against independent counts. Source cartography can be historic. |
| SER-01 | Scuole statali | integrated | 118 | Original institutional records and statistical periods are retained. Product integration and source-level collection are separate states. |
| SER-02 | Scuole paritarie | collected | 26 | Original institutional records and statistical periods are retained. Product integration and source-level collection are separate states. |
| SER-03 | Istituti scolastici provinciali | integrated | 33 | Original institutional records and statistical periods are retained. Product integration and source-level collection are separate states. |
| SER-04 | Edilizia e caratteristiche scolastiche | collected | 114 | School-building locations and reported surrounding-environment fields acquired for 2024/25. Rows are school/building associations, not distinct building counts. |
| SER-05 | Istruzione e titoli di studio | collected | 118 | Original institutional records and statistical periods are retained. Product integration and source-level collection are separate states. |
| SER-06 | Asili nido e servizi sociali | collected | 118 | OpenCivitas 2023 and 2022 social/nursery indicators and original dictionaries acquired using official entity crosswalks. Privacy, anomaly and missing flags preserved; standard needs are not service availability. |
| SER-07 | Strutture sanitarie | partial | 3 | Public/equivalent hospital structural statistics refer to 2022 and occur in three municipalities. Outpatient structures and current capacity require a separate source. |
| SER-08 | Farmacie e assistenza territoriale | integrated | 118 | Original institutional records and statistical periods are retained. Product integration and source-level collection are separate states. |
| MOB-01 | Strade provinciali | integrated | 0 | Original institutional records and statistical periods are retained. Product integration and source-level collection are separate states. |
| MOB-02 | Ordinanze e cantieri stradali | partial | 6 | Actual public provincial GeoJSON retained locally with original notices, date text and coordinates. It mixes road notices with other construction projects and includes expired date ranges. No current road closure, automatic validity interval or exhaustive works inventory inferred. Specific reuse terms were not supplied; local collection is separate from public redistribution. |
| MOB-03 | Ferrovie e stazioni | alternative | 55 | Historic SIAT railway line data exported completely using Esri JSON despite GeoJSON errors; OpenStreetMap rails/stations are separately available. Neither source proves current operating status. |
| MOB-04 | Trasporto pubblico e fermate | partial | 54 | OpenStreetMap supplies mapped stops/platforms. No reachable official open GTFS timetable covering Irpinia has been verified. |
| MOB-05 | Parco veicolare | collected | 118 | ACI 2024 municipal vehicle-category sheet covers all 118 municipalities. Registered stock is not road traffic. |
| MOB-06 | Pendolarismo e spostamenti | collected | 118 | Municipal commuting census export returns 2018–2019, not 2024; all origin/activity/gender dimensions retained. |
| MOB-07 | Abitazioni ed edifici | collected | 118 | Original institutional records and statistical periods are retained. Product integration and source-level collection are separate states. |
| MOB-08 | Quotazioni immobiliari OMI | not_collected | 0 | OMI public consultation is identified but no anonymous reusable bulk quote export is verified. Census housing counts are available but cannot replace market-price quotations. |

## Staged source families and available fields

### istat-boundaries-2026

Records: 118; associated municipalities: 118/118; periods: 2026-01-01.

Original detailed municipal geometry, actual PRJ transformation, representative interior points derived for weather sampling.

Staging file: `data/collection/istat-boundaries-2026.rows.jsonl.gz`; SHA-256: `eb0882a2240cf663841044f1f8aa06fac35a2e62ff4230d696de9feddc440573`.

- `municipal_boundaries` (3 fields): `properties`, `geometry`, `source_crs`
- Coverage by period: 2026-01-01: 118/118

Source: [istat-boundaries-2026](https://www.istat.it/storage/cartografia/confini_amministrativi/generalizzati/2026/Limiti01012026_g.zip)

### istat-183_285_df_dica_asiaulp_3

Records: 23,382; associated municipalities: 118/118; periods: 2023.

Preserve category hierarchy, source flags and original precision. No sums across overlapping classifications. Latest period is returned by the source, not inferred from the request.

Staging file: `data/collection/istat-183_285_df_dica_asiaulp_3.rows.jsonl.gz`; SHA-256: `a1c17301c90dac6e25c3f7c21dca232b1c22497d6abc1deb79042d8f6064538b`.

- `observations` (7 fields): `FREQ`, `REF_AREA`, `DATA_TYPE`, `ECON_ACTIVITY_NACE_2007`, `TIME_PERIOD`, `value`, `source_status`
- Coverage by period: 2023: 118/118
- Original definitions: `data/collection/istat-183_285_df_dica_asiaulp_3.dimensions.json`; SHA-256 `43d97a1dbca328e19bea4722dddb87649b05a17aee4e006f564d90ff5f666dcc`.

Source: [istat-183_285_df_dica_asiaulp_3](https://esploradati.istat.it/databrowserhub/api/core/nodes/1/datasets/IT1,183_285_DF_DICA_ASIAULP_3,1.0/data)

### istat-df_dcat_censagric2020_crops_all

Records: 3,960; associated municipalities: 118/118; periods: 2020.

Preserve category hierarchy, source flags and original precision. No sums across overlapping classifications. Latest period is returned by the source, not inferred from the request.

Staging file: `data/collection/istat-df_dcat_censagric2020_crops_all.rows.jsonl.gz`; SHA-256: `df70d94b21a041f4ffb5c34b6afe7ba7cb89d7b5998a73da4b91d978c3738d99`.

- `observations` (7 fields): `FREQ`, `REF_AREA`, `DATA_TYPE`, `TYPE_OF_CROP`, `TIME_PERIOD`, `value`, `source_status`
- Coverage by period: 2020: 118/118
- Original definitions: `data/collection/istat-df_dcat_censagric2020_crops_all.dimensions.json`; SHA-256 `e0575456543cce64113fd9339efefe6eaf03750168481fed8bc7fe7c55a05815`.

Source: [istat-df_dcat_censagric2020_crops_all](https://esploradati.istat.it/databrowserhub/api/core/nodes/2/datasets/IT1,DF_DCAT_CENSAGRIC2020_CROPS_ALL,1.0/data)

### istat-df_dcat_censagric2020_cattle_all

Records: 6,110; associated municipalities: 118/118; periods: 2020.

Preserve category hierarchy, source flags and original precision. No sums across overlapping classifications. Latest period is returned by the source, not inferred from the request.

Staging file: `data/collection/istat-df_dcat_censagric2020_cattle_all.rows.jsonl.gz`; SHA-256: `3a28e95dba3b112381658470fa98cefc1f99b1589c8538bb2689a752d8120b6d`.

- `observations` (8 fields): `FREQ`, `REF_AREA`, `DATA_TYPE`, `TYPE_OF_HERD`, `HEADS_NUMBER`, `TIME_PERIOD`, `value`, `source_status`
- Coverage by period: 2020: 118/118
- Original definitions: `data/collection/istat-df_dcat_censagric2020_cattle_all.dimensions.json`; SHA-256 `201742651f9e6ea844f2b779e069c782ed6e09019d5499ac439e4b295a189a4d`.

Source: [istat-df_dcat_censagric2020_cattle_all](https://esploradati.istat.it/databrowserhub/api/core/nodes/2/datasets/IT1,DF_DCAT_CENSAGRIC2020_CATTLE_ALL,1.0/data)

### istat-df_dcat_censagric2020_org_crops

Records: 1,910; associated municipalities: 114/118; periods: 2020.

Preserve category hierarchy, source flags and original precision. No sums across overlapping classifications. Latest period is returned by the source, not inferred from the request.

Staging file: `data/collection/istat-df_dcat_censagric2020_org_crops.rows.jsonl.gz`; SHA-256: `2325de1d5ffbdbcb0c240b9afe27cd6747ef89701f5c99f8356823a70f517b52`.

- `observations` (7 fields): `FREQ`, `REF_AREA`, `DATA_TYPE`, `TYPE_OF_CROP`, `TIME_PERIOD`, `value`, `source_status`
- Coverage by period: 2020: 114/118
- Original definitions: `data/collection/istat-df_dcat_censagric2020_org_crops.dimensions.json`; SHA-256 `d9f5350e05929c80cdd5b1d491e7839c72248549689631194b31fe485114e7ae`.

Source: [istat-df_dcat_censagric2020_org_crops](https://esploradati.istat.it/databrowserhub/api/core/nodes/2/datasets/IT1,DF_DCAT_CENSAGRIC2020_ORG_CROPS,1.0/data)

### istat-df_dcat_censagric2020_surf_irr_cons

Records: 496; associated municipalities: 116/118; periods: 2020.

Preserve category hierarchy, source flags and original precision. No sums across overlapping classifications. Latest period is returned by the source, not inferred from the request.

Staging file: `data/collection/istat-df_dcat_censagric2020_surf_irr_cons.rows.jsonl.gz`; SHA-256: `82ad6edcae14503d93a20ce066c4b36d43392d4069215c8226008bb76e2df393`.

- `observations` (6 fields): `FREQ`, `REF_AREA`, `DATA_TYPE`, `TIME_PERIOD`, `value`, `source_status`
- Coverage by period: 2020: 116/118
- Original definitions: `data/collection/istat-df_dcat_censagric2020_surf_irr_cons.dimensions.json`; SHA-256 `67b7ef2d5fe22633e16fdfafa4193744b8b40e3b26e52fcb4d04cd3eac3ae8b2`.

Source: [istat-df_dcat_censagric2020_surf_irr_cons](https://esploradati.istat.it/databrowserhub/api/core/nodes/2/datasets/IT1,DF_DCAT_CENSAGRIC2020_SURF_IRR_CONS,1.0/data)

### istat-df_dcat_censagric2020_labcat_all

Records: 9,013; associated municipalities: 118/118; periods: 2020.

Preserve category hierarchy, source flags and original precision. No sums across overlapping classifications. Latest period is returned by the source, not inferred from the request.

Staging file: `data/collection/istat-df_dcat_censagric2020_labcat_all.rows.jsonl.gz`; SHA-256: `fb91599c42ec344811db0ca8599ef8c200e7b6bd051d71ca55c9056824583ced`.

- `observations` (8 fields): `FREQ`, `REF_AREA`, `DATA_TYPE`, `LABOUR_FORCE_CATEG`, `SEX`, `TIME_PERIOD`, `value`, `source_status`
- Coverage by period: 2020: 118/118
- Original definitions: `data/collection/istat-df_dcat_censagric2020_labcat_all.dimensions.json`; SHA-256 `874d3db5622e8d601f930d440e771bb788498ee2b80d0c5631ae27b72d29511b`.

Source: [istat-df_dcat_censagric2020_labcat_all](https://esploradati.istat.it/databrowserhub/api/core/nodes/2/datasets/IT1,DF_DCAT_CENSAGRIC2020_LABCAT_ALL,1.0/data)

### istat-df_dcss_popres_series_tv_1

Records: 1,652; associated municipalities: 118/118; periods: 1951, 1961, 1971, 1981, 1991, 2001, 2011, 2018, 2019, 2020, 2021, 2022, 2023, 2024.

Preserve category hierarchy, source flags and original precision. No sums across overlapping classifications. Latest period is returned by the source, not inferred from the request.

Staging file: `data/collection/istat-df_dcss_popres_series_tv_1.rows.jsonl.gz`; SHA-256: `4e680c569356c4d822f3b61be7a1e2ed0330c755c6a94cefcbc08f9ebeaa5422`.

- `observations` (6 fields): `FREQ`, `REF_AREA`, `INDICATOR`, `TIME_PERIOD`, `value`, `source_status`
- Coverage by period: 1951: 118/118, 1961: 118/118, 1971: 118/118, 1981: 118/118, 1991: 118/118, 2001: 118/118, 2011: 118/118, 2018: 118/118, 2019: 118/118, 2020: 118/118, 2021: 118/118, 2022: 118/118, 2023: 118/118, 2024: 118/118
- Original definitions: `data/collection/istat-df_dcss_popres_series_tv_1.dimensions.json`; SHA-256 `2584e0220e5c763f21b5cafb9b20262da321e1a9a4436cda19b8a6e72a90755b`.

Source: [istat-df_dcss_popres_series_tv_1](https://esploradati.istat.it/databrowserhub/api/core/nodes/3/datasets/IT1,DF_DCSS_POPRES_SERIES_TV_1,1.0/data)

### istat-df_dcss_pop_demcitmig_tv_3

Records: 9,351; associated municipalities: 118/118; periods: 2024.

Preserve category hierarchy, source flags and original precision. No sums across overlapping classifications. Latest period is returned by the source, not inferred from the request.

Staging file: `data/collection/istat-df_dcss_pop_demcitmig_tv_3.rows.jsonl.gz`; SHA-256: `5ec65a60f039e2bd2632f6dce8573ce6cc58fdef91644c50c8b31c0f2de60b85`.

- `observations` (8 fields): `FREQ`, `REF_AREA`, `INDICATOR`, `GENDER`, `AREA_CONTRY_CITIZEN`, `TIME_PERIOD`, `value`, `source_status`
- Coverage by period: 2024: 118/118
- Original definitions: `data/collection/istat-df_dcss_pop_demcitmig_tv_3.dimensions.json`; SHA-256 `95b763398aecddaddcadf8ef76df091646680a82ee40b69a6702540cdeb200d3`.

Source: [istat-df_dcss_pop_demcitmig_tv_3](https://esploradati.istat.it/databrowserhub/api/core/nodes/3/datasets/IT1,DF_DCSS_POP_DEMCITMIG_TV_3,1.0/data)

### istat-df_dcss_fam_pop_tv_1

Records: 2,911; associated municipalities: 118/118; periods: 2018, 2019, 2020, 2021, 2022, 2023, 2024.

Preserve category hierarchy, source flags and original precision. No sums across overlapping classifications. Latest period is returned by the source, not inferred from the request.

Staging file: `data/collection/istat-df_dcss_fam_pop_tv_1.rows.jsonl.gz`; SHA-256: `a9223a0589d1969b51e85520dbd84b283d7a8696d1bb4e2a25fb712f24aff9ff`.

- `observations` (6 fields): `FREQ`, `REF_AREA`, `INDICATOR`, `TIME_PERIOD`, `value`, `source_status`
- Coverage by period: 2018: 118/118, 2019: 118/118, 2020: 118/118, 2021: 118/118, 2022: 118/118, 2023: 118/118, 2024: 118/118
- Original definitions: `data/collection/istat-df_dcss_fam_pop_tv_1.dimensions.json`; SHA-256 `97603a3d9aca5776665db6cebc7597c8d9585d55babc2ab8fefc5758da85168d`.

Source: [istat-df_dcss_fam_pop_tv_1](https://esploradati.istat.it/databrowserhub/api/core/nodes/3/datasets/IT1,DF_DCSS_FAM_POP_TV_1,1.0/data)

### istat-df_dcss_istr_lav_pen_2_tv_3

Records: 15,926; associated municipalities: 118/118; periods: 2024.

Preserve category hierarchy, source flags and original precision. No sums across overlapping classifications. Latest period is returned by the source, not inferred from the request.

Staging file: `data/collection/istat-df_dcss_istr_lav_pen_2_tv_3.rows.jsonl.gz`; SHA-256: `a27708cc51836630403bc55797c21c2c5d0f187f8a337585e67396349fc5ba4b`.

- `observations` (9 fields): `FREQ`, `REF_AREA`, `INDICATOR`, `GENDER`, `AGE_NOCLASS`, `CUR_ACT_STAT`, `TIME_PERIOD`, `value`, `source_status`
- Coverage by period: 2024: 118/118
- Original definitions: `data/collection/istat-df_dcss_istr_lav_pen_2_tv_3.dimensions.json`; SHA-256 `951aacd3aabdfbf157bcf26439d80964b9e1d4908c697f5525f9117b1b18685c`.

Source: [istat-df_dcss_istr_lav_pen_2_tv_3](https://esploradati.istat.it/databrowserhub/api/core/nodes/3/datasets/IT1,DF_DCSS_ISTR_LAV_PEN_2_TV_3,1.0/data)

### istat-df_dcss_istr_lav_pen_2_tv_1

Records: 13,378; associated municipalities: 118/118; periods: 2024.

Preserve category hierarchy, source flags and original precision. No sums across overlapping classifications. Latest period is returned by the source, not inferred from the request.

Staging file: `data/collection/istat-df_dcss_istr_lav_pen_2_tv_1.rows.jsonl.gz`; SHA-256: `fc1140198238689785680533b0191e5b56931e6e4ad5601fe656fc0a340420be`.

- `observations` (9 fields): `FREQ`, `REF_AREA`, `INDICATOR`, `GENDER`, `AGE_NOCLASS`, `EDU_ATTAIN`, `TIME_PERIOD`, `value`, `source_status`
- Coverage by period: 2024: 118/118
- Original definitions: `data/collection/istat-df_dcss_istr_lav_pen_2_tv_1.dimensions.json`; SHA-256 `60d8264a8ca42cdc2a18499f8c09f38db17574d9ce05abd59f0c6337d9218b18`.

Source: [istat-df_dcss_istr_lav_pen_2_tv_1](https://esploradati.istat.it/databrowserhub/api/core/nodes/3/datasets/IT1,DF_DCSS_ISTR_LAV_PEN_2_TV_1,1.0/data)

### istat-df_dcss_abitazioni_tv_1

Records: 1,062; associated municipalities: 118/118; periods: 2019, 2021, 2023.

Preserve category hierarchy, source flags and original precision. No sums across overlapping classifications. Latest period is returned by the source, not inferred from the request.

Staging file: `data/collection/istat-df_dcss_abitazioni_tv_1.rows.jsonl.gz`; SHA-256: `9e7e7d55e758530569eef200caea5ce0a94291808e449d96b743e782a93da6d6`.

- `observations` (6 fields): `FREQ`, `REF_AREA`, `INDICATOR`, `TIME_PERIOD`, `value`, `source_status`
- Coverage by period: 2019: 118/118, 2021: 118/118, 2023: 118/118
- Original definitions: `data/collection/istat-df_dcss_abitazioni_tv_1.dimensions.json`; SHA-256 `e1c533a385318ed62bedc02ab37ccaa05a33c22aa1867b51400f08d3b7466720`.

Source: [istat-df_dcss_abitazioni_tv_1](https://esploradati.istat.it/databrowserhub/api/core/nodes/3/datasets/IT1,DF_DCSS_ABITAZIONI_TV_1,1.0/data)

### istat-commuting_2018_2026

Records: 6,372; associated municipalities: 118/118; periods: 2018, 2019.

Preserve category hierarchy, source flags and original precision. No sums across overlapping classifications. Latest period is returned by the source, not inferred from the request.

Staging file: `data/collection/istat-commuting_2018_2026.rows.jsonl.gz`; SHA-256: `267324c526450d8708d52a397af4a24b54c5688da20689a147ea32c8db0bbac6`.

- `observations` (9 fields): `FREQ`, `REF_AREA`, `INDICATOR`, `GENDER`, `LOC_DEST`, `REAS_COMMUTING`, `TIME_PERIOD`, `value`, `source_status`
- Coverage by period: 2018: 118/118, 2019: 118/118
- Original definitions: `data/collection/istat-commuting_2018_2026.dimensions.json`; SHA-256 `d3760b82f1328235ad6cfee6c372c2ab0abbb6c86d57e865170b9a3192e5f959`.

Source: [istat-commuting_2018_2026](https://esploradati.istat.it/databrowserhub/api/core/nodes/3/datasets/IT1,DF_DCSS_ISTR_LAV_PEN_2_TV_5,1.0/data)

### istat-sections-2023

Records: 4,278; associated municipalities: 118/118; periods: 2023.

Section grain; statistical treatment and field definitions must be reviewed before aggregation.

Staging file: `data/collection/istat-sections-2023.rows.jsonl.gz`; SHA-256: `73d62b4d32542b6a26996a79ffc695b22ac0047c9ec38fab936c13f4baee75cb`.

- `R15_Campania_2023_sezioni` (138 fields): `CODREG`, `REGIONE`, `CODPRO`, `PROVINCIA`, `CODCOM`, `COMUNE`, `PROCOM`, `SEZ21_ID`, `COM_ASC1`, `COM_ASC2`, `COM_ASC3`, `P1`, `P2`, `P3`, `P14`, `P15`, `P16`, `P17`, `P18`, `P19`, `P20`, `P21`, `P22`, `P23`, `P24`, `P25`, `P26`, `P27`, `P28`, `P29`, `P30`, `P31`, `P32`, `P33`, `P34`, `P35`, `P36`, `P37`, `P38`, `P39`, `P40`, `P41`, `P42`, `P43`, `P44`, `P45`, `P67`, `P68`, `P69`, `P70`, `P71`, `P72`, `P73`, `P74`, `P75`, `P76`, `P77`, `P78`, `P79`, `P80`, `P81`, `P82`, `P83`, `P84`, `P85`, `P86`, `P87`, `P88`, `P89`, `P90`, `P91`, `P92`, `P93`, `P94`, `P95`, `P96`, `P97`, `P98`, `P99`, `P100`, `P101`, `P102`, `P103`, `IT1`, `IT2`, `IT3`, `IT4`, `IT5`, `IT6`, `IT7`, `IT8`, `IT9`, `IT10`, `IT11`, `IT12`, `ST1`, `ST2`, `ST2_B`, `ST3`, `ST4`, `ST5`, `ST16`, `ST17`, `ST18`, `ST19`, `ST20`, `ST21`, `ST22`, `ST23`, `ST24`, `ST25`, `ST26`, `ST27`, `ST28`, `ST29`, `ST30`, `ST31`, `ST32`, `ST33`, `EM1`, `EM2`, `EM3`, `EM4`, `EM5`, `EM6`, `PF1`, `PF3`, `PF4`, `PF5`, `PF6`, `PF7`, `PF8`, `PF9`, `NA1`, `A2`, `A3`, `A5`, `A8`
- Coverage by period: 2023: 118/118
- Original definitions: `data/collection/istat-sections-2023.dictionary.json`; SHA-256 `15cfc9099bac12fcdbafe288314f057a0547eafe0cc5149a3e0f5ffb47a7a6a8`.

Source: [istat-sections-2023](https://esploradati.istat.it/databrowser/DWL/PERMPOP/SUBCOM/Dati_regionali_2023.zip)

### aci-vehicles-2024

Records: 118; associated municipalities: 118/118; periods: 2024.

Registered vehicles, not road traffic or trips. Municipal sheet only.

Staging file: `data/collection/aci-vehicles-2024.rows.jsonl.gz`; SHA-256: `aa0a22f1ed4a5ac11ab8aa7e0e4132a7686dbe115cf894bf288642b5fee289ee`.

- `45_Comune_categoria` (16 fields): `Area Geografica`, `Regione`, `Provincia`, `Comune`, `AUTOBUS`, `AUTOCARRI TRASPORTO MERCI`, `AUTOVEICOLI SPECIALI / SPECIFICI`, `AUTOVETTURE`, `MOTOCARRI E QUADRICICLI TRASPORTO MERCI`, `MOTOCICLI`, `MOTOVEICOLI E QUADRICICLI SPECIALI / SPECIFICI`, `RIMORCHI E SEMIRIMORCHI SPECIALI / SPECIFICI`, `RIMORCHI E SEMIRIMORCHI TRASPORTO MERCI`, `TRATTORI STRADALI O MOTRICI`, `NON DEFINITO`, `Totale`
- Coverage by period: 2024: 118/118

Source: [aci-vehicles-2024](https://aci.gov.it//app/uploads/2025/11/Autoritratto-2024-OD.zip)

### ispra-waste-2024

Records: 118; associated municipalities: 118/118; periods: 2024.

Region(2)+province(3)+municipality(3) identifier; missing hyphens preserved. Per-capita denominators require population from the same year.

Staging file: `data/collection/ispra-waste-2024.rows.jsonl.gz`; SHA-256: `2f37daf7fb64e670988f3366449f3d3f52436c853905f2a8e4d39e27136cab9b`.

- `ispra_waste_2024.csv` (25 fields): `IstatComune`, `Regione`, `Provincia`, `Comune`, `Popolazione`, `Dato riferito a`, `Frazione umida(1) (t)`, `Verde (t)`, `Carta e cartone (t)`, `Vetro (t)`, `Legno (t)`, `Metallo (t)`, `Plastica (t)`, `RAEE (t)`, `Tessili (t)`, `Selettiva (t)`, `Rifiuti da C e D (t)`, `Pulizia stradale a recupero (t)`, `Ingombranti misti a recupero (t)`, `Altro (t)`, `Totale RD (t)`, `Ingombranti a smaltimento (t)`, `Indifferenziato (t)`, `Totale RU (t)`, `Percentuale RD (%)`
- Coverage by period: 2024: 118/118

Source: [ispra-waste-2024](https://www.catasto-rifiuti.isprambiente.it/get/getDettaglioComunale.csv.php?&aa=2024)

### mim-private-schools-202627

Records: 64; associated municipalities: 26/118; periods: 2026/2027.

Original fields and missingness retained.

Staging file: `data/collection/mim-private-schools-202627.rows.jsonl.gz`; SHA-256: `88ac79285d9483a03730cf52804072ba52a4c21b71f1a67c64a78d8a686b08d5`.

- `mim_par_202627.csv` (14 fields): `ANNOSCOLASTICO`, `AREAGEOGRAFICA`, `REGIONE`, `PROVINCIA`, `CODICESCUOLA`, `DENOMINAZIONESCUOLA`, `INDIRIZZOSCUOLA`, `CAPSCUOLA`, `CODICECOMUNESCUOLA`, `DESCRIZIONECOMUNE`, `DESCRIZIONETIPOLOGIAGRADOISTRUZIONESCUOLA`, `INDIRIZZOEMAILSCUOLA`, `INDIRIZZOPECSCUOLA`, `SITOWEBSCUOLA`
- Coverage by period: 2026/2027: 26/118

Source: [mim-private-schools-202627](https://dati.istruzione.it/opendata/SCUANAGRAFEPAR20262720260901.csv)

### health-hospitals-2022

Records: 3; associated municipalities: 3/118; periods: 2022.

Original fields and missingness retained.

Staging file: `data/collection/health-hospitals-2022.rows.jsonl.gz`; SHA-256: `f91a6fdc1dfcd91478f265fedba3e46af1114ec3c12854bb60ec5e02c4178918`.

- `health_hospitals.csv` (26 fields): `anno`, `codice_struttura`, `denominazione_struttura`, `comune`, `sigla_provincia_struttura`, `posti_letto_previsti`, `posti_letto_utilizzati`, `personale_uomini`, `personale_donne`, `totale_personale`, `medici_uomini`, `medici_donne`, `medici`, `infermieri_uomini`, `infermieri_donne`, `infermieri`, `ricoveri`, `giornate_degenza`, `giornate_disponibili`, `codice_tipo_struttura`, `Sottotipo struttura`, `Tipo struttura`, `codice_regione`, `Regione`, `codice_asl`, `asl`
- Coverage by period: 2022: 3/118

Source: [health-hospitals-2022](https://www.dati.salute.gov.it/sites/default/files/2025-01/Strutture_di_ricovero_pubbliche_presenti_nel_territorio_della_ASL.csv)

### interior-administrators-20260824

Records: 1,730; associated municipalities: 118/118; periods: 2026-08-24.

Original fields and missingness retained.

Staging file: `data/collection/interior-administrators-20260824.rows.jsonl.gz`; SHA-256: `ff5d78875d940a2408fa28c980b78505db8ed9de211d8a0f3962ec13dcdae956`.

- `admins_avellino.csv` (19 fields): `codice_regione`, `codice_provincia`, `codice_comune`, `denominazione_comune`, `sigla_provincia`, `popolazione_censita_alla_data_elezione`, `cognome`, `nome`, `sesso`, `data_nascita`, `luogo_nascita`, `livello_carica`, `descrizione_carica`, `incarico`, `data_elezione`, `data_entrata_in_carica`, `lista_appartenenza/collegamento`, `titolo_studio`, `professione`
- Coverage by period: 2026-08-24: 118/118

Source: [interior-administrators-20260824](https://dait.interno.gov.it/documenti/provincia_di_avellino.csv)

### arpac-groundwater-2025

Records: 244; associated municipalities: 10/118; periods: 2025.

Original fields and missingness retained.

Staging file: `data/collection/arpac-groundwater-2025.rows.jsonl.gz`; SHA-256: `a895bccb35a61a2270b0ca20c580da826122e0cabe58f6add7e82c899b49a0c8`.

- `monitoraggio-acque-sotterranee-s12.csv` (27 fields): `_id`, `cod_rete`, `Descrizione rete stazione`, `Cod tipologia rete`, `Cod ost appartenenza`, `Den ost appartenenza`, `Nat ost appartenenza cod`, `Nat ost appartenenza desc`, `cod_staz`, `Desc Staz`, `Cod tipologia staz`, `Desc tipologia staz`, `Tipo stazione`, `Cod Regione`, `Nome regione`, `Cod provincia`, `Nome prov`, `Cod comune`, `Nome comune`, `data`, `ANNO prelievo`, `inq`, `Desc inq`, `Metodo`, `Valore mis`, `um`, `gpi`
- Coverage by period: 2025: 10/118

Source: [arpac-groundwater-2025](https://dati.arpacampania.it/dataset/6056e19c-770d-422f-85bb-2875310e9765/resource/be2425d2-7cbf-4787-9468-c536644acd57/download/42f06f37-4602-4b84-9fc7-936b36ffbd47.csv)

### opencup-subjects

Records: 630; associated municipalities: 118/118; periods: 2026-09-01.

Source records, not a complete inventory of every municipality. OpenCUP subject location is not project location.

Staging file: `data/collection/opencup-subjects.rows.jsonl.gz`; SHA-256: `e64b61ea7a65e1b67408bceb07add07b7f6648c44af90b46368c3e93f3e8afa6`.

- `OpenCup_Soggetti.csv` (16 fields): `SOGGETTO_TITOLARE`, `PIVA_CODFISCALE_SOG_TITOLARE`, `INDIRIZZO_SOG_TITOLARE`, `TIPO_INDIRIZZO_SOG_TITOLARE`, `NUM_CIVICO_SOG_TITOLARE`, `LOCALITA_SOG_TITOLARE`, `CAP_SOGGETTO_TITOLARE`, `COMUNE_SOGGETTO_TITOLARE`, `CODICE_COMUNE_SOGG_TITOLARE`, `CODICE_SOTTOCATEG_SOGGETTO`, `SOTTOCATEGORIA_SOGGETTO`, `CODICE_CATEGORIA_SOGGETTO`, `CATEGORIA_SOGGETTO`, `CODICE_AREA_SOGGETTO`, `AREA_SOGGETTO`, `SOGGETTO_RICHIEDENTE`
- Coverage by period: 2026-09-01: 118/118

Source: [opencup-subjects](https://www.opencup.gov.it/portale/documents/21195/299152/OpendataSoggetti.zip/411e1e80-bce0-d085-bb96-b8036deb590f?t=1708680664714)

### opencoesione-campania-20260630

Records: 12,346; associated municipalities: 118/118; periods: 2017-04-30, 2017-06-30, 2017-12-31, 2018-06-30, 2019-02-28, 2019-06-30, 2020-02-29, 2020-06-30, 2020-12-31, 2021-06-30, 2022-04-30, 2022-10-31, 2023-02-28, 2023-06-30, 2023-10-31, 2024-04-30, 2025-02-28, 2025-04-30, 2025-06-30, 2025-08-31, 2025-10-31, 2025-12-31, 2026-02-28, 2026-04-30, 2026-06-30.

Projects associated with municipal locations; multi-location projects kept once. Do not allocate their whole cost to each municipality. Wider provincial/regional projects remain in the original source archive.

Staging file: `data/collection/opencoesione-campania-20260630.rows.jsonl.gz`; SHA-256: `44865df21ae1f7be7ccdae74c8ca0ef0d81acf69f194db88a0a7507c73cad782`.

- `progetti_esteso_CAM_20260630.csv` (204 fields): `COD_LOCALE_PROGETTO`, `CUP`, `OC_TITOLO_PROGETTO`, `OC_SINTESI_PROGETTO`, `OC_LINK`, `OC_COD_CICLO`, `OC_DESCR_CICLO`, `OC_COD_TEMA_SINTETICO`, `OC_TEMA_SINTETICO`, `COD_GRANDE_PROGETTO`, `DESCRIZIONE_GRANDE_PROGETTO`, `CUP_COD_NATURA`, `CUP_DESCR_NATURA`, `CUP_COD_TIPOLOGIA`, `CUP_DESCR_TIPOLOGIA`, `CUP_COD_SETTORE`, `CUP_DESCR_SETTORE`, `CUP_COD_SOTTOSETTORE`, `CUP_DESCR_SOTTOSETTORE`, `CUP_COD_CATEGORIA`, `CUP_DESCR_CATEGORIA`, `COD_ATECO`, `DESCRIZIONE_ATECO`, `OC_COD_TIPO_AIUTO`, `OC_DESCR_TIPO_AIUTO`, `OC_MACROAREA_PROGETTO`, `OC_MACROAREA_PROGRAMMA`, `OC_COD_SLL`, `OC_DENOMINAZIONE_SLL`, `FINANZ_UE`, `FINANZ_UE_FESR`, `FINANZ_UE_FSE`, `FINANZ_UE_FEASR`, `FINANZ_UE_FEAMP`, `FINANZ_UE_IOG`, `FINANZ_UE_ALTRO`, `FINANZ_STATO_FONDO_DI_ROTAZIONE`, `FINANZ_STATO_FSC`, `FINANZ_STATO_PAC`, `FINANZ_STATO_COMPLETAMENTI`, `FINANZ_STATO_ALTRI_PROVVEDIMENTI`, `FINANZ_REGIONE`, `FINANZ_PROVINCIA`, `FINANZ_COMUNE`, `FINANZ_RISORSE_LIBERATE`, `FINANZ_ALTRO_PUBBLICO`, `FINANZ_STATO_ESTERO`, `FINANZ_PRIVATO`, `FINANZ_DA_REPERIRE`, `FINANZ_TOTALE_PUBBLICO`, `ECONOMIE_TOTALI`, `ECONOMIE_TOTALI_PUBBLICHE`, `OC_FINANZ_UE_NETTO`, `OC_FINANZ_UE_FESR_NETTO`, `OC_FINANZ_UE_FSE_NETTO`, `OC_FINANZ_UE_FEASR_NETTO`, `OC_FINANZ_UE_FEAMP_NETTO`, `OC_FINANZ_UE_IOG_NETTO`, `OC_FINANZ_UE_ALTRO_NETTO`, `OC_FINANZ_STATO_FONDO_ROT_NETTO`, `OC_FINANZ_STATO_FSC_NETTO`, `OC_FINANZ_STATO_PAC_NETTO`, `OC_FINANZ_STATO_COMPL_NETTO`, `OC_FINANZ_STATO_ALTRI_PROV_NETTO`, `OC_FINANZ_REGIONE_NETTO`, `OC_FINANZ_PROVINCIA_NETTO`, `OC_FINANZ_COMUNE_NETTO`, `OC_FINANZ_RISORSE_LIBERATE_NETTO`, `OC_FINANZ_ALTRO_PUBBLICO_NETTO`, `OC_FINANZ_STATO_ESTERO_NETTO`, `OC_FINANZ_PRIVATO_NETTO`, `OC_FINANZ_TOT_PUB_NETTO`, `OC_COSTO_COESIONE`, `IMPEGNI`, `OC_IMPEGNI_GIURID_VINCOLANTI`, `OC_IMPEGNI_TRASFERIMENTI`, `OC_IMPEGNI_COESIONE`, `TOT_PAGAMENTI`, `OC_TOT_PAGAMENTI_BENEFICIARI`, `OC_TOT_PAGAMENTI_TRASFERIMENTI`, `OC_PAGAMENTI_COESIONE`, `COSTO_REALIZZATO`, `OC_DATA_INIZIO_PROGETTO`, `OC_DATA_FINE_PROGETTO_PREVISTA`, `OC_DATA_FINE_PROGETTO_EFFETTIVA`, `OC_STATO_FINANZIARIO`, `OC_STATO_PROGETTO`, `OC_STATO_PROCEDURALE`, `OC_COD_FASE_CORRENTE`, `OC_DESCR_FASE_CORRENTE`, `OC_FLAG_CUP`, `OC_FLAG_REGIONE_UNICA`, `OC_FLAG_VISUALIZZAZIONE`, `OC_FLAG_SNAI`, `DATA_AGGIORNAMENTO`, `COD_REGIONE`, `DEN_REGIONE`, `COD_PROVINCIA`, `DEN_PROVINCIA`, `COD_COMUNE`, `DEN_COMUNE`, `OC_AMBITO`, `OC_COD_FONTE`, `OC_DESCR_FONTE`, `FONDO_COMUNITARIO`, `OC_CODICE_PROGRAMMA`, `OC_DESCRIZIONE_PROGRAMMA`, `COD_OB_TEMATICO`, `DESCR_OB_TEMATICO`, `COD_PRIORITA_INVEST`, `DESCR_PRIORITA_INVEST`, `OC_COD_CATEGORIA_SPESA`, `OC_DESCR_CATEGORIA_SPESA`, `OC_ARTICOLAZIONE_PROGRAMMA`, `OC_COD_ARTICOLAZ_PROGRAMMA`, `OC_DESCR_ARTICOLAZ_PROGRAMMA`, `OC_SUBARTICOLAZIONE_PROGRAMMA`, `OC_COD_SUBARTICOLAZ_PROGRAMMA`, `OC_DESCR_SUBARTICOLAZ_PROGRAMMA`, `COD_STRUMENTO`, `DESCR_STRUMENTO`, `DESCR_TIPO_STRUMENTO`, `COD_PROCED_ATTIVAZIONE`, `DESCR_PROCED_ATTIVAZIONE`, `COD_TIPO_PROCED_ATTIVAZIONE`, `DESCR_TIPO_PROCED_ATTIVAZIONE`, `COSTO_RENDICONTABILE_UE`, `OC_TOT_PAGAMENTI_RENDICONTAB_UE`, `OC_TOT_PAGAMENTI_FSC`, `OC_TOT_PAGAMENTI_PAC`, `OC_FLAG_PAC`, `DATA_INIZIO_PREV_STUDIO_FATT`, `DATA_FINE_PREV_STUDIO_FATT`, `DATA_INIZIO_EFF_STUDIO_FATT`, `DATA_FINE_EFF_STUDIO_FATT`, `DATA_INIZIO_PREV_PROG_PREL`, `DATA_FINE_PREV_PROG_PREL`, `DATA_INIZIO_EFF_PROG_PREL`, `DATA_FINE_EFF_PROG_PREL`, `DATA_INIZIO_PREV_PROG_DEF`, `DATA_FINE_PREV_PROG_DEF`, `DATA_INIZIO_EFF_PROG_DEF`, `DATA_FINE_EFF_PROG_DEF`, `DATA_INIZIO_PREV_PROG_ESEC`, `DATA_FINE_PREV_PROG_ESEC`, `DATA_INIZIO_EFF_PROG_ESEC`, `DATA_FINE_EFF_PROG_ESEC`, `DATA_INIZIO_PREV_AGG_BANDO`, `DATA_FINE_PREV_AGG_BANDO`, `DATA_INIZIO_EFF_AGG_BANDO`, `DATA_FINE_EFF_AGG_BANDO`, `DATA_INIZIO_PREV_STIP_ATTRIB`, `DATA_FINE_PREV_STIP_ATTRIB`, `DATA_INIZIO_EFF_STIP_ATTRIB`, `DATA_FINE_EFF_STIP_ATTRIB`, `DATA_INIZIO_PREV_ESECUZIONE`, `DATA_FINE_PREV_ESECUZIONE`, `DATA_INIZIO_EFF_ESECUZIONE`, `DATA_FINE_EFF_ESECUZIONE`, `DATA_INIZIO_PREV_COLLAUDO`, `DATA_FINE_PREV_COLLAUDO`, `DATA_INIZIO_EFF_COLLAUDO`, `DATA_FINE_EFF_COLLAUDO`, `OC_CODFISC_PROGRAMMATORE`, `OC_DENOM_PROGRAMMATORE`, `OC_COD_FORMA_GIU_PROGRAMMATORE`, `OC_DESCR_FORMA_GIU_PROGRAMMATORE`, `OC_TOTALE_PROGRAMMATORI`, `OC_CODFISC_ATTUATORE`, `OC_DENOM_ATTUATORE`, `OC_COD_FORMA_GIU_ATTUATORE`, `OC_DESCR_FORMA_GIU_ATTUATORE`, `OC_TOTALE_ATTUATORI`, `OC_CODFISC_BENEFICIARIO`, `OC_DENOM_BENEFICIARIO`, `OC_COD_FORMA_GIU_BENEFICIARIO`, `OC_DESCR_FORMA_GIU_BENEFICIARIO`, `OC_TOTALE_BENEFICIARI`, `OC_CODFISC_REALIZZATORE`, `OC_DENOM_REALIZZATORE`, `OC_COD_FORMA_GIU_REALIZZATORE`, `OC_DESCR_FORMA_GIU_REALIZZATORE`, `OC_TOTALE_REALIZZATORI`, `OC_TOTALE_INDICATORI`, `COD_INDICATORE_1`, `DESCR_INDICATORE_1`, `UNITA_MISURA_INDICATORE_1`, `PROGRAMMATO_INDICATORE_1`, `REALIZZATO_INDICATORE_1`, `COD_INDICATORE_2`, `DESCR_INDICATORE_2`, `UNITA_MISURA_INDICATORE_2`, `PROGRAMMATO_INDICATORE_2`, `REALIZZATO_INDICATORE_2`, `COD_INDICATORE_3`, `DESCR_INDICATORE_3`, `UNITA_MISURA_INDICATORE_3`, `PROGRAMMATO_INDICATORE_3`, `REALIZZATO_INDICATORE_3`, `COD_INDICATORE_4`, `DESCR_INDICATORE_4`, `UNITA_MISURA_INDICATORE_4`, `PROGRAMMATO_INDICATORE_4`, `REALIZZATO_INDICATORE_4`
- Coverage by period: 2017-04-30: 1/118, 2017-06-30: 42/118, 2017-12-31: 46/118, 2018-06-30: 17/118, 2019-02-28: 7/118, 2019-06-30: 1/118, 2020-02-29: 63/118, 2020-06-30: 36/118, 2020-12-31: 48/118, 2021-06-30: 3/118, 2022-04-30: 1/118, 2022-10-31: 2/118, 2023-02-28: 1/118, 2023-06-30: 2/118, 2023-10-31: 82/118, 2024-04-30: 71/118, 2025-02-28: 1/118, 2025-04-30: 85/118, 2025-06-30: 1/118, 2025-08-31: 82/118, 2025-10-31: 117/118, 2025-12-31: 94/118, 2026-02-28: 71/118, 2026-04-30: 41/118, 2026-06-30: 118/118

Source: [opencoesione-campania-20260630](https://opencoesione.gov.it/it/opendata/regioni/progetti_esteso_CAM.zip)

### bdap-budget-2025

Records: 98,839; associated municipalities: 117/118; periods: 2025.

ELCOMU authorities only. Statements contain overlapping totals and line items; no automatic sum. Latest reporting year may be incomplete.

Staging file: `data/collection/bdap-budget-2025.rows.jsonl.gz`; SHA-256: `0050d88a0030a4b930fd725c3028a2615b2bccab78a02f0e08949d411ef913c7`.

- `2025_Bilanci di Rendiconto SDB Allegato l Parametri Obiettivi per Comuni_CAMPANIA.csv` (20 fields): `Esercizio Finanziario`, `Codice Tipologia Soggetto`, `Descrizione Tipologia Soggetto`, `Codice BDAP`, `Denominazione Soggetto`, `CF Soggetto`, `Data Cessazione Soggetto`, `Codice Zona Geografica`, `Descrizione Zona Geografica`, `Codice Regione`, `Descrizione Regione`, `Codice Provincia`, `Descrizione Provincia`, `Codice Comune`, `Descrizione Comune`, `Ordine di Esposizione`, `Codice Parametro Deficitario`, `Parametro Deficitario`, `Valore Parametro Deficitarietà`, `_unnamed_20`
- `2025_Bilanci di Rendiconto SDB Allegato m Parametri Obiettivi per Provincie e Città Metropolitane_CAMPANIA.csv` (20 fields): `Esercizio Finanziario`, `Codice Tipologia Soggetto`, `Descrizione Tipologia Soggetto`, `Codice BDAP`, `Denominazione Soggetto`, `CF Soggetto`, `Data Cessazione Soggetto`, `Codice Zona Geografica`, `Descrizione Zona Geografica`, `Codice Regione`, `Descrizione Regione`, `Codice Provincia`, `Descrizione Provincia`, `Codice Comune`, `Descrizione Comune`, `Ordine di Esposizione`, `Codice Parametro Deficitario`, `Parametro Deficitario`, `Valore Parametro Deficitarietà`, `_unnamed_20`
- `2025_Bilanci di Rendiconto SDB Allegato n Parametri Obiettivi per Comunità Montane_CAMPANIA.csv` (20 fields): `Esercizio Finanziario`, `Codice Tipologia Soggetto`, `Descrizione Tipologia Soggetto`, `Codice BDAP`, `Denominazione Soggetto`, `CF Soggetto`, `Data Cessazione Soggetto`, `Codice Zona Geografica`, `Descrizione Zona Geografica`, `Codice Regione`, `Descrizione Regione`, `Codice Provincia`, `Descrizione Provincia`, `Codice Comune`, `Descrizione Comune`, `Ordine di Esposizione`, `Codice Parametro Deficitario`, `Parametro Deficitario`, `Valore Parametro Deficitarietà`, `_unnamed_20`
- `2025_Rendiconto SDB Allegato A Risultato di Amministrazione_CAMPANIA.csv` (27 fields): `Esercizio Finanziario`, `Codice Tipologia Soggetto`, `Descrizione Tipologia Soggetto`, `Codice BDAP`, `Denominazione Soggetto`, `CF Soggetto`, `Data Cessazione Soggetto`, `Codice Zona Geografica`, `Descrizione Zona Geografica`, `Codice Regione`, `Descrizione Regione`, `Codice Provincia`, `Descrizione Provincia`, `Codice Comune`, `Descrizione Comune`, `Cod Voce Ris Amm Rend`, `Desc Voce Ris Amm Rend`, `Ordine di esposizione`, `Residui di Gestione`, `Competenza di Gestione`, `Totale di Gestione`, `ResAtt CR Acc Trib Stim DEF`, `ResAtt CC Acc Trib Stim DEF`, `ResAtt TOT Acc Trib Stim DEF`, `Di cui Disav Deb Autoriz e non Contr`, `Di cui Incassato su Tot Res Attivi`, `_unnamed_27`
- `2025_Rendiconto SDB Allegato a1 Risultato di Amministrazione Quote Accantonate_CAMPANIA.csv` (26 fields): `Esercizio Finanziario`, `Codice Tipologia Soggetto`, `Descrizione Tipologia Soggetto`, `Codice BDAP`, `Denominazione Soggetto`, `CF Soggetto`, `Data Cessazione Soggetto`, `Codice Zona Geografica`, `Descrizione Zona Geografica`, `Codice Regione`, `Descrizione Regione`, `Codice Provincia`, `Descrizione Provincia`, `Codice Comune`, `Descrizione Comune`, `Ordine di esposizione`, `Progressivo Riga`, `Voce Accantonamento`, `Codice Capitolo di Spesa`, `Descrizione Capitolo di Spesa`, `Risorse Accantonate al 1°Gennaio`, `Risorse Accantonate Applicate al Bilancio dell'Esercizio`, `Risorse Accantonate Stanziate nella Spesa del Bilancio dell'Esercizio`, `Variazione degli Accantonamenti Effettuata in Sede di Rendiconto`, `Risorse Accantonate nel Risultato di Amministrazione al 31 Dicembre`, `_unnamed_26`
- `2025_Rendiconto SDB Allegato a2 Risultato di Amministrazione Quote Vincolate_CAMPANIA.csv` (33 fields): `Esercizio Finanziario`, `Codice Tipologia Soggetto`, `Descrizione Tipologia Soggetto`, `Codice BDAP`, `Denominazione Soggetto`, `CF Soggetto`, `Data Cessazione Soggetto`, `Codice Zona Geografica`, `Descrizione Zona Geografica`, `Codice Regione`, `Descrizione Regione`, `Codice Provincia`, `Descrizione Provincia`, `Codice Comune`, `Descrizione Comune`, `Ordine di Esposizione`, `Progressivo Riga`, `Codice Voce Vincolo`, `Voce Vincolo`, `Codice Capitolo di Entrata`, `Descrizione Capitolo di Entrata`, `Codice Capitolo di Uscita`, `Descrizione Capitolo di Uscita`, `Risorse Vincolate nel Risultato di Amministrazione 1° Gennaio`, `Risorse Vincolate Applicate al Bilancio dell'Esercizio`, `Entrate Vincolate Accertate nell'Esercizio`, `Imp. Finanziati da Entr. Vinc. Accertate nell'Esercizio o da Quote Vincolate del Risultato di Ammi.ne`, `Fondo Pluriennale Vincolato al 31/12`, `Cancellazione: Residui Attivi Vinc, Vincolo su Quote Risultato di Ammin(+), Residui Passivi da Risorse Vincolate(-)`, `Impegni Finanziati dal Fondo Pluriennale di Entrata Cancellati`, `Risorse Vincolate nel Bilancio al 31/12`, `Risorse Vincolate nel Risultato di Amministrazione al 31/12`, `_unnamed_33`
- `2025_Rendiconto SDB Allegato a3 Risultato di Amministrazione Quote Destinate_CAMPANIA.csv` (29 fields): `Esercizio Finanziario`, `Codice Tipologia Soggetto`, `Descrizione Tipologia Soggetto`, `Codice BDAP`, `Denominazione Soggetto`, `CF Soggetto`, `Data Cessazione Soggetto`, `Codice Zona Geografica`, `Descrizione Zona Geografica`, `Codice Regione`, `Descrizione Regione`, `Codice Provincia`, `Descrizione Provincia`, `Codice Comune`, `Descrizione Comune`, `Ordine di esposizione`, `Progressivo Riga`, `Voce Investimenti`, `Codice Capitolo di Entrata`, `Descrizione Capitolo di Entrata`, `Codice Capitolo di Uscita`, `Descrizione Capitolo di Uscita`, `Risorse Destinate agli Investimenti al 1 Gennaio`, `Entrate Destinate agli Investimenti Accertate nell'Esercizio`, `Importo Impregni Imputati Esercizio del Rendiconto`, `Importo Complessivo Stanziamenti Fondo Pluriennale`, `Cancellazione di Risorse Destinate agli Investimenti`, `Importo Complessivo delle Quote Destinate agli Investimenti`, `_unnamed_29`
- `2025_Rendiconto SDB Allegato B FPV - Fondo Pluriennale Vincolato_CAMPANIA.csv` (29 fields): `Esercizio Finanziario`, `Codice Tipologia Soggetto`, `Descrizione Tipologia Soggetto`, `Codice BDAP`, `Denominazione Soggetto`, `CF Soggetto`, `Data Cessazione Soggetto`, `Codice Zona Geografica`, `Descrizione Zona Geografica`, `Codice Regione`, `Descrizione Regione`, `Codice Provincia`, `Descrizione Provincia`, `Codice Comune`, `Descrizione Comune`, `Codice Missione Arconet`, `Desc Missione Arconet`, `Codice Programma Arconet`, `Desc Programma Arconet`, `Imp. FPV EP`, `Impeg. Spese 1Anno`, `Econ. in CC`, `Econ. in CC Impeg. Pluriennali`, `Quota FP 2Anno  e Successivi`, `Impeg. Spese 2Anno`, `Impeg. Spese 3Anno`, `Impeg. Spese Imputaz. ND`, `FPV 1Anno`, `_unnamed_29`
- `2025_Rendiconto SDB Allegato C FCDE - Composizione Fondo Svalutazione Crediti_CAMPANIA.csv` (24 fields): `Esercizio Finanziario`, `Codice Tipologia Soggetto`, `Descrizione Tipologia Soggetto`, `Codice BDAP`, `Denominazione Soggetto`, `CF Soggetto`, `Data Cessazione Soggetto`, `Codice Zona Geografica`, `Descrizione Zona Geografica`, `Codice Regione`, `Descrizione Regione`, `Codice Provincia`, `Descrizione Provincia`, `Codice Comune`, `Descrizione Comune`, `Tot. Crediti - R.Attivi`, `Tot. Crediti - C.Stralc.`, `Tot. Crediti - Accert. ES`, `Fondo Sv.Crediti - RA`, `Fondo Sv. Crediti - C.Stralc.`, `Fondo Sv. Crediti - Accert. ES`, `Totale Crediti`, `Tot. Fondo Sv. Crediti`, `_unnamed_24`
- `2025_Rendiconto SDB Allegato C FCDE - Fondo Crediti Dubbia Esigibilita_CAMPANIA.csv` (35 fields): `Esercizio Finanziario`, `Codice Tipologia Soggetto`, `Descrizione Tipologia Soggetto`, `Codice BDAP`, `Denominazione Soggetto`, `CF Soggetto`, `Data Cessazione Soggetto`, `Codice Zona Geografica`, `Descrizione Zona Geografica`, `Codice Regione`, `Descrizione Regione`, `Codice Provincia`, `Descrizione Provincia`, `Codice Comune`, `Descrizione Comune`, `Codice Titolo Entrata Arconet`, `Desc Titolo Entrata Arconet`, `Cod Tipologia Entrata Arconet`, `Desc Tipologia Entrata Arconet`, `Res. Att. 1Anno`, `Res. Att. EP`, `Tot. Res. Att. 1Anno`, `Imp. Min. Fondo`, `Fondo Cr. DE`, `Res.Att.Accert.per Cassa 1Anno`, `Res.Att.Accert.per Cassa EP`, `Tot. Res.Att.Accert. per Cassa`, `Res.Att.non Accert.Cassa 1Anno`, `Res.Att.non Accert.Cassa EP`, `Tot. Res.Att.non Accert. Cassa`, `Perc. Acc. al Fondo`, `Perc.Acc.Fondo nonAccert.Cassa`, `Imp.Min.Fondo non Accert.Cassa`, `Imp. Fondo non Accert. Cassa`, `_unnamed_35`
- `2025_Rendiconto SDB Allegato C FCDE - Voce di Riepilogo_CAMPANIA.csv` (29 fields): `Esercizio Finanziario`, `Codice Tipologia Soggetto`, `Descrizione Tipologia Soggetto`, `Codice BDAP`, `Denominazione Soggetto`, `CF Soggetto`, `Data Cessazione Soggetto`, `Codice Zona Geografica`, `Descrizione Zona Geografica`, `Codice Regione`, `Descrizione Regione`, `Codice Provincia`, `Descrizione Provincia`, `Codice Comune`, `Descrizione Comune`, `Codice Titolo Entrata Arconet`, `Desc Titolo Entrata Arconet`, `Cod Tipologia Entrata Arconet`, `Desc Tipologia Entrata Arconet`, `Cod Comp Accant Fond Cred DE`, `Voce Comp Accant Fondo Cred DE`, `N Ord Comp Accant Fond Cred DE`, `Res. Att. 1Anno`, `Perc. Acc. al Fondo`, `Res. Att. EP`, `Tot. Res. Att. 1Anno`, `Imp. Min. Fondo`, `Fondo Cr. DE`, `_unnamed_29`
- `2025_Rendiconto SDB Allegato C FCDE Parziale_CAMPANIA.csv` (28 fields): `Esercizio Finanziario`, `Codice Tipologia Soggetto`, `Descrizione Tipologia Soggetto`, `Codice BDAP`, `Denominazione Soggetto`, `CF Soggetto`, `Data Cessazione Soggetto`, `Codice Zona Geografica`, `Descrizione Zona Geografica`, `Codice Regione`, `Descrizione Regione`, `Codice Provincia`, `Descrizione Provincia`, `Codice Comune`, `Descrizione Comune`, `Codice Titolo Entrata Arconet`, `Desc Titolo Entrata Arconet`, `Cod Tipologia Entrata Arconet`, `Desc Tipologia Entrata Arconet`, `Cod Categoria Entrata Arconet`, `Desc Categoria Entrata Arconet`, `Res. Att. 1Anno`, `Res. Att. EP`, `Perc. Acc. al Fondo`, `Tot. Res. Att. 1Anno`, `Imp. Min. Fondo`, `Fondo Cr. DE`, `_unnamed_28`
- `2025_Rendiconto SDB Allegato d Entrate per Categorie Enti Locali_CAMPANIA.csv` (26 fields): `Esercizio Finanziario`, `Codice Tipologia Soggetto`, `Descrizione Tipologia Soggetto`, `Codice BDAP`, `Denominazione Soggetto`, `CF Soggetto`, `Data Cessazione Soggetto`, `Codice Zona Geografica`, `Descrizione Zona Geografica`, `Codice Regione`, `Descrizione Regione`, `Codice Provincia`, `Descrizione Provincia`, `Codice Comune`, `Descrizione Comune`, `Codice Titolo Entrata Arconet`, `Desc Titolo Entrata Arconet`, `Cod Tipologia Entrata Arconet`, `Desc Tipologia Entrata Arconet`, `Cod Categoria Entrata Arconet`, `Desc Categoria Entrata Arconet`, `Accertamenti`, `Riscossioni in C/Residui`, `di cui entrate accertate non ricorrenti`, `Riscossioni in C/Competenza`, `_unnamed_26`
- `2025_Rendiconto SDB Allegato d Entrate per Categorie Regioni_CAMPANIA.csv` (26 fields): `Esercizio Finanziario`, `Codice Tipologia Soggetto`, `Descrizione Tipologia Soggetto`, `Codice BDAP`, `Denominazione Soggetto`, `CF Soggetto`, `Data Cessazione Soggetto`, `Codice Zona Geografica`, `Descrizione Zona Geografica`, `Codice Regione`, `Descrizione Regione`, `Codice Provincia`, `Descrizione Provincia`, `Codice Comune`, `Descrizione Comune`, `Codice Titolo Entrata Arconet`, `Desc Titolo Entrata Arconet`, `Cod Tipologia Entrata Arconet`, `Desc Tipologia Entrata Arconet`, `Cod Categoria Entrata Arconet`, `Desc Categoria Entrata Arconet`, `Accertamenti`, `Riscossioni in C/Residui`, `di cui entrate accertate non ricorrenti`, `Riscossioni in C/Competenza`, `_unnamed_26`
- `2025_Rendiconto SDB Allegato e Riepilogo Spese per Macroaggregato - Impegni_CAMPANIA.csv` (24 fields): `Esercizio Finanziario`, `Codice Tipologia Soggetto`, `Descrizione Tipologia Soggetto`, `Codice BDAP`, `Denominazione Soggetto`, `CF Soggetto`, `Data Cessazione Soggetto`, `Codice Zona Geografica`, `Descrizione Zona Geografica`, `Codice Regione`, `Descrizione Regione`, `Codice Provincia`, `Descrizione Provincia`, `Codice Comune`, `Descrizione Comune`, `Codice Titolo`, `Descrizione Titolo`, `Codice Secondo Livello`, `Descrizione Secondo Livello`, `Codice Macroaggregato Spesa`, `Descrizione Macroaggregato Spesa`, `Impegni Riepilogo`, `Di Cui Non Ricorrenti`, `_unnamed_24`
- `2025_Rendiconto SDB Allegato e Spese Correnti per Macroaggregato - Impegni_CAMPANIA.csv` (27 fields): `Esercizio Finanziario`, `Codice Tipologia Soggetto`, `Descrizione Tipologia Soggetto`, `Codice BDAP`, `Denominazione Soggetto`, `CF Soggetto`, `Data Cessazione Soggetto`, `Codice Zona Geografica`, `Descrizione Zona Geografica`, `Codice Regione`, `Descrizione Regione`, `Codice Provincia`, `Descrizione Provincia`, `Codice Comune`, `Descrizione Comune`, `Codice Missione Arconet`, `Desc Missione Arconet`, `Codice Programma Arconet`, `Desc Programma Arconet`, `Codice Titolo`, `Descrizione Titolo`, `Codice Secondo Livello`, `Descrizione Secondo Livello`, `Codice Macroaggregato Spesa`, `Descrizione Macroaggregato Spesa`, `Impegni`, `_unnamed_27`
- `2025_Rendiconto SDB Allegato e Spese Correnti per Macroaggregato - Pagamenti Conto Competenza_CAMPANIA.csv` (27 fields): `Esercizio Finanziario`, `Codice Tipologia Soggetto`, `Descrizione Tipologia Soggetto`, `Codice BDAP`, `Denominazione Soggetto`, `CF Soggetto`, `Data Cessazione Soggetto`, `Codice Zona Geografica`, `Descrizione Zona Geografica`, `Codice Regione`, `Descrizione Regione`, `Codice Provincia`, `Descrizione Provincia`, `Codice Comune`, `Descrizione Comune`, `Codice Missione Arconet`, `Desc Missione Arconet`, `Codice Programma Arconet`, `Desc Programma Arconet`, `Codice Titolo`, `Descrizione Titolo`, `Codice Secondo Livello`, `Descrizione Secondo Livello`, `Codice Macroaggregato Spesa`, `Descrizione Macroaggregato Spesa`, `Pagamenti C/Competenza`, `_unnamed_27`
- `2025_Rendiconto SDB Allegato e Spese Correnti per Macroaggregato - Pagamenti Conto Residui_CAMPANIA.csv` (27 fields): `Esercizio Finanziario`, `Codice Tipologia Soggetto`, `Descrizione Tipologia Soggetto`, `Codice BDAP`, `Denominazione Soggetto`, `CF Soggetto`, `Data Cessazione Soggetto`, `Codice Zona Geografica`, `Descrizione Zona Geografica`, `Codice Regione`, `Descrizione Regione`, `Codice Provincia`, `Descrizione Provincia`, `Codice Comune`, `Descrizione Comune`, `Codice Missione Arconet`, `Desc Missione Arconet`, `Codice Programma Arconet`, `Desc Programma Arconet`, `Codice Titolo`, `Descrizione Titolo`, `Codice Secondo Livello`, `Descrizione Secondo Livello`, `Codice Macroaggregato Spesa`, `Descrizione Macroaggregato Spesa`, `Pagamenti C/Residui`, `_unnamed_27`
- `2025_Rendiconto SDB Allegato e Spese in Conto Capitale per Macroaggregato - Impegni_CAMPANIA.csv` (27 fields): `Esercizio Finanziario`, `Codice Tipologia Soggetto`, `Descrizione Tipologia Soggetto`, `Codice BDAP`, `Denominazione Soggetto`, `CF Soggetto`, `Data Cessazione Soggetto`, `Codice Zona Geografica`, `Descrizione Zona Geografica`, `Codice Regione`, `Descrizione Regione`, `Codice Provincia`, `Descrizione Provincia`, `Codice Comune`, `Descrizione Comune`, `Codice Missione Arconet`, `Desc Missione Arconet`, `Codice Programma Arconet`, `Desc Programma Arconet`, `Codice Titolo`, `Descrizione Titolo`, `Codice Secondo Livello`, `Descrizione Secondo Livello`, `Codice Macroaggregato Spesa`, `Descrizione Macroaggregato Spesa`, `Impegni`, `_unnamed_27`
- `2025_Rendiconto SDB Allegato e Spese in Conto Capitale per Macroaggregato - Pagamenti Conto Competenza_CAMPANIA.csv` (27 fields): `Esercizio Finanziario`, `Codice Tipologia Soggetto`, `Descrizione Tipologia Soggetto`, `Codice BDAP`, `Denominazione Soggetto`, `CF Soggetto`, `Data Cessazione Soggetto`, `Codice Zona Geografica`, `Descrizione Zona Geografica`, `Codice Regione`, `Descrizione Regione`, `Codice Provincia`, `Descrizione Provincia`, `Codice Comune`, `Descrizione Comune`, `Codice Missione Arconet`, `Desc Missione Arconet`, `Codice Programma Arconet`, `Desc Programma Arconet`, `Codice Titolo`, `Descrizione Titolo`, `Codice Secondo Livello`, `Descrizione Secondo Livello`, `Codice Macroaggregato Spesa`, `Descrizione Macroaggregato Spesa`, `Pagamenti C/Competenza`, `_unnamed_27`
- `2025_Rendiconto SDB Allegato e Spese in Conto Capitale per Macroaggregato - Pagamenti Conto Residui_CAMPANIA.csv` (27 fields): `Esercizio Finanziario`, `Codice Tipologia Soggetto`, `Descrizione Tipologia Soggetto`, `Codice BDAP`, `Denominazione Soggetto`, `CF Soggetto`, `Data Cessazione Soggetto`, `Codice Zona Geografica`, `Descrizione Zona Geografica`, `Codice Regione`, `Descrizione Regione`, `Codice Provincia`, `Descrizione Provincia`, `Codice Comune`, `Descrizione Comune`, `Codice Missione Arconet`, `Desc Missione Arconet`, `Codice Programma Arconet`, `Desc Programma Arconet`, `Codice Titolo`, `Descrizione Titolo`, `Codice Secondo Livello`, `Descrizione Secondo Livello`, `Codice Macroaggregato Spesa`, `Descrizione Macroaggregato Spesa`, `Pagamenti C/Residui`, `_unnamed_27`
- `2025_Rendiconto SDB Allegato e Spese per Rimborso di Prestiti per Macroaggregato - Impegni_CAMPANIA.csv` (27 fields): `Esercizio Finanziario`, `Codice Tipologia Soggetto`, `Descrizione Tipologia Soggetto`, `Codice BDAP`, `Denominazione Soggetto`, `CF Soggetto`, `Data Cessazione Soggetto`, `Codice Zona Geografica`, `Descrizione Zona Geografica`, `Codice Regione`, `Descrizione Regione`, `Codice Provincia`, `Descrizione Provincia`, `Codice Comune`, `Descrizione Comune`, `Codice Missione Arconet`, `Desc Missione Arconet`, `Codice Programma Arconet`, `Desc Programma Arconet`, `Codice Titolo`, `Descrizione Titolo`, `Codice Secondo Livello`, `Descrizione Secondo Livello`, `Codice Macroaggregato Spesa`, `Descrizione Macroaggregato Spesa`, `Impegni`, `_unnamed_27`
- `2025_Rendiconto SDB Allegato e Spese per Servizi Conto Terzi per Macroaggregato - Impegni_CAMPANIA.csv` (27 fields): `Esercizio Finanziario`, `Codice Tipologia Soggetto`, `Descrizione Tipologia Soggetto`, `Codice BDAP`, `Denominazione Soggetto`, `CF Soggetto`, `Data Cessazione Soggetto`, `Codice Zona Geografica`, `Descrizione Zona Geografica`, `Codice Regione`, `Descrizione Regione`, `Codice Provincia`, `Descrizione Provincia`, `Codice Comune`, `Descrizione Comune`, `Codice Missione Arconet`, `Desc Missione Arconet`, `Codice Programma Arconet`, `Desc Programma Arconet`, `Codice Titolo`, `Descrizione Titolo`, `Codice Secondo Livello`, `Descrizione Secondo Livello`, `Codice Macroaggregato Spesa`, `Descrizione Macroaggregato Spesa`, `Impegni`, `_unnamed_27`
- `2025_Rendiconto SDB Allegato f Accertamenti Pluriennali_CAMPANIA.csv` (25 fields): `Esercizio Finanziario`, `Codice Tipologia Soggetto`, `Descrizione Tipologia Soggetto`, `Codice BDAP`, `Denominazione Soggetto`, `CF Soggetto`, `Data Cessazione Soggetto`, `Codice Zona Geografica`, `Descrizione Zona Geografica`, `Codice Regione`, `Descrizione Regione`, `Codice Provincia`, `Descrizione Provincia`, `Codice Comune`, `Descrizione Comune`, `Codice Titolo Entrate`, `Descrizione Titolo Entrate`, `Codice Tipologia Entrate`, `Descrizione Tipologia Entrate`, `Previsioni di competenza Anno1`, `Accertamenti Anno1`, `Previsioni di competenza Anno2`, `Accertamenti Anno2`, `Accertamenti Anni Successivi`, `_unnamed_25`
- `2025_Rendiconto SDB Allegato g Impegni Pluriennali_CAMPANIA.csv` (25 fields): `Esercizio Finanziario`, `Codice Tipologia Soggetto`, `Descrizione Tipologia Soggetto`, `Codice BDAP`, `Denominazione Soggetto`, `CF Soggetto`, `Data Cessazione Soggetto`, `Codice Zona Geografica`, `Descrizione Zona Geografica`, `Codice Regione`, `Descrizione Regione`, `Codice Provincia`, `Descrizione Provincia`, `Codice Comune`, `Descrizione Comune`, `Codice Titolo`, `Descrizione Titolo`, `Codice Macroaggregato`, `Descrizione Macroaggregato`, `Previsioni di competenza Anno1`, `Impegni Anno1`, `Previsioni di Competenza del Bilancio Pluriennale Anno2`, `Impegni Anno2`, `Impegni Anni Successivi`, `_unnamed_25`
- `2025_Rendiconto SDB Allegato h Costi per Missione_CAMPANIA.csv` (24 fields): `Esercizio Finanziario`, `Codice Tipologia Soggetto`, `Descrizione Tipologia Soggetto`, `Codice BDAP`, `Denominazione Soggetto`, `CF Soggetto`, `Data Cessazione Soggetto`, `Codice Zona Geografica`, `Descrizione Zona Geografica`, `Codice Regione`, `Descrizione Regione`, `Codice Provincia`, `Descrizione Provincia`, `Codice Comune`, `Descrizione Comune`, `Codice Missione Arconet`, `Descrizione Missione Arconet`, `Codice I Livello`, `Descrizione I Livello`, `Descrizione II Livello`, `Codice III Livello`, `Descrizione III Livello`, `Importo Voci CE Rendiconto`, `_unnamed_24`
- `2025_Rendiconto SDB Allegato j Spese su Contributi UE e Internazionali_CAMPANIA.csv` (35 fields): `Esercizio Finanziario`, `Codice Tipologia Soggetto`, `Descrizione Tipologia Soggetto`, `Codice BDAP`, `Denominazione Soggetto`, `CF Soggetto`, `Data Cessazione Soggetto`, `Codice Zona Geografica`, `Descrizione Zona Geografica`, `Codice Regione`, `Descrizione Regione`, `Codice Provincia`, `Descrizione Provincia`, `Codice Comune`, `Descrizione Comune`, `Codice Missione Arconet`, `Descrizione Missione Arconet`, `Codice Programma Arconet`, `Descrizione Programma Arconet`, `Codice Titolo`, `Descrizione Titolo`, `Residui Passivi Iniziali`, `Previsioni Definitive di Competenza`, `Previsioni Definitive di Cassa`, `Pagamenti C/Residuo`, `Pagamenti C/Competenza`, `Totale Pagamenti`, `Riaccertamenti Residui`, `Impegni`, `Fondo Puriennale Vincolato`, `Economie C/Competenza`, `Residui Passivi da Esercizi Precedenti`, `Residui Passivi da Esercizio di Competenza`, `Residui Passivi da riportare`, `_unnamed_35`
- `2025_Rendiconto SDB Allegato k Funzioni Delegate dalle Regioni_CAMPANIA.csv` (35 fields): `Esercizio Finanziario`, `Codice Tipologia Soggetto`, `Descrizione Tipologia Soggetto`, `Codice BDAP`, `Denominazione Soggetto`, `CF Soggetto`, `Data Cessazione Soggetto`, `Codice Zona Geografica`, `Descrizione Zona Geografica`, `Codice Regione`, `Descrizione Regione`, `Codice Provincia`, `Descrizione Provincia`, `Codice Comune`, `Descrizione Comune`, `Codice Missione Arconet`, `Descrizione Missione Arconet`, `Codice Programma Arconet`, `Descrizione Programma Arconet`, `Codice Titolo`, `Descrizione Titolo`, `Residui Passivi Iniziali`, `Previsioni Definitive di Competenza`, `Previsioni Definitive di Cassa`, `Pagamenti C/Residuo`, `Pagamenti C/Competenza`, `Totale Pagamenti`, `Riaccertamenti Residui`, `Impegni`, `Fondo Puriennale Vincolato`, `Economie C/Competenza`, `Residui Passivi da Esercizi Precedenti`, `Residui Passivi da Esercizio di Competenza`, `Residui Passivi da riportare`, `_unnamed_35`
- `2025_Rendiconto SDB Conto Economico_CAMPANIA.csv` (31 fields): `Esercizio Finanziario`, `Codice Tipologia Soggetto`, `Descrizione Tipologia Soggetto`, `Codice BDAP`, `Denominazione Soggetto`, `CF Soggetto`, `Data Cessazione Soggetto`, `Codice Zona Geografica`, `Descrizione Zona Geografica`, `Codice Regione`, `Descrizione Regione`, `Codice Provincia`, `Descrizione Provincia`, `Codice Comune`, `Descrizione Comune`, `Codice Voce Conto Economico`, `Prospetto I Livello`, `Gruppo I Livello`, `Codice I Livello`, `Descrizione I Livello`, `Prospetto II Livello`, `Gruppo II Livello`, `Codice II Livello`, `Descrizione II Livello`, `Prospetto III Livello`, `Gruppo III Livello`, `Codice III Livello`, `Descrizione III Livello`, `Valore Economico`, `Valore Economico Esercizio Precedente`, `_unnamed_31`
- `2025_Rendiconto SDB Entrate - Voce di Riepilogo_CAMPANIA.csv` (20 fields): `Esercizio Finanziario`, `Codice Tipologia Soggetto`, `Descrizione Tipologia Soggetto`, `Codice BDAP`, `Denominazione Soggetto`, `CF Soggetto`, `Data Cessazione Soggetto`, `Codice Zona Geografica`, `Descrizione Zona Geografica`, `Codice Regione`, `Descrizione Regione`, `Codice Provincia`, `Descrizione Provincia`, `Codice Comune`, `Descrizione Comune`, `Cod Voce di Riepilogo Entrate`, `Desc Voce di Riepilogo Entrate`, `Pre. Def. in CC`, `Pre. Def. in CC di cui UFA`, `_unnamed_20`
- `2025_Rendiconto SDB Entrate Riepilogo Titoli - Voce di Riepilogo_CAMPANIA.csv` (21 fields): `Esercizio Finanziario`, `Codice Tipologia Soggetto`, `Descrizione Tipologia Soggetto`, `Codice BDAP`, `Denominazione Soggetto`, `CF Soggetto`, `Data Cessazione Soggetto`, `Codice Zona Geografica`, `Descrizione Zona Geografica`, `Codice Regione`, `Descrizione Regione`, `Codice Provincia`, `Descrizione Provincia`, `Codice Comune`, `Descrizione Comune`, `Cod Voce di Riepilogo Entrate`, `Desc Voce di Riepilogo Entrate`, `Ordine Esposizione`, `Previsioni Definitive di Competenza (CP)`, `Previsioni Definitive in CC di cui utilizzo fondo anticipazioni`, `_unnamed_21`
- `2025_Rendiconto SDB Entrate Riepilogo Titoli_CAMPANIA.csv` (31 fields): `Esercizio Finanziario`, `Codice Tipologia Soggetto`, `Descrizione Tipologia Soggetto`, `Codice BDAP`, `Denominazione Soggetto`, `CF Soggetto`, `Data Cessazione Soggetto`, `Codice Zona Geografica`, `Descrizione Zona Geografica`, `Codice Regione`, `Descrizione Regione`, `Codice Provincia`, `Descrizione Provincia`, `Codice Comune`, `Descrizione Comune`, `Codice Titolo`, `Descrizione Titolo`, `Residui Attivi Iniziali`, `Previsioni Definitive di Competenza`, `Previsioni Definitive di Cassa`, `Riscossioni in C/Residui`, `Riscossioni in C/Competenza`, `Totale Riscossioni`, `Riaccertamenti Residui`, `Accertamenti`, `Residui Attivi in C/Residui`, `Maggiori o Minori Entrate di Cassa`, `Maggiori o Minori Entrate di Competenza`, `Residui Attivi in C/Competenza`, `Totale Residui Attivi da Riportare`, `_unnamed_31`
- `2025_Rendiconto SDB Entrate_CAMPANIA.csv` (33 fields): `Esercizio Finanziario`, `Codice Tipologia Soggetto`, `Descrizione Tipologia Soggetto`, `Codice BDAP`, `Denominazione Soggetto`, `CF Soggetto`, `Data Cessazione Soggetto`, `Codice Zona Geografica`, `Descrizione Zona Geografica`, `Codice Regione`, `Descrizione Regione`, `Codice Provincia`, `Descrizione Provincia`, `Codice Comune`, `Descrizione Comune`, `Codice Titolo Entrata Arconet`, `Desc Titolo Entrata Arconet`, `Cod Tipologia Entrata Arconet`, `Desc Tipologia Entrata Arconet`, `Residui Attivi Iniziali`, `Riscos. in CR`, `Riacc. Res.`, `Res. Att. In CR`, `Pre.  Def. in CC`, `Riscos. in CC`, `Accert. in CC`, `Magg. o min. entr. di CC`, `Res. Att. In CC`, `Pre.  Def. Di Cassa`, `Tot. Riscos.`, `Magg. o min. entr. di Cassa`, `Res. Att. da riportare tot.`, `_unnamed_33`
- `2025_Rendiconto SDB Equilibri Enti Locali_CAMPANIA.csv` (22 fields): `Esercizio Finanziario`, `Codice Tipologia Soggetto`, `Descrizione Tipologia Soggetto`, `Codice BDAP`, `Denominazione Soggetto`, `CF Soggetto`, `Data Cessazione Soggetto`, `Codice Zona Geografica`, `Descrizione Zona Geografica`, `Codice Regione`, `Descrizione Regione`, `Codice Provincia`, `Descrizione Provincia`, `Codice Comune`, `Descrizione Comune`, `Codice Voce Equil Bil Enti Loc`, `Desc Voce Equil Bil Enti Loc`, `Fondo di Cassa all'ini. eser.`, `Accert. o Impeg. in CC`, `Impeg. di cui FA di liq.`, `Impeg. di cui est. ant. prest.`, `_unnamed_22`
- `2025_Rendiconto SDB Equilibri Regioni_CAMPANIA.csv` (21 fields): `Esercizio Finanziario`, `Codice Tipologia Soggetto`, `Descrizione Tipologia Soggetto`, `Codice BDAP`, `Denominazione Soggetto`, `CF Soggetto`, `Data Cessazione Soggetto`, `Codice Zona Geografica`, `Descrizione Zona Geografica`, `Codice Regione`, `Descrizione Regione`, `Codice Provincia`, `Descrizione Provincia`, `Codice Comune`, `Descrizione Comune`, `Codice Voce Equil Bil Regioni`, `Desc Voce Equil Bil Regioni`, `Accert. o Impeg. in CC`, `Impeg. di cui FA di liq.`, `Impeg. di cui est. ant. prest.`, `_unnamed_21`
- `2025_Rendiconto SDB Quadro Generale Riassuntivo Entrate - Voce di Riepilogo_CAMPANIA.csv` (24 fields): `Esercizio Finanziario`, `Codice Tipologia Soggetto`, `Descrizione Tipologia Soggetto`, `Codice BDAP`, `Denominazione Soggetto`, `CF Soggetto`, `Data Cessazione Soggetto`, `Codice Zona Geografica`, `Descrizione Zona Geografica`, `Codice Regione`, `Descrizione Regione`, `Codice Provincia`, `Descrizione Provincia`, `Codice Comune`, `Descrizione Comune`, `Cod Voce di Riepilogo Entrate`, `Desc Voce di Riepilogo Entrate`, `Ordine di esposizione`, `Accert Conto Comp`, `Incassi Conto Comp`, `Accert Conto Comp di cui FAL`, `Accert di cui FPV fin. da debito`, `Accert di cui Disav. da debito`, `_unnamed_24`
- `2025_Rendiconto SDB Quadro Generale Riassuntivo Entrate_CAMPANIA.csv` (20 fields): `Esercizio Finanziario`, `Codice Tipologia Soggetto`, `Descrizione Tipologia Soggetto`, `Codice BDAP`, `Denominazione Soggetto`, `CF Soggetto`, `Data Cessazione Soggetto`, `Codice Zona Geografica`, `Descrizione Zona Geografica`, `Codice Regione`, `Descrizione Regione`, `Codice Provincia`, `Descrizione Provincia`, `Codice Comune`, `Descrizione Comune`, `Codice Titolo Entrata Arconet`, `Desc Titolo Entrata Arconet`, `Accertamenti`, `Incassi`, `_unnamed_20`
- `2025_Rendiconto SDB Quadro Generale Riassuntivo Gestione Bilancio e Accantonamenti_CAMPANIA.csv` (23 fields): `Esercizio Finanziario`, `Codice Tipologia Soggetto`, `Descrizione Tipologia Soggetto`, `Codice BDAP`, `Denominazione Soggetto`, `CF Soggetto`, `Data Cessazione Soggetto`, `Codice Zona Geografica`, `Descrizione Zona Geografica`, `Codice Regione`, `Descrizione Regione`, `Codice Provincia`, `Descrizione Provincia`, `Codice Comune`, `Descrizione Comune`, `GestBil Avanzo - Disavanzo di Competenza`, `GestBil Risorse Accantonate Stanziate Anno N`, `GestBil Risorse Vincolate nel Bilancio`, `GestBil Equilibrio di Bilancio`, `GestAcc Equilibrio di Bilancio`, `GestAcc Variazione Accantonamenti`, `GestAcc Equilibrio Complessivo`, `_unnamed_23`
- `2025_Rendiconto SDB Quadro Generale Riassuntivo Spese - Voce di Riepilogo_CAMPANIA.csv` (21 fields): `Esercizio Finanziario`, `Codice Tipologia Soggetto`, `Descrizione Tipologia Soggetto`, `Codice BDAP`, `Denominazione Soggetto`, `CF Soggetto`, `Data Cessazione Soggetto`, `Codice Zona Geografica`, `Descrizione Zona Geografica`, `Codice Regione`, `Descrizione Regione`, `Codice Provincia`, `Descrizione Provincia`, `Codice Comune`, `Descrizione Comune`, `Codice Voce di Riepilogo Spese`, `Desc Voce di Riepilogo Spese`, `Ordine di esposizione`, `Impegni`, `Pagamenti`, `_unnamed_21`
- `2025_Rendiconto SDB Quadro Generale Riassuntivo Spese_CAMPANIA.csv` (24 fields): `Esercizio Finanziario`, `Codice Tipologia Soggetto`, `Descrizione Tipologia Soggetto`, `Codice BDAP`, `Denominazione Soggetto`, `CF Soggetto`, `Data Cessazione Soggetto`, `Codice Zona Geografica`, `Descrizione Zona Geografica`, `Codice Regione`, `Descrizione Regione`, `Codice Provincia`, `Descrizione Provincia`, `Codice Comune`, `Descrizione Comune`, `Codice Titolo Spese Arconet`, `Desc Titolo Spese Arconet`, `Impegni`, `Pagamenti`, `Impegni di Fondo pluriennale vincolato`, `Impegni di cui Fondo pluriennale vincolato in c/capitale finanziato da debito`, `Impegni di cui Fondo Anticipazione di liquidità`, `Impegni Fondo Anticipazione di liq. stanziamento definitivo di bilancio`, `_unnamed_24`
- `2025_Rendiconto SDB Spese - Voce di Riepilogo_CAMPANIA.csv` (19 fields): `Esercizio Finanziario`, `Codice Tipologia Soggetto`, `Descrizione Tipologia Soggetto`, `Codice BDAP`, `Denominazione Soggetto`, `CF Soggetto`, `Data Cessazione Soggetto`, `Codice Zona Geografica`, `Descrizione Zona Geografica`, `Codice Regione`, `Descrizione Regione`, `Codice Provincia`, `Descrizione Provincia`, `Codice Comune`, `Descrizione Comune`, `Codice Voce di Riepilogo Spese`, `Desc Voce di Riepilogo Spese`, `Pre.  Def. in CC`, `_unnamed_19`
- `2025_Rendiconto SDB Spese Riepilogo Missioni - Voce di Riepilogo_CAMPANIA.csv` (20 fields): `Esercizio Finanziario`, `Codice Tipologia Soggetto`, `Descrizione Tipologia Soggetto`, `Codice BDAP`, `Denominazione Soggetto`, `CF Soggetto`, `Data Cessazione Soggetto`, `Codice Zona Geografica`, `Descrizione Zona Geografica`, `Codice Regione`, `Descrizione Regione`, `Codice Provincia`, `Descrizione Provincia`, `Codice Comune`, `Descrizione Comune`, `Codice Voce di Riepilogo`, `Descrizione Voce di Riepilogo`, `Ordine di Esposizione`, `Previsioni Definitive di Cassa`, `_unnamed_20`
- `2025_Rendiconto SDB Spese Riepilogo Missioni_CAMPANIA.csv` (31 fields): `Esercizio Finanziario`, `Codice Tipologia Soggetto`, `Descrizione Tipologia Soggetto`, `Codice BDAP`, `Denominazione Soggetto`, `CF Soggetto`, `Data Cessazione Soggetto`, `Codice Zona Geografica`, `Descrizione Zona Geografica`, `Codice Regione`, `Descrizione Regione`, `Codice Provincia`, `Descrizione Provincia`, `Codice Comune`, `Descrizione Comune`, `Codice Missione`, `Descrizione Missione`, `Residui Passivi Iniziali`, `Previsioni Definitive di Competenza`, `Previsioni Definitive di Cassa`, `Pagamenti C/Residuo`, `Pagamenti C/Competenza`, `Totale Pagamenti`, `Riaccertamenti Residui`, `Impegni`, `Fondo Puriennale Vincolato`, `Economie C/Competenza`, `Residui Passivi da Esercizi Precedenti`, `Residui Passivi da Esercizio di Competenza`, `Residui Passivi da riportare`, `_unnamed_31`
- `2025_Rendiconto SDB Spese Riepilogo Titoli - Voce di Riepilogo_CAMPANIA.csv` (20 fields): `Esercizio Finanziario`, `Codice Tipologia Soggetto`, `Descrizione Tipologia Soggetto`, `Codice BDAP`, `Denominazione Soggetto`, `CF Soggetto`, `Data Cessazione Soggetto`, `Codice Zona Geografica`, `Descrizione Zona Geografica`, `Codice Regione`, `Descrizione Regione`, `Codice Provincia`, `Descrizione Provincia`, `Codice Comune`, `Descrizione Comune`, `Codice Voce di Riepilogo`, `Descrizione Voce di Riepilogo`, `Ordine di Esposizione`, `Previsioni Definitive di Competenza`, `_unnamed_20`
- `2025_Rendiconto SDB Spese Riepilogo Titoli_CAMPANIA.csv` (31 fields): `Esercizio Finanziario`, `Codice Tipologia Soggetto`, `Descrizione Tipologia Soggetto`, `Codice BDAP`, `Denominazione Soggetto`, `CF Soggetto`, `Data Cessazione Soggetto`, `Codice Zona Geografica`, `Descrizione Zona Geografica`, `Codice Regione`, `Descrizione Regione`, `Codice Provincia`, `Descrizione Provincia`, `Codice Comune`, `Descrizione Comune`, `Codice Titolo`, `Descrizione Titolo`, `Residui Passivi Iniziali`, `Previsioni Definitive di Competenza`, `Previsioni Definitive di Cassa`, `Pagamenti in C/Residui`, `Pagamenti in C/Competenza`, `Totale Pagamenti`, `Riaccertamenti Residui`, `Impegni`, `Fondo Pluriennale Vincolato`, `Economie di Competenza`, `Residui Passivi da Esercizi Precedenti`, `Residui Passivi da Esercizio di Competenza`, `Residui passivi da riportare totale`, `_unnamed_31`
- `2025_Rendiconto SDB Spese_CAMPANIA.csv` (35 fields): `Esercizio Finanziario`, `Codice Tipologia Soggetto`, `Descrizione Tipologia Soggetto`, `Codice BDAP`, `Denominazione Soggetto`, `CF Soggetto`, `Data Cessazione Soggetto`, `Codice Zona Geografica`, `Descrizione Zona Geografica`, `Codice Regione`, `Descrizione Regione`, `Codice Provincia`, `Descrizione Provincia`, `Codice Comune`, `Descrizione Comune`, `Codice Missione Arconet`, `Desc Missione Arconet`, `Codice Programma Arconet`, `Desc Programma Arconet`, `Codice Titolo Spese Arconet`, `Desc Titolo Spese Arconet`, `Res. Pass. Iniziali`, `Pag. in CR`, `Riacc. Res.`, `Res. Pas. In CR`, `Pre.  Def. in CC`, `Pag. in CC`, `Impegni`, `Econ. in CC`, `Res. Pas. In CC`, `Pre.  Def. Di Cassa`, `Tot. Pag.`, `FPV`, `Res. Pas. da riportare tot.`, `_unnamed_35`
- `2025_Rendiconto SDB Stato Patrimoniale Attivo_CAMPANIA.csv` (30 fields): `Esercizio Finanziario`, `Codice Tipologia Soggetto`, `Descrizione Tipologia Soggetto`, `Codice BDAP`, `Denominazione Soggetto`, `CF Soggetto`, `Data Cessazione Soggetto`, `Codice Zona Geografica`, `Descrizione Zona Geografica`, `Codice Regione`, `Descrizione Regione`, `Codice Provincia`, `Descrizione Provincia`, `Codice Comune`, `Descrizione Comune`, `Codice I Livello`, `Descrizione I Livello`, `Codice II Livello`, `Descrizione II Livello`, `Codice III Livello`, `Descrizione III Livello`, `Codice IV Livello`, `Descrizione IV Livello`, `Codice v Livello`, `Descrizione V Livello`, `Consistenza Anno Corrente`, `Consistenza Anno Precedente`, `Di Cui Consistenza Anno Corrente`, `Di Cui Consistenza Anno Precedente`, `_unnamed_30`
- `2025_Rendiconto SDB Stato Patrimoniale Passivo - Conti di Ordine_CAMPANIA.csv` (24 fields): `Esercizio Finanziario`, `Codice Tipologia Soggetto`, `Descrizione Tipologia Soggetto`, `Codice BDAP`, `Denominazione Soggetto`, `CF Soggetto`, `Data Cessazione Soggetto`, `Codice Zona Geografica`, `Descrizione Zona Geografica`, `Codice Regione`, `Descrizione Regione`, `Codice Provincia`, `Descrizione Provincia`, `Codice Comune`, `Descrizione Comune`, `Codice I Livello`, `Descrizione I Livello`, `Codice II Livello`, `Descrizione II Livello`, `Codice III Livello`, `Descrizione III Livello`, `Consistenza Anno Corrente`, `Consistenza Anno Precedente`, `_unnamed_24`
- `2025_Rendiconto SDB Stato Patrimoniale Passivo_CAMPANIA.csv` (28 fields): `Esercizio Finanziario`, `Codice Tipologia Soggetto`, `Descrizione Tipologia Soggetto`, `Codice BDAP`, `Denominazione Soggetto`, `CF Soggetto`, `Data Cessazione Soggetto`, `Codice Zona Geografica`, `Descrizione Zona Geografica`, `Codice Regione`, `Descrizione Regione`, `Codice Provincia`, `Descrizione Provincia`, `Codice Comune`, `Descrizione Comune`, `Codice I Livello`, `Descrizione I Livello`, `Codice II Livello`, `Descrizione II Livello`, `Codice III Livello`, `Descrizione III Livello`, `Codice IV Livello`, `Descrizione IV Livello`, `Codice V Livello`, `Descrizione V Livello`, `Consistenza Anno Corrente`, `Consistenza Anno Precedente`, `_unnamed_28`
- Coverage by period: 2025: 117/118

Source: [bdap-budget-2025](https://openbdap.rgs.mef.gov.it/Datasets_FET/Rendiconto/2025/2025_Rendiconto%20-%20Schemi%20di%20bilancio_CAMPANIA.zip)

### bdap-indicators-2025

Records: 18,654; associated municipalities: 117/118; periods: 2025.

ELCOMU authorities only. Statements contain overlapping totals and line items; no automatic sum. Latest reporting year may be incomplete.

Staging file: `data/collection/bdap-indicators-2025.rows.jsonl.gz`; SHA-256: `99c16498c03db74f69a14403cedbab4ccf87ef357543854f7bf9276ddd047916`.

- `2025_Rendiconto PDI Analitici di Entrate 2-b_CAMPANIA.csv` (28 fields): `Esercizio Finanziario`, `Codice Tipologia Soggetto`, `Descrizione Tipologia Soggetto`, `Codice BDAP`, `Denominazione Soggetto`, `CF Soggetto`, `Data Cessazione Soggetto`, `Codice Zona Geografica`, `Descrizione Zona Geografica`, `Codice Regione`, `Descrizione Regione`, `Codice Provincia`, `Descrizione Provincia`, `Codice Comune`, `Descrizione Comune`, `Codice Titolo`, `Descrizione Titolo`, `Codice Tipologia`, `Descrizione Tipologia`, `Previsioni Iniziali Competenza/Totale Previsioni Iniziali Competenza`, `Previsioni Definitive Competenza/Totale Previsioni Definitive Competenza`, `Accertamenti/Totale Accertamenti`, `Incidenza Riscossione Prevista nel Bilancio di Previsione Iniziale`, `Incidenza Riscossione Prevista nelle Previsioni Definitive`, `Incidenza Riscossione Complessiva`, `Incidenza Riscossione dei Crediti Esigibili nell'Esercizio Finanziario`, `Incidenza Riscossione dei Crediti Esigibili negli Esercizi Precedenti`, `_unnamed_28`
- `2025_Rendiconto PDI Analitici di Entrate 4-b_CAMPANIA.csv` (28 fields): `Esercizio Finanziario`, `Codice Tipologia Soggetto`, `Descrizione Tipologia Soggetto`, `Codice BDAP`, `Denominazione Soggetto`, `CF Soggetto`, `Data Cessazione Soggetto`, `Codice Zona Geografica`, `Descrizione Zona Geografica`, `Codice Regione`, `Descrizione Regione`, `Codice Provincia`, `Descrizione Provincia`, `Codice Comune`, `Descrizione Comune`, `Codice Titolo`, `Descrizione Titolo`, `Codice Tipologia`, `Descrizione Tipologia`, `Previsioni Iniziali Competenza/Totale Previsioni Iniziali Competenza`, `Previsioni Definitive Competenza/Totale Previsioni Definitive Competenza`, `Accertamenti/Totale Accertamenti`, `Incidenza Riscossione Prevista nel Bilancio Di Previsione Iniziale`, `Incidenza Riscossione Prevista nelle Previsioni Definitive`, `Incidenza Riscossione Complessiva`, `Incidenza Riscossione dei Crediti Esigibili nell'esercizio Finanziario`, `Incidenza Riscossione dei Crediti Esigibili negli Esercizi Precedenti`, `_unnamed_28`
- `2025_Rendiconto PDI Analitici di Spese 2-c_CAMPANIA.csv` (27 fields): `Esercizio Finanziario`, `Codice Tipologia Soggetto`, `Descrizione Tipologia Soggetto`, `Codice BDAP`, `Denominazione Soggetto`, `CF Soggetto`, `Data Cessazione Soggetto`, `Codice Zona Geografica`, `Descrizione Zona Geografica`, `Codice Regione`, `Descrizione Regione`, `Codice Provincia`, `Descrizione Provincia`, `Codice Comune`, `Descrizione Comune`, `Codice Missione Arconet`, `Descrizione Missione Arconet`, `Codice Programma Arconet`, `Descrizione Programma Arconet`, `Incidenza Missione Programma Previsione Iniziale`, `Incidenza Missione Programma Di Cui Fondo Pluriennale Vincolato Previsione Iniziale`, `Incidenza Missione Programma Previsione Definitiva`, `Incidenza Missione Programma Di Cui Fondo Pluriennale Vincolato Previsione Definitiva`, `Incidenza Missione Programma Dati di Rendiconto`, `Incidenza Missione Programma Di Cui Fondo Pluriennale Vincolato Dati di Rendiconto`, `Incidenza Missione Programma Di Cui Incidenza Economia di Spesa Dati di Rendiconto`, `_unnamed_27`
- `2025_Rendiconto PDI Analitici di Spese 2-d_CAMPANIA.csv` (25 fields): `Esercizio Finanziario`, `Codice Tipologia Soggetto`, `Descrizione Tipologia Soggetto`, `Codice BDAP`, `Denominazione Soggetto`, `CF Soggetto`, `Data Cessazione Soggetto`, `Codice Zona Geografica`, `Descrizione Zona Geografica`, `Codice Regione`, `Descrizione Regione`, `Codice Provincia`, `Descrizione Provincia`, `Codice Comune`, `Descrizione Comune`, `Codice Missione Arconet`, `Descrizione Missione Arconet`, `Codice Programma Arconet`, `Descrizione Programma Arconet`, `Capacità di Pagamento Previsione Iniziale`, `Capacità di Pagamento Previsione Definitive`, `Capacità di Pagamento a Consuntivo`, `Capacità Di Pagamento delle Spese in Conto Competenza Impegni`, `Capacità Di Pagamento delle Spese Esigibili negli Esercizi Precedenti`, `_unnamed_25`
- `2025_Rendiconto PDI Analitici di Spese 4-c_CAMPANIA.csv` (27 fields): `Esercizio Finanziario`, `Codice Tipologia Soggetto`, `Descrizione Tipologia Soggetto`, `Codice BDAP`, `Denominazione Soggetto`, `CF Soggetto`, `Data Cessazione Soggetto`, `Codice Zona Geografica`, `Descrizione Zona Geografica`, `Codice Regione`, `Descrizione Regione`, `Codice Provincia`, `Descrizione Provincia`, `Codice Comune`, `Descrizione Comune`, `Codice Missione Arconet`, `Descrizione Missione Arconet`, `Codice Programma Arconet`, `Descrizione Programma Arconet`, `Incidenza Missione Programma Previsione Iniziale`, `Incidenza Missione Programma Di Cui Fondo Pluriennale Vincolato Previsione Iniziale`, `Incidenza Missione Programma Previsione Definitiva`, `Incidenza Missione Programma Di Cui Fondo Pluriennale Vincolato Previsione Definitiva`, `Incidenza Missione Programma Dati di Rendiconto`, `Incidenza Missione Programma Di Cui Fondo Pluriennale Vincolato Dati di Rendiconto`, `Incidenza Missione Programma Di Cui Incidenza Economia Di Spesa Dati di Rendiconto`, `_unnamed_27`
- `2025_Rendiconto PDI Analitici di Spese 4-d_CAMPANIA.csv` (25 fields): `Esercizio Finanziario`, `Codice Tipologia Soggetto`, `Descrizione Tipologia Soggetto`, `Codice BDAP`, `Denominazione Soggetto`, `CF Soggetto`, `Data Cessazione Soggetto`, `Codice Zona Geografica`, `Descrizione Zona Geografica`, `Codice Regione`, `Descrizione Regione`, `Codice Provincia`, `Descrizione Provincia`, `Codice Comune`, `Descrizione Comune`, `Codice Missione Arconet`, `Descrizione Missione Arconet`, `Codice Programma Arconet`, `Descrizione Programma Arconet`, `Capacità di Pagamento Previsione Iniziale`, `Capacità di Pagamento Previsione Definitive`, `Capacità di Pagamento a Consuntivo`, `Capacità di Pagamento delle Spese in Conto Competenza Impegni`, `Capacità di Pagamento delle Spese Esigibili negli Esercizi Precedenti`, `_unnamed_25`
- `2025_Rendiconto PDI Sintetici Allegato 2-a_CAMPANIA.csv` (24 fields): `Esercizio Finanziario`, `Codice Tipologia Soggetto`, `Descrizione Tipologia Soggetto`, `Codice BDAP`, `Denominazione Soggetto`, `CF Soggetto`, `Data Cessazione Soggetto`, `Codice Zona Geografica`, `Descrizione Zona Geografica`, `Codice Regione`, `Descrizione Regione`, `Codice Provincia`, `Descrizione Provincia`, `Codice Comune`, `Descrizione Comune`, `Codice Tipologia Indicatore Sintetico 2)a`, `Descrizione Tipologia Indicatore Sintetico 2)a`, `Codice Indicatore Sintetico 2)a`, `Descrizione Indicatore Sintetico 2)a`, `Definizione Indicatore Sintetico 2)a`, `Indicatore Tutte Le Missioni`, `Indicatore Solo Per Missione 13 - Tutela Della Salute`, `Indicatore Tutte Le Spese al Netto Missione 13`, `_unnamed_24`
- `2025_Rendiconto PDI Sintetici Allegato 4-a_CAMPANIA.csv` (22 fields): `Esercizio Finanziario`, `Codice Tipologia Soggetto`, `Descrizione Tipologia Soggetto`, `Codice BDAP`, `Denominazione Soggetto`, `CF Soggetto`, `Data Cessazione Soggetto`, `Codice Zona Geografica`, `Descrizione Zona Geografica`, `Codice Regione`, `Descrizione Regione`, `Codice Provincia`, `Descrizione Provincia`, `Codice Comune`, `Descrizione Comune`, `Codice Tipologia Indicatore Sintetico 4)a`, `Descrizione Tipologia Indicatore Sintetico 4)a`, `Codice Indicatore Sintetico 4)a`, `Descrizione Indicatore Sintetico 4)a`, `Definizione Indicatore Sintetico 4)a`, `Valore Indicatore`, `_unnamed_22`
- Coverage by period: 2025: 117/118

Source: [bdap-indicators-2025](https://openbdap.rgs.mef.gov.it/Datasets_FET/Rendiconto/2025/2025_Rendiconto%20-%20Piano%20degli%20indicatori_CAMPANIA.zip)

### istat-foreign-age-2026

Records: 12,036; associated municipalities: 118/118; periods: 2026.

Population at 1 January 2026, estimate explicitly labelled by ISTAT.

Staging file: `data/collection/istat-foreign-age-2026.rows.jsonl.gz`; SHA-256: `5efaef1ec9dd469dcf1f22f5e4ff47e835ad754ab5a442ef7d220ab12214f451`.

- `STRASA_2026_it_064_Avellino.csv` (5 fields): `Codice comune`, `Comune`, `Età`, `Maschi`, `Femmine`
- Coverage by period: 2026: 118/118

Source: [istat-foreign-age-2026](https://demo.istat.it/data/strasa/STRASA_2026_it_064_Avellino.zip)

### istat-monthly-2024

Records: 4,956; associated municipalities: 118/118; periods: 2024.

Monthly balance; retain Mese and Sesso fields. Annual totals and monthly stocks are different concepts.

Staging file: `data/collection/istat-monthly-2024.rows.jsonl.gz`; SHA-256: `82f829168113da8e4cf4f6a9520c6d1ec2d208f9b9926a49d38cbb25058394c0`.

- `Bilancio_demografico_mensile_2024.csv` (26 fields): `Anno`, `Mese`, `Nome mese`, `Sesso`, `Popolazione inizio periodo`, `Nati vivi`, `Morti`, `Saldo naturale`, `Immigrati da altro comune`, `Emigrati per altro comune`, `Saldo migratorio interno`, `Immigrati dall'estero`, `Emigrati per l'estero`, `Saldo migratorio con l'estero`, `Unità in più/meno dovute a variazioni territoriali`, `Popolazione fine periodo`, `Codice comune`, `Comune`, `Codice provincia`, `Provincia`, `Codice regione`, `Regione`, `Codice ripartizione`, `Ripartizione`, `Codice nazione`, `Nazione`
- Coverage by period: 2024: 118/118

Source: [istat-monthly-2024](https://demo.istat.it/data/d7b/D7B2024.csv.zip)

### istat-projections-2025-2050

Records: 9,282; associated municipalities: 17/118; periods: 2025, 2026, 2027, 2028, 2029, 2030, 2031, 2032, 2033, 2034, 2035, 2036, 2037, 2038, 2039, 2040, 2041, 2042, 2043, 2044, 2045, 2046, 2047, 2048, 2049, 2050.

Median scenario projections, not observed data. Small municipalities may be excluded by the publisher.

Staging file: `data/collection/istat-projections-2025-2050.rows.jsonl.gz`; SHA-256: `b563373b8c18990f466b3677fd13c54285c6e269343efc8504d28b753b593c9b`.

- `Previsioni_comunali_popolazione_per_eta-Comuni_Campania.csv` (9 fields): `Anno`, `Codice comune`, `Comune`, `Codice provincia`, `Provincia`, `Età`, `Maschi`, `Femmine`, `Totale`
- Coverage by period: 2025: 17/118, 2026: 17/118, 2027: 17/118, 2028: 17/118, 2029: 17/118, 2030: 17/118, 2031: 17/118, 2032: 17/118, 2033: 17/118, 2034: 17/118, 2035: 17/118, 2036: 17/118, 2037: 17/118, 2038: 17/118, 2039: 17/118, 2040: 17/118, 2041: 17/118, 2042: 17/118, 2043: 17/118, 2044: 17/118, 2045: 17/118, 2046: 17/118, 2047: 17/118, 2048: 17/118, 2049: 17/118, 2050: 17/118

Source: [istat-projections-2025-2050](https://demo.istat.it/data/previsionicomunali/Previsioni_comunali_popolazione_per_eta-Comuni_Campania.csv.zip)

### inps-pensions-regional-2020-2024

Records: 9,527; associated municipalities: 0/118; periods: 2020, 2021, 2022, 2023, 2024.

Regional pension awards/cohorts by quarter. No municipal coverage; annual pension income from MEF is a different municipal measure.

Staging file: `data/collection/inps-pensions-regional-2020-2024.rows.jsonl.gz`; SHA-256: `7ca3bb2a428f4281554bc4de619972580ec2cdee5dc43df5498a903ab2e45e36`.

- `inps_pensions.csv` (11 fields): `Anno_decorrenza`, `SESSO`, `tgestio`, `classe_importo`, `classe_eta`, `area_geografica`, `gestione`, `Categoria`, `Regione`, `Trimestrale`, `Numero_pensioni`
- Coverage by period: 2020: 0/118, 2021: 0/118, 2022: 0/118, 2023: 0/118, 2024: 0/118

Source: [inps-pensions-regional-2020-2024](https://opendata.inps.it/download/dataset/migr2024/dataset_6002.csv)

### arpac-air-2025

Records: 372,625; associated municipalities: 3/118; periods: 2025.

Station measurements, not a municipal air quality score. -9999 is retained as a source sentinel and must not enter calculations.

Staging file: `data/collection/arpac-air-2025.rows.jsonl.gz`; SHA-256: `59dabfeeaac7bd00b72c4cbd845fbd128c01171adbad3bcee1ada3853664c3a7`.

- `dati-monitoraggio-qualita-aria.csv` (6 fields): `_id`, `STAZIONE`, `DATA_RILEVAZIONE`, `CODICE_INQUINANTE`, `UNITA_MISURA`, `VALORE`
- Coverage by period: 2025: 3/118

Source: [arpac-air-2025](https://dati.arpacampania.it/datastore/dump/88ee65bf-3e24-42bb-a840-77b514421a85)

### bdap-budget-2024

Records: 99,091; associated municipalities: 118/118; periods: 2024.

ELCOMU statements. Hierarchical totals require semantic selection before adding values.

Staging file: `data/collection/bdap-budget-2024.rows.jsonl.gz`; SHA-256: `a38663d12db69cc5e2d53dd187b0bbebf1bb9246b1962a3a91ccee61321cc732`.

- `2024_Bilanci di Rendiconto SDB Allegato l Parametri Obiettivi per Comuni_CAMPANIA.csv` (20 fields): `Esercizio Finanziario`, `Codice Tipologia Soggetto`, `Descrizione Tipologia Soggetto`, `Codice BDAP`, `Denominazione Soggetto`, `CF Soggetto`, `Data Cessazione Soggetto`, `Codice Zona Geografica`, `Descrizione Zona Geografica`, `Codice Regione`, `Descrizione Regione`, `Codice Provincia`, `Descrizione Provincia`, `Codice Comune`, `Descrizione Comune`, `Ordine di Esposizione`, `Codice Parametro Deficitario`, `Parametro Deficitario`, `Valore Parametro Deficitarietà`, `_unnamed_20`
- `2024_Bilanci di Rendiconto SDB Allegato m Parametri Obiettivi per Provincie e Città Metropolitane_CAMPANIA.csv` (20 fields): `Esercizio Finanziario`, `Codice Tipologia Soggetto`, `Descrizione Tipologia Soggetto`, `Codice BDAP`, `Denominazione Soggetto`, `CF Soggetto`, `Data Cessazione Soggetto`, `Codice Zona Geografica`, `Descrizione Zona Geografica`, `Codice Regione`, `Descrizione Regione`, `Codice Provincia`, `Descrizione Provincia`, `Codice Comune`, `Descrizione Comune`, `Ordine di Esposizione`, `Codice Parametro Deficitario`, `Parametro Deficitario`, `Valore Parametro Deficitarietà`, `_unnamed_20`
- `2024_Bilanci di Rendiconto SDB Allegato n Parametri Obiettivi per Comunità Montane_CAMPANIA.csv` (20 fields): `Esercizio Finanziario`, `Codice Tipologia Soggetto`, `Descrizione Tipologia Soggetto`, `Codice BDAP`, `Denominazione Soggetto`, `CF Soggetto`, `Data Cessazione Soggetto`, `Codice Zona Geografica`, `Descrizione Zona Geografica`, `Codice Regione`, `Descrizione Regione`, `Codice Provincia`, `Descrizione Provincia`, `Codice Comune`, `Descrizione Comune`, `Ordine di Esposizione`, `Codice Parametro Deficitario`, `Parametro Deficitario`, `Valore Parametro Deficitarietà`, `_unnamed_20`
- `2024_Rendiconto SDB Allegato A Risultato di Amministrazione_CAMPANIA.csv` (27 fields): `Esercizio Finanziario`, `Codice Tipologia Soggetto`, `Descrizione Tipologia Soggetto`, `Codice BDAP`, `Denominazione Soggetto`, `CF Soggetto`, `Data Cessazione Soggetto`, `Codice Zona Geografica`, `Descrizione Zona Geografica`, `Codice Regione`, `Descrizione Regione`, `Codice Provincia`, `Descrizione Provincia`, `Codice Comune`, `Descrizione Comune`, `Cod Voce Ris Amm Rend`, `Desc Voce Ris Amm Rend`, `Ordine di esposizione`, `Residui di Gestione`, `Competenza di Gestione`, `Totale di Gestione`, `ResAtt CR Acc Trib Stim DEF`, `ResAtt CC Acc Trib Stim DEF`, `ResAtt TOT Acc Trib Stim DEF`, `Di cui Disav Deb Autoriz e non Contr`, `Di cui Incassato su Tot Res Attivi`, `_unnamed_27`
- `2024_Rendiconto SDB Allegato a1 Risultato di Amministrazione Quote Accantonate_CAMPANIA.csv` (26 fields): `Esercizio Finanziario`, `Codice Tipologia Soggetto`, `Descrizione Tipologia Soggetto`, `Codice BDAP`, `Denominazione Soggetto`, `CF Soggetto`, `Data Cessazione Soggetto`, `Codice Zona Geografica`, `Descrizione Zona Geografica`, `Codice Regione`, `Descrizione Regione`, `Codice Provincia`, `Descrizione Provincia`, `Codice Comune`, `Descrizione Comune`, `Ordine di esposizione`, `Progressivo Riga`, `Voce Accantonamento`, `Codice Capitolo di Spesa`, `Descrizione Capitolo di Spesa`, `Risorse Accantonate al 1°Gennaio`, `Risorse Accantonate Applicate al Bilancio dell'Esercizio`, `Risorse Accantonate Stanziate nella Spesa del Bilancio dell'Esercizio`, `Variazione degli Accantonamenti Effettuata in Sede di Rendiconto`, `Risorse Accantonate nel Risultato di Amministrazione al 31 Dicembre`, `_unnamed_26`
- `2024_Rendiconto SDB Allegato a2 Risultato di Amministrazione Quote Vincolate_CAMPANIA.csv` (33 fields): `Esercizio Finanziario`, `Codice Tipologia Soggetto`, `Descrizione Tipologia Soggetto`, `Codice BDAP`, `Denominazione Soggetto`, `CF Soggetto`, `Data Cessazione Soggetto`, `Codice Zona Geografica`, `Descrizione Zona Geografica`, `Codice Regione`, `Descrizione Regione`, `Codice Provincia`, `Descrizione Provincia`, `Codice Comune`, `Descrizione Comune`, `Ordine di Esposizione`, `Progressivo Riga`, `Codice Voce Vincolo`, `Voce Vincolo`, `Codice Capitolo di Entrata`, `Descrizione Capitolo di Entrata`, `Codice Capitolo di Uscita`, `Descrizione Capitolo di Uscita`, `Risorse Vincolate nel Risultato di Amministrazione 1° Gennaio`, `Risorse Vincolate Applicate al Bilancio dell'Esercizio`, `Entrate Vincolate Accertate nell'Esercizio`, `Imp. Finanziati da Entr. Vinc. Accertate nell'Esercizio o da Quote Vincolate del Risultato di Ammi.ne`, `Fondo Pluriennale Vincolato al 31/12`, `Cancellazione: Residui Attivi Vinc, Vincolo su Quote Risultato di Ammin(+), Residui Passivi da Risorse Vincolate(-)`, `Impegni Finanziati dal Fondo Pluriennale di Entrata Cancellati`, `Risorse Vincolate nel Bilancio al 31/12`, `Risorse Vincolate nel Risultato di Amministrazione al 31/12`, `_unnamed_33`
- `2024_Rendiconto SDB Allegato a3 Risultato di Amministrazione Quote Destinate_CAMPANIA.csv` (29 fields): `Esercizio Finanziario`, `Codice Tipologia Soggetto`, `Descrizione Tipologia Soggetto`, `Codice BDAP`, `Denominazione Soggetto`, `CF Soggetto`, `Data Cessazione Soggetto`, `Codice Zona Geografica`, `Descrizione Zona Geografica`, `Codice Regione`, `Descrizione Regione`, `Codice Provincia`, `Descrizione Provincia`, `Codice Comune`, `Descrizione Comune`, `Ordine di esposizione`, `Progressivo Riga`, `Voce Investimenti`, `Codice Capitolo di Entrata`, `Descrizione Capitolo di Entrata`, `Codice Capitolo di Uscita`, `Descrizione Capitolo di Uscita`, `Risorse Destinate agli Investimenti al 1 Gennaio`, `Entrate Destinate agli Investimenti Accertate nell'Esercizio`, `Importo Impregni Imputati Esercizio del Rendiconto`, `Importo Complessivo Stanziamenti Fondo Pluriennale`, `Cancellazione di Risorse Destinate agli Investimenti`, `Importo Complessivo delle Quote Destinate agli Investimenti`, `_unnamed_29`
- `2024_Rendiconto SDB Allegato B FPV - Fondo Pluriennale Vincolato_CAMPANIA.csv` (29 fields): `Esercizio Finanziario`, `Codice Tipologia Soggetto`, `Descrizione Tipologia Soggetto`, `Codice BDAP`, `Denominazione Soggetto`, `CF Soggetto`, `Data Cessazione Soggetto`, `Codice Zona Geografica`, `Descrizione Zona Geografica`, `Codice Regione`, `Descrizione Regione`, `Codice Provincia`, `Descrizione Provincia`, `Codice Comune`, `Descrizione Comune`, `Codice Missione Arconet`, `Desc Missione Arconet`, `Codice Programma Arconet`, `Desc Programma Arconet`, `Imp. FPV EP`, `Impeg. Spese 1Anno`, `Econ. in CC`, `Econ. in CC Impeg. Pluriennali`, `Quota FP 2Anno  e Successivi`, `Impeg. Spese 2Anno`, `Impeg. Spese 3Anno`, `Impeg. Spese Imputaz. ND`, `FPV 1Anno`, `_unnamed_29`
- `2024_Rendiconto SDB Allegato C FCDE - Composizione Fondo Svalutazione Crediti_CAMPANIA.csv` (24 fields): `Esercizio Finanziario`, `Codice Tipologia Soggetto`, `Descrizione Tipologia Soggetto`, `Codice BDAP`, `Denominazione Soggetto`, `CF Soggetto`, `Data Cessazione Soggetto`, `Codice Zona Geografica`, `Descrizione Zona Geografica`, `Codice Regione`, `Descrizione Regione`, `Codice Provincia`, `Descrizione Provincia`, `Codice Comune`, `Descrizione Comune`, `Tot. Crediti - R.Attivi`, `Tot. Crediti - C.Stralc.`, `Tot. Crediti - Accert. ES`, `Fondo Sv.Crediti - RA`, `Fondo Sv. Crediti - C.Stralc.`, `Fondo Sv. Crediti - Accert. ES`, `Totale Crediti`, `Tot. Fondo Sv. Crediti`, `_unnamed_24`
- `2024_Rendiconto SDB Allegato C FCDE - Fondo Crediti Dubbia Esigibilita_CAMPANIA.csv` (35 fields): `Esercizio Finanziario`, `Codice Tipologia Soggetto`, `Descrizione Tipologia Soggetto`, `Codice BDAP`, `Denominazione Soggetto`, `CF Soggetto`, `Data Cessazione Soggetto`, `Codice Zona Geografica`, `Descrizione Zona Geografica`, `Codice Regione`, `Descrizione Regione`, `Codice Provincia`, `Descrizione Provincia`, `Codice Comune`, `Descrizione Comune`, `Codice Titolo Entrata Arconet`, `Desc Titolo Entrata Arconet`, `Cod Tipologia Entrata Arconet`, `Desc Tipologia Entrata Arconet`, `Res. Att. 1Anno`, `Res. Att. EP`, `Tot. Res. Att. 1Anno`, `Imp. Min. Fondo`, `Fondo Cr. DE`, `Res.Att.Accert.per Cassa 1Anno`, `Res.Att.Accert.per Cassa EP`, `Tot. Res.Att.Accert. per Cassa`, `Res.Att.non Accert.Cassa 1Anno`, `Res.Att.non Accert.Cassa EP`, `Tot. Res.Att.non Accert. Cassa`, `Perc. Acc. al Fondo`, `Perc.Acc.Fondo nonAccert.Cassa`, `Imp.Min.Fondo non Accert.Cassa`, `Imp. Fondo non Accert. Cassa`, `_unnamed_35`
- `2024_Rendiconto SDB Allegato C FCDE - Voce di Riepilogo_CAMPANIA.csv` (29 fields): `Esercizio Finanziario`, `Codice Tipologia Soggetto`, `Descrizione Tipologia Soggetto`, `Codice BDAP`, `Denominazione Soggetto`, `CF Soggetto`, `Data Cessazione Soggetto`, `Codice Zona Geografica`, `Descrizione Zona Geografica`, `Codice Regione`, `Descrizione Regione`, `Codice Provincia`, `Descrizione Provincia`, `Codice Comune`, `Descrizione Comune`, `Codice Titolo Entrata Arconet`, `Desc Titolo Entrata Arconet`, `Cod Tipologia Entrata Arconet`, `Desc Tipologia Entrata Arconet`, `Cod Comp Accant Fond Cred DE`, `Voce Comp Accant Fondo Cred DE`, `N Ord Comp Accant Fond Cred DE`, `Res. Att. 1Anno`, `Perc. Acc. al Fondo`, `Res. Att. EP`, `Tot. Res. Att. 1Anno`, `Imp. Min. Fondo`, `Fondo Cr. DE`, `_unnamed_29`
- `2024_Rendiconto SDB Allegato C FCDE Parziale_CAMPANIA.csv` (28 fields): `Esercizio Finanziario`, `Codice Tipologia Soggetto`, `Descrizione Tipologia Soggetto`, `Codice BDAP`, `Denominazione Soggetto`, `CF Soggetto`, `Data Cessazione Soggetto`, `Codice Zona Geografica`, `Descrizione Zona Geografica`, `Codice Regione`, `Descrizione Regione`, `Codice Provincia`, `Descrizione Provincia`, `Codice Comune`, `Descrizione Comune`, `Codice Titolo Entrata Arconet`, `Desc Titolo Entrata Arconet`, `Cod Tipologia Entrata Arconet`, `Desc Tipologia Entrata Arconet`, `Cod Categoria Entrata Arconet`, `Desc Categoria Entrata Arconet`, `Res. Att. 1Anno`, `Res. Att. EP`, `Perc. Acc. al Fondo`, `Tot. Res. Att. 1Anno`, `Imp. Min. Fondo`, `Fondo Cr. DE`, `_unnamed_28`
- `2024_Rendiconto SDB Allegato d Entrate per Categorie Enti Locali_CAMPANIA.csv` (26 fields): `Esercizio Finanziario`, `Codice Tipologia Soggetto`, `Descrizione Tipologia Soggetto`, `Codice BDAP`, `Denominazione Soggetto`, `CF Soggetto`, `Data Cessazione Soggetto`, `Codice Zona Geografica`, `Descrizione Zona Geografica`, `Codice Regione`, `Descrizione Regione`, `Codice Provincia`, `Descrizione Provincia`, `Codice Comune`, `Descrizione Comune`, `Codice Titolo Entrata Arconet`, `Desc Titolo Entrata Arconet`, `Cod Tipologia Entrata Arconet`, `Desc Tipologia Entrata Arconet`, `Cod Categoria Entrata Arconet`, `Desc Categoria Entrata Arconet`, `Accertamenti`, `Riscossioni in C/Residui`, `di cui entrate accertate non ricorrenti`, `Riscossioni in C/Competenza`, `_unnamed_26`
- `2024_Rendiconto SDB Allegato d Entrate per Categorie Regioni_CAMPANIA.csv` (26 fields): `Esercizio Finanziario`, `Codice Tipologia Soggetto`, `Descrizione Tipologia Soggetto`, `Codice BDAP`, `Denominazione Soggetto`, `CF Soggetto`, `Data Cessazione Soggetto`, `Codice Zona Geografica`, `Descrizione Zona Geografica`, `Codice Regione`, `Descrizione Regione`, `Codice Provincia`, `Descrizione Provincia`, `Codice Comune`, `Descrizione Comune`, `Codice Titolo Entrata Arconet`, `Desc Titolo Entrata Arconet`, `Cod Tipologia Entrata Arconet`, `Desc Tipologia Entrata Arconet`, `Cod Categoria Entrata Arconet`, `Desc Categoria Entrata Arconet`, `Accertamenti`, `Riscossioni in C/Residui`, `di cui entrate accertate non ricorrenti`, `Riscossioni in C/Competenza`, `_unnamed_26`
- `2024_Rendiconto SDB Allegato e Riepilogo Spese per Macroaggregato - Impegni_CAMPANIA.csv` (24 fields): `Esercizio Finanziario`, `Codice Tipologia Soggetto`, `Descrizione Tipologia Soggetto`, `Codice BDAP`, `Denominazione Soggetto`, `CF Soggetto`, `Data Cessazione Soggetto`, `Codice Zona Geografica`, `Descrizione Zona Geografica`, `Codice Regione`, `Descrizione Regione`, `Codice Provincia`, `Descrizione Provincia`, `Codice Comune`, `Descrizione Comune`, `Codice Titolo`, `Descrizione Titolo`, `Codice Secondo Livello`, `Descrizione Secondo Livello`, `Codice Macroaggregato Spesa`, `Descrizione Macroaggregato Spesa`, `Impegni Riepilogo`, `Di Cui Non Ricorrenti`, `_unnamed_24`
- `2024_Rendiconto SDB Allegato e Spese Correnti per Macroaggregato - Impegni_CAMPANIA.csv` (27 fields): `Esercizio Finanziario`, `Codice Tipologia Soggetto`, `Descrizione Tipologia Soggetto`, `Codice BDAP`, `Denominazione Soggetto`, `CF Soggetto`, `Data Cessazione Soggetto`, `Codice Zona Geografica`, `Descrizione Zona Geografica`, `Codice Regione`, `Descrizione Regione`, `Codice Provincia`, `Descrizione Provincia`, `Codice Comune`, `Descrizione Comune`, `Codice Missione Arconet`, `Desc Missione Arconet`, `Codice Programma Arconet`, `Desc Programma Arconet`, `Codice Titolo`, `Descrizione Titolo`, `Codice Secondo Livello`, `Descrizione Secondo Livello`, `Codice Macroaggregato Spesa`, `Descrizione Macroaggregato Spesa`, `Impegni`, `_unnamed_27`
- `2024_Rendiconto SDB Allegato e Spese Correnti per Macroaggregato - Pagamenti Conto Competenza_CAMPANIA.csv` (27 fields): `Esercizio Finanziario`, `Codice Tipologia Soggetto`, `Descrizione Tipologia Soggetto`, `Codice BDAP`, `Denominazione Soggetto`, `CF Soggetto`, `Data Cessazione Soggetto`, `Codice Zona Geografica`, `Descrizione Zona Geografica`, `Codice Regione`, `Descrizione Regione`, `Codice Provincia`, `Descrizione Provincia`, `Codice Comune`, `Descrizione Comune`, `Codice Missione Arconet`, `Desc Missione Arconet`, `Codice Programma Arconet`, `Desc Programma Arconet`, `Codice Titolo`, `Descrizione Titolo`, `Codice Secondo Livello`, `Descrizione Secondo Livello`, `Codice Macroaggregato Spesa`, `Descrizione Macroaggregato Spesa`, `Pagamenti C/Competenza`, `_unnamed_27`
- `2024_Rendiconto SDB Allegato e Spese Correnti per Macroaggregato - Pagamenti Conto Residui_CAMPANIA.csv` (27 fields): `Esercizio Finanziario`, `Codice Tipologia Soggetto`, `Descrizione Tipologia Soggetto`, `Codice BDAP`, `Denominazione Soggetto`, `CF Soggetto`, `Data Cessazione Soggetto`, `Codice Zona Geografica`, `Descrizione Zona Geografica`, `Codice Regione`, `Descrizione Regione`, `Codice Provincia`, `Descrizione Provincia`, `Codice Comune`, `Descrizione Comune`, `Codice Missione Arconet`, `Desc Missione Arconet`, `Codice Programma Arconet`, `Desc Programma Arconet`, `Codice Titolo`, `Descrizione Titolo`, `Codice Secondo Livello`, `Descrizione Secondo Livello`, `Codice Macroaggregato Spesa`, `Descrizione Macroaggregato Spesa`, `Pagamenti C/Residui`, `_unnamed_27`
- `2024_Rendiconto SDB Allegato e Spese in Conto Capitale per Macroaggregato - Impegni_CAMPANIA.csv` (27 fields): `Esercizio Finanziario`, `Codice Tipologia Soggetto`, `Descrizione Tipologia Soggetto`, `Codice BDAP`, `Denominazione Soggetto`, `CF Soggetto`, `Data Cessazione Soggetto`, `Codice Zona Geografica`, `Descrizione Zona Geografica`, `Codice Regione`, `Descrizione Regione`, `Codice Provincia`, `Descrizione Provincia`, `Codice Comune`, `Descrizione Comune`, `Codice Missione Arconet`, `Desc Missione Arconet`, `Codice Programma Arconet`, `Desc Programma Arconet`, `Codice Titolo`, `Descrizione Titolo`, `Codice Secondo Livello`, `Descrizione Secondo Livello`, `Codice Macroaggregato Spesa`, `Descrizione Macroaggregato Spesa`, `Impegni`, `_unnamed_27`
- `2024_Rendiconto SDB Allegato e Spese in Conto Capitale per Macroaggregato - Pagamenti Conto Competenza_CAMPANIA.csv` (27 fields): `Esercizio Finanziario`, `Codice Tipologia Soggetto`, `Descrizione Tipologia Soggetto`, `Codice BDAP`, `Denominazione Soggetto`, `CF Soggetto`, `Data Cessazione Soggetto`, `Codice Zona Geografica`, `Descrizione Zona Geografica`, `Codice Regione`, `Descrizione Regione`, `Codice Provincia`, `Descrizione Provincia`, `Codice Comune`, `Descrizione Comune`, `Codice Missione Arconet`, `Desc Missione Arconet`, `Codice Programma Arconet`, `Desc Programma Arconet`, `Codice Titolo`, `Descrizione Titolo`, `Codice Secondo Livello`, `Descrizione Secondo Livello`, `Codice Macroaggregato Spesa`, `Descrizione Macroaggregato Spesa`, `Pagamenti C/Competenza`, `_unnamed_27`
- `2024_Rendiconto SDB Allegato e Spese in Conto Capitale per Macroaggregato - Pagamenti Conto Residui_CAMPANIA.csv` (27 fields): `Esercizio Finanziario`, `Codice Tipologia Soggetto`, `Descrizione Tipologia Soggetto`, `Codice BDAP`, `Denominazione Soggetto`, `CF Soggetto`, `Data Cessazione Soggetto`, `Codice Zona Geografica`, `Descrizione Zona Geografica`, `Codice Regione`, `Descrizione Regione`, `Codice Provincia`, `Descrizione Provincia`, `Codice Comune`, `Descrizione Comune`, `Codice Missione Arconet`, `Desc Missione Arconet`, `Codice Programma Arconet`, `Desc Programma Arconet`, `Codice Titolo`, `Descrizione Titolo`, `Codice Secondo Livello`, `Descrizione Secondo Livello`, `Codice Macroaggregato Spesa`, `Descrizione Macroaggregato Spesa`, `Pagamenti C/Residui`, `_unnamed_27`
- `2024_Rendiconto SDB Allegato e Spese per Rimborso di Prestiti per Macroaggregato - Impegni_CAMPANIA.csv` (27 fields): `Esercizio Finanziario`, `Codice Tipologia Soggetto`, `Descrizione Tipologia Soggetto`, `Codice BDAP`, `Denominazione Soggetto`, `CF Soggetto`, `Data Cessazione Soggetto`, `Codice Zona Geografica`, `Descrizione Zona Geografica`, `Codice Regione`, `Descrizione Regione`, `Codice Provincia`, `Descrizione Provincia`, `Codice Comune`, `Descrizione Comune`, `Codice Missione Arconet`, `Desc Missione Arconet`, `Codice Programma Arconet`, `Desc Programma Arconet`, `Codice Titolo`, `Descrizione Titolo`, `Codice Secondo Livello`, `Descrizione Secondo Livello`, `Codice Macroaggregato Spesa`, `Descrizione Macroaggregato Spesa`, `Impegni`, `_unnamed_27`
- `2024_Rendiconto SDB Allegato e Spese per Servizi Conto Terzi per Macroaggregato - Impegni_CAMPANIA.csv` (27 fields): `Esercizio Finanziario`, `Codice Tipologia Soggetto`, `Descrizione Tipologia Soggetto`, `Codice BDAP`, `Denominazione Soggetto`, `CF Soggetto`, `Data Cessazione Soggetto`, `Codice Zona Geografica`, `Descrizione Zona Geografica`, `Codice Regione`, `Descrizione Regione`, `Codice Provincia`, `Descrizione Provincia`, `Codice Comune`, `Descrizione Comune`, `Codice Missione Arconet`, `Desc Missione Arconet`, `Codice Programma Arconet`, `Desc Programma Arconet`, `Codice Titolo`, `Descrizione Titolo`, `Codice Secondo Livello`, `Descrizione Secondo Livello`, `Codice Macroaggregato Spesa`, `Descrizione Macroaggregato Spesa`, `Impegni`, `_unnamed_27`
- `2024_Rendiconto SDB Allegato f Accertamenti Pluriennali_CAMPANIA.csv` (25 fields): `Esercizio Finanziario`, `Codice Tipologia Soggetto`, `Descrizione Tipologia Soggetto`, `Codice BDAP`, `Denominazione Soggetto`, `CF Soggetto`, `Data Cessazione Soggetto`, `Codice Zona Geografica`, `Descrizione Zona Geografica`, `Codice Regione`, `Descrizione Regione`, `Codice Provincia`, `Descrizione Provincia`, `Codice Comune`, `Descrizione Comune`, `Codice Titolo Entrate`, `Descrizione Titolo Entrate`, `Codice Tipologia Entrate`, `Descrizione Tipologia Entrate`, `Previsioni di competenza Anno1`, `Accertamenti Anno1`, `Previsioni di competenza Anno2`, `Accertamenti Anno2`, `Accertamenti Anni Successivi`, `_unnamed_25`
- `2024_Rendiconto SDB Allegato g Impegni Pluriennali_CAMPANIA.csv` (25 fields): `Esercizio Finanziario`, `Codice Tipologia Soggetto`, `Descrizione Tipologia Soggetto`, `Codice BDAP`, `Denominazione Soggetto`, `CF Soggetto`, `Data Cessazione Soggetto`, `Codice Zona Geografica`, `Descrizione Zona Geografica`, `Codice Regione`, `Descrizione Regione`, `Codice Provincia`, `Descrizione Provincia`, `Codice Comune`, `Descrizione Comune`, `Codice Titolo`, `Descrizione Titolo`, `Codice Macroaggregato`, `Descrizione Macroaggregato`, `Previsioni di competenza Anno1`, `Impegni Anno1`, `Previsioni di Competenza del Bilancio Pluriennale Anno2`, `Impegni Anno2`, `Impegni Anni Successivi`, `_unnamed_25`
- `2024_Rendiconto SDB Allegato h Costi per Missione_CAMPANIA.csv` (24 fields): `Esercizio Finanziario`, `Codice Tipologia Soggetto`, `Descrizione Tipologia Soggetto`, `Codice BDAP`, `Denominazione Soggetto`, `CF Soggetto`, `Data Cessazione Soggetto`, `Codice Zona Geografica`, `Descrizione Zona Geografica`, `Codice Regione`, `Descrizione Regione`, `Codice Provincia`, `Descrizione Provincia`, `Codice Comune`, `Descrizione Comune`, `Codice Missione Arconet`, `Descrizione Missione Arconet`, `Codice I Livello`, `Descrizione I Livello`, `Descrizione II Livello`, `Codice III Livello`, `Descrizione III Livello`, `Importo Voci CE Rendiconto`, `_unnamed_24`
- `2024_Rendiconto SDB Allegato i Politica Regionale Unitaria_CAMPANIA.csv` (35 fields): `Esercizio Finanziario`, `Codice Tipologia Soggetto`, `Descrizione Tipologia Soggetto`, `Codice BDAP`, `Denominazione Soggetto`, `CF Soggetto`, `Data Cessazione Soggetto`, `Codice Zona Geografica`, `Descrizione Zona Geografica`, `Codice Regione`, `Descrizione Regione`, `Codice Provincia`, `Descrizione Provincia`, `Codice Comune`, `Descrizione Comune`, `Codice Missione Arconet`, `Descrizione Missione Arconet`, `Codice Programma Arconet`, `Descrizione Programma Arconet`, `Codice Titolo`, `Descrizione Titolo`, `Residui Passivi Iniziali`, `Previsioni Definitive di Competenza`, `Previsioni Definitive di Cassa`, `Pagamenti C/Residuo`, `Pagamenti C/Competenza`, `Totale Pagamenti`, `Riaccertamenti Residui`, `Impegni`, `Fondo Puriennale Vincolato`, `Economie C/Competenza`, `Residui Passivi da Esercizi Precedenti`, `Residui Passivi da Esercizio di Competenza`, `Residui Passivi da riportare`, `_unnamed_35`
- `2024_Rendiconto SDB Allegato j Spese su Contributi UE e Internazionali_CAMPANIA.csv` (35 fields): `Esercizio Finanziario`, `Codice Tipologia Soggetto`, `Descrizione Tipologia Soggetto`, `Codice BDAP`, `Denominazione Soggetto`, `CF Soggetto`, `Data Cessazione Soggetto`, `Codice Zona Geografica`, `Descrizione Zona Geografica`, `Codice Regione`, `Descrizione Regione`, `Codice Provincia`, `Descrizione Provincia`, `Codice Comune`, `Descrizione Comune`, `Codice Missione Arconet`, `Descrizione Missione Arconet`, `Codice Programma Arconet`, `Descrizione Programma Arconet`, `Codice Titolo`, `Descrizione Titolo`, `Residui Passivi Iniziali`, `Previsioni Definitive di Competenza`, `Previsioni Definitive di Cassa`, `Pagamenti C/Residuo`, `Pagamenti C/Competenza`, `Totale Pagamenti`, `Riaccertamenti Residui`, `Impegni`, `Fondo Puriennale Vincolato`, `Economie C/Competenza`, `Residui Passivi da Esercizi Precedenti`, `Residui Passivi da Esercizio di Competenza`, `Residui Passivi da riportare`, `_unnamed_35`
- `2024_Rendiconto SDB Allegato k Funzioni Delegate dalle Regioni_CAMPANIA.csv` (35 fields): `Esercizio Finanziario`, `Codice Tipologia Soggetto`, `Descrizione Tipologia Soggetto`, `Codice BDAP`, `Denominazione Soggetto`, `CF Soggetto`, `Data Cessazione Soggetto`, `Codice Zona Geografica`, `Descrizione Zona Geografica`, `Codice Regione`, `Descrizione Regione`, `Codice Provincia`, `Descrizione Provincia`, `Codice Comune`, `Descrizione Comune`, `Codice Missione Arconet`, `Descrizione Missione Arconet`, `Codice Programma Arconet`, `Descrizione Programma Arconet`, `Codice Titolo`, `Descrizione Titolo`, `Residui Passivi Iniziali`, `Previsioni Definitive di Competenza`, `Previsioni Definitive di Cassa`, `Pagamenti C/Residuo`, `Pagamenti C/Competenza`, `Totale Pagamenti`, `Riaccertamenti Residui`, `Impegni`, `Fondo Puriennale Vincolato`, `Economie C/Competenza`, `Residui Passivi da Esercizi Precedenti`, `Residui Passivi da Esercizio di Competenza`, `Residui Passivi da riportare`, `_unnamed_35`
- `2024_Rendiconto SDB Conto Economico_CAMPANIA.csv` (31 fields): `Esercizio Finanziario`, `Codice Tipologia Soggetto`, `Descrizione Tipologia Soggetto`, `Codice BDAP`, `Denominazione Soggetto`, `CF Soggetto`, `Data Cessazione Soggetto`, `Codice Zona Geografica`, `Descrizione Zona Geografica`, `Codice Regione`, `Descrizione Regione`, `Codice Provincia`, `Descrizione Provincia`, `Codice Comune`, `Descrizione Comune`, `Codice Voce Conto Economico`, `Prospetto I Livello`, `Gruppo I Livello`, `Codice I Livello`, `Descrizione I Livello`, `Prospetto II Livello`, `Gruppo II Livello`, `Codice II Livello`, `Descrizione II Livello`, `Prospetto III Livello`, `Gruppo III Livello`, `Codice III Livello`, `Descrizione III Livello`, `Valore Economico`, `Valore Economico Esercizio Precedente`, `_unnamed_31`
- `2024_Rendiconto SDB Entrate - Voce di Riepilogo_CAMPANIA.csv` (20 fields): `Esercizio Finanziario`, `Codice Tipologia Soggetto`, `Descrizione Tipologia Soggetto`, `Codice BDAP`, `Denominazione Soggetto`, `CF Soggetto`, `Data Cessazione Soggetto`, `Codice Zona Geografica`, `Descrizione Zona Geografica`, `Codice Regione`, `Descrizione Regione`, `Codice Provincia`, `Descrizione Provincia`, `Codice Comune`, `Descrizione Comune`, `Cod Voce di Riepilogo Entrate`, `Desc Voce di Riepilogo Entrate`, `Pre. Def. in CC`, `Pre. Def. in CC di cui UFA`, `_unnamed_20`
- `2024_Rendiconto SDB Entrate Riepilogo Titoli - Voce di Riepilogo_CAMPANIA.csv` (21 fields): `Esercizio Finanziario`, `Codice Tipologia Soggetto`, `Descrizione Tipologia Soggetto`, `Codice BDAP`, `Denominazione Soggetto`, `CF Soggetto`, `Data Cessazione Soggetto`, `Codice Zona Geografica`, `Descrizione Zona Geografica`, `Codice Regione`, `Descrizione Regione`, `Codice Provincia`, `Descrizione Provincia`, `Codice Comune`, `Descrizione Comune`, `Cod Voce di Riepilogo Entrate`, `Desc Voce di Riepilogo Entrate`, `Ordine Esposizione`, `Previsioni Definitive di Competenza (CP)`, `Previsioni Definitive in CC di cui utilizzo fondo anticipazioni`, `_unnamed_21`
- `2024_Rendiconto SDB Entrate Riepilogo Titoli_CAMPANIA.csv` (31 fields): `Esercizio Finanziario`, `Codice Tipologia Soggetto`, `Descrizione Tipologia Soggetto`, `Codice BDAP`, `Denominazione Soggetto`, `CF Soggetto`, `Data Cessazione Soggetto`, `Codice Zona Geografica`, `Descrizione Zona Geografica`, `Codice Regione`, `Descrizione Regione`, `Codice Provincia`, `Descrizione Provincia`, `Codice Comune`, `Descrizione Comune`, `Codice Titolo`, `Descrizione Titolo`, `Residui Attivi Iniziali`, `Previsioni Definitive di Competenza`, `Previsioni Definitive di Cassa`, `Riscossioni in C/Residui`, `Riscossioni in C/Competenza`, `Totale Riscossioni`, `Riaccertamenti Residui`, `Accertamenti`, `Residui Attivi in C/Residui`, `Maggiori o Minori Entrate di Cassa`, `Maggiori o Minori Entrate di Competenza`, `Residui Attivi in C/Competenza`, `Totale Residui Attivi da Riportare`, `_unnamed_31`
- `2024_Rendiconto SDB Entrate_CAMPANIA.csv` (33 fields): `Esercizio Finanziario`, `Codice Tipologia Soggetto`, `Descrizione Tipologia Soggetto`, `Codice BDAP`, `Denominazione Soggetto`, `CF Soggetto`, `Data Cessazione Soggetto`, `Codice Zona Geografica`, `Descrizione Zona Geografica`, `Codice Regione`, `Descrizione Regione`, `Codice Provincia`, `Descrizione Provincia`, `Codice Comune`, `Descrizione Comune`, `Codice Titolo Entrata Arconet`, `Desc Titolo Entrata Arconet`, `Cod Tipologia Entrata Arconet`, `Desc Tipologia Entrata Arconet`, `Residui Attivi Iniziali`, `Riscos. in CR`, `Riacc. Res.`, `Res. Att. In CR`, `Pre.  Def. in CC`, `Riscos. in CC`, `Accert. in CC`, `Magg. o min. entr. di CC`, `Res. Att. In CC`, `Pre.  Def. Di Cassa`, `Tot. Riscos.`, `Magg. o min. entr. di Cassa`, `Res. Att. da riportare tot.`, `_unnamed_33`
- `2024_Rendiconto SDB Equilibri Enti Locali_CAMPANIA.csv` (22 fields): `Esercizio Finanziario`, `Codice Tipologia Soggetto`, `Descrizione Tipologia Soggetto`, `Codice BDAP`, `Denominazione Soggetto`, `CF Soggetto`, `Data Cessazione Soggetto`, `Codice Zona Geografica`, `Descrizione Zona Geografica`, `Codice Regione`, `Descrizione Regione`, `Codice Provincia`, `Descrizione Provincia`, `Codice Comune`, `Descrizione Comune`, `Codice Voce Equil Bil Enti Loc`, `Desc Voce Equil Bil Enti Loc`, `Fondo di Cassa all'ini. eser.`, `Accert. o Impeg. in CC`, `Impeg. di cui FA di liq.`, `Impeg. di cui est. ant. prest.`, `_unnamed_22`
- `2024_Rendiconto SDB Equilibri Regioni_CAMPANIA.csv` (21 fields): `Esercizio Finanziario`, `Codice Tipologia Soggetto`, `Descrizione Tipologia Soggetto`, `Codice BDAP`, `Denominazione Soggetto`, `CF Soggetto`, `Data Cessazione Soggetto`, `Codice Zona Geografica`, `Descrizione Zona Geografica`, `Codice Regione`, `Descrizione Regione`, `Codice Provincia`, `Descrizione Provincia`, `Codice Comune`, `Descrizione Comune`, `Codice Voce Equil Bil Regioni`, `Desc Voce Equil Bil Regioni`, `Accert. o Impeg. in CC`, `Impeg. di cui FA di liq.`, `Impeg. di cui est. ant. prest.`, `_unnamed_21`
- `2024_Rendiconto SDB Quadro Generale Riassuntivo Entrate - Voce di Riepilogo_CAMPANIA.csv` (24 fields): `Esercizio Finanziario`, `Codice Tipologia Soggetto`, `Descrizione Tipologia Soggetto`, `Codice BDAP`, `Denominazione Soggetto`, `CF Soggetto`, `Data Cessazione Soggetto`, `Codice Zona Geografica`, `Descrizione Zona Geografica`, `Codice Regione`, `Descrizione Regione`, `Codice Provincia`, `Descrizione Provincia`, `Codice Comune`, `Descrizione Comune`, `Cod Voce di Riepilogo Entrate`, `Desc Voce di Riepilogo Entrate`, `Ordine di esposizione`, `Accert Conto Comp`, `Incassi Conto Comp`, `Accert Conto Comp di cui FAL`, `Accert di cui FPV fin. da debito`, `Accert di cui Disav. da debito`, `_unnamed_24`
- `2024_Rendiconto SDB Quadro Generale Riassuntivo Entrate_CAMPANIA.csv` (20 fields): `Esercizio Finanziario`, `Codice Tipologia Soggetto`, `Descrizione Tipologia Soggetto`, `Codice BDAP`, `Denominazione Soggetto`, `CF Soggetto`, `Data Cessazione Soggetto`, `Codice Zona Geografica`, `Descrizione Zona Geografica`, `Codice Regione`, `Descrizione Regione`, `Codice Provincia`, `Descrizione Provincia`, `Codice Comune`, `Descrizione Comune`, `Codice Titolo Entrata Arconet`, `Desc Titolo Entrata Arconet`, `Accertamenti`, `Incassi`, `_unnamed_20`
- `2024_Rendiconto SDB Quadro Generale Riassuntivo Gestione Bilancio e Accantonamenti_CAMPANIA.csv` (23 fields): `Esercizio Finanziario`, `Codice Tipologia Soggetto`, `Descrizione Tipologia Soggetto`, `Codice BDAP`, `Denominazione Soggetto`, `CF Soggetto`, `Data Cessazione Soggetto`, `Codice Zona Geografica`, `Descrizione Zona Geografica`, `Codice Regione`, `Descrizione Regione`, `Codice Provincia`, `Descrizione Provincia`, `Codice Comune`, `Descrizione Comune`, `GestBil Avanzo - Disavanzo di Competenza`, `GestBil Risorse Accantonate Stanziate Anno N`, `GestBil Risorse Vincolate nel Bilancio`, `GestBil Equilibrio di Bilancio`, `GestAcc Equilibrio di Bilancio`, `GestAcc Variazione Accantonamenti`, `GestAcc Equilibrio Complessivo`, `_unnamed_23`
- `2024_Rendiconto SDB Quadro Generale Riassuntivo Spese - Voce di Riepilogo_CAMPANIA.csv` (21 fields): `Esercizio Finanziario`, `Codice Tipologia Soggetto`, `Descrizione Tipologia Soggetto`, `Codice BDAP`, `Denominazione Soggetto`, `CF Soggetto`, `Data Cessazione Soggetto`, `Codice Zona Geografica`, `Descrizione Zona Geografica`, `Codice Regione`, `Descrizione Regione`, `Codice Provincia`, `Descrizione Provincia`, `Codice Comune`, `Descrizione Comune`, `Codice Voce di Riepilogo Spese`, `Desc Voce di Riepilogo Spese`, `Ordine di esposizione`, `Impegni`, `Pagamenti`, `_unnamed_21`
- `2024_Rendiconto SDB Quadro Generale Riassuntivo Spese_CAMPANIA.csv` (24 fields): `Esercizio Finanziario`, `Codice Tipologia Soggetto`, `Descrizione Tipologia Soggetto`, `Codice BDAP`, `Denominazione Soggetto`, `CF Soggetto`, `Data Cessazione Soggetto`, `Codice Zona Geografica`, `Descrizione Zona Geografica`, `Codice Regione`, `Descrizione Regione`, `Codice Provincia`, `Descrizione Provincia`, `Codice Comune`, `Descrizione Comune`, `Codice Titolo Spese Arconet`, `Desc Titolo Spese Arconet`, `Impegni`, `Pagamenti`, `Impegni di Fondo pluriennale vincolato`, `Impegni di cui Fondo pluriennale vincolato in c/capitale finanziato da debito`, `Impegni di cui Fondo Anticipazione di liquidità`, `Impegni Fondo Anticipazione di liq. stanziamento definitivo di bilancio`, `_unnamed_24`
- `2024_Rendiconto SDB Spese - Voce di Riepilogo_CAMPANIA.csv` (19 fields): `Esercizio Finanziario`, `Codice Tipologia Soggetto`, `Descrizione Tipologia Soggetto`, `Codice BDAP`, `Denominazione Soggetto`, `CF Soggetto`, `Data Cessazione Soggetto`, `Codice Zona Geografica`, `Descrizione Zona Geografica`, `Codice Regione`, `Descrizione Regione`, `Codice Provincia`, `Descrizione Provincia`, `Codice Comune`, `Descrizione Comune`, `Codice Voce di Riepilogo Spese`, `Desc Voce di Riepilogo Spese`, `Pre.  Def. in CC`, `_unnamed_19`
- `2024_Rendiconto SDB Spese Riepilogo Missioni - Voce di Riepilogo_CAMPANIA.csv` (20 fields): `Esercizio Finanziario`, `Codice Tipologia Soggetto`, `Descrizione Tipologia Soggetto`, `Codice BDAP`, `Denominazione Soggetto`, `CF Soggetto`, `Data Cessazione Soggetto`, `Codice Zona Geografica`, `Descrizione Zona Geografica`, `Codice Regione`, `Descrizione Regione`, `Codice Provincia`, `Descrizione Provincia`, `Codice Comune`, `Descrizione Comune`, `Codice Voce di Riepilogo`, `Descrizione Voce di Riepilogo`, `Ordine di Esposizione`, `Previsioni Definitive di Cassa`, `_unnamed_20`
- `2024_Rendiconto SDB Spese Riepilogo Missioni_CAMPANIA.csv` (31 fields): `Esercizio Finanziario`, `Codice Tipologia Soggetto`, `Descrizione Tipologia Soggetto`, `Codice BDAP`, `Denominazione Soggetto`, `CF Soggetto`, `Data Cessazione Soggetto`, `Codice Zona Geografica`, `Descrizione Zona Geografica`, `Codice Regione`, `Descrizione Regione`, `Codice Provincia`, `Descrizione Provincia`, `Codice Comune`, `Descrizione Comune`, `Codice Missione`, `Descrizione Missione`, `Residui Passivi Iniziali`, `Previsioni Definitive di Competenza`, `Previsioni Definitive di Cassa`, `Pagamenti C/Residuo`, `Pagamenti C/Competenza`, `Totale Pagamenti`, `Riaccertamenti Residui`, `Impegni`, `Fondo Puriennale Vincolato`, `Economie C/Competenza`, `Residui Passivi da Esercizi Precedenti`, `Residui Passivi da Esercizio di Competenza`, `Residui Passivi da riportare`, `_unnamed_31`
- `2024_Rendiconto SDB Spese Riepilogo Titoli - Voce di Riepilogo_CAMPANIA.csv` (20 fields): `Esercizio Finanziario`, `Codice Tipologia Soggetto`, `Descrizione Tipologia Soggetto`, `Codice BDAP`, `Denominazione Soggetto`, `CF Soggetto`, `Data Cessazione Soggetto`, `Codice Zona Geografica`, `Descrizione Zona Geografica`, `Codice Regione`, `Descrizione Regione`, `Codice Provincia`, `Descrizione Provincia`, `Codice Comune`, `Descrizione Comune`, `Codice Voce di Riepilogo`, `Descrizione Voce di Riepilogo`, `Ordine di Esposizione`, `Previsioni Definitive di Competenza`, `_unnamed_20`
- `2024_Rendiconto SDB Spese Riepilogo Titoli_CAMPANIA.csv` (31 fields): `Esercizio Finanziario`, `Codice Tipologia Soggetto`, `Descrizione Tipologia Soggetto`, `Codice BDAP`, `Denominazione Soggetto`, `CF Soggetto`, `Data Cessazione Soggetto`, `Codice Zona Geografica`, `Descrizione Zona Geografica`, `Codice Regione`, `Descrizione Regione`, `Codice Provincia`, `Descrizione Provincia`, `Codice Comune`, `Descrizione Comune`, `Codice Titolo`, `Descrizione Titolo`, `Residui Passivi Iniziali`, `Previsioni Definitive di Competenza`, `Previsioni Definitive di Cassa`, `Pagamenti in C/Residui`, `Pagamenti in C/Competenza`, `Totale Pagamenti`, `Riaccertamenti Residui`, `Impegni`, `Fondo Pluriennale Vincolato`, `Economie di Competenza`, `Residui Passivi da Esercizi Precedenti`, `Residui Passivi da Esercizio di Competenza`, `Residui passivi da riportare totale`, `_unnamed_31`
- `2024_Rendiconto SDB Spese_CAMPANIA.csv` (35 fields): `Esercizio Finanziario`, `Codice Tipologia Soggetto`, `Descrizione Tipologia Soggetto`, `Codice BDAP`, `Denominazione Soggetto`, `CF Soggetto`, `Data Cessazione Soggetto`, `Codice Zona Geografica`, `Descrizione Zona Geografica`, `Codice Regione`, `Descrizione Regione`, `Codice Provincia`, `Descrizione Provincia`, `Codice Comune`, `Descrizione Comune`, `Codice Missione Arconet`, `Desc Missione Arconet`, `Codice Programma Arconet`, `Desc Programma Arconet`, `Codice Titolo Spese Arconet`, `Desc Titolo Spese Arconet`, `Res. Pass. Iniziali`, `Pag. in CR`, `Riacc. Res.`, `Res. Pas. In CR`, `Pre.  Def. in CC`, `Pag. in CC`, `Impegni`, `Econ. in CC`, `Res. Pas. In CC`, `Pre.  Def. Di Cassa`, `Tot. Pag.`, `FPV`, `Res. Pas. da riportare tot.`, `_unnamed_35`
- `2024_Rendiconto SDB Stato Patrimoniale Attivo_CAMPANIA.csv` (30 fields): `Esercizio Finanziario`, `Codice Tipologia Soggetto`, `Descrizione Tipologia Soggetto`, `Codice BDAP`, `Denominazione Soggetto`, `CF Soggetto`, `Data Cessazione Soggetto`, `Codice Zona Geografica`, `Descrizione Zona Geografica`, `Codice Regione`, `Descrizione Regione`, `Codice Provincia`, `Descrizione Provincia`, `Codice Comune`, `Descrizione Comune`, `Codice I Livello`, `Descrizione I Livello`, `Codice II Livello`, `Descrizione II Livello`, `Codice III Livello`, `Descrizione III Livello`, `Codice IV Livello`, `Descrizione IV Livello`, `Codice v Livello`, `Descrizione V Livello`, `Consistenza Anno Corrente`, `Consistenza Anno Precedente`, `Di Cui Consistenza Anno Corrente`, `Di Cui Consistenza Anno Precedente`, `_unnamed_30`
- `2024_Rendiconto SDB Stato Patrimoniale Passivo - Conti di Ordine_CAMPANIA.csv` (24 fields): `Esercizio Finanziario`, `Codice Tipologia Soggetto`, `Descrizione Tipologia Soggetto`, `Codice BDAP`, `Denominazione Soggetto`, `CF Soggetto`, `Data Cessazione Soggetto`, `Codice Zona Geografica`, `Descrizione Zona Geografica`, `Codice Regione`, `Descrizione Regione`, `Codice Provincia`, `Descrizione Provincia`, `Codice Comune`, `Descrizione Comune`, `Codice I Livello`, `Descrizione I Livello`, `Codice II Livello`, `Descrizione II Livello`, `Codice III Livello`, `Descrizione III Livello`, `Consistenza Anno Corrente`, `Consistenza Anno Precedente`, `_unnamed_24`
- `2024_Rendiconto SDB Stato Patrimoniale Passivo_CAMPANIA.csv` (28 fields): `Esercizio Finanziario`, `Codice Tipologia Soggetto`, `Descrizione Tipologia Soggetto`, `Codice BDAP`, `Denominazione Soggetto`, `CF Soggetto`, `Data Cessazione Soggetto`, `Codice Zona Geografica`, `Descrizione Zona Geografica`, `Codice Regione`, `Descrizione Regione`, `Codice Provincia`, `Descrizione Provincia`, `Codice Comune`, `Descrizione Comune`, `Codice I Livello`, `Descrizione I Livello`, `Codice II Livello`, `Descrizione II Livello`, `Codice III Livello`, `Descrizione III Livello`, `Codice IV Livello`, `Descrizione IV Livello`, `Codice V Livello`, `Descrizione V Livello`, `Consistenza Anno Corrente`, `Consistenza Anno Precedente`, `_unnamed_28`
- Coverage by period: 2024: 118/118

Source: [bdap-budget-2024](https://openbdap.rgs.mef.gov.it/Datasets_FET/Rendiconto/2024/2024_Rendiconto%20-%20Schemi%20di%20bilancio_CAMPANIA.zip)

### bdap-indicators-2024

Records: 18,771; associated municipalities: 118/118; periods: 2024.

ELCOMU statements. Hierarchical totals require semantic selection before adding values.

Staging file: `data/collection/bdap-indicators-2024.rows.jsonl.gz`; SHA-256: `a262725ed8443e7a2130bdec6bc29088313106f9cc8cfae950bdb603c44d51f9`.

- `2024_Rendiconto PDI Analitici di Entrate 2-b_CAMPANIA.csv` (28 fields): `Esercizio Finanziario`, `Codice Tipologia Soggetto`, `Descrizione Tipologia Soggetto`, `Codice BDAP`, `Denominazione Soggetto`, `CF Soggetto`, `Data Cessazione Soggetto`, `Codice Zona Geografica`, `Descrizione Zona Geografica`, `Codice Regione`, `Descrizione Regione`, `Codice Provincia`, `Descrizione Provincia`, `Codice Comune`, `Descrizione Comune`, `Codice Titolo`, `Descrizione Titolo`, `Codice Tipologia`, `Descrizione Tipologia`, `Previsioni Iniziali Competenza/Totale Previsioni Iniziali Competenza`, `Previsioni Definitive Competenza/Totale Previsioni Definitive Competenza`, `Accertamenti/Totale Accertamenti`, `Incidenza Riscossione Prevista nel Bilancio di Previsione Iniziale`, `Incidenza Riscossione Prevista nelle Previsioni Definitive`, `Incidenza Riscossione Complessiva`, `Incidenza Riscossione dei Crediti Esigibili nell'Esercizio Finanziario`, `Incidenza Riscossione dei Crediti Esigibili negli Esercizi Precedenti`, `_unnamed_28`
- `2024_Rendiconto PDI Analitici di Entrate 4-b_CAMPANIA.csv` (28 fields): `Esercizio Finanziario`, `Codice Tipologia Soggetto`, `Descrizione Tipologia Soggetto`, `Codice BDAP`, `Denominazione Soggetto`, `CF Soggetto`, `Data Cessazione Soggetto`, `Codice Zona Geografica`, `Descrizione Zona Geografica`, `Codice Regione`, `Descrizione Regione`, `Codice Provincia`, `Descrizione Provincia`, `Codice Comune`, `Descrizione Comune`, `Codice Titolo`, `Descrizione Titolo`, `Codice Tipologia`, `Descrizione Tipologia`, `Previsioni Iniziali Competenza/Totale Previsioni Iniziali Competenza`, `Previsioni Definitive Competenza/Totale Previsioni Definitive Competenza`, `Accertamenti/Totale Accertamenti`, `Incidenza Riscossione Prevista nel Bilancio Di Previsione Iniziale`, `Incidenza Riscossione Prevista nelle Previsioni Definitive`, `Incidenza Riscossione Complessiva`, `Incidenza Riscossione dei Crediti Esigibili nell'esercizio Finanziario`, `Incidenza Riscossione dei Crediti Esigibili negli Esercizi Precedenti`, `_unnamed_28`
- `2024_Rendiconto PDI Analitici di Spese 2-c_CAMPANIA.csv` (27 fields): `Esercizio Finanziario`, `Codice Tipologia Soggetto`, `Descrizione Tipologia Soggetto`, `Codice BDAP`, `Denominazione Soggetto`, `CF Soggetto`, `Data Cessazione Soggetto`, `Codice Zona Geografica`, `Descrizione Zona Geografica`, `Codice Regione`, `Descrizione Regione`, `Codice Provincia`, `Descrizione Provincia`, `Codice Comune`, `Descrizione Comune`, `Codice Missione Arconet`, `Descrizione Missione Arconet`, `Codice Programma Arconet`, `Descrizione Programma Arconet`, `Incidenza Missione Programma Previsione Iniziale`, `Incidenza Missione Programma Di Cui Fondo Pluriennale Vincolato Previsione Iniziale`, `Incidenza Missione Programma Previsione Definitiva`, `Incidenza Missione Programma Di Cui Fondo Pluriennale Vincolato Previsione Definitiva`, `Incidenza Missione Programma Dati di Rendiconto`, `Incidenza Missione Programma Di Cui Fondo Pluriennale Vincolato Dati di Rendiconto`, `Incidenza Missione Programma Di Cui Incidenza Economia di Spesa Dati di Rendiconto`, `_unnamed_27`
- `2024_Rendiconto PDI Analitici di Spese 2-d_CAMPANIA.csv` (25 fields): `Esercizio Finanziario`, `Codice Tipologia Soggetto`, `Descrizione Tipologia Soggetto`, `Codice BDAP`, `Denominazione Soggetto`, `CF Soggetto`, `Data Cessazione Soggetto`, `Codice Zona Geografica`, `Descrizione Zona Geografica`, `Codice Regione`, `Descrizione Regione`, `Codice Provincia`, `Descrizione Provincia`, `Codice Comune`, `Descrizione Comune`, `Codice Missione Arconet`, `Descrizione Missione Arconet`, `Codice Programma Arconet`, `Descrizione Programma Arconet`, `Capacità di Pagamento Previsione Iniziale`, `Capacità di Pagamento Previsione Definitive`, `Capacità di Pagamento a Consuntivo`, `Capacità Di Pagamento delle Spese in Conto Competenza Impegni`, `Capacità Di Pagamento delle Spese Esigibili negli Esercizi Precedenti`, `_unnamed_25`
- `2024_Rendiconto PDI Analitici di Spese 4-c_CAMPANIA.csv` (27 fields): `Esercizio Finanziario`, `Codice Tipologia Soggetto`, `Descrizione Tipologia Soggetto`, `Codice BDAP`, `Denominazione Soggetto`, `CF Soggetto`, `Data Cessazione Soggetto`, `Codice Zona Geografica`, `Descrizione Zona Geografica`, `Codice Regione`, `Descrizione Regione`, `Codice Provincia`, `Descrizione Provincia`, `Codice Comune`, `Descrizione Comune`, `Codice Missione Arconet`, `Descrizione Missione Arconet`, `Codice Programma Arconet`, `Descrizione Programma Arconet`, `Incidenza Missione Programma Previsione Iniziale`, `Incidenza Missione Programma Di Cui Fondo Pluriennale Vincolato Previsione Iniziale`, `Incidenza Missione Programma Previsione Definitiva`, `Incidenza Missione Programma Di Cui Fondo Pluriennale Vincolato Previsione Definitiva`, `Incidenza Missione Programma Dati di Rendiconto`, `Incidenza Missione Programma Di Cui Fondo Pluriennale Vincolato Dati di Rendiconto`, `Incidenza Missione Programma Di Cui Incidenza Economia Di Spesa Dati di Rendiconto`, `_unnamed_27`
- `2024_Rendiconto PDI Analitici di Spese 4-d_CAMPANIA.csv` (25 fields): `Esercizio Finanziario`, `Codice Tipologia Soggetto`, `Descrizione Tipologia Soggetto`, `Codice BDAP`, `Denominazione Soggetto`, `CF Soggetto`, `Data Cessazione Soggetto`, `Codice Zona Geografica`, `Descrizione Zona Geografica`, `Codice Regione`, `Descrizione Regione`, `Codice Provincia`, `Descrizione Provincia`, `Codice Comune`, `Descrizione Comune`, `Codice Missione Arconet`, `Descrizione Missione Arconet`, `Codice Programma Arconet`, `Descrizione Programma Arconet`, `Capacità di Pagamento Previsione Iniziale`, `Capacità di Pagamento Previsione Definitive`, `Capacità di Pagamento a Consuntivo`, `Capacità di Pagamento delle Spese in Conto Competenza Impegni`, `Capacità di Pagamento delle Spese Esigibili negli Esercizi Precedenti`, `_unnamed_25`
- `2024_Rendiconto PDI Sintetici Allegato 2-a_CAMPANIA.csv` (24 fields): `Esercizio Finanziario`, `Codice Tipologia Soggetto`, `Descrizione Tipologia Soggetto`, `Codice BDAP`, `Denominazione Soggetto`, `CF Soggetto`, `Data Cessazione Soggetto`, `Codice Zona Geografica`, `Descrizione Zona Geografica`, `Codice Regione`, `Descrizione Regione`, `Codice Provincia`, `Descrizione Provincia`, `Codice Comune`, `Descrizione Comune`, `Codice Tipologia Indicatore Sintetico 2)a`, `Descrizione Tipologia Indicatore Sintetico 2)a`, `Codice Indicatore Sintetico 2)a`, `Descrizione Indicatore Sintetico 2)a`, `Definizione Indicatore Sintetico 2)a`, `Indicatore Tutte Le Missioni`, `Indicatore Solo Per Missione 13 - Tutela Della Salute`, `Indicatore Tutte Le Spese al Netto Missione 13`, `_unnamed_24`
- `2024_Rendiconto PDI Sintetici Allegato 4-a_CAMPANIA.csv` (22 fields): `Esercizio Finanziario`, `Codice Tipologia Soggetto`, `Descrizione Tipologia Soggetto`, `Codice BDAP`, `Denominazione Soggetto`, `CF Soggetto`, `Data Cessazione Soggetto`, `Codice Zona Geografica`, `Descrizione Zona Geografica`, `Codice Regione`, `Descrizione Regione`, `Codice Provincia`, `Descrizione Provincia`, `Codice Comune`, `Descrizione Comune`, `Codice Tipologia Indicatore Sintetico 4)a`, `Descrizione Tipologia Indicatore Sintetico 4)a`, `Codice Indicatore Sintetico 4)a`, `Descrizione Indicatore Sintetico 4)a`, `Definizione Indicatore Sintetico 4)a`, `Valore Indicatore`, `_unnamed_22`
- Coverage by period: 2024: 118/118

Source: [bdap-indicators-2024](https://openbdap.rgs.mef.gov.it/Datasets_FET/Rendiconto/2024/2024_Rendiconto%20-%20Piano%20degli%20indicatori_CAMPANIA.zip)

### mic-cultural-places-campania

Records: 55; associated municipalities: 36/118; periods: undated_source_records.

Museum and cultural place records. Individual opening hours and descriptions may be stale; no record modification dates supplied.

Staging file: `data/collection/mic-cultural-places-campania.rows.jsonl.gz`; SHA-256: `8c8dd9dc037f36a55109699b3f9746b06304b54cda41106650dd049cfb28d1a4`.

- `cultural_sites` (2 fields): `place`, `related_geography`
- Coverage by period: undated_source_records: 36/118

Source: [mic-cultural-places-campania](https://dati.beniculturali.it/dataset/dataset-luoghiCampania.json)

### mim-building-locations-202425

Records: 695; associated municipalities: 114/118; periods: 202425.

Building-school associations: count distinct CODICEEDIFICIO for buildings, not CSV rows.

Staging file: `data/collection/mim-building-locations-202425.rows.jsonl.gz`; SHA-256: `1edc591a14bc9d3934437381793d15fbb9fe52418fae14a6295f02f94f7e96ec`.

- `EDIANAGRAFESTA202120242520250806.csv` (10 fields): `ANNOSCOLASTICO`, `CODICESCUOLA`, `CODICEEDIFICIO`, `CODICECOMUNE`, `DESCRIZIONECOMUNE`, `SIGLAPROVINCIA`, `TIPOLOGIAINDIRIZZO`, `DENOMINAZIONEINDIRIZZO`, `NUMEROCIVICO`, `CAP`
- Coverage by period: 202425: 114/118

Source: [mim-building-locations-202425](https://dati.istruzione.it/opendata/EDIANAGRAFESTA202120242520250806.csv)

### mim-building-environment-202425

Records: 695; associated municipalities: 114/118; periods: 202425.

Reported building surroundings; underscores and blank fields preserved; not independently measured pollution.

Staging file: `data/collection/mim-building-environment-202425.rows.jsonl.gz`; SHA-256: `50c1b5d5ab83a24b431123f7e951291de764611a1b4d93dec12ac8c7b921069f`.

- `EDIAMBIENTESTA202120242520250806.csv` (21 fields): `ANNOSCOLASTICO`, `CODICESCUOLA`, `CODICEEDIFICIO`, `CONTESTOSENZADISTURBI`, `VICINANZADISCARICA`, `VICINANZAINDUSTRIEINQUINANTI`, `VICINANZAACQUEINQUINANTI`, `VICINANZAFONTIINQUINAMENTOATMOSFERICO`, `VICINANZAFONTIINQUINAMENTOACUSTICO`, `VICINANZASORGENTIRADIAZIONIELETTROMAGNETICHE`, `VICINANZACIMITERI`, `VICINANZAALTRIDISTURBI`, `CRITICITASPECIFICHEAREASCOLASTICA`, `ASSENZAPIAZZOLAADEGUATA`, `AREANONRECINTATA`, `PRESENZAGRANDETRAFFICO`, `PRESENZATRANSITOFERROVIARIO`, `PREESISTENZEINDUSTRIALIABBANDONATE`, `ZONAURBANADEGRADATA`, `VICINANZAINDUSTRIEARISCHIO`, `ALTRECRITICITASPECIFICHE`
- Coverage by period: 202425: 114/118

Source: [mim-building-environment-202425](https://dati.istruzione.it/opendata/EDIAMBIENTESTA202120242520250806.csv)

### pnrr-localizations-20260613

Records: 3,677; associated municipalities: 118/118; periods: 2026-06-13.

Municipal locations use separate province and municipality components. Retain allocation percentage and multi-location projects.

Staging file: `data/collection/pnrr-localizations-20260613.rows.jsonl.gz`; SHA-256: `d6f0a8b5b7b9f1745e8e455f3d1af7964b1f53105abb5ebbbd7100688c0688de`.

- `PNRR_Localizzazione.csv` (14 fields): `Codice Univoco Submisura`, `Descrizione Submisura`, `CUP`, `Codice Locale Progetto`, `Regione`, `Descrizione Regione`, `Provincia`, `Descrizione Provincia`, `Comune`, `Descrizione Comune`, `Indirizzo`, `CAP`, `Percentuale di Localizzazione`, `Data di Estrazione`
- Coverage by period: 2026-06-13: 118/118

Source: [pnrr-localizations-20260613](https://www.italiadomani.gov.it/content/dam/sogei-ng/opendata/PNRR_Localizzazione.csv)

### pnrr-projects-20260613

Records: 2,938; associated municipalities: 118/118; periods: 2026-06-13.

Join on CUP plus Codice Locale Progetto, not CUP alone. Project/contract amounts cannot be counted once for every municipal location. PNRR subset, not all public contracts.

Staging file: `data/collection/pnrr-projects-20260613.rows.jsonl.gz`; SHA-256: `a09ea78dd74147ba218a906018e4bd1d27e5c53410f9a81c7e00484e9fb23750`.

- `PNRR_Progetti.csv` (63 fields): `Programma`, `Missione`, `Descrizione Missione`, `Componente`, `Descrizione Componente`, `ID Misura`, `Codice Univoco Misura`, `Descrizione Misura`, `ID Submisura`, `Codice CID`, `Codice Univoco Submisura`, `Descrizione Submisura`, `Amministrazione Titolare`, `Codice Identificativo Procedura di Attivazione`, `Titolo Procedura`, `Tipologia Procedura di Attivazione`, `CUP`, `Codice Locale Progetto`, `Stato CUP`, `Stato Avanzamento Progetto`, `CUP Codice Natura`, `CUP Descrizione Natura`, `CUP Codice Tipologia`, `CUP Descrizione Tipologia`, `CUP Codice Settore`, `CUP Descrizione Settore`, `CUP Codice Sottosettore`, `CUP Descrizione Sottosettore`, `CUP Codice Categoria`, `CUP Descrizione Categoria`, `Titolo Progetto`, `Sintesi Progetto`, `Descrizione Tipo Aiuto`, `Finanziamento - Stato`, `Finanziamento Stato - Bilancio`, `Finanziamento Stato - FOI`, `Finanziamento Prosecuzione Opere Pubbliche - FPOP`, `Finanziamento UE (Diverso da PNRR)`, `Finanziamento Regione`, `Finanziamento Provincia`, `Finanziamento Comune`, `Finanziamento Altro Pubblico`, `Finanziamento Privato`, `Finanziamento da Reperire`, `Finanziamento PNRR`, `Finanziamento PNC`, `Altri Fondi`, `Finanziamento Totale`, `Finanziamento Totale Pubblico`, `Finanziamento Totale Pubblico Netto`, `Soggetto Attuatore`, `Codice Fiscale Soggetto Attuatore`, `Flag Progetti in Essere`, `Data Inizio Progetto Prevista`, `Data Inizio Progetto Effettiva`, `Data Fine Progetto Prevista`, `Data Fine Progetto Effettiva`, `Data di Estrazione`, `Data Ultima Validazione`, `Esito Ultima Validazione`, `Codice Fase Iter di Progetto`, `Descrizione Fase Iter di Progetto`, `Stato Fase Iter di Progetto`
- Coverage by period: 2026-06-13: 118/118

Source: [pnrr-projects-20260613](https://www.italiadomani.gov.it/content/dam/sogei-ng/opendata/PNRR_Progetti.csv)

### pnrr-procurements-20260613

Records: 1,973; associated municipalities: 117/118; periods: 2026-06-13.

Join on CUP plus Codice Locale Progetto, not CUP alone. Project/contract amounts cannot be counted once for every municipal location. PNRR subset, not all public contracts.

Staging file: `data/collection/pnrr-procurements-20260613.rows.jsonl.gz`; SHA-256: `378d6a78e5004598f5445a5ef96e1bb58843ad0e891c251c76cdfd475e8a620f`.

- `PNRR_Gare.csv` (19 fields): `Codice Univoco Submisura`, `Descrizione Submisura`, `Descrizione Procedura di Aggiudicazione`, `CUP`, `Codice Locale Progetto`, `CIG`, `CIG Accordo Quadro`, `Codice Procedura Utente`, `Modalità di Realizzazione`, `Codice Interno PDA`, `Oggetto Principale del Contratto`, `Oggetto Gara`, `Data Pubblicazione del CIG`, `Codice Motivo Assenza CIG`, `Descrizione Motivo Assenza CIG`, `Importo Complessivo Gara`, `Importo Aggiudicazione`, `Data Aggiudicazione Definitiva`, `Data di Estrazione`
- Coverage by period: 2026-06-13: 117/118

Source: [pnrr-procurements-20260613](https://www.italiadomani.gov.it/content/dam/sogei-ng/opendata/PNRR_Gare.csv)

### anac-cig-2025

Records: 8,428; associated municipalities: 118/118; periods: 2025-01-02, 2025-01-03, 2025-01-07, 2025-01-08, 2025-01-09, 2025-01-10, 2025-01-13, 2025-01-14, 2025-01-15, 2025-01-16, 2025-01-17, 2025-01-20, 2025-01-21, 2025-01-22, 2025-01-23, 2025-01-24, 2025-01-27, 2025-01-28, 2025-01-29, 2025-01-30, 2025-01-31, 2025-02-03, 2025-02-04, 2025-02-05, 2025-02-06, 2025-02-07, 2025-02-10, 2025-02-11, 2025-02-12, 2025-02-13, 2025-02-14, 2025-02-17, 2025-02-18, 2025-02-19, 2025-02-20, 2025-02-21, 2025-02-22, 2025-02-24, 2025-02-25, 2025-02-26, 2025-02-27, 2025-02-28, 2025-03-01, 2025-03-03, 2025-03-04, 2025-03-05, 2025-03-06, 2025-03-07, 2025-03-10, 2025-03-11, 2025-03-12, 2025-03-13, 2025-03-14, 2025-03-17, 2025-03-18, 2025-03-19, 2025-03-20, 2025-03-21, 2025-03-24, 2025-03-25, 2025-03-26, 2025-03-27, 2025-03-28, 2025-03-31, 2025-04-01, 2025-04-02, 2025-04-03, 2025-04-04, 2025-04-07, 2025-04-08, 2025-04-09, 2025-04-10, 2025-04-11, 2025-04-12, 2025-04-13, 2025-04-14, 2025-04-15, 2025-04-16, 2025-04-17, 2025-04-18, 2025-04-19, 2025-04-20, 2025-04-22, 2025-04-23, 2025-04-24, 2025-04-25, 2025-04-27, 2025-04-28, 2025-04-29, 2025-04-30, 2025-05-01, 2025-05-02, 2025-05-03, 2025-05-05, 2025-05-06, 2025-05-07, 2025-05-08, 2025-05-09, 2025-05-10, 2025-05-12, 2025-05-13, 2025-05-14, 2025-05-15, 2025-05-16, 2025-05-19, 2025-05-20, 2025-05-21, 2025-05-22, 2025-05-23, 2025-05-26, 2025-05-27, 2025-05-28, 2025-05-29, 2025-05-30, 2025-06-03, 2025-06-04, 2025-06-05, 2025-06-06, 2025-06-09, 2025-06-10, 2025-06-11, 2025-06-12, 2025-06-13, 2025-06-16, 2025-06-17, 2025-06-18, 2025-06-19, 2025-06-20, 2025-06-21, 2025-06-23, 2025-06-24, 2025-06-25, 2025-06-26, 2025-06-27, 2025-06-30, 2025-07-01, 2025-07-02, 2025-07-03, 2025-07-04, 2025-07-06, 2025-07-07, 2025-07-08, 2025-07-09, 2025-07-10, 2025-07-11, 2025-07-14, 2025-07-15, 2025-07-16, 2025-07-17, 2025-07-18, 2025-07-21, 2025-07-22, 2025-07-23, 2025-07-24, 2025-07-25, 2025-07-28, 2025-07-29, 2025-07-30, 2025-07-31, 2025-08-01, 2025-08-04, 2025-08-05, 2025-08-06, 2025-08-07, 2025-08-08, 2025-08-11, 2025-08-12, 2025-08-13, 2025-08-14, 2025-08-18, 2025-08-19, 2025-08-20, 2025-08-21, 2025-08-22, 2025-08-25, 2025-08-26, 2025-08-27, 2025-08-28, 2025-08-29, 2025-09-01, 2025-09-02, 2025-09-03, 2025-09-04, 2025-09-05, 2025-09-08, 2025-09-09, 2025-09-10, 2025-09-11, 2025-09-12, 2025-09-15, 2025-09-16, 2025-09-17, 2025-09-18, 2025-09-19, 2025-09-22, 2025-09-23, 2025-09-24, 2025-09-25, 2025-09-26, 2025-09-29, 2025-09-30, 2025-10-01, 2025-10-02, 2025-10-03, 2025-10-06, 2025-10-07, 2025-10-08, 2025-10-09, 2025-10-10, 2025-10-12, 2025-10-13, 2025-10-14, 2025-10-15, 2025-10-16, 2025-10-17, 2025-10-20, 2025-10-21, 2025-10-22, 2025-10-23, 2025-10-24, 2025-10-25, 2025-10-27, 2025-10-28, 2025-10-29, 2025-10-30, 2025-10-31, 2025-11-03, 2025-11-04, 2025-11-05, 2025-11-06, 2025-11-07, 2025-11-10, 2025-11-11, 2025-11-12, 2025-11-13, 2025-11-14, 2025-11-15, 2025-11-17, 2025-11-18, 2025-11-19, 2025-11-20, 2025-11-21, 2025-11-26, 2025-11-27, 2025-11-28, 2025-12-01, 2025-12-02, 2025-12-03, 2025-12-04, 2025-12-05, 2025-12-06, 2025-12-08, 2025-12-09, 2025-12-10, 2025-12-11, 2025-12-12, 2025-12-15, 2025-12-16, 2025-12-17, 2025-12-18, 2025-12-19, 2025-12-22, 2025-12-23, 2025-12-24, 2025-12-29, 2025-12-30, 2025-12-31.

One verified monthly CIG partition. Authority fiscal-code associations and contract-location associations retained separately. Monthly partitions are not a full annual inventory.

Staging file: `data/collection/anac-cig-2025.rows.jsonl.gz`; SHA-256: `b394dec7b11279b98851d99c0886902df539b936665a79904f3dc5428a4b59bb`.

- `cig_csv_2025_05.csv` (63 fields): `cig`, `cig_accordo_quadro`, `numero_gara`, `oggetto_gara`, `importo_complessivo_gara`, `n_lotti_componenti`, `oggetto_lotto`, `importo_lotto`, `oggetto_principale_contratto`, `stato`, `settore`, `luogo_istat`, `provincia`, `data_pubblicazione`, `data_scadenza_offerta`, `cod_tipo_scelta_contraente`, `tipo_scelta_contraente`, `cod_modalita_realizzazione`, `modalita_realizzazione`, `codice_ausa`, `cf_amministrazione_appaltante`, `denominazione_amministrazione_appaltante`, `sezione_regionale`, `id_centro_costo`, `denominazione_centro_costo`, `anno_pubblicazione`, `mese_pubblicazione`, `cod_cpv`, `descrizione_cpv`, `flag_prevalente`, `COD_MOTIVO_CANCELLAZIONE`, `MOTIVO_CANCELLAZIONE`, `DATA_CANCELLAZIONE`, `DATA_ULTIMO_PERFEZIONAMENTO`, `COD_MODALITA_INDIZIONE_SPECIALI`, `MODALITA_INDIZIONE_SPECIALI`, `COD_MODALITA_INDIZIONE_SERVIZI`, `MODALITA_INDIZIONE_SERVIZI`, `DURATA_PREVISTA`, `COD_STRUMENTO_SVOLGIMENTO`, `STRUMENTO_SVOLGIMENTO`, `FLAG_URGENZA`, `COD_MOTIVO_URGENZA`, `MOTIVO_URGENZA`, `FLAG_DELEGA`, `FUNZIONI_DELEGATE`, `CF_SA_DELEGANTE`, `DENOMINAZIONE_SA_DELEGANTE`, `CF_SA_DELEGATA`, `DENOMINAZIONE_SA_DELEGATA`, `IMPORTO_SICUREZZA`, `TIPO_APPALTO_RISERVATO`, `CUI_PROGRAMMA`, `FLAG_PREV_RIPETIZIONI`, `COD_IPOTESI_COLLEGAMENTO`, `IPOTESI_COLLEGAMENTO`, `CIG_COLLEGAMENTO`, `COD_ESITO`, `ESITO`, `DATA_COMUNICAZIONE_ESITO`, `FLAG_PNRR_PNC`, `_authority_municipality_code`, `_contract_location_municipality_code`
- `cig_csv_2025_01.csv` (63 fields): `cig`, `cig_accordo_quadro`, `numero_gara`, `oggetto_gara`, `importo_complessivo_gara`, `n_lotti_componenti`, `oggetto_lotto`, `importo_lotto`, `oggetto_principale_contratto`, `stato`, `settore`, `luogo_istat`, `provincia`, `data_pubblicazione`, `data_scadenza_offerta`, `cod_tipo_scelta_contraente`, `tipo_scelta_contraente`, `cod_modalita_realizzazione`, `modalita_realizzazione`, `codice_ausa`, `cf_amministrazione_appaltante`, `denominazione_amministrazione_appaltante`, `sezione_regionale`, `id_centro_costo`, `denominazione_centro_costo`, `anno_pubblicazione`, `mese_pubblicazione`, `cod_cpv`, `descrizione_cpv`, `flag_prevalente`, `COD_MOTIVO_CANCELLAZIONE`, `MOTIVO_CANCELLAZIONE`, `DATA_CANCELLAZIONE`, `DATA_ULTIMO_PERFEZIONAMENTO`, `COD_MODALITA_INDIZIONE_SPECIALI`, `MODALITA_INDIZIONE_SPECIALI`, `COD_MODALITA_INDIZIONE_SERVIZI`, `MODALITA_INDIZIONE_SERVIZI`, `DURATA_PREVISTA`, `COD_STRUMENTO_SVOLGIMENTO`, `STRUMENTO_SVOLGIMENTO`, `FLAG_URGENZA`, `COD_MOTIVO_URGENZA`, `MOTIVO_URGENZA`, `FLAG_DELEGA`, `FUNZIONI_DELEGATE`, `CF_SA_DELEGANTE`, `DENOMINAZIONE_SA_DELEGANTE`, `CF_SA_DELEGATA`, `DENOMINAZIONE_SA_DELEGATA`, `IMPORTO_SICUREZZA`, `TIPO_APPALTO_RISERVATO`, `CUI_PROGRAMMA`, `FLAG_PREV_RIPETIZIONI`, `COD_IPOTESI_COLLEGAMENTO`, `IPOTESI_COLLEGAMENTO`, `CIG_COLLEGAMENTO`, `COD_ESITO`, `ESITO`, `DATA_COMUNICAZIONE_ESITO`, `FLAG_PNRR_PNC`, `_authority_municipality_code`, `_contract_location_municipality_code`
- `cig_csv_2025_02.csv` (63 fields): `cig`, `cig_accordo_quadro`, `numero_gara`, `oggetto_gara`, `importo_complessivo_gara`, `n_lotti_componenti`, `oggetto_lotto`, `importo_lotto`, `oggetto_principale_contratto`, `stato`, `settore`, `luogo_istat`, `provincia`, `data_pubblicazione`, `data_scadenza_offerta`, `cod_tipo_scelta_contraente`, `tipo_scelta_contraente`, `cod_modalita_realizzazione`, `modalita_realizzazione`, `codice_ausa`, `cf_amministrazione_appaltante`, `denominazione_amministrazione_appaltante`, `sezione_regionale`, `id_centro_costo`, `denominazione_centro_costo`, `anno_pubblicazione`, `mese_pubblicazione`, `cod_cpv`, `descrizione_cpv`, `flag_prevalente`, `COD_MOTIVO_CANCELLAZIONE`, `MOTIVO_CANCELLAZIONE`, `DATA_CANCELLAZIONE`, `DATA_ULTIMO_PERFEZIONAMENTO`, `COD_MODALITA_INDIZIONE_SPECIALI`, `MODALITA_INDIZIONE_SPECIALI`, `COD_MODALITA_INDIZIONE_SERVIZI`, `MODALITA_INDIZIONE_SERVIZI`, `DURATA_PREVISTA`, `COD_STRUMENTO_SVOLGIMENTO`, `STRUMENTO_SVOLGIMENTO`, `FLAG_URGENZA`, `COD_MOTIVO_URGENZA`, `MOTIVO_URGENZA`, `FLAG_DELEGA`, `FUNZIONI_DELEGATE`, `CF_SA_DELEGANTE`, `DENOMINAZIONE_SA_DELEGANTE`, `CF_SA_DELEGATA`, `DENOMINAZIONE_SA_DELEGATA`, `IMPORTO_SICUREZZA`, `TIPO_APPALTO_RISERVATO`, `CUI_PROGRAMMA`, `FLAG_PREV_RIPETIZIONI`, `COD_IPOTESI_COLLEGAMENTO`, `IPOTESI_COLLEGAMENTO`, `CIG_COLLEGAMENTO`, `COD_ESITO`, `ESITO`, `DATA_COMUNICAZIONE_ESITO`, `FLAG_PNRR_PNC`, `_authority_municipality_code`, `_contract_location_municipality_code`
- `cig_csv_2025_03.csv` (63 fields): `cig`, `cig_accordo_quadro`, `numero_gara`, `oggetto_gara`, `importo_complessivo_gara`, `n_lotti_componenti`, `oggetto_lotto`, `importo_lotto`, `oggetto_principale_contratto`, `stato`, `settore`, `luogo_istat`, `provincia`, `data_pubblicazione`, `data_scadenza_offerta`, `cod_tipo_scelta_contraente`, `tipo_scelta_contraente`, `cod_modalita_realizzazione`, `modalita_realizzazione`, `codice_ausa`, `cf_amministrazione_appaltante`, `denominazione_amministrazione_appaltante`, `sezione_regionale`, `id_centro_costo`, `denominazione_centro_costo`, `anno_pubblicazione`, `mese_pubblicazione`, `cod_cpv`, `descrizione_cpv`, `flag_prevalente`, `COD_MOTIVO_CANCELLAZIONE`, `MOTIVO_CANCELLAZIONE`, `DATA_CANCELLAZIONE`, `DATA_ULTIMO_PERFEZIONAMENTO`, `COD_MODALITA_INDIZIONE_SPECIALI`, `MODALITA_INDIZIONE_SPECIALI`, `COD_MODALITA_INDIZIONE_SERVIZI`, `MODALITA_INDIZIONE_SERVIZI`, `DURATA_PREVISTA`, `COD_STRUMENTO_SVOLGIMENTO`, `STRUMENTO_SVOLGIMENTO`, `FLAG_URGENZA`, `COD_MOTIVO_URGENZA`, `MOTIVO_URGENZA`, `FLAG_DELEGA`, `FUNZIONI_DELEGATE`, `CF_SA_DELEGANTE`, `DENOMINAZIONE_SA_DELEGANTE`, `CF_SA_DELEGATA`, `DENOMINAZIONE_SA_DELEGATA`, `IMPORTO_SICUREZZA`, `TIPO_APPALTO_RISERVATO`, `CUI_PROGRAMMA`, `FLAG_PREV_RIPETIZIONI`, `COD_IPOTESI_COLLEGAMENTO`, `IPOTESI_COLLEGAMENTO`, `CIG_COLLEGAMENTO`, `COD_ESITO`, `ESITO`, `DATA_COMUNICAZIONE_ESITO`, `FLAG_PNRR_PNC`, `_authority_municipality_code`, `_contract_location_municipality_code`
- `cig_csv_2025_04.csv` (63 fields): `cig`, `cig_accordo_quadro`, `numero_gara`, `oggetto_gara`, `importo_complessivo_gara`, `n_lotti_componenti`, `oggetto_lotto`, `importo_lotto`, `oggetto_principale_contratto`, `stato`, `settore`, `luogo_istat`, `provincia`, `data_pubblicazione`, `data_scadenza_offerta`, `cod_tipo_scelta_contraente`, `tipo_scelta_contraente`, `cod_modalita_realizzazione`, `modalita_realizzazione`, `codice_ausa`, `cf_amministrazione_appaltante`, `denominazione_amministrazione_appaltante`, `sezione_regionale`, `id_centro_costo`, `denominazione_centro_costo`, `anno_pubblicazione`, `mese_pubblicazione`, `cod_cpv`, `descrizione_cpv`, `flag_prevalente`, `COD_MOTIVO_CANCELLAZIONE`, `MOTIVO_CANCELLAZIONE`, `DATA_CANCELLAZIONE`, `DATA_ULTIMO_PERFEZIONAMENTO`, `COD_MODALITA_INDIZIONE_SPECIALI`, `MODALITA_INDIZIONE_SPECIALI`, `COD_MODALITA_INDIZIONE_SERVIZI`, `MODALITA_INDIZIONE_SERVIZI`, `DURATA_PREVISTA`, `COD_STRUMENTO_SVOLGIMENTO`, `STRUMENTO_SVOLGIMENTO`, `FLAG_URGENZA`, `COD_MOTIVO_URGENZA`, `MOTIVO_URGENZA`, `FLAG_DELEGA`, `FUNZIONI_DELEGATE`, `CF_SA_DELEGANTE`, `DENOMINAZIONE_SA_DELEGANTE`, `CF_SA_DELEGATA`, `DENOMINAZIONE_SA_DELEGATA`, `IMPORTO_SICUREZZA`, `TIPO_APPALTO_RISERVATO`, `CUI_PROGRAMMA`, `FLAG_PREV_RIPETIZIONI`, `COD_IPOTESI_COLLEGAMENTO`, `IPOTESI_COLLEGAMENTO`, `CIG_COLLEGAMENTO`, `COD_ESITO`, `ESITO`, `DATA_COMUNICAZIONE_ESITO`, `FLAG_PNRR_PNC`, `_authority_municipality_code`, `_contract_location_municipality_code`
- `cig_csv_2025_06.csv` (63 fields): `cig`, `cig_accordo_quadro`, `numero_gara`, `oggetto_gara`, `importo_complessivo_gara`, `n_lotti_componenti`, `oggetto_lotto`, `importo_lotto`, `oggetto_principale_contratto`, `stato`, `settore`, `luogo_istat`, `provincia`, `data_pubblicazione`, `data_scadenza_offerta`, `cod_tipo_scelta_contraente`, `tipo_scelta_contraente`, `cod_modalita_realizzazione`, `modalita_realizzazione`, `codice_ausa`, `cf_amministrazione_appaltante`, `denominazione_amministrazione_appaltante`, `sezione_regionale`, `id_centro_costo`, `denominazione_centro_costo`, `anno_pubblicazione`, `mese_pubblicazione`, `cod_cpv`, `descrizione_cpv`, `flag_prevalente`, `COD_MOTIVO_CANCELLAZIONE`, `MOTIVO_CANCELLAZIONE`, `DATA_CANCELLAZIONE`, `DATA_ULTIMO_PERFEZIONAMENTO`, `COD_MODALITA_INDIZIONE_SPECIALI`, `MODALITA_INDIZIONE_SPECIALI`, `COD_MODALITA_INDIZIONE_SERVIZI`, `MODALITA_INDIZIONE_SERVIZI`, `DURATA_PREVISTA`, `COD_STRUMENTO_SVOLGIMENTO`, `STRUMENTO_SVOLGIMENTO`, `FLAG_URGENZA`, `COD_MOTIVO_URGENZA`, `MOTIVO_URGENZA`, `FLAG_DELEGA`, `FUNZIONI_DELEGATE`, `CF_SA_DELEGANTE`, `DENOMINAZIONE_SA_DELEGANTE`, `CF_SA_DELEGATA`, `DENOMINAZIONE_SA_DELEGATA`, `IMPORTO_SICUREZZA`, `TIPO_APPALTO_RISERVATO`, `CUI_PROGRAMMA`, `FLAG_PREV_RIPETIZIONI`, `COD_IPOTESI_COLLEGAMENTO`, `IPOTESI_COLLEGAMENTO`, `CIG_COLLEGAMENTO`, `COD_ESITO`, `ESITO`, `DATA_COMUNICAZIONE_ESITO`, `FLAG_PNRR_PNC`, `_authority_municipality_code`, `_contract_location_municipality_code`
- `cig_csv_2025_07.csv` (63 fields): `cig`, `cig_accordo_quadro`, `numero_gara`, `oggetto_gara`, `importo_complessivo_gara`, `n_lotti_componenti`, `oggetto_lotto`, `importo_lotto`, `oggetto_principale_contratto`, `stato`, `settore`, `luogo_istat`, `provincia`, `data_pubblicazione`, `data_scadenza_offerta`, `cod_tipo_scelta_contraente`, `tipo_scelta_contraente`, `cod_modalita_realizzazione`, `modalita_realizzazione`, `codice_ausa`, `cf_amministrazione_appaltante`, `denominazione_amministrazione_appaltante`, `sezione_regionale`, `id_centro_costo`, `denominazione_centro_costo`, `anno_pubblicazione`, `mese_pubblicazione`, `cod_cpv`, `descrizione_cpv`, `flag_prevalente`, `COD_MOTIVO_CANCELLAZIONE`, `MOTIVO_CANCELLAZIONE`, `DATA_CANCELLAZIONE`, `DATA_ULTIMO_PERFEZIONAMENTO`, `COD_MODALITA_INDIZIONE_SPECIALI`, `MODALITA_INDIZIONE_SPECIALI`, `COD_MODALITA_INDIZIONE_SERVIZI`, `MODALITA_INDIZIONE_SERVIZI`, `DURATA_PREVISTA`, `COD_STRUMENTO_SVOLGIMENTO`, `STRUMENTO_SVOLGIMENTO`, `FLAG_URGENZA`, `COD_MOTIVO_URGENZA`, `MOTIVO_URGENZA`, `FLAG_DELEGA`, `FUNZIONI_DELEGATE`, `CF_SA_DELEGANTE`, `DENOMINAZIONE_SA_DELEGANTE`, `CF_SA_DELEGATA`, `DENOMINAZIONE_SA_DELEGATA`, `IMPORTO_SICUREZZA`, `TIPO_APPALTO_RISERVATO`, `CUI_PROGRAMMA`, `FLAG_PREV_RIPETIZIONI`, `COD_IPOTESI_COLLEGAMENTO`, `IPOTESI_COLLEGAMENTO`, `CIG_COLLEGAMENTO`, `COD_ESITO`, `ESITO`, `DATA_COMUNICAZIONE_ESITO`, `FLAG_PNRR_PNC`, `_authority_municipality_code`, `_contract_location_municipality_code`
- `cig_csv_2025_08.csv` (63 fields): `cig`, `cig_accordo_quadro`, `numero_gara`, `oggetto_gara`, `importo_complessivo_gara`, `n_lotti_componenti`, `oggetto_lotto`, `importo_lotto`, `oggetto_principale_contratto`, `stato`, `settore`, `luogo_istat`, `provincia`, `data_pubblicazione`, `data_scadenza_offerta`, `cod_tipo_scelta_contraente`, `tipo_scelta_contraente`, `cod_modalita_realizzazione`, `modalita_realizzazione`, `codice_ausa`, `cf_amministrazione_appaltante`, `denominazione_amministrazione_appaltante`, `sezione_regionale`, `id_centro_costo`, `denominazione_centro_costo`, `anno_pubblicazione`, `mese_pubblicazione`, `cod_cpv`, `descrizione_cpv`, `flag_prevalente`, `COD_MOTIVO_CANCELLAZIONE`, `MOTIVO_CANCELLAZIONE`, `DATA_CANCELLAZIONE`, `DATA_ULTIMO_PERFEZIONAMENTO`, `COD_MODALITA_INDIZIONE_SPECIALI`, `MODALITA_INDIZIONE_SPECIALI`, `COD_MODALITA_INDIZIONE_SERVIZI`, `MODALITA_INDIZIONE_SERVIZI`, `DURATA_PREVISTA`, `COD_STRUMENTO_SVOLGIMENTO`, `STRUMENTO_SVOLGIMENTO`, `FLAG_URGENZA`, `COD_MOTIVO_URGENZA`, `MOTIVO_URGENZA`, `FLAG_DELEGA`, `FUNZIONI_DELEGATE`, `CF_SA_DELEGANTE`, `DENOMINAZIONE_SA_DELEGANTE`, `CF_SA_DELEGATA`, `DENOMINAZIONE_SA_DELEGATA`, `IMPORTO_SICUREZZA`, `TIPO_APPALTO_RISERVATO`, `CUI_PROGRAMMA`, `FLAG_PREV_RIPETIZIONI`, `COD_IPOTESI_COLLEGAMENTO`, `IPOTESI_COLLEGAMENTO`, `CIG_COLLEGAMENTO`, `COD_ESITO`, `ESITO`, `DATA_COMUNICAZIONE_ESITO`, `FLAG_PNRR_PNC`, `_authority_municipality_code`, `_contract_location_municipality_code`
- `cig_csv_2025_09.csv` (63 fields): `cig`, `cig_accordo_quadro`, `numero_gara`, `oggetto_gara`, `importo_complessivo_gara`, `n_lotti_componenti`, `oggetto_lotto`, `importo_lotto`, `oggetto_principale_contratto`, `stato`, `settore`, `luogo_istat`, `provincia`, `data_pubblicazione`, `data_scadenza_offerta`, `cod_tipo_scelta_contraente`, `tipo_scelta_contraente`, `cod_modalita_realizzazione`, `modalita_realizzazione`, `codice_ausa`, `cf_amministrazione_appaltante`, `denominazione_amministrazione_appaltante`, `sezione_regionale`, `id_centro_costo`, `denominazione_centro_costo`, `anno_pubblicazione`, `mese_pubblicazione`, `cod_cpv`, `descrizione_cpv`, `flag_prevalente`, `COD_MOTIVO_CANCELLAZIONE`, `MOTIVO_CANCELLAZIONE`, `DATA_CANCELLAZIONE`, `DATA_ULTIMO_PERFEZIONAMENTO`, `COD_MODALITA_INDIZIONE_SPECIALI`, `MODALITA_INDIZIONE_SPECIALI`, `COD_MODALITA_INDIZIONE_SERVIZI`, `MODALITA_INDIZIONE_SERVIZI`, `DURATA_PREVISTA`, `COD_STRUMENTO_SVOLGIMENTO`, `STRUMENTO_SVOLGIMENTO`, `FLAG_URGENZA`, `COD_MOTIVO_URGENZA`, `MOTIVO_URGENZA`, `FLAG_DELEGA`, `FUNZIONI_DELEGATE`, `CF_SA_DELEGANTE`, `DENOMINAZIONE_SA_DELEGANTE`, `CF_SA_DELEGATA`, `DENOMINAZIONE_SA_DELEGATA`, `IMPORTO_SICUREZZA`, `TIPO_APPALTO_RISERVATO`, `CUI_PROGRAMMA`, `FLAG_PREV_RIPETIZIONI`, `COD_IPOTESI_COLLEGAMENTO`, `IPOTESI_COLLEGAMENTO`, `CIG_COLLEGAMENTO`, `COD_ESITO`, `ESITO`, `DATA_COMUNICAZIONE_ESITO`, `FLAG_PNRR_PNC`, `_authority_municipality_code`, `_contract_location_municipality_code`
- `cig_csv_2025_10.csv` (63 fields): `cig`, `cig_accordo_quadro`, `numero_gara`, `oggetto_gara`, `importo_complessivo_gara`, `n_lotti_componenti`, `oggetto_lotto`, `importo_lotto`, `oggetto_principale_contratto`, `stato`, `settore`, `luogo_istat`, `provincia`, `data_pubblicazione`, `data_scadenza_offerta`, `cod_tipo_scelta_contraente`, `tipo_scelta_contraente`, `cod_modalita_realizzazione`, `modalita_realizzazione`, `codice_ausa`, `cf_amministrazione_appaltante`, `denominazione_amministrazione_appaltante`, `sezione_regionale`, `id_centro_costo`, `denominazione_centro_costo`, `anno_pubblicazione`, `mese_pubblicazione`, `cod_cpv`, `descrizione_cpv`, `flag_prevalente`, `COD_MOTIVO_CANCELLAZIONE`, `MOTIVO_CANCELLAZIONE`, `DATA_CANCELLAZIONE`, `DATA_ULTIMO_PERFEZIONAMENTO`, `COD_MODALITA_INDIZIONE_SPECIALI`, `MODALITA_INDIZIONE_SPECIALI`, `COD_MODALITA_INDIZIONE_SERVIZI`, `MODALITA_INDIZIONE_SERVIZI`, `DURATA_PREVISTA`, `COD_STRUMENTO_SVOLGIMENTO`, `STRUMENTO_SVOLGIMENTO`, `FLAG_URGENZA`, `COD_MOTIVO_URGENZA`, `MOTIVO_URGENZA`, `FLAG_DELEGA`, `FUNZIONI_DELEGATE`, `CF_SA_DELEGANTE`, `DENOMINAZIONE_SA_DELEGANTE`, `CF_SA_DELEGATA`, `DENOMINAZIONE_SA_DELEGATA`, `IMPORTO_SICUREZZA`, `TIPO_APPALTO_RISERVATO`, `CUI_PROGRAMMA`, `FLAG_PREV_RIPETIZIONI`, `COD_IPOTESI_COLLEGAMENTO`, `IPOTESI_COLLEGAMENTO`, `CIG_COLLEGAMENTO`, `COD_ESITO`, `ESITO`, `DATA_COMUNICAZIONE_ESITO`, `FLAG_PNRR_PNC`, `_authority_municipality_code`, `_contract_location_municipality_code`
- `cig_csv_2025_11.csv` (63 fields): `cig`, `cig_accordo_quadro`, `numero_gara`, `oggetto_gara`, `importo_complessivo_gara`, `n_lotti_componenti`, `oggetto_lotto`, `importo_lotto`, `oggetto_principale_contratto`, `stato`, `settore`, `luogo_istat`, `provincia`, `data_pubblicazione`, `data_scadenza_offerta`, `cod_tipo_scelta_contraente`, `tipo_scelta_contraente`, `cod_modalita_realizzazione`, `modalita_realizzazione`, `codice_ausa`, `cf_amministrazione_appaltante`, `denominazione_amministrazione_appaltante`, `sezione_regionale`, `id_centro_costo`, `denominazione_centro_costo`, `anno_pubblicazione`, `mese_pubblicazione`, `cod_cpv`, `descrizione_cpv`, `flag_prevalente`, `COD_MOTIVO_CANCELLAZIONE`, `MOTIVO_CANCELLAZIONE`, `DATA_CANCELLAZIONE`, `DATA_ULTIMO_PERFEZIONAMENTO`, `COD_MODALITA_INDIZIONE_SPECIALI`, `MODALITA_INDIZIONE_SPECIALI`, `COD_MODALITA_INDIZIONE_SERVIZI`, `MODALITA_INDIZIONE_SERVIZI`, `DURATA_PREVISTA`, `COD_STRUMENTO_SVOLGIMENTO`, `STRUMENTO_SVOLGIMENTO`, `FLAG_URGENZA`, `COD_MOTIVO_URGENZA`, `MOTIVO_URGENZA`, `FLAG_DELEGA`, `FUNZIONI_DELEGATE`, `CF_SA_DELEGANTE`, `DENOMINAZIONE_SA_DELEGANTE`, `CF_SA_DELEGATA`, `DENOMINAZIONE_SA_DELEGATA`, `IMPORTO_SICUREZZA`, `TIPO_APPALTO_RISERVATO`, `CUI_PROGRAMMA`, `FLAG_PREV_RIPETIZIONI`, `COD_IPOTESI_COLLEGAMENTO`, `IPOTESI_COLLEGAMENTO`, `CIG_COLLEGAMENTO`, `COD_ESITO`, `ESITO`, `DATA_COMUNICAZIONE_ESITO`, `FLAG_PNRR_PNC`, `_authority_municipality_code`, `_contract_location_municipality_code`
- `cig_csv_2025_12.csv` (63 fields): `cig`, `cig_accordo_quadro`, `numero_gara`, `oggetto_gara`, `importo_complessivo_gara`, `n_lotti_componenti`, `oggetto_lotto`, `importo_lotto`, `oggetto_principale_contratto`, `stato`, `settore`, `luogo_istat`, `provincia`, `data_pubblicazione`, `data_scadenza_offerta`, `cod_tipo_scelta_contraente`, `tipo_scelta_contraente`, `cod_modalita_realizzazione`, `modalita_realizzazione`, `codice_ausa`, `cf_amministrazione_appaltante`, `denominazione_amministrazione_appaltante`, `sezione_regionale`, `id_centro_costo`, `denominazione_centro_costo`, `anno_pubblicazione`, `mese_pubblicazione`, `cod_cpv`, `descrizione_cpv`, `flag_prevalente`, `COD_MOTIVO_CANCELLAZIONE`, `MOTIVO_CANCELLAZIONE`, `DATA_CANCELLAZIONE`, `DATA_ULTIMO_PERFEZIONAMENTO`, `COD_MODALITA_INDIZIONE_SPECIALI`, `MODALITA_INDIZIONE_SPECIALI`, `COD_MODALITA_INDIZIONE_SERVIZI`, `MODALITA_INDIZIONE_SERVIZI`, `DURATA_PREVISTA`, `COD_STRUMENTO_SVOLGIMENTO`, `STRUMENTO_SVOLGIMENTO`, `FLAG_URGENZA`, `COD_MOTIVO_URGENZA`, `MOTIVO_URGENZA`, `FLAG_DELEGA`, `FUNZIONI_DELEGATE`, `CF_SA_DELEGANTE`, `DENOMINAZIONE_SA_DELEGANTE`, `CF_SA_DELEGATA`, `DENOMINAZIONE_SA_DELEGATA`, `IMPORTO_SICUREZZA`, `TIPO_APPALTO_RISERVATO`, `CUI_PROGRAMMA`, `FLAG_PREV_RIPETIZIONI`, `COD_IPOTESI_COLLEGAMENTO`, `IPOTESI_COLLEGAMENTO`, `CIG_COLLEGAMENTO`, `COD_ESITO`, `ESITO`, `DATA_COMUNICAZIONE_ESITO`, `FLAG_PNRR_PNC`, `_authority_municipality_code`, `_contract_location_municipality_code`
- Coverage by period: 2025-01-02: 16/118, 2025-01-03: 7/118, 2025-01-07: 9/118, 2025-01-08: 15/118, 2025-01-09: 7/118, 2025-01-10: 15/118, 2025-01-13: 9/118, 2025-01-14: 10/118, 2025-01-15: 9/118, 2025-01-16: 9/118, 2025-01-17: 12/118, 2025-01-20: 15/118, 2025-01-21: 15/118, 2025-01-22: 14/118, 2025-01-23: 5/118, 2025-01-24: 7/118, 2025-01-27: 13/118, 2025-01-28: 12/118, 2025-01-29: 10/118, 2025-01-30: 15/118, 2025-01-31: 9/118, 2025-02-03: 10/118, 2025-02-04: 14/118, 2025-02-05: 11/118, 2025-02-06: 10/118, 2025-02-07: 14/118, 2025-02-10: 9/118, 2025-02-11: 16/118, 2025-02-12: 12/118, 2025-02-13: 12/118, 2025-02-14: 10/118, 2025-02-17: 17/118, 2025-02-18: 12/118, 2025-02-19: 14/118, 2025-02-20: 11/118, 2025-02-21: 10/118, 2025-02-22: 1/118, 2025-02-24: 14/118, 2025-02-25: 20/118, 2025-02-26: 12/118, 2025-02-27: 8/118, 2025-02-28: 12/118, 2025-03-01: 1/118, 2025-03-03: 11/118, 2025-03-04: 14/118, 2025-03-05: 13/118, 2025-03-06: 13/118, 2025-03-07: 17/118, 2025-03-10: 16/118, 2025-03-11: 13/118, 2025-03-12: 9/118, 2025-03-13: 16/118, 2025-03-14: 14/118, 2025-03-17: 14/118, 2025-03-18: 16/118, 2025-03-19: 4/118, 2025-03-20: 13/118, 2025-03-21: 18/118, 2025-03-24: 17/118, 2025-03-25: 16/118, 2025-03-26: 14/118, 2025-03-27: 5/118, 2025-03-28: 9/118, 2025-03-31: 15/118, 2025-04-01: 23/118, 2025-04-02: 16/118, 2025-04-03: 14/118, 2025-04-04: 19/118, 2025-04-07: 6/118, 2025-04-08: 18/118, 2025-04-09: 14/118, 2025-04-10: 15/118, 2025-04-11: 17/118, 2025-04-12: 1/118, 2025-04-13: 1/118, 2025-04-14: 18/118, 2025-04-15: 14/118, 2025-04-16: 18/118, 2025-04-17: 14/118, 2025-04-18: 27/118, 2025-04-19: 5/118, 2025-04-20: 1/118, 2025-04-22: 21/118, 2025-04-23: 26/118, 2025-04-24: 18/118, 2025-04-25: 1/118, 2025-04-27: 2/118, 2025-04-28: 24/118, 2025-04-29: 24/118, 2025-04-30: 17/118, 2025-05-01: 2/118, 2025-05-02: 20/118, 2025-05-03: 1/118, 2025-05-05: 12/118, 2025-05-06: 23/118, 2025-05-07: 24/118, 2025-05-08: 17/118, 2025-05-09: 12/118, 2025-05-10: 1/118, 2025-05-12: 16/118, 2025-05-13: 18/118, 2025-05-14: 17/118, 2025-05-15: 12/118, 2025-05-16: 15/118, 2025-05-19: 14/118, 2025-05-20: 17/118, 2025-05-21: 18/118, 2025-05-22: 13/118, 2025-05-23: 12/118, 2025-05-26: 11/118, 2025-05-27: 16/118, 2025-05-28: 11/118, 2025-05-29: 12/118, 2025-05-30: 13/118, 2025-06-03: 13/118, 2025-06-04: 16/118, 2025-06-05: 11/118, 2025-06-06: 16/118, 2025-06-09: 13/118, 2025-06-10: 18/118, 2025-06-11: 14/118, 2025-06-12: 13/118, 2025-06-13: 12/118, 2025-06-16: 14/118, 2025-06-17: 11/118, 2025-06-18: 13/118, 2025-06-19: 12/118, 2025-06-20: 10/118, 2025-06-21: 2/118, 2025-06-23: 10/118, 2025-06-24: 15/118, 2025-06-25: 14/118, 2025-06-26: 14/118, 2025-06-27: 14/118, 2025-06-30: 11/118, 2025-07-01: 10/118, 2025-07-02: 16/118, 2025-07-03: 15/118, 2025-07-04: 12/118, 2025-07-06: 1/118, 2025-07-07: 8/118, 2025-07-08: 8/118, 2025-07-09: 9/118, 2025-07-10: 10/118, 2025-07-11: 12/118, 2025-07-14: 12/118, 2025-07-15: 9/118, 2025-07-16: 16/118, 2025-07-17: 11/118, 2025-07-18: 12/118, 2025-07-21: 8/118, 2025-07-22: 12/118, 2025-07-23: 9/118, 2025-07-24: 9/118, 2025-07-25: 14/118, 2025-07-28: 15/118, 2025-07-29: 12/118, 2025-07-30: 14/118, 2025-07-31: 11/118, 2025-08-01: 11/118, 2025-08-04: 10/118, 2025-08-05: 17/118, 2025-08-06: 13/118, 2025-08-07: 9/118, 2025-08-08: 17/118, 2025-08-11: 15/118, 2025-08-12: 11/118, 2025-08-13: 9/118, 2025-08-14: 5/118, 2025-08-18: 1/118, 2025-08-19: 5/118, 2025-08-20: 4/118, 2025-08-21: 5/118, 2025-08-22: 15/118, 2025-08-25: 7/118, 2025-08-26: 1/118, 2025-08-27: 10/118, 2025-08-28: 12/118, 2025-08-29: 15/118, 2025-09-01: 9/118, 2025-09-02: 11/118, 2025-09-03: 9/118, 2025-09-04: 12/118, 2025-09-05: 13/118, 2025-09-08: 18/118, 2025-09-09: 17/118, 2025-09-10: 33/118, 2025-09-11: 15/118, 2025-09-12: 8/118, 2025-09-15: 8/118, 2025-09-16: 15/118, 2025-09-17: 16/118, 2025-09-18: 12/118, 2025-09-19: 18/118, 2025-09-22: 9/118, 2025-09-23: 20/118, 2025-09-24: 13/118, 2025-09-25: 13/118, 2025-09-26: 12/118, 2025-09-29: 7/118, 2025-09-30: 15/118, 2025-10-01: 7/118, 2025-10-02: 17/118, 2025-10-03: 15/118, 2025-10-06: 16/118, 2025-10-07: 15/118, 2025-10-08: 14/118, 2025-10-09: 8/118, 2025-10-10: 15/118, 2025-10-12: 1/118, 2025-10-13: 10/118, 2025-10-14: 12/118, 2025-10-15: 13/118, 2025-10-16: 17/118, 2025-10-17: 14/118, 2025-10-20: 17/118, 2025-10-21: 12/118, 2025-10-22: 13/118, 2025-10-23: 11/118, 2025-10-24: 16/118, 2025-10-25: 1/118, 2025-10-27: 17/118, 2025-10-28: 11/118, 2025-10-29: 12/118, 2025-10-30: 7/118, 2025-10-31: 11/118, 2025-11-03: 12/118, 2025-11-04: 14/118, 2025-11-05: 11/118, 2025-11-06: 9/118, 2025-11-07: 15/118, 2025-11-10: 12/118, 2025-11-11: 12/118, 2025-11-12: 19/118, 2025-11-13: 11/118, 2025-11-14: 13/118, 2025-11-15: 1/118, 2025-11-17: 13/118, 2025-11-18: 9/118, 2025-11-19: 15/118, 2025-11-20: 16/118, 2025-11-21: 8/118, 2025-11-26: 4/118, 2025-11-27: 2/118, 2025-11-28: 20/118, 2025-12-01: 17/118, 2025-12-02: 15/118, 2025-12-03: 12/118, 2025-12-04: 12/118, 2025-12-05: 17/118, 2025-12-06: 1/118, 2025-12-08: 1/118, 2025-12-09: 15/118, 2025-12-10: 18/118, 2025-12-11: 19/118, 2025-12-12: 18/118, 2025-12-15: 14/118, 2025-12-16: 17/118, 2025-12-17: 14/118, 2025-12-18: 21/118, 2025-12-19: 20/118, 2025-12-22: 19/118, 2025-12-23: 22/118, 2025-12-24: 28/118, 2025-12-29: 14/118, 2025-12-30: 24/118, 2025-12-31: 22/118

Source: [anac-cig-2025](https://dati.anticorruzione.it/opendata/download/dataset/cig-2025/filesystem/cig_csv_2025_05.zip)

### openmeteo-history-first-10

Records: 21,920; associated municipalities: 10/118; periods: 2020, 2021, 2022, 2023, 2024, 2025.

Reanalysis at an interior representative point derived from official boundaries. Some municipalities share a grid cell. API 429 on wider simultaneous history acquisition is recorded; no fabricated replacement.

Staging file: `data/collection/openmeteo-history-first-10.rows.jsonl.gz`; SHA-256: `5eef3fd4b81781e99bfc755c9b7ce4ee700dfe3d20294f93bedc85eac41dc189`.

- `daily_reanalysis` (7 fields): `date`, `temperature_2m_mean`, `temperature_2m_min`, `temperature_2m_max`, `precipitation_sum`, `grid`, `model`
- Coverage by period: 2020: 10/118, 2021: 10/118, 2022: 10/118, 2023: 10/118, 2024: 10/118, 2025: 10/118

Source: [openmeteo-history-first-10](https://archive-api.open-meteo.com/v1/archive?latitude=40.881026%2C41.001765%2C40.94478%2C40.977402%2C41.172622%2C40.917553%2C40.968156%2C40.91336%2C40.810307%2C40.966987&longitude=14.813335%2C14.785196%2C15.330326%2C15.478727%2C15.128411%2C14.839671%2C14.602923%2C14.786673%2C15.103386%2C14.639306&start_date=2020-01-01&end_date=2025-12-31&daily=temperature_2m_mean%2Ctemperature_2m_min%2Ctemperature_2m_max%2Cprecipitation_sum&timezone=Europe%2FRome&models=era5_land)

### openmeteo-2025-remaining-108

Records: 39,420; associated municipalities: 108/118; periods: 2025.

Reanalysis at an interior representative point derived from official boundaries. Some municipalities share a grid cell. API 429 on wider simultaneous history acquisition is recorded; no fabricated replacement.

Staging file: `data/collection/openmeteo-2025-remaining-108.rows.jsonl.gz`; SHA-256: `93e138d352c2a0843c99e64e228ed4b69bd84ee59118372d1f646ebd91e1b6e3`.

- `daily_reanalysis` (7 fields): `date`, `temperature_2m_mean`, `temperature_2m_min`, `temperature_2m_max`, `precipitation_sum`, `grid`, `model`
- Coverage by period: 2025: 108/118

Source: [openmeteo-2025-remaining-108](https://archive-api.open-meteo.com/v1/archive?latitude=41.009364%2C41.094057%2C40.89532%2C40.77163%2C40.92337%2C40.94992%2C40.81769%2C40.954054%2C41.019218%2C41.241066%2C40.876829%2C41.045934%2C40.924443%2C40.927798%2C41.01837%2C40.896982%2C41.039811%2C40.9294%2C40.868926%2C40.874197%2C40.876513%2C41.072842%2C41.010754%2C40.858592%2C40.997066%2C41.010406%2C41.258279%2C41.067526%2C40.967814%2C40.976083%2C41.051556%2C40.974491%2C40.874122%2C40.860729%2C40.986295%2C40.941847%2C40.899222%2C41.110223%2C40.927464%2C41.051347%2C41.254669%2C41.20885%2C40.969146%2C40.902201%2C40.961368%2C41.032879%2C40.829604%2C40.915298%2C41.003986%2C41.006718%2C40.919659%2C40.872293%2C40.933009%2C40.874977%2C40.939837%2C40.899482%2C40.934429%2C40.957296%2C41.027946%2C41.047495%2C40.992862%2C40.991695%2C40.979494%2C40.954513%2C40.849106%2C41.035063%2C40.966881%2C41.030406%2C40.912921%2C40.960849%2C41.019939%2C40.878848%2C41.059428%2C40.927797%2C41.088975%2C40.874599%2C40.851986%2C41.010069%2C40.975339%2C40.933435%2C41.013647%2C40.891599%2C41.209895%2C41.088392%2C40.740514%2C40.832467%2C40.958448%2C40.827469%2C40.904319%2C40.941706%2C41.016689%2C40.956853%2C40.894735%2C41.016429%2C40.865568%2C40.940155%2C41.03091%2C41.029204%2C41.05202%2C41.009954%2C41.031609%2C41.082012%2C41.060679%2C40.973237%2C41.11526%2C40.856896%2C41.124422%2C40.826674&longitude=15.365797%2C14.993012%2C15.374473%2C15.186081%2C15.448784%2C14.870912%2C15.224488%2C14.780537%2C15.207038%2C15.01571%2C15.028017%2C15.179743%2C15.054412%2C14.982143%2C14.62042%2C14.838835%2C14.79164%2C14.924158%2C14.779599%2C15.311512%2C14.591512%2C15.137074%2C15.023785%2C14.729427%2C15.164789%2C15.062646%2C15.17051%2C15.065031%2C14.791464%2C15.239373%2C15.451722%2C14.939365%2C14.611691%2C15.179623%2C14.985636%2C14.846467%2C14.583063%2C15.038981%2C14.716085%2C14.990006%2C15.233609%2C15.042696%2C14.886665%2C14.700125%2C14.818051%2C14.857418%2C15.006262%2C15.005708%2C14.905755%2C15.535128%2C15.26224%2C14.679028%2C14.667908%2C15.111545%2C14.747088%2C14.60823%2C14.88796%2C15.032763%2C14.793093%2C14.88068%2C14.735762%2C14.829042%2C14.850366%2C14.674521%2C14.659089%2C14.712576%2C15.157951%2C14.592327%2C14.902913%2C14.966205%2C14.664979%2C14.843084%2C15.207654%2C14.861523%2C15.222196%2C14.878607%2C15.364996%2C14.993701%2C14.744208%2C15.181662%2C14.852869%2C14.871944%2C15.206744%2C15.318761%2C15.190754%2C14.908671%2C14.639775%2C14.847854%2C14.891109%2C14.602326%2C15.150077%2C14.727413%2C14.652852%2C14.964393%2C15.246792%2C15.093105%2C14.919974%2C14.818508%2C15.238685%2C14.83215%2C15.276593%2C15.259002%2C14.924088%2C15.098484%2C15.161905%2C14.936971%2C15.221412%2C14.778807&start_date=2025-01-01&end_date=2025-12-31&daily=temperature_2m_mean%2Ctemperature_2m_min%2Ctemperature_2m_max%2Cprecipitation_sum&timezone=Europe%2FRome&models=era5_land)

### siat-cultural-layer-1

Records: 11; associated municipalities: 11/118; periods: undated_publisher_layer.

Geographic intersection against 2026 boundaries. Source cartography can be historic; API errors and truncation are not data.

Staging file: `data/collection/siat-cultural-layer-1.rows.jsonl.gz`; SHA-256: `c6dd1825a2ec99e3fbc75a63d3ae0ffb0c6552b68608662e0b856537472ab4d0`.

- `features` (5 fields): `source_feature_index`, `type`, `id`, `geometry`, `properties`
- Coverage by period: undated_publisher_layer: 11/118

Source: [siat-cultural-layer-1](https://siat2.provincia.avellino.it/server/rest/services/QC14_Componenti_strutturali_sistema_dei_beni_culturali/MapServer/1/query?f=geojson&where=1%3D1&outFields=%2A&outSR=4326&returnGeometry=true&orderByFields=OBJECTID&resultRecordCount=5000)

### siat-cultural-layer-2

Records: 74; associated municipalities: 70/118; periods: undated_publisher_layer.

Geographic intersection against 2026 boundaries. Source cartography can be historic; API errors and truncation are not data.

Staging file: `data/collection/siat-cultural-layer-2.rows.jsonl.gz`; SHA-256: `92e7fddcd631dd4fc4cd8e5dbb1a862943ba1d7d504a112fee789f0ef7557d89`.

- `features` (5 fields): `source_feature_index`, `type`, `id`, `geometry`, `properties`
- Coverage by period: undated_publisher_layer: 70/118

Source: [siat-cultural-layer-2](https://siat2.provincia.avellino.it/server/rest/services/QC14_Componenti_strutturali_sistema_dei_beni_culturali/MapServer/2/query?f=geojson&where=1%3D1&outFields=%2A&outSR=4326&returnGeometry=true&orderByFields=OBJECTID&resultRecordCount=5000)

### siat-cultural-layer-3

Records: 14; associated municipalities: 11/118; periods: undated_publisher_layer.

Geographic intersection against 2026 boundaries. Source cartography can be historic; API errors and truncation are not data.

Staging file: `data/collection/siat-cultural-layer-3.rows.jsonl.gz`; SHA-256: `db88662e8cc23a7e5420a906364dc3a97d1d7ea30b6448763602fe08ed0dd231`.

- `features` (5 fields): `source_feature_index`, `type`, `id`, `geometry`, `properties`
- Coverage by period: undated_publisher_layer: 11/118

Source: [siat-cultural-layer-3](https://siat2.provincia.avellino.it/server/rest/services/QC14_Componenti_strutturali_sistema_dei_beni_culturali/MapServer/3/query?f=geojson&where=1%3D1&outFields=%2A&outSR=4326&returnGeometry=true&orderByFields=OBJECTID&resultRecordCount=5000)

### siat-cultural-layer-4

Records: 26; associated municipalities: 24/118; periods: undated_publisher_layer.

Geographic intersection against 2026 boundaries. Source cartography can be historic; API errors and truncation are not data.

Staging file: `data/collection/siat-cultural-layer-4.rows.jsonl.gz`; SHA-256: `5fc4663ad6d6181a008479a1f5dc807d9d879f9218e9dd3949cc5323b2f38279`.

- `features` (5 fields): `source_feature_index`, `type`, `id`, `geometry`, `properties`
- Coverage by period: undated_publisher_layer: 24/118

Source: [siat-cultural-layer-4](https://siat2.provincia.avellino.it/server/rest/services/QC14_Componenti_strutturali_sistema_dei_beni_culturali/MapServer/4/query?f=geojson&where=1%3D1&outFields=%2A&outSR=4326&returnGeometry=true&orderByFields=OBJECTID&resultRecordCount=5000)

### siat-cultural-layer-6

Records: 117; associated municipalities: 40/118; periods: undated_publisher_layer.

Geographic intersection against 2026 boundaries. Source cartography can be historic; API errors and truncation are not data.

Staging file: `data/collection/siat-cultural-layer-6.rows.jsonl.gz`; SHA-256: `929d309102453865d0d617f8dbf0610f65793084e58311ed908267cb6a7017a5`.

- `features` (5 fields): `source_feature_index`, `type`, `id`, `geometry`, `properties`
- Coverage by period: undated_publisher_layer: 40/118

Source: [siat-cultural-layer-6](https://siat2.provincia.avellino.it/server/rest/services/QC14_Componenti_strutturali_sistema_dei_beni_culturali/MapServer/6/query?f=geojson&where=1%3D1&outFields=%2A&outSR=4326&returnGeometry=true&orderByFields=OBJECTID&resultRecordCount=5000)

### siat-cultural-layer-7

Records: 13; associated municipalities: 17/118; periods: undated_publisher_layer.

Geographic intersection against 2026 boundaries. Source cartography can be historic; API errors and truncation are not data.

Staging file: `data/collection/siat-cultural-layer-7.rows.jsonl.gz`; SHA-256: `e613acf50e6f06089dbbbc33e4bec7a1b1706f5fb581a037d5ebe2ffeeae20be`.

- `features` (5 fields): `source_feature_index`, `type`, `id`, `geometry`, `properties`
- Coverage by period: undated_publisher_layer: 17/118

Source: [siat-cultural-layer-7](https://siat2.provincia.avellino.it/server/rest/services/QC14_Componenti_strutturali_sistema_dei_beni_culturali/MapServer/7/query?f=geojson&where=1%3D1&outFields=%2A&outSR=4326&returnGeometry=true&orderByFields=OBJECTID&resultRecordCount=5000)

### siat-cultural-layer-8

Records: 172; associated municipalities: 116/118; periods: undated_publisher_layer.

Geographic intersection against 2026 boundaries. Source cartography can be historic; API errors and truncation are not data.

Staging file: `data/collection/siat-cultural-layer-8.rows.jsonl.gz`; SHA-256: `b977aee16aef88586323438d7cd49d5d4a983720cce0466f786b3f0175dda179`.

- `features` (5 fields): `source_feature_index`, `type`, `id`, `geometry`, `properties`
- Coverage by period: undated_publisher_layer: 116/118

Source: [siat-cultural-layer-8](https://siat2.provincia.avellino.it/server/rest/services/QC14_Componenti_strutturali_sistema_dei_beni_culturali/MapServer/8/query?f=geojson&where=1%3D1&outFields=%2A&outSR=4326&returnGeometry=true&orderByFields=OBJECTID&resultRecordCount=5000)

### siat-cultural-layer-9

Records: 40; associated municipalities: 42/118; periods: undated_publisher_layer.

Geographic intersection against 2026 boundaries. Source cartography can be historic; API errors and truncation are not data.

Staging file: `data/collection/siat-cultural-layer-9.rows.jsonl.gz`; SHA-256: `efa5c141c1274353cb2af3ffa29f8870d822a8b9d3a39a0ad9936261bad1af9a`.

- `features` (5 fields): `source_feature_index`, `type`, `id`, `geometry`, `properties`
- Coverage by period: undated_publisher_layer: 42/118

Source: [siat-cultural-layer-9](https://siat2.provincia.avellino.it/server/rest/services/QC14_Componenti_strutturali_sistema_dei_beni_culturali/MapServer/9/query?f=geojson&where=1%3D1&outFields=%2A&outSR=4326&returnGeometry=true&orderByFields=OBJECTID&resultRecordCount=5000)

### siat-cultural-layer-12

Records: 312; associated municipalities: 118/118; periods: undated_publisher_layer.

Geographic intersection against 2026 boundaries. Source cartography can be historic; API errors and truncation are not data.

Staging file: `data/collection/siat-cultural-layer-12.rows.jsonl.gz`; SHA-256: `3724011f3a8886df4f33b050de90ba5624b071e74d9426aa389bd6cd124db253`.

- `features` (5 fields): `source_feature_index`, `type`, `id`, `geometry`, `properties`
- Coverage by period: undated_publisher_layer: 118/118

Source: [siat-cultural-layer-12](https://siat2.provincia.avellino.it/server/rest/services/QC14_Componenti_strutturali_sistema_dei_beni_culturali/MapServer/12/query?f=geojson&where=1%3D1&outFields=%2A&outSR=4326&returnGeometry=true&orderByFields=OBJECTID&resultRecordCount=5000)

### siat-cultural-layer-18

Records: 32; associated municipalities: 94/118; periods: undated_publisher_layer.

Geographic intersection against 2026 boundaries. Source cartography can be historic; API errors and truncation are not data.

Staging file: `data/collection/siat-cultural-layer-18.rows.jsonl.gz`; SHA-256: `19b53025a56bdd2c049ee33e1dcc0f33fa620d30de233e23c082964fc7a2efc9`.

- `features` (5 fields): `source_feature_index`, `type`, `id`, `geometry`, `properties`
- Coverage by period: undated_publisher_layer: 94/118

Source: [siat-cultural-layer-18](https://siat2.provincia.avellino.it/server/rest/services/QC14_Componenti_strutturali_sistema_dei_beni_culturali/MapServer/18/query?f=geojson&where=1%3D1&outFields=%2A&outSR=4326&returnGeometry=true&orderByFields=OBJECTID&resultRecordCount=5000)

### siat-cultural-layer-19

Records: 6; associated municipalities: 7/118; periods: undated_publisher_layer.

Geographic intersection against 2026 boundaries. Source cartography can be historic; API errors and truncation are not data.

Staging file: `data/collection/siat-cultural-layer-19.rows.jsonl.gz`; SHA-256: `9bac4fcf8c82393d8518f1341f326c2fa2d771e15ceac581e28fcebcfcdec0e1`.

- `features` (5 fields): `source_feature_index`, `type`, `id`, `geometry`, `properties`
- Coverage by period: undated_publisher_layer: 7/118

Source: [siat-cultural-layer-19](https://siat2.provincia.avellino.it/server/rest/services/QC14_Componenti_strutturali_sistema_dei_beni_culturali/MapServer/19/query?f=geojson&where=1%3D1&outFields=%2A&outSR=4326&returnGeometry=true&orderByFields=OBJECTID&resultRecordCount=5000)

### siat-cultural-localities

Records: 1,634; associated municipalities: 118/118; periods: undated_publisher_layer.

Geographic intersection against 2026 boundaries. Source cartography can be historic; API errors and truncation are not data.

Staging file: `data/collection/siat-cultural-localities.rows.jsonl.gz`; SHA-256: `9aad252c4aacbb8b7976debc85ddab92eab5eaca53dfd9b8c0c66ede1ca67294`.

- `features` (5 fields): `source_feature_index`, `type`, `id`, `geometry`, `properties`
- Coverage by period: undated_publisher_layer: 118/118

Source: [siat-cultural-localities](https://siat2.provincia.avellino.it/server/rest/services/QC14_Componenti_strutturali_sistema_dei_beni_culturali/MapServer/22/query?f=geojson&where=1%3D1&outFields=%2A&outSR=4326&returnGeometry=true&orderByFields=OBJECTID&resultRecordCount=1000&resultOffset=0)

### ispra-hazard-municipal

Records: 118; associated municipalities: 118/118; periods: mixed_vintages.

Live public IdroGEO municipal detail. Population baselines include 2011/2021. Hazard-map edition not encoded in this API response; retain mixed vintages, do not label current risk forecasts.

Staging file: `data/collection/ispra-hazard-municipal.rows.jsonl.gz`; SHA-256: `79f1a73afc83f8d9ddf12e72ca812aa4313bae0dcf1cfa8813aa0a62e4547452`.

- `records` (134 fields): `uid`, `osmid`, `breadcrumb`, `nome`, `extent`, `ar_kmq`, `ar_id_p3`, `ar_id_p2`, `ar_id_p1`, `aridp3_p`, `aridp2_p`, `aridp1_p`, `pop_res011`, `pop_res021`, `pop_gio`, `pop_gio_p`, `pop_adu`, `pop_adu_p`, `pop_anz`, `pop_anz_p`, `pop_idr_p3`, `pop_idr_p2`, `pop_idr_p1`, `popidp3_p`, `popidp2_p`, `popidp1_p`, `fam_tot`, `fam_tot011`, `fam_idr_p3`, `fam_idr_p2`, `fam_idr_p1`, `famidp3_p`, `famidp2_p`, `famidp1_p`, `ed_tot`, `ed_tot011`, `ed_idr_p3`, `ed_idr_p2`, `ed_idr_p1`, `edidp3_p`, `edidp2_p`, `edidp1_p`, `im_tot`, `im_tot011`, `im_idr_p3`, `im_idr_p2`, `im_idr_p1`, `imidp3_p`, `imidp2_p`, `imidp1_p`, `n_vir`, `n_vir019`, `bbcc_id_p3`, `bbcc_id_p2`, `bbcc_id_p1`, `bbccidp3_p`, `bbccidp2_p`, `bbccidp1_p`, `ar_fr_p4`, `ar_fr_p3`, `ar_fr_p2`, `ar_fr_p1`, `ar_fr_aa`, `ar_fr_p3p4`, `ar_frp4_p`, `ar_frp3_p`, `ar_frp2_p`, `ar_frp1_p`, `ar_fraa_p`, `ar_frp3p4p`, `pop_fr_p4`, `pop_fr_p3`, `pop_fr_p2`, `pop_fr_p1`, `pop_fr_aa`, `popfr_p3p4`, `popfrp4_p`, `popfrp3_p`, `popfrp2_p`, `popfrp1_p`, `popfraa_p`, `popfrp3p4p`, `fam_fr_p4`, `fam_fr_p3`, `fam_fr_p2`, `fam_fr_p1`, `fam_fr_aa`, `famfr_p3p4`, `famfrp4_p`, `famfrp3_p`, `famfrp2_p`, `famfrp1_p`, `famfraa_p`, `famfrp3p4p`, `ed_fr_p4`, `ed_fr_p3`, `ed_fr_p2`, `ed_fr_p1`, `ed_fr_aa`, `ed_fr_p3p4`, `edfrp4_p`, `edfrp3_p`, `edfrp2_p`, `edfrp1_p`, `edfraa_p`, `edfrp3p4p`, `im_fr_p4`, `im_fr_p3`, `im_fr_p2`, `im_fr_p1`, `im_fr_aa`, `imfr_p3p4`, `imfrp4_p`, `imfrp3_p`, `imfrp2_p`, `imfrp1_p`, `imfraa_p`, `imfrp3p4p`, `bbcc_fr_p4`, `bbcc_fr_p3`, `bbcc_fr_p2`, `bbcc_fr_p1`, `bbcc_fr_aa`, `bbccfrp3p4`, `bbccfrp4_p`, `bbccfrp3_p`, `bbccfrp2_p`, `bbccfrp1_p`, `bbccfraa_p`, `bbccfrp34p`, `cod_rip`, `cod_reg`, `cod_prov`, `pro_com`
- Coverage by period: mixed_vintages: 118/118

Source: [ispra-hazard-municipal](https://idrogeo.isprambiente.it/api/pir/comuni/64001)

### mase-natura2000-2025

Records: 20; associated municipalities: 69/118; periods: 2025-12.

December 2025 transmission. Geometry intersection gives source sites touching municipalities; overlapping designations cannot be summed as independent areas.

Staging file: `data/collection/mase-natura2000-2025.rows.jsonl.gz`; SHA-256: `e4ae0f26053d6897c09a56a911044d6ff9e4f53ceb45222a7f8ea47014e39dec`.

- `natura2000_sites` (3 fields): `properties`, `geometry`, `source_geometry_valid`
- Coverage by period: 2025-12: 69/118

Source: [mase-natura2000-2025](https://download.mase.gov.it/Natura2000/Trasmissione%20CE_dicembre2025/sic_zps_ita_32_tuttiicampi.zip)

### osm-transport

Records: 527; associated municipalities: 54/118; periods: 2026-10-13.

Free complementary mapped rail infrastructure and stops. No public GTFS timetable or verified operating status supplied.

Staging file: `data/collection/osm-transport.rows.jsonl.gz`; SHA-256: `0f57193cd73f606bd5d9b3b626aa1e87ff2431bf611fe44376eb0298d407a0c1`.

- `mapped_infrastructure` (2 fields): `osm`, `geometry`
- Coverage by period: 2026-10-13: 54/118

Source: [osm-transport](https://overpass-api.de/api/interpreter?data=%5Bout%3Ajson%5D%5Btimeout%3A40%5D%3B%28way%5B%22railway%22%3D%22rail%22%5D%2840.706645%2C14.559463%2C41.286272%2C15.570283%29%3Bnode%5B%22railway%22~%22station%7Chalt%22%5D%2840.706645%2C14.559463%2C41.286272%2C15.570283%29%3Bnode%5B%22highway%22%3D%22bus_stop%22%5D%2840.706645%2C14.559463%2C41.286272%2C15.570283%29%3Bnode%5B%22public_transport%22%3D%22platform%22%5D%2840.706645%2C14.559463%2C41.286272%2C15.570283%29%3B%29%3Bout+body+geom%3B)

### ingv-events-2020-2026

Records: 517; associated municipalities: 65/118; periods: 2020, 2021, 2022, 2023, 2024, 2025, 2026.

Observed catalog epicentres. Distinct from seismic zoning or future hazard; original depth, magnitude and author retained.

Staging file: `data/collection/ingv-events-2020-2026.rows.jsonl.gz`; SHA-256: `9b0bc06cb9be91530521d3d75f9b648396b20701b3882761fd3acec0979de769`.

- `earthquake_epicentres` (14 fields): `#EventID`, `Time`, `Latitude`, `Longitude`, `Depth/Km`, `Author`, `Catalog`, `Contributor`, `ContributorID`, `MagType`, `Magnitude`, `MagAuthor`, `EventLocationName`, `EventType`
- Coverage by period: 2020: 25/118, 2021: 25/118, 2022: 19/118, 2023: 25/118, 2024: 14/118, 2025: 28/118, 2026: 30/118

Source: [ingv-events-2020-2026](https://webservices.ingv.it/fdsnws/event/1/query?starttime=2020-01-01&endtime=2026-10-12&minlatitude=40.70664495966275&maxlatitude=41.28627197434336&minlongitude=14.559463459143798&maxlongitude=15.570283241762331&format=text)

### istat-tourism-capacity-2002-2025

Records: 2,820; associated municipalities: 118/118; periods: 2002, 2003, 2004, 2005, 2006, 2007, 2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025.

Municipal accommodation capacity with original types, bedrooms/beds/establishments. No tourist arrivals or occupancy inferred from capacity. Original historical municipality codes not merged.

Staging file: `data/collection/istat-tourism-capacity-2002-2025.rows.jsonl.gz`; SHA-256: `7f8e5b983b1d4e0cadc8d5194aaaac999ea8733cbe8c9dbef25c1b1225487282`.

- `Capacità ricettiva` (100 fields): `Anno/Year`, `Regioni / Regions`, `Cod. Reg.`, `Province / Provinces`, `Cod. Prov.`, `Comuni / Municipalities`, `Codice Comune / Municipality code`, `Cod. Istat`, `5 stelle e 5 stelle lusso / 5 tars-5 stars deluxe: Numero / Number`, `5 stelle e 5 stelle lusso / 5 tars-5 stars deluxe: Letti / Beds`, `5 stelle e 5 stelle lusso / 5 tars-5 stars deluxe: Camere / Bedrooms`, `5 stelle e 5 stelle lusso / 5 tars-5 stars deluxe: Bagni / Bathrooms`, `4 stelle  / 4 stars: Numero / Number`, `4 stelle  / 4 stars: Letti / Beds`, `4 stelle  / 4 stars: Camere / Bedrooms`, `4 stelle  / 4 stars: Bagni / Bathrooms`, `3 stelle  / 3 stars: Numero / Number`, `3 stelle  / 3 stars: Letti / Beds`, `3 stelle  / 3 stars: Camere / Bedrooms`, `3 stelle  / 3 stars: Bagni / Bathrooms`, `2 stelle  / 2 stars: Numero / Number`, `2 stelle  / 2 stars: Letti / Beds`, `2 stelle  / 2 stars: Camere / Bedrooms`, `2 stelle  / 2 stars: Bagni / Bathrooms`, `1 stella / 1 star: Numero / Number`, `1 stella / 1 star: Letti / Beds`, `1 stella / 1 star: Camere / Bedrooms`, `1 stella / 1 star: Bagni / Bathrooms`, `residenze turistico alberghiere /: Numero / Number`, `residenze turistico alberghiere /: Letti / Beds`, `residenze turistico alberghiere /: Camere / Bedrooms`, `residenze turistico alberghiere /: Bagni / Bathrooms`, `totale alberghi / hotels total: Numero / Number`, `totale alberghi / hotels total: Letti / Beds`, `totale alberghi / hotels total: Camere / Bedrooms`, `totale alberghi / hotels total: Bagni / Bathrooms`, `campeggi e villaggi turistici  / tourist camp-sites: Numero / Number`, `campeggi e villaggi turistici  / tourist camp-sites: Letti / Beds`, `alloggi in affitto  / holiday dwellings (a): Numero / Number`, `alloggi in affitto  / holiday dwellings (a): Letti / Beds`, `agriturismi / farmhouses: Numero / Number`, `agriturismi / farmhouses: Letti / Beds`, `ostelli per la gioventù / youth hostels: Numero / Number`, `ostelli per la gioventù / youth hostels: Letti / Beds`, `case per ferie / tourist dormitories: Numero / Number`, `case per ferie / tourist dormitories: Letti / Beds`, `rifugi alpini / mountain hut: Numero / Number`, `rifugi alpini / mountain hut: Letti / Beds`, `altri esercizi ricettivi / other accommodations: Numero / Number`, `altri esercizi ricettivi / other accommodations: Letti / Beds`, `bed & breakfast: Numero / Number`, `bed & breakfast: Letti / Beds`, `totale extra-alberghieri / total other accommodations: Numero / Number`, `totale extra-alberghieri / total other accommodations: Letti / Beds`, `totale extra-alberghieri / total other accommodations: Numero / Number__2`, `totale extra-alberghieri / total other accommodations: Letti / Beds__2`, `_unused_57`, `_unused_58`, `_unused_59`, `_unused_60`, `_unused_61`, `_unused_62`, `_unused_63`, `_unused_64`, `_unused_65`, `_unused_66`, `_unused_67`, `_unused_68`, `_unused_69`, `_unused_70`, `_unused_71`, `_unused_72`, `_unused_73`, `_unused_74`, `_unused_75`, `_unused_76`, `_unused_77`, `_unused_78`, `_unused_79`, `_unused_80`, `_unused_81`, `_unused_82`, `_unused_83`, `_unused_84`, `_unused_85`, `_unused_86`, `_unused_87`, `_unused_88`, `_unused_89`, `_unused_90`, `_unused_91`, `_unused_92`, `_unused_93`, `_unused_94`, `_unused_95`, `_unused_96`, `_unused_97`, `_unused_98`, `_unused_99`, `_unused_100`
- Coverage by period: 2002: 117/118, 2003: 117/118, 2004: 117/118, 2005: 117/118, 2006: 117/118, 2007: 117/118, 2008: 117/118, 2009: 117/118, 2010: 117/118, 2011: 117/118, 2012: 117/118, 2013: 117/118, 2014: 118/118, 2015: 118/118, 2016: 118/118, 2017: 118/118, 2018: 118/118, 2019: 118/118, 2020: 118/118, 2021: 118/118, 2022: 118/118, 2023: 118/118, 2024: 118/118, 2025: 118/118

Source: [istat-tourism-capacity-2002-2025](https://esploradati.istat.it/databrowser/DWL/Servizi/DCSC%20Capacity%20of%20tourist%20accommodation%20municipal.zip)

### istat-historical-agriculture-1982-2010

Records: 796,384; associated municipalities: 117/118; periods: 1982, 1990, 2000, 2010.

Original municipal historical agriculture census code table, all published dimensions and periods retained. No unreviewed fusion of historical municipality codes.

Staging file: `data/collection/istat-historical-agriculture-1982-2010.rows.jsonl.gz`; SHA-256: `3e218f3ea2f7db5c6bd758123f964cd3260c1c75da93d7d173af62e8f2048e9c`.

- `historical_agriculture_code_table` (16 fields): `ITTER107`, `TIPO_DATO5`, `TIPO_DATO5_DETT`, `ZONA_ALTIM`, `COLTIV_CONDUZ`, `TIT_POSSESSO`, `CLASSE_SAU_A`, `CLASSE_SAU_B`, `UTILTERR_A`, `UTILTERR_B`, `TIPO_ALLEVAMENTO`, `MANODOPERA`, `DURATA`, `TIME`, `Value`, `Flags`
- Coverage by period: 1982: 117/118, 1990: 117/118, 2000: 117/118, 2010: 117/118
- Original definitions: `data/collection/istat-historical-agriculture-1982-2010.dictionary.json`; SHA-256 `5dbbac40453c6bb5a9631641fd9fed6fc93be014252a4948defbbc97ecafdbbb`.

Source: [istat-historical-agriculture-1982-2010](https://esploradati.istat.it/databrowser/DWL/censtatv5db/Agricoltura/DICA_SERIESTOR1-data.zip)

### mef-income-2020-full-fields

Records: 118; associated municipalities: 118/118; periods: 2020.

All original tax variables, income sources/brackets, frequencies and amounts retained. Suppressed or empty values are not imputed. Tax year, not declaration or publication year.

Staging file: `data/collection/mef-income-2020-full-fields.rows.jsonl.gz`; SHA-256: `8ce4f976160a8769d7a8e50f1aa105cfe5b75fd5c4365bd4f2b435946bcf9d62`.

- `Redditi_e_principali_variabili_IRPEF_su_base_comunale_CSV_2020.csv` (51 fields): `Anno di imposta`, `Codice catastale`, `Codice Istat Comune`, `Denominazione Comune`, `Sigla Provincia`, `Regione`, `Codice Istat Regione`, `Numero contribuenti`, `Reddito da fabbricati - Frequenza`, `Reddito da fabbricati - Ammontare in euro`, `Reddito da lavoro dipendente e assimilati - Frequenza`, `Reddito da lavoro dipendente e assimilati - Ammontare in euro`, `Reddito da pensione - Frequenza`, `Reddito da pensione - Ammontare in euro`, `Reddito da lavoro autonomo (comprensivo dei valori nulli) - Frequenza`, `Reddito da lavoro autonomo (comprensivo dei valori nulli) - Ammontare in euro`, `Reddito di spettanza dell'imprenditore in contabilita' ordinaria  (comprensivo dei valori nulli) - Frequenza`, `Reddito di spettanza dell'imprenditore in contabilita' ordinaria  (comprensivo dei valori nulli) - Ammontare in euro`, `Reddito di spettanza dell'imprenditore in contabilita' semplificata (comprensivo dei valori nulli) - Frequenza`, `Reddito di spettanza dell'imprenditore in contabilita' semplificata (comprensivo dei valori nulli) - Ammontare in euro`, `Reddito da partecipazione  (comprensivo dei valori nulli) - Frequenza`, `Reddito da partecipazione  (comprensivo dei valori nulli) - Ammontare in euro`, `Reddito imponibile - Frequenza`, `Reddito imponibile - Ammontare in euro`, `Imposta netta - Frequenza`, `Imposta netta - Ammontare in euro`, `Bonus spettante - Frequenza`, `Bonus spettante - Ammontare in euro`, `Reddito imponibile addizionale - Frequenza`, `Reddito imponibile addizionale - Ammontare in euro`, `Addizionale regionale dovuta - Frequenza`, `Addizionale regionale dovuta - Ammontare in euro`, `Addizionale comunale dovuta - Frequenza`, `Addizionale comunale dovuta - Ammontare in euro`, `Reddito complessivo minore o uguale a zero euro - Frequenza`, `Reddito complessivo minore o uguale a zero euro - Ammontare in euro`, `Reddito complessivo da 0 a 10000 euro - Frequenza`, `Reddito complessivo da 0 a 10000 euro - Ammontare in euro`, `Reddito complessivo da 10000 a 15000 euro - Frequenza`, `Reddito complessivo da 10000 a 15000 euro - Ammontare in euro`, `Reddito complessivo da 15000 a 26000 euro - Frequenza`, `Reddito complessivo da 15000 a 26000 euro - Ammontare in euro`, `Reddito complessivo da 26000 a 55000 euro - Frequenza`, `Reddito complessivo da 26000 a 55000 euro - Ammontare in euro`, `Reddito complessivo da 55000 a 75000 euro - Frequenza`, `Reddito complessivo da 55000 a 75000 euro - Ammontare in euro`, `Reddito complessivo da 75000 a 120000 euro - Frequenza`, `Reddito complessivo da 75000 a 120000 euro - Ammontare in euro`, `Reddito complessivo oltre 120000 euro - Frequenza`, `Reddito complessivo oltre 120000 euro - Ammontare in euro`, `_source_trailing_unlabelled_empty_cells`
- Coverage by period: 2020: 118/118

Source: [mef-income-2020-full-fields](https://www1.finanze.gov.it/finanze/analisi_stat/public/v_4_0_0/contenuti/Redditi_e_principali_variabili_IRPEF_su_base_comunale_CSV_2020.zip?d=1615465800)

### mef-income-2021-full-fields

Records: 118; associated municipalities: 118/118; periods: 2021.

All original tax variables, income sources/brackets, frequencies and amounts retained. Suppressed or empty values are not imputed. Tax year, not declaration or publication year.

Staging file: `data/collection/mef-income-2021-full-fields.rows.jsonl.gz`; SHA-256: `fb57fcd473e4471db844515e5502c0585677a7cf1ce80c25863f972e51891f1a`.

- `Redditi_e_principali_variabili_IRPEF_su_base_comunale_CSV_2021.csv` (51 fields): `Anno di imposta`, `Codice catastale`, `Codice Istat Comune`, `Denominazione Comune`, `Sigla Provincia`, `Regione`, `Codice Istat Regione`, `Numero contribuenti`, `Reddito da fabbricati - Frequenza`, `Reddito da fabbricati - Ammontare in euro`, `Reddito da lavoro dipendente e assimilati - Frequenza`, `Reddito da lavoro dipendente e assimilati - Ammontare in euro`, `Reddito da pensione - Frequenza`, `Reddito da pensione - Ammontare in euro`, `Reddito da lavoro autonomo (comprensivo dei valori nulli) - Frequenza`, `Reddito da lavoro autonomo (comprensivo dei valori nulli) - Ammontare in euro`, `Reddito di spettanza dell'imprenditore in contabilita' ordinaria  (comprensivo dei valori nulli) - Frequenza`, `Reddito di spettanza dell'imprenditore in contabilita' ordinaria  (comprensivo dei valori nulli) - Ammontare in euro`, `Reddito di spettanza dell'imprenditore in contabilita' semplificata (comprensivo dei valori nulli) - Frequenza`, `Reddito di spettanza dell'imprenditore in contabilita' semplificata (comprensivo dei valori nulli) - Ammontare in euro`, `Reddito da partecipazione  (comprensivo dei valori nulli) - Frequenza`, `Reddito da partecipazione  (comprensivo dei valori nulli) - Ammontare in euro`, `Reddito imponibile - Frequenza`, `Reddito imponibile - Ammontare in euro`, `Imposta netta - Frequenza`, `Imposta netta - Ammontare in euro`, `Trattamento spettante - Frequenza`, `Trattamento spettante - Ammontare in euro`, `Reddito imponibile addizionale - Frequenza`, `Reddito imponibile addizionale - Ammontare in euro`, `Addizionale regionale dovuta - Frequenza`, `Addizionale regionale dovuta - Ammontare in euro`, `Addizionale comunale dovuta - Frequenza`, `Addizionale comunale dovuta - Ammontare in euro`, `Reddito complessivo minore o uguale a zero euro - Frequenza`, `Reddito complessivo minore o uguale a zero euro - Ammontare in euro`, `Reddito complessivo da 0 a 10000 euro - Frequenza`, `Reddito complessivo da 0 a 10000 euro - Ammontare in euro`, `Reddito complessivo da 10000 a 15000 euro - Frequenza`, `Reddito complessivo da 10000 a 15000 euro - Ammontare in euro`, `Reddito complessivo da 15000 a 26000 euro - Frequenza`, `Reddito complessivo da 15000 a 26000 euro - Ammontare in euro`, `Reddito complessivo da 26000 a 55000 euro - Frequenza`, `Reddito complessivo da 26000 a 55000 euro - Ammontare in euro`, `Reddito complessivo da 55000 a 75000 euro - Frequenza`, `Reddito complessivo da 55000 a 75000 euro - Ammontare in euro`, `Reddito complessivo da 75000 a 120000 euro - Frequenza`, `Reddito complessivo da 75000 a 120000 euro - Ammontare in euro`, `Reddito complessivo oltre 120000 euro - Frequenza`, `Reddito complessivo oltre 120000 euro - Ammontare in euro`, `_source_trailing_unlabelled_empty_cells`
- Coverage by period: 2021: 118/118

Source: [mef-income-2021-full-fields](https://www1.finanze.gov.it/finanze/analisi_stat/public/v_4_0_0/contenuti/Redditi_e_principali_variabili_IRPEF_su_base_comunale_CSV_2021.zip?d=1615465800)

### mef-income-2022-full-fields

Records: 118; associated municipalities: 118/118; periods: 2022.

All original tax variables, income sources/brackets, frequencies and amounts retained. Suppressed or empty values are not imputed. Tax year, not declaration or publication year.

Staging file: `data/collection/mef-income-2022-full-fields.rows.jsonl.gz`; SHA-256: `479b964f614806198bd19782275e0f8a5618a991e577fbf2a50d533a583f7516`.

- `Redditi_e_principali_variabili_IRPEF_su_base_comunale_CSV_2022.csv` (51 fields): `Anno di imposta`, `Codice catastale`, `Codice Istat Comune`, `Denominazione Comune`, `Sigla Provincia`, `Regione`, `Codice Istat Regione`, `Numero contribuenti`, `Reddito da fabbricati - Frequenza`, `Reddito da fabbricati - Ammontare in euro`, `Reddito da lavoro dipendente e assimilati - Frequenza`, `Reddito da lavoro dipendente e assimilati - Ammontare in euro`, `Reddito da pensione - Frequenza`, `Reddito da pensione - Ammontare in euro`, `Reddito da lavoro autonomo (comprensivo dei valori nulli) - Frequenza`, `Reddito da lavoro autonomo (comprensivo dei valori nulli) - Ammontare in euro`, `Reddito di spettanza dell'imprenditore in contabilita' ordinaria  (comprensivo dei valori nulli) - Frequenza`, `Reddito di spettanza dell'imprenditore in contabilita' ordinaria  (comprensivo dei valori nulli) - Ammontare in euro`, `Reddito di spettanza dell'imprenditore in contabilita' semplificata (comprensivo dei valori nulli) - Frequenza`, `Reddito di spettanza dell'imprenditore in contabilita' semplificata (comprensivo dei valori nulli) - Ammontare in euro`, `Reddito da partecipazione  (comprensivo dei valori nulli) - Frequenza`, `Reddito da partecipazione  (comprensivo dei valori nulli) - Ammontare in euro`, `Reddito imponibile - Frequenza`, `Reddito imponibile - Ammontare in euro`, `Imposta netta - Frequenza`, `Imposta netta - Ammontare in euro`, `Trattamento spettante - Frequenza`, `Trattamento spettante - Ammontare in euro`, `Reddito imponibile addizionale - Frequenza`, `Reddito imponibile addizionale - Ammontare in euro`, `Addizionale regionale dovuta - Frequenza`, `Addizionale regionale dovuta - Ammontare in euro`, `Addizionale comunale dovuta - Frequenza`, `Addizionale comunale dovuta - Ammontare in euro`, `Reddito complessivo minore o uguale a zero euro - Frequenza`, `Reddito complessivo minore o uguale a zero euro - Ammontare in euro`, `Reddito complessivo da 0 a 10000 euro - Frequenza`, `Reddito complessivo da 0 a 10000 euro - Ammontare in euro`, `Reddito complessivo da 10000 a 15000 euro - Frequenza`, `Reddito complessivo da 10000 a 15000 euro - Ammontare in euro`, `Reddito complessivo da 15000 a 26000 euro - Frequenza`, `Reddito complessivo da 15000 a 26000 euro - Ammontare in euro`, `Reddito complessivo da 26000 a 55000 euro - Frequenza`, `Reddito complessivo da 26000 a 55000 euro - Ammontare in euro`, `Reddito complessivo da 55000 a 75000 euro - Frequenza`, `Reddito complessivo da 55000 a 75000 euro - Ammontare in euro`, `Reddito complessivo da 75000 a 120000 euro - Frequenza`, `Reddito complessivo da 75000 a 120000 euro - Ammontare in euro`, `Reddito complessivo oltre 120000 euro - Frequenza`, `Reddito complessivo oltre 120000 euro - Ammontare in euro`, `_source_trailing_unlabelled_empty_cells`
- Coverage by period: 2022: 118/118

Source: [mef-income-2022-full-fields](https://www1.finanze.gov.it/finanze/analisi_stat/public/v_4_0_0/contenuti/Redditi_e_principali_variabili_IRPEF_su_base_comunale_CSV_2022.zip?d=1615465800)

### mef-income-2023-full-fields

Records: 118; associated municipalities: 118/118; periods: 2023.

All original tax variables, income sources/brackets, frequencies and amounts retained. Suppressed or empty values are not imputed. Tax year, not declaration or publication year.

Staging file: `data/collection/mef-income-2023-full-fields.rows.jsonl.gz`; SHA-256: `76117407844fdc9b6d24b9450ea97a8bf41ed4ab2c9693d65db18dfd287c7f61`.

- `Redditi_e_principali_variabili_IRPEF_su_base_comunale_CSV_2023.csv` (52 fields): `Anno di imposta`, `Codice catastale`, `Codice Istat Comune`, `Denominazione Comune`, `Sigla Provincia`, `Regione`, `Codice Istat Regione`, `Numero contribuenti`, `Reddito da fabbricati - Frequenza`, `Reddito da fabbricati - Ammontare in euro`, `Reddito da lavoro dipendente e assimilati - Frequenza`, `Reddito da lavoro dipendente e assimilati - Ammontare in euro`, `Reddito da pensione - Frequenza`, `Reddito da pensione - Ammontare in euro`, `Reddito da lavoro autonomo (comprensivo dei valori nulli) - Frequenza`, `Reddito da lavoro autonomo (comprensivo dei valori nulli) - Ammontare in euro`, `Reddito di spettanza dell'imprenditore in contabilita' ordinaria  (comprensivo dei valori nulli) - Frequenza`, `Reddito di spettanza dell'imprenditore in contabilita' ordinaria  (comprensivo dei valori nulli) - Ammontare in euro`, `Reddito di spettanza dell'imprenditore in contabilita' semplificata (comprensivo dei valori nulli) - Frequenza`, `Reddito di spettanza dell'imprenditore in contabilita' semplificata (comprensivo dei valori nulli) - Ammontare in euro`, `Reddito da partecipazione  (comprensivo dei valori nulli) - Frequenza`, `Reddito da partecipazione  (comprensivo dei valori nulli) - Ammontare in euro`, `Reddito imponibile - Frequenza`, `Reddito imponibile - Ammontare in euro`, `Imposta netta - Frequenza`, `Imposta netta - Ammontare in euro`, `Trattamento spettante - Frequenza`, `Trattamento spettante - Ammontare in euro`, `Reddito imponibile addizionale - Frequenza`, `Reddito imponibile addizionale - Ammontare in euro`, `Addizionale regionale dovuta - Frequenza`, `Addizionale regionale dovuta - Ammontare in euro`, `Addizionale comunale dovuta - Frequenza`, `Addizionale comunale dovuta - Ammontare in euro`, `Reddito complessivo - Frequenza`, `Reddito complessivo - Ammontare in euro`, `Reddito complessivo minore o uguale a zero euro - Frequenza`, `Reddito complessivo minore o uguale a zero euro - Ammontare in euro`, `Reddito complessivo da 0 a 10000 euro - Frequenza`, `Reddito complessivo da 0 a 10000 euro - Ammontare in euro`, `Reddito complessivo da 10000 a 15000 euro - Frequenza`, `Reddito complessivo da 10000 a 15000 euro - Ammontare in euro`, `Reddito complessivo da 15000 a 26000 euro - Frequenza`, `Reddito complessivo da 15000 a 26000 euro - Ammontare in euro`, `Reddito complessivo da 26000 a 55000 euro - Frequenza`, `Reddito complessivo da 26000 a 55000 euro - Ammontare in euro`, `Reddito complessivo da 55000 a 75000 euro - Frequenza`, `Reddito complessivo da 55000 a 75000 euro - Ammontare in euro`, `Reddito complessivo da 75000 a 120000 euro - Frequenza`, `Reddito complessivo da 75000 a 120000 euro - Ammontare in euro`, `Reddito complessivo oltre 120000 euro - Frequenza`, `Reddito complessivo oltre 120000 euro - Ammontare in euro`
- Coverage by period: 2023: 118/118

Source: [mef-income-2023-full-fields](https://www1.finanze.gov.it/finanze/analisi_stat/public/v_4_0_0/contenuti/Redditi_e_principali_variabili_IRPEF_su_base_comunale_CSV_2023.zip?d=1615465800)

### mef-income-2024-full-fields

Records: 118; associated municipalities: 118/118; periods: 2024.

All original tax variables, income sources/brackets, frequencies and amounts retained. Suppressed or empty values are not imputed. Tax year, not declaration or publication year.

Staging file: `data/collection/mef-income-2024-full-fields.rows.jsonl.gz`; SHA-256: `4b928765e77b627deac1d9be72afd828ebd1838f09a89ccd7484124e9e090a40`.

- `Redditi_e_principali_variabili_IRPEF_su_base_comunale_CSV_2024.csv` (52 fields): `Anno di imposta`, `Codice catastale`, `Codice Istat Comune`, `Denominazione Comune`, `Sigla Provincia`, `Regione`, `Codice Istat Regione`, `Numero contribuenti`, `Reddito da fabbricati - Frequenza`, `Reddito da fabbricati - Ammontare in euro`, `Reddito da lavoro dipendente e assimilati - Frequenza`, `Reddito da lavoro dipendente e assimilati - Ammontare in euro`, `Reddito da pensione - Frequenza`, `Reddito da pensione - Ammontare in euro`, `Reddito da lavoro autonomo (comprensivo dei valori nulli) - Frequenza`, `Reddito da lavoro autonomo (comprensivo dei valori nulli) - Ammontare in euro`, `Reddito di spettanza dell'imprenditore in contabilita' ordinaria  (comprensivo dei valori nulli) - Frequenza`, `Reddito di spettanza dell'imprenditore in contabilita' ordinaria  (comprensivo dei valori nulli) - Ammontare in euro`, `Reddito di spettanza dell'imprenditore in contabilita' semplificata (comprensivo dei valori nulli) - Frequenza`, `Reddito di spettanza dell'imprenditore in contabilita' semplificata (comprensivo dei valori nulli) - Ammontare in euro`, `Reddito da partecipazione  (comprensivo dei valori nulli) - Frequenza`, `Reddito da partecipazione  (comprensivo dei valori nulli) - Ammontare in euro`, `Reddito imponibile - Frequenza`, `Reddito imponibile - Ammontare in euro`, `Imposta netta - Frequenza`, `Imposta netta - Ammontare in euro`, `Trattamento spettante - Frequenza`, `Trattamento spettante - Ammontare in euro`, `Reddito imponibile addizionale - Frequenza`, `Reddito imponibile addizionale - Ammontare in euro`, `Addizionale regionale dovuta - Frequenza`, `Addizionale regionale dovuta - Ammontare in euro`, `Addizionale comunale dovuta - Frequenza`, `Addizionale comunale dovuta - Ammontare in euro`, `Reddito complessivo - Frequenza`, `Reddito complessivo - Ammontare in euro`, `Reddito complessivo minore o uguale a zero euro - Frequenza`, `Reddito complessivo minore o uguale a zero euro - Ammontare in euro`, `Reddito complessivo da 0 a 10000 euro - Frequenza`, `Reddito complessivo da 0 a 10000 euro - Ammontare in euro`, `Reddito complessivo da 10000 a 15000 euro - Frequenza`, `Reddito complessivo da 10000 a 15000 euro - Ammontare in euro`, `Reddito complessivo da 15000 a 26000 euro - Frequenza`, `Reddito complessivo da 15000 a 26000 euro - Ammontare in euro`, `Reddito complessivo da 26000 a 55000 euro - Frequenza`, `Reddito complessivo da 26000 a 55000 euro - Ammontare in euro`, `Reddito complessivo da 55000 a 75000 euro - Frequenza`, `Reddito complessivo da 55000 a 75000 euro - Ammontare in euro`, `Reddito complessivo da 75000 a 120000 euro - Frequenza`, `Reddito complessivo da 75000 a 120000 euro - Ammontare in euro`, `Reddito complessivo oltre 120000 euro - Frequenza`, `Reddito complessivo oltre 120000 euro - Ammontare in euro`
- Coverage by period: 2024: 118/118

Source: [mef-income-2024-full-fields](https://www1.finanze.gov.it/finanze/analisi_stat/public/v_4_0_0/contenuti/Redditi_e_principali_variabili_IRPEF_su_base_comunale_CSV_2024.zip?d=1615465800)

### siat-cultural-lines-15

Records: 5; associated municipalities: 47/118; periods: undated_publisher_layer.

Successful complete Esri JSON alternative to failing GeoJSON export. Source line classification is historic; current operating status is not inferred.

Staging file: `data/collection/siat-cultural-lines-15.rows.jsonl.gz`; SHA-256: `9949c8d4fe20d414a7ded4004dbebf7e0e04548d7f581ddb3f3c53d0b0023c77`.

- `line_features` (2 fields): `esri_feature`, `geometry`
- Coverage by period: undated_publisher_layer: 47/118

Source: [siat-cultural-lines-15](https://siat2.provincia.avellino.it/server/rest/services/QC14_Componenti_strutturali_sistema_dei_beni_culturali/MapServer/15/query?f=json&where=1%3D1&outFields=%2A&outSR=4326&returnGeometry=true&orderByFields=OBJECTID&resultRecordCount=5000&returnM=false&returnZ=false)

### siat-cultural-lines-16

Records: 42; associated municipalities: 26/118; periods: undated_publisher_layer.

Successful complete Esri JSON alternative to failing GeoJSON export. Source line classification is historic; current operating status is not inferred.

Staging file: `data/collection/siat-cultural-lines-16.rows.jsonl.gz`; SHA-256: `ba21403e63cc15b2957c4d2451d7b2c7211e41035410746ad17f5f46f07dc6ec`.

- `line_features` (2 fields): `esri_feature`, `geometry`
- Coverage by period: undated_publisher_layer: 26/118

Source: [siat-cultural-lines-16](https://siat2.provincia.avellino.it/server/rest/services/QC14_Componenti_strutturali_sistema_dei_beni_culturali/MapServer/16/query?f=json&where=1%3D1&outFields=%2A&outSR=4326&returnGeometry=true&orderByFields=OBJECTID&resultRecordCount=5000&returnM=false&returnZ=false)

### arpac-surface-water-2025

Records: 2,911; associated municipalities: 14/118; periods: 2025.

Complete previous-year source partition. Censored measurements such as <0.01 remain original strings; do not replace them with observed zero.

Staging file: `data/collection/arpac-surface-water-2025.rows.jsonl.gz`; SHA-256: `98eccf5f7c699fe1709f4ec9d73aebf19a6a4174d64f1df469b877ee289a6099`.

- `arpac_surface_water_2025.csv` (27 fields): `_id`, `cod_rete`, `Descrizione rete stazione`, `Cod tipologia rete`, `Cod ost appartenenza`, `Den ost appartenenza`, `Nat ost appartenenza cod`, `Nat ost appartenenza desc`, `cod_staz`, `Desc Staz`, `Cod tipologia staz`, `Desc tipologia staz`, `Tipo stazione`, `Cod Regione`, `Nome regione`, `Cod provincia`, `Nome prov`, `Cod comune`, `Nome comune`, `data`, `ANNO prelievo`, `inq`, `Desc inq`, `Metodo`, `Valore mis`, `um`, `gpi`
- Coverage by period: 2025: 14/118

Source: [arpac-surface-water-2025](https://dati.arpacampania.it/datastore/dump/d0f8620e-c70a-4f76-9961-94ef7c7476df)

### bdap-personnel-2024

Records: 445; associated municipalities: 115/118; periods: 2024.

Public CSV export completed through the publisher form without email or credentials. Municipal BDAP IDs reconciled to the independently acquired 2024 financial statements; all employee gender/category/contract variables retained. Export URLs may need re-discovery through the public form.

Staging file: `data/collection/bdap-personnel-2024.rows.jsonl.gz`; SHA-256: `ebd26290a67004d32fe02a9046bae0671dfccb222e6fd32435e48a471c0778d8`.

- `bdap_personnel_actual_export.csv` (28 fields): `Anno Rilevazione`, `Descrizione Tipo Istituzione`, `Codice Istituzione`, `Codice Ente BDAP`, `Descrizione Ente`, `Codice Comparto`, `Descrizione Comparto`, `Codice Contratto Lavoro`, `Descrizione Contratto Lavoro`, `Codice Macrocategoria`, `Descrizione Macrocategoria`, `Codice Categoria`, `Descrizione Categoria`, `Numero Dipendenti Donne Tempo Pieno`, `Numero Dipendenti Uomini Tempo Pieno`, `Numero Dipendenti Donne Part time Inf. 50%`, `Numero Dipendenti Uomini Part time Inf. 50%`, `Numero Dipendenti Donne Part time Sup. 50%`, `Numero Dipendenti Uomini Part time Sup. 50%`, `Numero Dipendenti Donne Tempo Determinato`, `Numero Dipendenti Uomini Tempo Determinato`, `Numero Dipendenti Donne Formazione Lavoro`, `Numero Dipendenti Uomini Formazione Lavoro`, `Numero Dipendenti Donne Lavoro Interinale`, `Numero Dipendenti Uomini Lavoro Interinale`, `Numero Dipendenti Donne Lavoro Socialmente Utile`, `Numero Dipendenti Uomini Lavoro Socialmente Utile`, `_unnamed_28`
- Coverage by period: 2024: 115/118

Source: [bdap-personnel-2024](https://bdap-opendata.rgs.mef.gov.it/export/csv/2024---Dipendenti-Pubblici---Occupazione-Complessiva---Dati-analitici-per-Ente.csv)

### corine-irpinia-2018

Records: 1,318; associated municipalities: 118/118; periods: 2018.

Complete 2400-feature bounding-box export split by unique source OBJECTIDs into bounded batches. Original CLC classes, source polygon areas and geometries retained. Municipal intersections do not make full polygon areas additive within a municipality. Minimum mapping unit is 25 ha, so this cannot replace fine-resolution soil consumption.

Staging file: `data/collection/corine-irpinia-2018.rows.jsonl.gz`; SHA-256: `c8aeaf45774d6ae9bd02ffcedb37e9d704d9767540a65f7404b1c9c03ff58739`.

- `features` (5 fields): `source_feature_index`, `type`, `id`, `geometry`, `properties`
- Coverage by period: 2018: 118/118

Source: [corine-irpinia-2018](https://image.discomap.eea.europa.eu/arcgis/rest/services/Corine/CLC2018_WM/MapServer/0/query?where=OBJECTID+IN+%28597980%2C597989%2C597994%2C597999%2C598004%2C598009%2C598010%2C598016%2C598020%2C598021%2C598023%2C598028%2C598030%2C598032%2C598034%2C598040%2C598043%2C598045%2C598047%2C599819%2C599830%2C599834%2C599837%2C599841%2C599843%2C599847%2C599849%2C599854%2C599856%2C599858%2C599862%2C599863%2C599867%2C599870%2C599871%2C599875%2C599877%2C599884%2C599885%2C599887%2C599890%2C599893%2C599895%2C599898%2C599900%2C599901%2C599905%2C599906%2C599908%2C599913%2C599914%2C599915%2C599918%2C599919%2C599921%2C599923%2C599926%2C599927%2C599929%2C599930%2C599932%2C599936%2C599946%2C599947%2C599948%2C599949%2C599954%2C599955%2C599958%2C599964%2C599966%2C599969%2C599970%2C599975%2C599979%2C599981%2C599982%2C599983%2C599985%2C599991%2C599997%2C600004%2C600013%2C600014%2C600019%2C600021%2C600022%2C600030%2C600033%2C600035%2C600037%2C600040%2C600044%2C600054%2C600055%2C600057%2C600058%2C600062%2C600063%2C600064%2C600066%2C600070%2C600076%2C600077%2C600081%2C600083%2C600085%2C600086%2C600087%2C600088%2C600093%2C600094%2C600095%2C600100%2C600102%2C600490%2C600496%2C600499%2C600502%2C600508%2C600510%2C600511%2C600512%2C600513%2C600514%2C600521%2C600530%2C600531%2C600537%2C600544%2C600547%2C600554%2C600555%2C600598%2C600602%2C600937%2C600950%2C601001%2C604089%2C604105%2C604113%2C604125%2C604133%2C604141%2C604144%2C604157%2C604171%2C604172%2C604195%2C604199%2C604213%2C604221%2C604224%2C604225%2C604230%2C604233%2C604235%2C604236%2C604237%2C604240%2C604242%2C604257%2C604259%2C604267%2C604286%2C604304%2C604305%2C604307%2C604309%2C604312%2C604316%2C604319%2C604325%2C604327%2C604334%2C604335%2C604342%2C604345%2C605825%2C605826%2C605828%2C605829%2C605834%2C605835%2C605836%2C605837%2C605838%2C605839%2C605840%2C605841%2C605843%2C605845%2C605847%2C605848%2C605849%2C605853%2C605855%2C605861%2C605862%2C605863%2C605864%2C605865%2C605867%2C605870%2C605871%2C605874%2C605875%2C605879%2C605881%2C605882%2C605883%2C605886%2C605888%2C605891%2C605894%2C605900%2C605901%2C607741%2C607746%2C607747%2C607750%2C607756%2C607757%2C607771%2C607786%2C607794%2C607797%2C607798%2C607804%2C607808%2C607818%2C608279%2C608282%2C608284%2C608288%2C608289%2C608292%2C608293%2C608297%2C608298%2C609355%2C609357%2C611667%2C611679%2C611686%2C611710%2C611715%2C611717%2C611719%2C611721%2C611722%2C611726%2C611733%2C611735%2C611740%2C611748%2C611759%2C611760%2C611762%2C611767%2C611770%2C611773%2C611781%2C611783%2C611788%2C611792%2C611796%2C611798%2C611800%2C611811%2C611814%2C611815%2C611816%2C611820%2C611828%2C611834%2C611835%2C611836%2C611838%2C611844%2C611845%2C611852%2C611857%2C611859%2C611869%2C611872%2C611873%2C611876%2C611884%2C611892%2C611893%2C611897%2C611900%2C611906%2C611908%2C611910%2C611923%2C611924%2C611932%2C611936%2C611939%2C611941%2C611945%2C611946%2C611947%2C611949%2C611950%2C611952%2C611953%2C611962%2C611970%2C611971%2C611972%2C611978%2C611991%2C611993%2C611996%2C611999%2C612001%2C612004%2C612010%2C616241%2C616242%2C616259%2C616265%2C616280%2C616283%2C616293%2C616298%2C616305%2C616307%2C616312%2C616326%2C616329%2C616332%2C616333%2C616343%2C616345%2C616346%2C616359%2C616362%2C616370%2C616373%2C616381%2C616389%2C616390%2C616397%2C616399%2C616401%2C616406%2C616415%2C616423%2C616439%2C616440%2C616444%2C616456%2C616472%2C616475%2C616481%2C616491%2C616500%2C616502%2C616504%2C616505%2C616516%2C616519%2C616522%2C616523%2C616525%2C616526%2C616531%2C616542%2C616547%2C616550%2C616551%2C616556%2C616570%2C616574%2C616575%2C616580%2C616590%2C616592%2C616598%2C616602%2C616617%2C616624%2C616626%2C616629%2C616635%2C616638%2C616641%2C616647%2C616648%2C616653%2C616661%2C616666%2C616670%2C616678%2C616680%2C616685%2C616689%2C616697%2C616709%2C616713%2C616714%2C616715%2C616722%2C616729%2C616733%2C616735%2C616736%2C616737%2C616741%2C619618%2C619683%2C619685%2C619687%2C619688%2C619693%2C619695%2C619696%2C619708%2C619716%2C619721%2C619727%2C619730%2C619734%2C619737%2C619738%2C619740%2C619749%2C619757%2C619764%2C619768%2C619770%2C619771%2C619780%2C619782%2C619792%2C619795%2C619798%2C619802%2C619812%2C619813%2C619815%2C619818%2C619819%2C619821%2C619822%2C619823%2C619835%2C619850%2C619855%2C619865%2C619867%2C619870%2C619880%2C619881%2C619884%2C619885%2C619887%2C619894%2C619896%2C619899%2C619900%2C619902%2C619903%2C619909%2C619914%2C619915%2C619917%2C620981%2C621008%2C621010%2C621020%2C621021%2C621023%2C621024%2C621025%2C621031%2C621032%2C621033%2C621039%2C621040%2C621044%2C621852%2C621860%2C621867%2C621870%2C621875%2C621881%2C621882%2C621885%2C621888%2C621890%2C621894%2C621895%2C621897%2C621899%2C623060%29&outFields=%2A&outSR=4326&f=geojson&returnGeometry=true&resultRecordCount=1000&orderByFields=OBJECTID)

### mef-participations-2023

Records: 395; associated municipalities: 102/118; periods: 2023.

Actual MEF 2023 participations CSV. Authority fiscal identifiers reconciled to municipal BDAP identities; participating-company seat is not used as the municipal association. Original percentages, indirect flags, company accounts and review decisions retained.

Staging file: `data/collection/mef-participations-2023.rows.jsonl.gz`; SHA-256: `fd917601fb9c9c7e2f2d613dedc0cc7a50703e7fe6af1591c3b122f6642afc59`.

- `mef_participations_2023.csv` (93 fields): `Amministrazione Settore Istituzionale`, `Amministrazione Macrocategoria`, `Amministrazione Categoria`, `Amministrazione Denominazione`, `Amministrazione Codice Fiscale`, `Appartenenza perimetro TUSP`, `Appartenenza perimetro Revisione Periodica`, `Amministrazione Regione Sede`, `Amministrazione Provincia Sede`, `Amministrazione Comune Sede`, `Partecipata Denominazione`, `Partecipata Codice Fiscale`, `Partecipata Anno di costituzione`, `Partecipata Forma Giuridica`, `Partecipata Stato Giuridico`, `Partecipata Anno inizio procedura`, `Partecipata Nazione`, `Partecipata Regione Sede`, `Partecipata Provincia Sede`, `Partecipata Comune Sede`, `Emittente Azioni Quotate`, `Emittente Strumenti Quotati`, `Società controllata da una quotata`, `GAL`, `Partecipata Settore Attività`, `Partecipata Divisione ATECO`, `Servizi affidati`, `Servizio affidato 1`, `Modalità affidamento servizio 1`, `Ente affidante servizio 1`, `Importo impegnato servizio 1`, `Servizio affidato 2`, `Modalità affidamento servizio 2`, `Ente affidante servizio 2`, `Importo impegnato servizio 2`, `Servizio affidato 3`, `Modalità affidamento servizio 3`, `Ente affidante servizio 3`, `Importo impegnato servizio 3`, `Servizio affidato 4`, `Modalità affidamento servizio 4`, `Ente affidante servizio 4`, `Importo impegnato servizio 4`, `Servizio affidato 5`, `Modalità affidamento servizio 5`, `Ente affidante servizio 5`, `Importo impegnato servizio 5`, `Quota partecipazione diretta (%)`, `Partecipazione indiretta`, `Tipo controllo`, `Totale oneri - Importo impegnato`, `Totale oneri - Importo pagato c/residui`, `Totale oneri - Importo pagato c/competenza`, `Partecipata Tipo contabilità`, `Partecipata Tipo bilancio`, `Partecipata Bilancio di esercizio approvato`, `Partecipata Numero di addetti`, `Partecipata Patrimonio Netto - CO.E.P.`, `Partecipata Risultato d'esercizio - CO.E.P.`, `Partecipata Valore della produzione - CO.E.P.`, `Partecipata Costo della produzione - CO.E.P.`, `Partecipata Costo del personale - CO.E.P.`, `Partecipata Patrimonio netto - CO.F.`, `Partecipata Totale Entrate - CO.F.`, `Partecipata Totale uscite - CO.F.`, `Partecipata Spese per personale - CO.F.`, `Nr. amministratori`, `Nr. componenti organo di controllo`, `Partecipata bilancio di esercizio 2023 approvato`, `Risultato d'esercizio 2023`, `Fatturato 2023`, `Partecipata bilancio di esercizio 2022 approvato`, `Risultato d'esercizio 2022`, `Fatturato 2022`, `Partecipata bilancio di esercizio 2021 approvato`, `Risultato d'esercizio 2021`, `Fatturato 2021`, `Partecipata bilancio di esercizio 2020 approvato`, `Risultato d'esercizio 2020`, `Partecipata bilancio di esercizio 2019 approvato`, `Risultato d'esercizio 2019`, `Partecipazione ancora detenuta alla data di adozione del provvedimento`, `Società controllata da una quotata dichiarata`, `Attività a favore Amm.`, `Società all. A`, `Attività svolta`, `Quota soggetto privato`, `Attività analoghe (art.20, c.2 lett.c)`, `Contenimento dei costi (art.20, c.2 lett.f)`, `Aggregazione di società (art.20, c.2 lett.g)`, `Esito della ricognizione`, `Modalità Razionalizzazione`, `Termine Razionalizzazione`
- Coverage by period: 2023: 102/118

Source: [mef-participations-2023](https://www.de.mef.gov.it/modules/documenti_it/attivo_patrimonio/partecipazioni_2023/dati_partecipazioni_anno_2023.csv)

### mic-arco-properties

Records: 30; associated municipalities: 2/118; periods: undated_catalog_relations.

Actual ArCo RDF location relations in the Avellino province graph, independently counted. Includes catalog labels, types and location roles; shooting and collecting locations are not current storage sites. Not an exhaustive local cultural-property inventory.

Staging file: `data/collection/mic-arco-properties.rows.jsonl.gz`; SHA-256: `a048d411a33604669447c58099d50f25e27cc1359f71e07b52456f18ac4748bc`.

- `cultural_property_location_relations` (8 fields): `property`, `type`, `label`, `location`, `role`, `city`, `cityLabel`, `_rdf_bindings`
- Coverage by period: undated_catalog_relations: 2/118

Source: [mic-arco-properties](https://dati.cultura.gov.it/sparql?query=SELECT+DISTINCT+%3Fproperty+%3Ftype+%3Flabel+%3Flocation+%3Frole+%3Fcity+%3FcityLabel+WHERE+%7B+GRAPH+%3Chttps%3A%2F%2Fw3id.org%2Farco%2Fdata%3E+%7B+%3Faddress+%3Chttps%3A%2F%2Fw3id.org%2Fitalia%2Fonto%2FCLV%2FhasProvince%3E+%3Chttps%3A%2F%2Fw3id.org%2Farco%2Fresource%2FProvince%2Favellino%3E+.+%3Ffeature+%3Chttps%3A%2F%2Fw3id.org%2Fitalia%2Fonto%2FCLV%2FhasAddress%3E+%3Faddress+.+%3Flocation+%3Chttps%3A%2F%2Fw3id.org%2Farco%2Fontology%2Flocation%2FatLocation%3E+%3Ffeature+.+%3Fproperty+%3Chttps%3A%2F%2Fw3id.org%2Farco%2Fontology%2Flocation%2FhasTimeIndexedTypedLocation%3E+%3Flocation+.+%3Fproperty+a+%3Ftype+.+FILTER%28STRSTARTS%28STR%28%3Ftype%29%2C%22https%3A%2F%2Fw3id.org%2Farco%2Fontology%2Farco%2F%22%29%29+%3Faddress+%3Chttps%3A%2F%2Fw3id.org%2Fitalia%2Fonto%2FCLV%2FhasCity%3E+%3Fcity+.+%3Fcity+%3Chttp%3A%2F%2Fwww.w3.org%2F2000%2F01%2Frdf-schema%23label%3E+%3FcityLabel+.+OPTIONAL+%7B+%3Fproperty+%3Chttp%3A%2F%2Fwww.w3.org%2F2000%2F01%2Frdf-schema%23label%3E+%3Flabel+%7D+OPTIONAL+%7B+%3Flocation+%3Chttps%3A%2F%2Fw3id.org%2Farco%2Fontology%2Flocation%2FhasLocationType%3E+%3Frole+%7D+%7D+%7D+ORDER+BY+%3Fproperty+%3Flocation+%3Ftype+%3Flabel+%3FcityLabel&format=application%2Fsparql-results%2Bjson)

### movimprese-province-2025

Records: 1; associated municipalities: 0/118; periods: 2025.

Original provincial registrations, closures, balance and growth rate extracted from the official 2025 Unioncamere annual report. No municipal figures are inferred.

Staging file: `data/collection/movimprese-province-2025.rows.jsonl.gz`; SHA-256: `6b35a8dc367bd6be03a3ad990dabab3c90597c1afdb56fd9f9a994a229e7e652`.

- `provincial_annual_business_demography` (6 fields): `PROVINCE`, `Iscrizioni`, `Cessazioni`, `Saldo`, `Tasso % di crescita`, `_source_table_index`
- Coverage by period: 2025: 0/118

Source: [movimprese-province-2025](https://www.unioncamere.gov.it/sites/default/files/articoli/2026-02/23012026_com_movi_anno_2025.docx)

### civitas-2023-ind-amministr-01-it

Records: 4,720; associated municipalities: 118/118; periods: 2023.

Original OpenCivitas source fields and variable dictionary retained. Entity USERNAME is reconciled through the matching official workbook. Privacy/anomaly/blank values and functional-definition flags are retained without imputation. Budget appropriations, standard needs, output estimates and service counts require separate interpretation.

Staging file: `data/collection/civitas-2023-ind-amministr-01-it.rows.jsonl.gz`; SHA-256: `3e859a331436812f1265fdddb124fd438ece40582276433527f4324902694933`.

- `2023_Ind_AMMINISTR_01_IT.csv` (5 fields): `USERNAME`, `Indicatore/Determinante`, `Valore`, `Anomalia`, `Privacy`
- Original variable codes: `ADDETTI_I_P_MEAN`, `COORD_OUT`, `COORD_SPESA`, `COSTO_LAVORO_PROAB`, `D03`, `DESCR_NON_VALUTABILE_OUT`, `DESCR_NON_VALUTABILE_SPESA`, `DIFF_OUT_PERC`, `DIPENDENTI_X1000AB`, `DUMMY_AMMALTR_GP_ASSOC`, `DUMMY_AMMANAG_GP_ASSOC`, `DUMMY_AMMTRIB_GP_ASSOC`, `DUMMY_AMMUFFT_GP_ASSOC`, `FL_DIF_OUTPUT_MAG_0`, `FL_DIF_OUTPUT_MIN_0`, `FL_DIF_SPESA_MAG_0`, `FL_DIF_SPESA_MIN_0`, `FL_NO_VALUTABILE`, `FL_SPESA_MENO_OUT_MENO`, `FL_SPESA_MENO_OUT_PIU`, `FL_SPESA_PIU_OUT_MENO`, `FL_SPESA_PIU_OUT_PIU`, `FST_RIPROPORZIONATO_BI`, `FST_RIPROPORZIONATO_BI_PROAB`, `F_ADDETTI_I_P_MEAN`, `F_COSTO_LAV_AMM_SCOST`, `F_IMMOBILI_TOTALI_P`, `F_INV_POP`, `F_SISMICO_RISCHIO_ALTO_MEAN`, `IMMOBILI_TOTALI_P`, `MOTIVO_RECUPERO_SPESA`, `NON_VALUTABILE_OUT`, `NON_VALUTABILE_SPESA`, `OMI_UFFICI_AFF_MQ_2023_EURO`, `POSIZIONE_OUTPUT_PERC`, `POSIZIONE_SPESA_PERC`, `REDDITO_MEAN`, `SISMICO_RISCHIO_ALTO_MEAN`, `SPESA_STORICA`, `SPESA_STORICA_PROAB`
- Coverage by period: 2023: 118/118
- Original definitions: `data/collection/civitas-2023-ind-amministr-01-it.dictionary.json`; SHA-256 `75729fcae1c3f24c5ac1dd3aaf83fb9ef8f49358100d6e4aa1e7adca12f8057f`.

Source: [civitas-2023-ind-amministr-01-it](https://www.opencivitas.it/portale/documents/20118/0/2023_Ind_AMMINISTR_01_IT.csv/45e7ec1b-d282-278d-de7b-73af1b374255)

### civitas-2023-ind-polizia-01-it

Records: 7,316; associated municipalities: 118/118; periods: 2023.

Original OpenCivitas source fields and variable dictionary retained. Entity USERNAME is reconciled through the matching official workbook. Privacy/anomaly/blank values and functional-definition flags are retained without imputation. Budget appropriations, standard needs, output estimates and service counts require separate interpretation.

Staging file: `data/collection/civitas-2023-ind-polizia-01-it.rows.jsonl.gz`; SHA-256: `c3eab6ed297a5c3514acd686ed43c2421fe9e30f555cbbef046384513e7b598e`.

- `2023_Ind_POLIZIA_01_IT.csv` (5 fields): `USERNAME`, `Indicatore/Determinante`, `Valore`, `Anomalia`, `Privacy`
- Original variable codes: `COORD_OUT`, `COORD_SPESA`, `COSTO_LAVORO_PROAB`, `D03`, `DENSITA_MEAN`, `DESCR_NON_VALUTABILE_OUT`, `DESCR_NON_VALUTABILE_SPESA`, `DIFF_OUT_PERC`, `DIFF_PENDOLARI_N_PM`, `DIPENDENTI_X1000AB`, `DUMMY_ARMATO`, `DUMMY_NOTTURNO`, `DUMMY_POLIZIA_ASSOC`, `FL_DIF_OUTPUT_MAG_0`, `FL_DIF_OUTPUT_MIN_0`, `FL_DIF_SPESA_MAG_0`, `FL_DIF_SPESA_MIN_0`, `FL_NO_VALUTABILE`, `FL_SPESA_MENO_OUT_MENO`, `FL_SPESA_MENO_OUT_PIU`, `FL_SPESA_PIU_OUT_MENO`, `FL_SPESA_PIU_OUT_PIU`, `FST_RIPROPORZIONATO_BI`, `FST_RIPROPORZIONATO_BI_PROAB`, `F_COSTO_TOT_MEDIO_LAV_SCOST`, `F_DENSITA_MEAN`, `F_DIFF_PENDOLARI_N_P`, `F_DUMMY_ARMATO`, `F_ISTAT_GENER_STRADE_KM_MEAN`, `F_MERCATI_P_MEAN`, `F_M_INCIDENTI_P`, `F_M_QUERELE_P`, `F_OUTPUT_ALTRI_ESOGENI_P`, `F_PRESENZE_COMUNE_P_MEAN`, `F_PREZZO_VEIC_FINALE_POL_SCOST`, `F_STALLI_P_MEAN`, `INCIDENTI_PM`, `ISTAT_GENER_STRADE_KM_MEAN`, `M11_TOT_PM`, `M12_TOT_PM`, `M21_TOT_PM`, `M22_TOT_PM`, `MERCATI_P_MEAN_PM`, `MOTIVO_RECUPERO_SPESA`, `M_FERMI_AMMINISTRATIVI_PM`, `M_INFO_INVESTIGATIVE_PM`, `M_RICORSI_PM`, `M_RIMOZIONI_PM`, `M_SANZIONI_ATTIVITA_PM`, `NON_VALUTABILE_OUT`, `NON_VALUTABILE_SPESA`, `ORE_ANNUE_SERVIZIO_ESTERN`, `OUTPUT_ALTRI_ESOGENI_PM`, `OUT_COMPOSITO_STORICO_X1000AB`, `POSIZIONE_OUTPUT_PERC`, `POSIZIONE_SPESA_PERC`, `PRESENZE_COMUNE_P_MP`, `PREZZO_VEIC_FINALE_POLIZIA`, `REDDITO_MEAN`, `SPESA_STORICA`, `SPESA_STORICA_PROAB`, `STALLI_P_MEAN_PM`
- Coverage by period: 2023: 118/118
- Original definitions: `data/collection/civitas-2023-ind-polizia-01-it.dictionary.json`; SHA-256 `74040ef43511add71b98a27ffbc23f98172797e31533226f44c45ab0484ae0ae`.

Source: [civitas-2023-ind-polizia-01-it](https://www.opencivitas.it/portale/documents/20118/0/2023_Ind_POLIZIA_01_IT.csv/175d849b-35f1-c439-c869-fe48959a24ce)

### civitas-2023-ind-rifiuti-01-it

Records: 5,310; associated municipalities: 118/118; periods: 2023.

Original OpenCivitas source fields and variable dictionary retained. Entity USERNAME is reconciled through the matching official workbook. Privacy/anomaly/blank values and functional-definition flags are retained without imputation. Budget appropriations, standard needs, output estimates and service counts require separate interpretation.

Staging file: `data/collection/civitas-2023-ind-rifiuti-01-it.rows.jsonl.gz`; SHA-256: `ed785f3e557419afcf1d537987e8a4a985939831ae457f1be8c2f5c8d832216f`.

- `2023_Ind_RIFIUTI_01_IT.csv` (4 fields): `USERNAME`, `Indicatore/Determinante`, `Valore`, `Anomalia`
- Original variable codes: `AER_ANAER_REG_2023_N`, `CENTRI_RACCOLTA_2023`, `COEINCENERITORI_REG_2023_N`, `COORD_OUT`, `COORD_SPESA`, `DESCR_NON_VALUTABILE_OUT`, `DESCR_NON_VALUTABILE_SPESA`, `DIFF_OUT_PERC`, `DISCARICHE_REG_2023_N`, `DISTANZA_IMPIANTI_POND`, `DUMMY_RIFIUTI_ASSOC`, `FL_DIF_OUTPUT_MAG_0`, `FL_DIF_OUTPUT_MIN_0`, `FL_DIF_SPESA_MAG_0`, `FL_DIF_SPESA_MIN_0`, `FL_NO_VALUTABILE`, `FL_SPESA_MENO_OUT_MENO`, `FL_SPESA_MENO_OUT_PIU`, `FL_SPESA_PIU_OUT_MENO`, `FL_SPESA_PIU_OUT_PIU`, `FST_RIPROPORZIONATO_BI`, `FST_RIPROPORZIONATO_BI_PROAB`, `F_BASE`, `F_CONTESTO`, `F_DIFFERENZIATA`, `F_DISECONOMIE`, `F_DISTANZA`, `F_GESTIONE`, `F_INFRASTRUTTURE`, `F_TIPRACCOLTA`, `MOTIVO_RECUPERO_SPESA`, `NON_VALUTABILE_OUT`, `NON_VALUTABILE_SPESA`, `POSIZIONE_OUTPUT_PERC`, `POSIZIONE_SPESA_PERC`, `PRCREG_RU_TRATT_AER_ANAER_2023`, `PRCREG_RU_TRATT_COEINCENER_2023`, `PRCREG_RU_TRATT_DISCARICA_2023`, `RACCOLTA_DOMICILIARE_2023`, `RACCOLTA_SU_CHIAMATA_2023`, `RACC_DIFFER_PERC`, `RIFIUTI_URBANI_P_KG`, `SPESA_STORICA`, `SPESA_STORICA_PROAB`, `TMB_REG_2023_N`
- Coverage by period: 2023: 118/118
- Original definitions: `data/collection/civitas-2023-ind-rifiuti-01-it.dictionary.json`; SHA-256 `721830a0e394f8a48269221d011fb6c81dcb91eda6cdb3492b36eba086d01b65`.

Source: [civitas-2023-ind-rifiuti-01-it](https://www.opencivitas.it/portale/documents/20118/0/2023_Ind_RIFIUTI_01_IT.csv/34fd224a-5cac-7676-3016-7c55fe5d6450)

### civitas-fc90-a-com-1

Records: 118; associated municipalities: 118/118; periods: 2023.

Original OpenCivitas source fields and variable dictionary retained. Entity USERNAME is reconciled through the matching official workbook. Privacy/anomaly/blank values and functional-definition flags are retained without imputation. Budget appropriations, standard needs, output estimates and service counts require separate interpretation.

Staging file: `data/collection/civitas-fc90-a-com-1.rows.jsonl.gz`; SHA-256: `63bdd6c4caaf43ea00f8eb85a2ce826dc63f4ee705dcfda8f7aa5ea35a128b1d`.

- `FC90_A_com_1.csv` (366 fields): `USERNAME`, `A0100001`, `A0200001`, `A0300001`, `A0400001`, `A0500001`, `A0600001`, `A0700001`, `A0800001`, `B0100001`, `B0100002`, `B0100003`, `B0100004`, `B0100005`, `B0100006`, `B0200001`, `B0200002`, `B0200003`, `B0200004`, `B0200005`, `B0200006`, `B0300001`, `B0300002`, `B0300003`, `B0300004`, `B0300005`, `B0300006`, `B0400001`, `B0400002`, `B0400003`, `B0400004`, `B0400005`, `B0400006`, `B0500001`, `B0500002`, `B0500003`, `B0500004`, `B0500005`, `B0500006`, `B0600001`, `B0600002`, `B0600003`, `B0600004`, `B0600005`, `B0600006`, `B0700001`, `B0700002`, `B0700003`, `B0700004`, `B0700005`, `B0700006`, `B0800001`, `B0800002`, `B0800003`, `B0800004`, `B0800005`, `B0800006`, `B0900001`, `B0900002`, `B0900003`, `B0900004`, `B0900005`, `B0900006`, `B1000001`, `B1000002`, `B1000003`, `B1000004`, `B1000005`, `B1000006`, `B1100001`, `B1100002`, `B1100003`, `B1100004`, `B1100005`, `B1100006`, `B1200001`, `B1200002`, `B1200003`, `B1200004`, `B1200005`, `B1200006`, `B1300001`, `B1300002`, `B1300003`, `B1300004`, `B1300005`, `B1300006`, `B1400001`, `B1400002`, `B1400003`, `B1400004`, `B1400005`, `B1400006`, `B1500001`, `B1500002`, `B1500003`, `B1500004`, `B1500005`, `B1500006`, `B1600001`, `B1600002`, `B1600003`, `B1600004`, `B1600005`, `B1600006`, `B1700001`, `B1700002`, `B1700003`, `B1700004`, `B1700005`, `B1700006`, `B1800001`, `B1800002`, `B1800003`, `B1800004`, `B1800005`, `B1800006`, `B1900001`, `B1900002`, `B1900003`, `B1900004`, `B1900005`, `B1900006`, `B2000001`, `C0100001`, `C0100002`, `C0200001`, `C0200002`, `C0300001`, `C0300002`, `C0400001`, `C0400002`, `C0500001`, `C0500002`, `C0600001`, `C0600002`, `C0700001`, `C0700002`, `C0800001`, `C0800002`, `C0900001`, `C0900002`, `C1000001`, `C1100001`, `C1200001`, `C1200002`, `C1300001`, `C1300002`, `C1400001`, `C1500001`, `C1600001`, `C1700001`, `C1700002`, `C1800001`, `C1800002`, `C1900001`, `C1900002`, `C2000001`, `C2000002`, `C2100001`, `C2100002`, `C2200001`, `C2300001`, `C2400001`, `C2500001`, `C2600001`, `C2700001`, `C2800001`, `C2900001`, `C2900002`, `C3000001`, `E0100001`, `E0100002`, `E0100003`, `E0100004`, `E0200001`, `E0200002`, `E0200003`, `E0200004`, `E0300001`, `E0300002`, `E0300003`, `E0300004`, `E0400001`, `E0400002`, `E0400003`, `E0400004`, `E0500001`, `E0500002`, `E0500003`, `E0500004`, `E0600001`, `E0600002`, `E0700001`, `E0700002`, `E0800001`, `E0800002`, `E0900001`, `E0900002`, `E1000001`, `F0100001`, `F0100002`, `F0200001`, `F0200002`, `F0300001`, `F0300002`, `F0400001`, `F0400002`, `F0500001`, `F0500002`, `F0500003`, `F0600001`, `M0100001`, `M0200001`, `M0300001`, `M0400001`, `M0500001`, `M0700001`, `M0800001`, `M0900001`, `M1000001`, `M1100001`, `M1200001`, `M1300001`, `M1400001`, `M1500001`, `M1600001`, `M1700001`, `M1800001`, `M1900001`, `M2000001`, `M2100001`, `M2200001`, `M2300001`, `M2400001`, `M2600001`, `M2700001`, `M2800001`, `M2900001`, `M3000001`, `M3100001`, `M3200001`, `M3300001`, `M3400001`, `M3500001`, `M3600001`, `M3700001`, `M3800001`, `M3900001`, `M4000001`, `M4100001`, `M4200001`, `M4300001`, `M4400001`, `M4500001`, `M4600001`, `M4700001`, `M4800001`, `M4900001`, `M5000001`, `M5100001`, `M5200001`, `M5300001`, `M5400001`, `M5500001`, `M5600001`, `M5700001`, `MSGQC001`, `MSGQM001`, `MSGQM002`, `MSGQM003`, `MSGQM004`, `MSGQN001`, `N0100001`, `N0100002`, `N0100003`, `N0200001`, `N0200002`, `N0200003`, `N0300001`, `N0300002`, `N0300003`, `N0400001`, `N0400002`, `N0400003`, `N0500001`, `N0500002`, `N0500003`, `N0600001`, `N0600002`, `N0600003`, `N0700001`, `N0700002`, `N0700003`, `N0800001`, `N0800002`, `N0800003`, `N0900001`, `N0900002`, `N0900003`, `N1000001`, `N1000002`, `N1000003`, `N1100001`, `N1100002`, `N1100003`, `N1200001`, `N1200002`, `N1200003`, `N1300001`, `N1300002`, `N1300003`, `N1400001`, `N1400002`, `N1400003`, `N1500001`, `N1500002`, `N1500003`, `N1600001`, `N1600002`, `N1600003`, `N1700001`, `N1700002`, `N1700003`, `N1800001`, `N1800002`, `N1800003`, `N1900001`, `N1900002`, `N1900003`, `N2000001`, `N2000002`, `N2000003`, `N2100001`, `N2100002`, `N2100003`, `N2200001`, `N2200002`, `N2200003`, `N2300001`, `N2300002`, `N2300003`, `N2400001`, `N2400002`, `N2400003`, `N2500001`, `N2500002`, `N2500003`, `N2600001`, `N2600002`, `N2600003`, `N2700001`, `N2700002`, `N2700003`, `N2800001`, `N2800002`, `N2800003`, `N2900001`, `N2900002`, `N2900003`, `N3000001`, `N3000002`, `N3000003`, `N3100002`, `N3100003`, `N3200001`
- Coverage by period: 2023: 118/118
- Original definitions: `data/collection/civitas-fc90-a-com-1.dictionary.json`; SHA-256 `dcee871edea515f592e1d8f7559aaee257068f7622283afc3e21b0ce0c72392a`.

Source: [civitas-fc90-a-com-1](https://www.opencivitas.it/portale/documents/20118/0/FC90_A_com_1.csv/c4b34c9e-8147-5f98-dfb3-88bf24d100b2)

### civitas-fc90-b-com-1

Records: 118; associated municipalities: 118/118; periods: 2023.

Original OpenCivitas source fields and variable dictionary retained. Entity USERNAME is reconciled through the matching official workbook. Privacy/anomaly/blank values and functional-definition flags are retained without imputation. Budget appropriations, standard needs, output estimates and service counts require separate interpretation.

Staging file: `data/collection/civitas-fc90-b-com-1.rows.jsonl.gz`; SHA-256: `a3ea7f0bf4a488348d5b0740899a488ad2aeff4878aa9b4b167b48c7afdd034e`.

- `FC90_B_com_1.csv` (246 fields): `USERNAME`, `S0200001`, `S0200002`, `S0200003`, `S0200004`, `S0200005`, `S0200006`, `S0200007`, `S0200008`, `S0200009`, `S0200010`, `S0200011`, `S0200012`, `S02A0001`, `S02A0002`, `S02A0003`, `S02A0004`, `S02A0005`, `S02A0006`, `S02A0007`, `S02A0008`, `S02A0009`, `S02A0010`, `S02A0011`, `S02A0012`, `S0300001`, `S0300002`, `S0300003`, `S0300004`, `S0300005`, `S0300006`, `S0300007`, `S0300008`, `S0300009`, `S0300010`, `S0300011`, `S0300012`, `S03C0001`, `S03C0002`, `S03C0003`, `S0400001`, `S0400002`, `S0400003`, `S0400004`, `S0400005`, `S0400006`, `S0400007`, `S0400008`, `S0400009`, `S0400010`, `S0400011`, `S0400012`, `S0500001`, `S0500002`, `S0500003`, `S0500004`, `S0500005`, `S0500006`, `S0500007`, `S0500008`, `S0500009`, `S0500010`, `S0500011`, `S0500012`, `S05A0001`, `S05A0002`, `S05A0003`, `S05A0004`, `S05A0005`, `S05A0006`, `S05A0007`, `S05A0008`, `S05A0009`, `S05A0010`, `S05A0011`, `S05A0012`, `S0600001`, `S0600002`, `S0600003`, `S0600004`, `S0600005`, `S0600006`, `S0600007`, `S0600008`, `S0600009`, `S0600010`, `S0600011`, `S0600012`, `S0800001`, `S0800002`, `S0800003`, `S0800004`, `S0800005`, `S0800006`, `S0800007`, `S0800008`, `S0800009`, `S0800010`, `S0800011`, `S0800012`, `S08A0001`, `S08A0002`, `S08A0003`, `S08A0004`, `S08A0005`, `S08A0006`, `S08A0007`, `S08A0008`, `S08A0009`, `S08A0010`, `S08A0011`, `S08A0012`, `S1000001`, `S1000002`, `S1000003`, `S1000004`, `S1000005`, `S1000006`, `S1000007`, `S1000008`, `S1000009`, `S1000010`, `S1000011`, `S1000012`, `S1100001`, `S1100002`, `S1100003`, `S1100004`, `S1100005`, `S1100006`, `S1100007`, `S1100008`, `S1100009`, `S1100010`, `S1100011`, `S1100012`, `S1200001`, `S1200002`, `S1200003`, `S1200004`, `S1200005`, `S1200006`, `S1200007`, `S1200008`, `S1200009`, `S1200010`, `S1200011`, `S1200012`, `W0100001`, `W0100002`, `X0000001`, `X0000002`, `X0000003`, `X00A0001`, `X00A0002`, `X00A0003`, `X0100001`, `X0100002`, `X0100003`, `X0100004`, `X0100005`, `X0100006`, `X0100007`, `X0100008`, `X0100009`, `X0100010`, `X0100011`, `X0100012`, `X01A0001`, `X01A0002`, `X01A0003`, `X01A0004`, `X0200001`, `X0200002`, `X0200003`, `X0300001`, `X0300002`, `X0400001`, `X0400002`, `X0400003`, `X0400004`, `X0400005`, `X0500001`, `X0500002`, `X0600001`, `X0600002`, `X0700001`, `X0700002`, `X0700003`, `X0700004`, `X0700005`, `X0700006`, `X0700007`, `X0700008`, `X0700009`, `X0700010`, `X0700011`, `X0700012`, `X0800001`, `X0800002`, `X0800003`, `X0800004`, `X0800005`, `X0800006`, `X0800007`, `X0800008`, `X0800009`, `X0800010`, `X0800011`, `X0800012`, `X1000001`, `X1000002`, `X1000003`, `X1000004`, `X1000005`, `X1000006`, `X1000007`, `X1000008`, `X1000009`, `X1000010`, `X1000011`, `X1000012`, `Z0100001`, `Z0100002`, `Z0100003`, `Z0100004`, `Z0100005`, `Z0100006`, `Z0100007`, `Z0100008`, `Z0100009`, `Z0100010`, `Z0100011`, `Z0100012`, `Z0200001`, `Z0200002`, `Z0200003`, `Z0200004`, `Z0200005`, `Z0200006`, `Z0200007`, `Z0200008`, `Z0200009`, `Z0200010`, `Z0200011`, `Z0200012`
- Coverage by period: 2023: 118/118
- Original definitions: `data/collection/civitas-fc90-b-com-1.dictionary.json`; SHA-256 `9c35ed506f812151cd11e8c3818155079a1c45a83b8600a80dab223510c138d8`.

Source: [civitas-fc90-b-com-1](https://www.opencivitas.it/portale/documents/20118/0/FC90_B_com_1.csv/c9ed27b3-00c4-4cae-d51b-9113f99056f3)

### civitas-2026-var-fsc-1-2026-it

Records: 3,304; associated municipalities: 118/118; periods: 2026.

Original OpenCivitas source fields and variable dictionary retained. Entity USERNAME is reconciled through the matching official workbook. Privacy/anomaly/blank values and functional-definition flags are retained without imputation. Budget appropriations, standard needs, output estimates and service counts require separate interpretation. The FSC 2026 entity workbook lacks municipal ISTAT keys: exact official municipal names within province 064 are used explicitly; the 118-key mapping is validated before collection.

Staging file: `data/collection/civitas-2026-var-fsc-1-2026-it.rows.jsonl.gz`; SHA-256: `6c8b5cd6eef292bbe2b75acab4e7c367fd9a334818b114f0790ba51aa882dc11`.

- `2026_VAR_FSC_1_2026_IT.csv` (3 fields): `USERNAME`, `Componenti di calcolo del fondo`, `Valore`
- Original variable codes: `ACCANTONAMENTO_FINALE`, `CAPACITA_FISCALE`, `CONTRIBUTO_PICCOLI_COMUNI`, `CORRETTIVO_449DBIS`, `CORRETTIVO_450`, `DOTAZIONE_FINALE_FSC`, `DOTAZIONE_NETTA_FSC`, `FABBISOGNO_STANDARD`, `FONDO_FSC_STANDARD`, `FONDO_FSC_STORICO`, `FONDO_PEREQUATIVO`, `FONDO_STORICO`, `IMU_STANDARD`, `IMU_TASI_STANDARD`, `PERCENTUALE_STANDARD`, `POPOLAZIONE`, `QUOTA_DI_ALIMENTAZIONE`, `RISORSE_AGGIUNTIVE`, `RISORSE_ASILI_NIDO`, `RISORSE_ASILI_NIDO_FELS`, `RISORSE_SERVIZI_SOCIALI`, `RISORSE_SERVIZI_SOCIALI_FELS`, `RISORSE_TRASPORTO_STUD_DISABILI`, `RISORSE_TRASP_STUD_DISABILI_FELS`, `RISTORO_IMU_TASI`, `TASI_STANDARD`, `TOTALE_RIDUZIONI_RETTIFICHE`, `TOTALE_RISORSE_STORICHE`
- Coverage by period: 2026: 118/118
- Original definitions: `data/collection/civitas-2026-var-fsc-1-2026-it.dictionary.json`; SHA-256 `866f16816fd80e8447ad4b8a9b16bd06c2db1c47ec5356e1dfce47b1e074d9ab`.

Source: [civitas-2026-var-fsc-1-2026-it](https://www.opencivitas.it/portale/documents/20118/0/2026_VAR_FSC_1_2026_IT.csv/63988461-9ae1-ce7d-13f0-fab3c9c7b77a)

### civitas-2023-ind-istruz-01-it

Records: 6,726; associated municipalities: 118/118; periods: 2023.

Original OpenCivitas source fields and variable dictionary retained. Entity USERNAME is reconciled through the matching official workbook. Privacy/anomaly/blank values and functional-definition flags are retained without imputation. Budget appropriations, standard needs, output estimates and service counts require separate interpretation.

Staging file: `data/collection/civitas-2023-ind-istruz-01-it.rows.jsonl.gz`; SHA-256: `d24c8e95ee1bf02afeabfa3b8e00b6832f23cf6781461b1440839eb7ea8d71ba`.

- `2023_Ind_ISTRUZ_01_IT.csv` (5 fields): `USERNAME`, `Indicatore/Determinante`, `Valore`, `Anomalia`, `Privacy`
- Original variable codes: `COORD_OUT`, `COORD_SPESA`, `COSTO_LAVORO_PROAB`, `D03`, `DESCR_NON_VALUTABILE_OUT`, `DESCR_NON_VALUTABILE_SPESA`, `DIFF_OUT_PERC`, `DIPENDENTI_X1000AB`, `DUMMY_ISTALTR_GP_ASSOC`, `DUMMY_ISTDISA_GP_ASSOC`, `DUMMY_ISTINFA_GP_ASSOC`, `DUMMY_ISTPRSE_GP_ASSOC`, `DUMMY_ISTREFE_GP_ASSOC`, `DUMMY_ISTTRAS_GP_ASSOC`, `FL_DIF_OUTPUT_MAG_0`, `FL_DIF_OUTPUT_MIN_0`, `FL_DIF_SPESA_MAG_0`, `FL_DIF_SPESA_MIN_0`, `FL_NO_VALUTABILE`, `FL_SPESA_MENO_OUT_MENO`, `FL_SPESA_MENO_OUT_PIU`, `FL_SPESA_PIU_OUT_MENO`, `FL_SPESA_PIU_OUT_PIU`, `FST_RIPROPORZIONATO_BI`, `FST_RIPROPORZIONATO_BI_PROAB`, `F_D03_SCOST`, `F_INTERCEPT`, `F_INV_POP_3_14_MEAN`, `F_M_AL_COMUNALI_P_MEAN`, `F_M_AL_DISABILI_COMU_P_MEAN`, `F_M_AL_PRIVATE_P`, `F_M_PASTI_TOT_P_MEAN`, `F_M_PREPOST_ESTIVI_P`, `F_M_SCUOLE_STAT_COM_N_P`, `F_M_SPAZI_TOT_P`, `F_M_TRASPORTO_UTENTI_P`, `F_M_TRASP_DISABILI_P_MEAN`, `F_QUOTA_CLTP_PRIMSEC1`, `INCIDENZA_POP_3_14_PERC`, `MOTIVO_RECUPERO_SPESA`, `M_AL_COMUNALI_PERC`, `M_AL_DISABILI_COMU_PERC`, `M_AL_PRIVATE_PERC`, `M_PREPOST_ESTIVI_PERC`, `M_REFEZIONE_PERC`, `M_SPAZI_TOT_P`, `M_TRASPORTO_DISABILI_PERC`, `M_TRASPORTO_UTENTI_PERC`, `NON_VALUTABILE_OUT`, `NON_VALUTABILE_SPESA`, `OUT_COMPOSITO_STORICO_X1000AB`, `POP_3_14_N_XSCUOLA`, `POSIZIONE_OUTPUT_PERC`, `POSIZIONE_SPESA_PERC`, `QUOTA_CLTP_PRIMSEC1_PERC`, `SPESA_STORICA`, `SPESA_STORICA_PROAB`
- Coverage by period: 2023: 118/118
- Original definitions: `data/collection/civitas-2023-ind-istruz-01-it.dictionary.json`; SHA-256 `3fd1960da25f7c84b8d81fc6f518afe7ec1681c6c2370509d7d579a4747c7e6d`.

Source: [civitas-2023-ind-istruz-01-it](https://www.opencivitas.it/portale/documents/20118/0/2023_Ind_ISTRUZ_01_IT.csv/c9b4ea9e-d2c1-9ae4-3587-ceea43985da3)

### civitas-2023-ind-tot-01-it

Records: 9,794; associated municipalities: 118/118; periods: 2023.

Original OpenCivitas source fields and variable dictionary retained. Entity USERNAME is reconciled through the matching official workbook. Privacy/anomaly/blank values and functional-definition flags are retained without imputation. Budget appropriations, standard needs, output estimates and service counts require separate interpretation.

Staging file: `data/collection/civitas-2023-ind-tot-01-it.rows.jsonl.gz`; SHA-256: `f60b43c91df3e97bbf6e1acc6292522d6791287764f0905a232fb1212264c84a`.

- `2023_Ind_TOT_01_IT.csv` (5 fields): `USERNAME`, `Indicatore/Determinante`, `Valore`, `Anomalia`, `Privacy`
- Original variable codes: `COORD_OUT`, `COORD_SPESA`, `COSTO_LAVORO_PROAB`, `D03`, `DESCR_NON_VALUTABILE_OUT_TOT`, `DESCR_NON_VALUTABILE_SPESA_TOT`, `DIFF_OUT_PERC_TOT`, `DIPENDENTI_X1000AB`, `FL_DIF_OUTPUT_MAG_0`, `FL_DIF_OUTPUT_MIN_0`, `FL_DIF_SPESA_MAG_0`, `FL_DIF_SPESA_MIN_0`, `FL_NO_CONFRONTO_OUT`, `FL_NO_CONFRONTO_SPESA`, `FL_NO_VALUTABILE`, `FL_SPESA_MENO_OUT_MENO`, `FL_SPESA_MENO_OUT_PIU`, `FL_SPESA_PIU_OUT_MENO`, `FL_SPESA_PIU_OUT_PIU`, `FST_RIPROPORZIONATO_BI`, `FST_RIPROPORZIONATO_BI_PROAB`, `F_ABIT_DISP_MEAN_C`, `F_ABIT_LOC_E_ALTRI_UTIL_MEAN_C`, `F_ADDETTI_I_P_MEAN`, `F_ALUNNI_HANDICAP_MEAN`, `F_ASILO_NIDO`, `F_CONTESTO`, `F_COSTO_LAV_SCOST_AMM`, `F_COSTO_LAV_SCOST_IST`, `F_COSTO_LAV_SCOST_POL`, `F_COSTO_LAV_SCOST_TERR`, `F_COSTO_LAV_SCOST_VIAB`, `F_DENSITA_MEAN`, `F_DEPRIVAZIONE_MEAN`, `F_DIFFERENZIATA`, `F_DIFF_PENDOLARI_N_P`, `F_DISECONOMIA_SCALA`, `F_DISTANZA`, `F_DUMMY_ARMATO`, `F_DUMMY_STRUTTURE`, `F_FASCIA_SON`, `F_GESTIONE`, `F_IMMOBILI_TOTALI_P`, `F_INCID_15_64_MEAN`, `F_INCID_65_74_MEAN`, `F_INCID_OLTRE_75_MEAN`, `F_INCID_POP_STRA_MEAN`, `F_INFRASTRUTTURE`, `F_INTERCEPT_IMM_VET`, `F_INTERCEPT_POP_3_14`, `F_INTERCEPT_TONN_RIF`, `F_ISTAT_GENER_STRADE_KM_MEAN`, `F_ISTAT_SUPERF_TOTALE_KMQ_P`, `F_MERCATI_P_MEAN`, `F_M_AL_COMUNALI_P_MEAN`, `F_M_AL_DISABILI_COMU_P_MEAN`, `F_M_AL_PRIVATE_P`, `F_M_INCIDENTI_P`, `F_M_PASTI_TOT_P_MEAN`, `F_M_PREPOST_ESTIVI_P`, `F_M_QUERELE_P`, `F_M_SCUOLE_STAT_COM_N_P`, `F_M_SPAZI_TOT_P`, `F_M_TRASPORTO_UTENTI_P`, `F_M_TRASP_DISABILI_P_MEAN`, `F_OUTPUT_ALTRI_ESOGENI_P`, `F_OUTPUT_ST_CON_P_LUCE_C`, `F_P4_P3_Q`, `F_POP_C`, `F_PRESENZE_COMUNE_MEAN`, `F_PREZZO_VEIC_FINALE_POL_SCOST`, `F_QUOTA_CLTP_PRIMSEC1`, `F_SISMICO_RISCHIO_ALTO`, `F_STALLI_P_MEAN`, `F_TIPRACCOLTA`, `F_VALORE_BENCHMARK_ORE`, `F_VALORE_BENCHMARK_UT`, `POSIZIONE_OUTPUT_PERC_TOT`, `POSIZIONE_SPESA_PERC_TOT`, `SERV_NO_VALUT_OUT_TOT`, `SERV_NO_VALUT_SPESA_TOT`, `SPESA_STORICA`, `SPESA_STORICA_PROAB`
- Coverage by period: 2023: 118/118
- Original definitions: `data/collection/civitas-2023-ind-tot-01-it.dictionary.json`; SHA-256 `070083134d2eedb8119e57b95346c972f2caac95bfa5eabb98fb9c5baa9b84ba`.

Source: [civitas-2023-ind-tot-01-it](https://www.opencivitas.it/portale/documents/20118/0/2023_Ind_TOT_01_IT.csv/1086db31-bf42-8678-0520-c77eacce2a23)

### civitas-2023-ind-terr-viab-01-it

Records: 8,968; associated municipalities: 118/118; periods: 2023.

Original OpenCivitas source fields and variable dictionary retained. Entity USERNAME is reconciled through the matching official workbook. Privacy/anomaly/blank values and functional-definition flags are retained without imputation. Budget appropriations, standard needs, output estimates and service counts require separate interpretation.

Staging file: `data/collection/civitas-2023-ind-terr-viab-01-it.rows.jsonl.gz`; SHA-256: `0482e1c8a5607a80f34b8bb5d3578b6952fa3e9df069155cb127089a0c92ad75`.

- `2023_Ind_TERR_VIAB_01_IT.csv` (5 fields): `USERNAME`, `Indicatore/Determinante`, `Valore`, `Anomalia`, `Privacy`
- Original variable codes: `A5_X1000AB`, `COORD_OUT`, `COORD_SPESA`, `COSTO_LAVORO_PROAB`, `COSTO_LAVORO_TERR_PROAB`, `COSTO_LAVORO_VIAB_PROAB`, `D0300004`, `D0300007`, `D03_VET`, `DESCR_NON_VALUTABILE_OUT`, `DESCR_NON_VALUTABILE_SPESA`, `DIFF_OUT_PERC`, `DIPENDENTI_TERR_X1000AB`, `DIPENDENTI_VIAB_X1000AB`, `DIPENDENTI_X1000AB`, `DUMMY_TERR_ASSOCIATA`, `DUMMY_VIAB_ASSOCIATA`, `FL_DIF_OUTPUT_MAG_0`, `FL_DIF_OUTPUT_MIN_0`, `FL_DIF_SPESA_MAG_0`, `FL_DIF_SPESA_MIN_0`, `FL_NO_VALUTABILE`, `FL_SISMA_1`, `FL_SPESA_MENO_OUT_MENO`, `FL_SPESA_MENO_OUT_PIU`, `FL_SPESA_PIU_OUT_MENO`, `FL_SPESA_PIU_OUT_PIU`, `FST_RIPROPORZIONATO_BI`, `FST_RIPROPORZIONATO_BI_PROAB`, `F_ABIT_DISP_MEAN_C`, `F_ABIT_LOC_E_ALTRI_UTIL_MEAN_C`, `F_BASE`, `F_COSTO_LAV_TERR_SCOST`, `F_COSTO_LAV_VIAB_SCOST`, `F_FL_SISMA_1`, `F_INV_IMM`, `F_OUTPUT_ST_CON_P_LUCE_C`, `F_P4_P3_Q`, `F_POP_C`, `F_PRESENZE_MEAN_C`, `F_STRADE_KM_MEAN_C`, `F_SUPERF_KMQ_MEAN_C`, `ISTAT_GENER_STRADE_INTER_KM`, `ISTAT_SUPERF_TOTALE_KMQ`, `M27_28_X1000AB`, `M34_X1000AB`, `M35_X1000AB`, `M36_X1000AB`, `M37_X1000AB`, `M38_X1000AB`, `M39_X1000AB`, `M40_X1000AB`, `M45_X1000AB`, `M46_X1000AB`, `M47_X1000AB`, `M48_X1000AB`, `M49_50_X1000AB`, `M51_X1000AB`, `M52_X1000AB`, `M53_X1000AB`, `M54_X1000AB`, `MOTIVO_RECUPERO_SPESA_VET`, `NON_VALUTABILE_OUT`, `NON_VALUTABILE_SPESA`, `OUT_COMPOSITO_STORICO_X1000AB`, `PERC_ABIT_DISP`, `PERC_ABIT_LOC_E_ALTRI_UTIL`, `PERC_AREE_VERDI`, `PERC_PISTE_CICLABILI`, `PERC_POP_FRANE`, `POPOLAZIONE_X1000IMM`, `POSIZIONE_OUTPUT_PERC`, `POSIZIONE_SPESA_PERC`, `PRESENZE_COMUNE_X1000AB`, `SPESA_STORICA`, `SPESA_STORICA_PROAB`
- Coverage by period: 2023: 118/118
- Original definitions: `data/collection/civitas-2023-ind-terr-viab-01-it.dictionary.json`; SHA-256 `e7f707ddc4b6f10229c38bab610831d48621572bf135c30403448cdf3bf14b9c`.

Source: [civitas-2023-ind-terr-viab-01-it](https://www.opencivitas.it/portale/documents/20118/0/2023_Ind_TERR_VIAB_01_IT/5565663a-6434-27e1-1b7a-273e87b02635)

### civitas-2023-ind-socnid-01-it

Records: 10,266; associated municipalities: 118/118; periods: 2023.

Original OpenCivitas source fields and variable dictionary retained. Entity USERNAME is reconciled through the matching official workbook. Privacy/anomaly/blank values and functional-definition flags are retained without imputation. Budget appropriations, standard needs, output estimates and service counts require separate interpretation.

Staging file: `data/collection/civitas-2023-ind-socnid-01-it.rows.jsonl.gz`; SHA-256: `909357a5fbc3d069eb86cf5fde609116862a9d8440a1f0f7f7069172d80faf22`.

- `2023_Ind_SOCNID_01_IT.csv` (5 fields): `USERNAME`, `Indicatore/Determinante`, `Valore`, `Anomalia`, `Privacy`
- Original variable codes: `ALUNNI_HANDICAP_MEAN_X1000AB`, `COORD_OUT`, `COORD_SPESA`, `COPERTURA_NID_NEW`, `COSTO_LAVORO_PROAB`, `COSTO_LAVORO_SON`, `DEPRIVAZIONE_MEAN`, `DESCR_NON_VALUTABILE_OUT`, `DESCR_NON_VALUTABILE_SPESA`, `DIFF_OUT_PERC`, `DIPENDENTI_X1000AB`, `DUMMY_NECRO_ASSOCIATA`, `DUMMY_SOC_ASSOCIATA`, `DUMMY_STRUTTURE`, `EDUCATORI_TOT_C`, `FG_NID_OPENCIVITAS_XLS`, `FL_DIF_OUTPUT_MAG_0`, `FL_DIF_OUTPUT_MIN_0`, `FL_DIF_SPESA_MAG_0`, `FL_DIF_SPESA_MIN_0`, `FL_NO_VALUTABILE`, `FL_SPESA_MENO_OUT_MENO`, `FL_SPESA_MENO_OUT_PIU`, `FL_SPESA_PIU_OUT_MENO`, `FL_SPESA_PIU_OUT_PIU`, `FST_RIPROPORZIONATO_BI`, `FST_RIPROPORZIONATO_BI_PROAB`, `FST_RIPR_BI_NID`, `FST_RIPR_BI_NID_PROAB`, `FST_RIPR_BI_SOC`, `FST_RIPR_BI_SOC_PROAB`, `F_ALUNNI_HANDICAP_MEAN`, `F_ASILO_NIDO`, `F_DEPRIVAZIONE_MEAN`, `F_DUMMY_STRUTTURE`, `F_FASCIA`, `F_INCID_15_64_MEAN`, `F_INCID_65_74_MEAN`, `F_INCID_OLTRE_75_MEAN`, `F_INCID_POP_STRA_MEAN`, `F_VALORE_BENCHMARK_ORE`, `F_VALORE_BENCHMARK_UT`, `INCID_15_64_MEAN`, `INCID_65_74_MEAN`, `INCID_OLTRE_75_MEAN`, `INCID_POP_STRA_MEAN`, `IND_POP02_SU_POPTOT_PCT`, `M12_SOC24_P_X1000AB`, `M15_SOC24_P_X1000AB`, `M18_SOC24_P_X1000AB`, `M21_SOC24_P_X1000AB`, `M24_SOC24_P_X1000AB`, `M27_SOC24_P_X1000AB`, `M30_SOC24_P_X1000AB`, `M35_SOC24_P_X1000AB`, `M36_SOC24_P_X1000AB`, `M37_SOC24_P_X1000AB`, `M38_SOC24_P_X1000AB`, `M39_SOC24_P_X1000AB`, `M40_SOC24_P_X1000AB`, `M41_SOC24_P_X1000AB`, `M44_SOC24_P_X1000AB`, `M47_SOC24_P_X1000AB`, `M50_SOC24_P_X1000AB`, `M53_SOC24_P_X1000AB`, `M56_SOC24_P_X1000AB`, `M59_SOC24_P_X1000AB`, `MOTIVO_RECUPERO_SPESA`, `NON_VALUTABILE_OUT`, `NON_VALUTABILE_SPESA`, `OMI_LIVELLO_AFFITTI_MEAN`, `PERC_COPERTURA_SOC`, `POSIZIONE_OUTPUT_PERC`, `POSIZIONE_SPESA_PERC`, `REDDITO_MEAN`, `SPESA_STORICA`, `SPESA_STORICA_NID`, `SPESA_STORICA_NID_PROAB`, `SPESA_STORICA_PROAB`, `SPESA_STORICA_SOC`, `SPESA_STORICA_SOC_PROAB`, `SUPERF_TOT_C`, `UTENTI_ESTERNA_C`, `UTENTI_LATTANTI_C`, `UTENTI_PARZIALE_C`, `UTENTI_REFEZIONE_C`, `UTENTI_VOUCHER_C`
- Coverage by period: 2023: 118/118
- Original definitions: `data/collection/civitas-2023-ind-socnid-01-it.dictionary.json`; SHA-256 `12bafa3323b7cd80038605f0b3ff885292fc54961e4f7b165cbe547bf8132aa3`.

Source: [civitas-2023-ind-socnid-01-it](https://www.opencivitas.it/portale/documents/20118/0/2023_Ind_SOCNID_01_IT/cfedc2c9-b05d-07cb-da97-decaf9190f5f)

### civitas-2022-ind-fc80socnid-1

Records: 10,266; associated municipalities: 118/118; periods: 2022.

Original OpenCivitas source fields and variable dictionary retained. Entity USERNAME is reconciled through the matching official workbook. Privacy/anomaly/blank values and functional-definition flags are retained without imputation. Budget appropriations, standard needs, output estimates and service counts require separate interpretation.

Staging file: `data/collection/civitas-2022-ind-fc80socnid-1.rows.jsonl.gz`; SHA-256: `1fccc531a2a766dc99bb13a1beb1bbbbd69ed31169a95a3e8f5b2fc64195c738`.

- `2022_Ind_FC80SOCNID_1.csv` (5 fields): `USERNAME`, `Indicatore/Determinante`, `Valore`, `Anomalia`, `Privacy`
- Original variable codes: `ALUNNI_HANDICAP_MEAN_X1000AB`, `COORD_OUT`, `COORD_SPESA`, `COPERTURA_NID_NEW`, `COSTO_LAVORO_PROAB`, `COSTO_LAVORO_SON`, `DEPRIVAZIONE_MEAN`, `DESCR_NON_VALUTABILE_OUT`, `DESCR_NON_VALUTABILE_SPESA`, `DIFF_OUT_PERC`, `DIPENDENTI_X1000AB`, `DUMMY_NECRO_ASSOCIATA`, `DUMMY_SOC_ASSOCIATA`, `DUMMY_STRUTTURE`, `EDUCATORI_TOT_C`, `FG_NID_OPENCIVITAS_XLS`, `FL_DIF_OUTPUT_MAG_0`, `FL_DIF_OUTPUT_MIN_0`, `FL_DIF_SPESA_MAG_0`, `FL_DIF_SPESA_MIN_0`, `FL_NO_VALUTABILE`, `FL_SPESA_MENO_OUT_MENO`, `FL_SPESA_MENO_OUT_PIU`, `FL_SPESA_PIU_OUT_MENO`, `FL_SPESA_PIU_OUT_PIU`, `FST_RIPROPORZIONATO_BI`, `FST_RIPROPORZIONATO_BI_PROAB`, `FST_RIPR_BI_NID`, `FST_RIPR_BI_NID_PROAB`, `FST_RIPR_BI_SOC`, `FST_RIPR_BI_SOC_PROAB`, `F_ALUNNI_HANDICAP_MEAN`, `F_ASILO_NIDO`, `F_DEPRIVAZIONE_MEAN`, `F_DUMMY_STRUTTURE`, `F_FASCIA`, `F_INCID_15_64_MEAN`, `F_INCID_65_74_MEAN`, `F_INCID_OLTRE_75_MEAN`, `F_INCID_POP_STRA_MEAN`, `F_VALORE_BENCHMARK_ORE`, `F_VALORE_BENCHMARK_UT`, `INCID_15_64_MEAN`, `INCID_65_74_MEAN`, `INCID_OLTRE_75_MEAN`, `INCID_POP_STRA_MEAN`, `IND_POP02_SU_POPTOT_PCT`, `M12_SOC23_P_X1000AB`, `M15_SOC23_P_X1000AB`, `M18_SOC23_P_X1000AB`, `M21_SOC23_P_X1000AB`, `M24_SOC23_P_X1000AB`, `M27_SOC23_P_X1000AB`, `M30_SOC23_P_X1000AB`, `M35_SOC23_P_X1000AB`, `M36_SOC23_P_X1000AB`, `M37_SOC23_P_X1000AB`, `M38_SOC23_P_X1000AB`, `M39_SOC23_P_X1000AB`, `M40_SOC23_P_X1000AB`, `M41_SOC23_P_X1000AB`, `M44_SOC23_P_X1000AB`, `M47_SOC23_P_X1000AB`, `M50_SOC23_P_X1000AB`, `M53_SOC23_P_X1000AB`, `M56_SOC23_P_X1000AB`, `M59_SOC23_P_X1000AB`, `MOTIVO_RECUPERO_SPESA`, `NON_VALUTABILE_OUT`, `NON_VALUTABILE_SPESA`, `OMI_LIVELLO_AFFITTI_MEAN`, `PERC_COPERTURA_SOC`, `POSIZIONE_OUTPUT_PERC`, `POSIZIONE_SPESA_PERC`, `REDDITO_MEAN`, `SPESA_STORICA`, `SPESA_STORICA_NID`, `SPESA_STORICA_NID_PROAB`, `SPESA_STORICA_PROAB`, `SPESA_STORICA_SOC`, `SPESA_STORICA_SOC_PROAB`, `SUPERF_TOT_C`, `UTENTI_ESTERNA_C`, `UTENTI_LATTANTI_C`, `UTENTI_PARZIALE_C`, `UTENTI_REFEZIONE_C`, `UTENTI_VOUCHER_C`
- Coverage by period: 2022: 118/118
- Original definitions: `data/collection/civitas-2022-ind-fc80socnid-1.dictionary.json`; SHA-256 `116aae72c0f249e92e75d4b912a623604d856832fb01c11119481f7aab664761`.

Source: [civitas-2022-ind-fc80socnid-1](https://www.opencivitas.it/portale/documents/20118/0/2022_Ind_FC80SOCNID_1/7253fba5-65ef-c16e-534b-7dabbf9b38b0)

### province-works-notices

Records: 11; associated municipalities: 6/118; periods: undated_publisher_layer.

Actual public provincial GeoJSON retained locally with original notices, date text and coordinates. It mixes road notices with other construction projects and includes expired date ranges. No current road closure, automatic validity interval or exhaustive works inventory inferred. Specific reuse terms were not supplied; local collection is separate from public redistribution.

Staging file: `data/collection/province-works-notices.rows.jsonl.gz`; SHA-256: `594630fac2fdce527b2ac8cc06e5cfbadd049daed6d297d1fd30a30e1ea012d9`.

- `features` (4 fields): `source_feature_index`, `type`, `properties`, `geometry`
- Coverage by period: undated_publisher_layer: 6/118

Source: [province-works-notices](https://www.provincia.avellino.it/cprvnvll/images/OpenData/OrdinanzeeCantieri/OrdinanzeeCantieri.json)

## Failed or empty collections

- `arpac-surface-water-2026`: No matching records returned for this geography/period. Source artifacts remain inspectable.
- `siat-cultural-layer-15`: ValueError: Expected complete GeoJSON FeatureCollection Source artifacts remain inspectable. Resolved using: siat-cultural-lines-15.
- `siat-cultural-layer-16`: ValueError: Expected complete GeoJSON FeatureCollection Source artifacts remain inspectable. Resolved using: siat-cultural-lines-16.
