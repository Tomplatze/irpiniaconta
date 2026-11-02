# ISPRA municipal soil consumption: verified integration

Verification date: **12 October 2026**. Publisher: ISPRA / SNPA. Adapter: `etl/adapters/ispra_soil.py`.

## Official access and annuality

The [official data landing page](https://www.isprambiente.gov.it/it/attivita/suolo-e-territorio/suolo/il-consumo-di-suolo/i-dati-sul-consumo-di-suolo) links to the [national, provincial and municipal XLSX extract](https://www.isprambiente.gov.it/it/attivita/suolo-e-territorio/suolo/il-consumo-di-suolo/consumo_di_suolo_estratto_dati_2025_anni_2006_2024.xlsx). Anonymous download returned HTTP 200 and a valid Excel workbook, 1,725,183 bytes. SHA-256: `8eca417fc871726f4adc32309538a81d9ba8ff7c4e2182ed92e3b989411d17ab`.

The report edition is **2025**; its latest observation year is **2024**. The sheet `Comuni_2006_2024` explicitly labels the columns with 2024. Do not label these measurements as observations for 2025. The [official preliminary 2025 notice](https://www.isprambiente.gov.it/it/news/consumo-di-suolo-condivisione-dei-dati-preliminari-2025) states that definitive 2025 data are expected at the end of October 2026. Preliminary data require registration and are excluded from this integration. The verified source snapshot is pinned; the adapter does not claim to discover future releases automatically.

## Licence and attribution

ISPRA's [soil monitoring methodology page](https://www.isprambiente.gov.it/it/attivita/suolo-e-territorio/suolo/il-consumo-di-suolo/la-misura-del-consumo-di-suolo) explicitly declares **CC BY 3.0 IT** for the complete soil-consumption data and derived indicators and points to the data landing page. This is the publisher's general declaration for this dataset family; the ArcGIS layer copyright field is empty and is not used as licence evidence. The declaration page was downloaded, preserved and checked by the adapter. Licence text: [Creative Commons Attribution 3.0 Italy](https://creativecommons.org/licenses/by/3.0/it/).

Use attribution to **ISPRA / SNPA, Consumo di suolo, edition 2025, observations 2024** with the landing-page and licence links. Normalization and provincial filtering are modifications by Atlante Irpinia. The prototype keeps the source metadata and attribution links visible in its catalog.

## Schema and normalization

| Official column | Normalized indicator | Unit | Meaning |
| --- | --- | --- | --- |
| `PRO_COM` | municipality code | six-digit text | Official ISTAT municipal code; leading zero restored. |
| `Suolo consumato 2024 [ettari]` | `soil_consumed_ha` | ha | Total artificial land surface observed in 2024. |
| `Suolo consumato 2024 [%]` | `soil_consumed_pct` | % | Artificial surface divided by total municipal territorial surface. |
| `Incremento netto 2023-2024 [ettari]` | `soil_net_change_ha` | ha | Increase in consumed surface minus restored land between 2023 and 2024. |

The official `Descrizione_campi` worksheet provides the definitions and units. The adapter filters codes beginning with `064`, verifies `Nome_Provincia = Avellino`, rejects duplicate codes and schema changes, and requires 118 municipal rows. Codes are not assumed to form a contiguous sequence: the current list extends to `064121` because retired municipality codes are absent. Null, suppression and real zero are distinct; a negative net-change value is valid and retained. Floating-point workbook precision is retained, with presentation rounding delegated to the UI.

## Real verification results

- **118 municipality codes**, **354 observations**, **354 observed values**, **0 missing or suppressed values** in the acquired extract for the three chosen indicators.
- The official [ArcGIS municipal layer](https://sinacloud.isprambiente.it/arcgisina/rest/services/sina_consumo_suolo/Statistiche_consumo_suolo_2025/FeatureServer/1) was separately downloaded as JSON metadata. An anonymous query with `cod_prov = 64`, `returnGeometry = false` returned 118 rows, without a transfer-limit flag. Both artifacts are preserved.
- Fields `pro_com_t`, `csuolo1_24`, `csuolo4_24`, `csuolo8_24` cross-check the workbook's code, hectares, percentage and annual net change. **All 354 values matched within 0.005**, the API's two-decimal rounding tolerance. The canonical import uses XLSX because its percentage values preserve greater precision.
- `measurement(0)` remains observed zero; `measurement(None)` remains missing null; `measurement('..')` remains suppressed null; `measurement(-0.67)` retains its observed negative value. Non-finite values and unexpected textual measurements are rejected.
- The offline adapter replay succeeded with matching SHA-256 records. HTTP status, resolved URL, content type, byte size, acquisition time and SHA-256 are recorded in `data/raw/ispra_*.acquisition.json`.

No source-access blocker was found for this verified annuality. Cross-source reconciliation against the authoritative ISTAT registry and common quality checks are performed by the shared ingestion pipeline; the ISPRA code-prefix filter alone does not replace those checks.
