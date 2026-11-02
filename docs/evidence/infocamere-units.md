# InfoCamere municipal local-unit verification

Status: **blocked for Avellino municipal comparisons**, verified 12 October 2026. No local-unit values are loaded, and unavailable municipalities are never represented as zero.

## The supplied lead is a Tuscany dataset

The [dati.gov.it record d92d4eb9-077e-4c05-a05e-fa833aabd490](https://www.dati.gov.it/node/view-dataset/dataset?id=d92d4eb9-077e-4c05-a05e-fa833aabd490) is **Imprese e unità locali InfoCamere 2025**, published by **Regione Toscana**, not a national municipal distribution. It links to [Tuscany package e3879a61-c73b-4457-a1b7-f2720eb8956a](https://dati.toscana.it/dataset/e3879a61-c73b-4457-a1b7-f2720eb8956a).

The browsed Tuscany landing page returned 403 in the research browser. However, its public [CKAN package API](https://dati.toscana.it/api/3/action/package_show?id=e3879a61-c73b-4457-a1b7-f2720eb8956a) and the actual [municipal 2025 CSV distribution](https://dati.toscana.it/dataset/e3879a61-c73b-4457-a1b7-f2720eb8956a/resource/f5e43d7d-21ed-4d30-aa2d-fce7dd421d0c/download/unitalocali2025.csv) were downloaded successfully with HTTP 200. Thus this is a **coverage blocker**, not a claimed unavailable file.

## Actual downloaded file

- 388,188 bytes; SHA-256 `66253cdfad15955f29cd3b157a54c88bd8c8fd660837ccda68e355509aeff4f2`.
- Retrieved at `2026-10-12T14:03:35.335074+00:00`.
- CSV, **comma** delimiter, decoded as Windows-1252 (strict UTF-8 fails).
- 4,738 rows, 277 municipal codes including unassigned province-level `000` municipal entries.
- Only province codes `045`, `046`, `047`, `048`, `049`, `050`, `051`, `052`, `053`, `100` occur: Tuscany.
- Rows and municipal codes beginning `064`: **0**.
- Actual headers: `Anno,Cod_Istat_Provincia,Provincia,Cod_Istat_Comune,Comune ,Cod_Sezione,Sezione,UL_Attive,UL_ArtigianeAttive`.

The Tuscany schema is verified. The schema, observation period, coverage and reuse licence of a prospective **Avellino municipal** export remain **unverified**. The adapter validates the example, reports the geographic blocker, and returns no observations. It includes a named-column normalization parser that selects exact six-digit `064` codes and sums disjoint ATECO sections; changed coverage requires manual licence and semantic review before import. This parser is a future integration seam, not evidence of an acquired Avellino dataset.

## Conflicting licence metadata

The national catalog attaches [CC BY 4.0](https://w3id.org/italia/controlled-vocabulary/licences/A21_CCBY40) to the municipal resource, but the downloaded Tuscany CKAN package declares `license_id: cc-by-sa`, with `license_url: http://www.opendefinition.org/licenses/cc-by-sa`. The discrepancy is preserved in the prototype catalog. It is an additional unresolved reuse issue; the prototype does not silently choose the less restrictive identifier.

## Irpinia and national sources checked

The [CCIAA Irpinia Sannio statistical-information page](https://www.irpiniasannio.camcom.it/informazione-statistica) confirms that Stockview provides municipal statistics, whereas Movimprese's free web data are by province. Its current [public dashboard](https://public.tableau.com/app/profile/economia.territoriale/viz/EconomiaIrpiniaSannio/Inumerichiavedeltrimestre?publish=yes) is linked by the institution, but a reusable municipal local-unit distribution and matching licence were not verified.

The [CCIAA quarterly-bulletins page](https://www.irpiniasannio.camcom.it/valirsannio/attivita/informazione-economica/bollettini-trimestrali) offers provincial bulletins through Q2 2026 and instructs municipal administrations to request their own municipal reports. This shows a possible acquisition path, not a currently reusable bulk dataset. No email or request was sent.

[InfoCamere Movimprese](https://www.infocamere.it/movimprese) states that its online tables cover provinces, regions and Italy. Its [published usage conditions](https://www.infocamere.it/dam/jcr:e9da8e0a-5e8b-49d7-bf3a-dc5f5ea86d3b/Movimprese%20-%20Condizioni%20di%20utilizzo.2025-04-30-17-11-02.pdf) permit use and dissemination with attribution. Those conditions belong to Movimprese downloads and do not establish the licence of a future Stockview municipal export. National open-data localizations published by CCIAA Marche also provide provincial coverage; their municipal distributions cover Marche. Neither may be relabelled as 118 municipal local-unit observations.

## Required unblock

Obtain an official downloadable/exported distribution covering all 118 Avellino municipalities, with ISTAT codes, reference date, measure definitions, treatment of headquarters versus local units, ATECO classification and an explicit reuse licence. The acquisition should distinguish **active local units**, **registered local units**, **headquarters**, and **active localizations** (headquarters plus units), which are not interchangeable measures. Confirm whether sections are disjoint and whether total rows are present to prevent double counting. Then update the pinned adapter endpoint, validate it against the municipality register and document the new artefact.

Raw catalog and example CSV snapshots plus acquisition sidecars remain under `data/raw/infocamere-*` as evidence only; the executable blocked adapter can be replayed offline. This is a bounded verification result, not a claim that municipal data do not exist anywhere.
