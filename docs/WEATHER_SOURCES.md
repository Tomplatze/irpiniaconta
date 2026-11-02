# Weather alternatives — real endpoint verification

Checked on 2026-10-13. This is source collection and validation, not published weather for the 118 municipalities. Full response/request hashes and HTTP evidence are in `data/weather-verification.json` and local `data/raw/`.

| Candidate | Actual historical test | Actual recent test | Access and reuse | Important limit |
| --- | --- | --- | --- | --- |
| [Open-Meteo historical API](https://open-meteo.com/en/docs/historical-weather-api) | 7 complete days, 2025-01-01 to 2025-01-07, temperature and precipitation | 7 complete days, 2026-09-27 to 2026-10-03 | No key used; data CC BY 4.0. [Free API terms](https://open-meteo.com/en/terms) restrict the free service to non-commercial use; advertising/promotional use needs a commercial-access review | ERA5 is a model/reanalysis grid, not a measurement at every town. ERA5-Land returned null precipitation; that sample was rejected, not filled with zero |
| [NASA POWER daily API](https://power.larc.nasa.gov/docs/services/api/temporal/daily/) | 7 complete days, 2025-01-01 to 2025-01-07, T2M and PRECTOTCORR | 7 complete days, 2026-09-27 to 2026-10-03 | Free public endpoint reached without a key. Retain NASA POWER and original source attribution using its [reference guide](https://power.larc.nasa.gov/docs/referencing/); do not invent a CC licence | Coarse grid represents spatial averages. Nearby municipalities can share the same cell; mountain elevation can differ substantially from its average |

Both endpoints actually returned finite temperature/rainfall values, the expected dates and units. Seven-day samples prove those requests were accessible; they do not prove uninterrupted availability, every historical year, accurate municipal representation or a future refresh.

Open-Meteo data rights and hosted-service access terms are separate. A CC BY data licence does not make commercial access to the hosted free endpoint unrestricted. NASA's original source policies and attribution must remain attached to any product publication; no messages were sent to either provider and no subscriptions or accounts were created.

[Meteostat](https://dev.meteostat.net/data.html) is another documented free-data candidate, currently untested here. Its current developer/legal pages declare CC BY 4.0 for redistributed datasets, whereas an older support page still mentions BY-NC. Station coverage, original providers and substitution of observations with model data need source-specific review before importing values. It is not marked ready merely from documentation.

## Geography collected

The actual [ISTAT 2026 generalized boundary archive](https://www.istat.it/notizia/confini-delle-unita-amministrative-a-fini-statistici-al-1-gennaio-2018-2/) was downloaded. Its original municipal DBF attributes reconcile exactly all 118 current ISTAT codes. The filtered original attributes are in `data/boundary-attributes-2026.csv`; ZIP hash, CRS and verification are in `data/geography-verification.json`. The actual ZIP has no CPG file: attributes were strictly decoded as UTF-8, consistent with the publisher documentation. No CRS, centroid or station association is guessed.

## Before municipal climate publication

Choose a declared representation method: a reviewed local station, a representative location, or a boundary-weighted grid aggregation. Validate all 118 mappings, altitude/grid limitations, temporal completeness and missing-value semantics. Keep source model and daily timezone consistent across history. Precipitation totals require complete days; averages cannot silently ignore missing dates.

Public indicators should be few: annual average temperature and annual rainfall, with a simple history. A long-term climate normal requires a sufficiently long comparable period. Current forecasts belong to a separate weather context and must not be mixed into historic climate statistics. No climate observations from these candidates have been inserted into the municipal database yet.

Configuration is centralized in `config/weather-candidates.json`. Run `.venv/bin/python -m etl.weather_probe` for explicit live verification, or add `--offline` to revalidate retained responses for the same recent window. This does not install an automation. A date-dependent recent sample must be freshly acquired if its window changes.
