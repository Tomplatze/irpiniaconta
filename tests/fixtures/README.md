# Institutional test fixtures

`istat/` contains unmodified official ISTAT artifacts acquired on 12 October 2026, with their acquisition sidecars. These are real source data used only to verify parsing; the tests that alter their contents write the altered copies to temporary directories.

Publisher and attribution: ISTAT. Default reuse terms: CC BY 4.0, unless otherwise stated. Legal source: https://www.istat.it/note-legali/ . Exact download URLs, SHA-256 hashes and the agriculture read-only POST request are recorded in the sidecars and `docs/evidence/istat_*.md`.

The full national municipality registry is retained because replacing it with a handcrafted list would weaken the canonical geography test. Agriculture and demographics are the actual Avellino provincial extracts.
