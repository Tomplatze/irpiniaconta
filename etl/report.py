"""Generate a factual source inventory from the hash-verified normalized acquisition."""
from pathlib import Path
from etl.pipeline import ROOT,replay_snapshot
from etl.registry import load_scope


def cell(value:object) -> str:
    """Keep original source fields safe inside Markdown table cells."""
    return str(value or '—').replace('|','\\|').replace('\n',' ')


def generate() -> Path:
    """Report measured integration scope without interpreting a page check as data verification."""
    _,results,report=replay_snapshot(ROOT/'data/snapshot.json')
    scope=load_scope();datasets={row.metadata['id']:row for row in results}
    ready=[row for row in results if row.metadata['status']=='ready']
    lines=['# Source inventory — prototype 0.2','',f"Generated from verified snapshot run `{report['run_id']}`; completed {report['completed_at']}.",'',
      f"The catalogue contains {len(scope['sources'])} scope items. {len(ready)} are integrated; {sum(source['adapter'] is None for source in scope['sources'])} have no implemented adapter, and {sum(source['adapter'] is not None and datasets[source['dataset_id'] or source['id']].metadata['status']!='ready' for source in scope['sources'])} executable adapters currently stop without publishing values. Unimplemented items are development gaps, not evidence that an institutional dataset cannot be integrated. HTTP reachability checks do not establish licensing, format validity, timeliness or municipal coverage.",'',
      '## Imported distributions','', '| ID | Publisher / distribution | Format | Source periods | Numeric cells | Entities / associated | Reuse licence |','| --- | --- | --- | --- | ---: | ---: | --- |']
    for source in scope['sources']:
        result=datasets[source['dataset_id'] or source['id']];meta=result.metadata
        if meta['status']!='ready':continue
        periods=sorted({row.period for row in result.observations})
        period=periods[0] if len(periods)==1 else f'{periods[0]} to {periods[-1]}' if periods else meta['period']
        lines.append('| '+' | '.join(map(cell,[source['id'],f"[{meta['publisher']} — {source['title']}]({meta['landing_url']})",meta['format'],period,len(result.observations),f"{len(result.entities)} / {sum(row.municipality_code is not None for row in result.entities)}",meta['license']]))+' |')
    lines.extend(['','## All 81 scope items','', '| ID | Category / item | Integration state | Actual blocker or publication boundary |','| --- | --- | --- | --- |'])
    for source in scope['sources']:
        result=datasets[source['dataset_id'] or source['id']]
        state='Integrated' if result.metadata['status']=='ready' else 'Access/reuse review' if source['status']=='restricted' else 'Implemented adapter blocked' if source['adapter'] else 'Not implemented / requires verification'
        detail='Validated import; see original metadata, indicator-period coverage and acquisition artifacts.' if result.metadata['status']=='ready' else result.metadata['blocker']
        lines.append('| '+' | '.join(map(cell,[source['id'],f"[{source['title']}]({source['landing_url']})",state,detail]))+' |')
    lines.extend(['','## Interpretation boundaries','',
      '- ISTAT population 2026-01-01 is explicitly an estimate. Demographic balances 2021–2025 include a provisional 2025 release. Population at year end is a separate metric.',
      '- MEF tax years 2020–2024 contain different schemas. All published numeric amount/frequency columns are retained. Historical overall totals and frequencies are derived from eight exhaustive official income bins only when every input is present. Missing or suppressed inputs propagate to null. Mean income uses its own declaration frequency, not residents. Nominal euros are not inflation-adjusted.',
      '- ISPRA current stock is definitive 2024; the current workbook also provides source-defined annual/multiyear net-change intervals. Negative net change is legitimate restoration. No historical stock is reconstructed from the changes and no preliminary 2025 value is substituted.',
      '- Agriculture is the 2020 census, agricultural year 2019–2020, by holding headquarters. Only holdings and utilized agricultural area are imported. Crop, livestock and older-census adapters remain development work.',
      '- OpenCivitas imports four monetary indicators from the reviewed 2023 municipal functions release. This is not an imported complete budget or all service-level outputs. Specific RDF dataset terms declare CC BY 4.0; generic portal legal text differs.',
      '- PA Digitale includes funded applications with original status and identifiers. A/E statuses contribute to count and voucher totals; withdrawn records remain traceable. These are not amounts actually paid or unique project counts.',
      '- IPA counts registered entities of all published types by registered municipality, not only municipal administrations or service catchments. Public contact-person details are not imported.',
      '- MIM school years 2025/26 and 2026/27 use a bijective cadastral-to-ISTAT crosswalk from the official registry. Administrative school units and school headquarters are separate counts; neither is a verified building inventory.',
      '- Provincial JSON catalogues retain exact original fields. Exact repeated rows are removed; approximate duplicates and locality names are not guessed. Counts without listed records are null because catalogue completeness is not proven. Inventory observation vintages are unspecified; acquisition dates are not original construction/cataloguing dates.',
      '- Provincial roads remain provincial; no municipal road-length estimate is inferred. Provincial institute associations use original MIM headquarters identifiers; unresolved rows remain null.',
      '- Pharmacy records are filtered by published opening/closing validity at the export date. Counts include the source types, including branches/dispensaries. Reviewed predecessor Montoro codes map only current locations, retain original keys and do not alter historical statistics. Coordinates with mixed publisher/OSM provenance are not imported.',
      '- InfoCamere municipal Avellino units remain blocked: the verified public file covers Tuscany. A licensed Stockview Avellino export is needed. No request to another organization was sent.',
      '- SCIA current daily-grid help expressly prohibits reproduction, transfer and distribution on other websites. No climate values are imported. ERA5 also requires accepted CDS access terms and an explicit spatial aggregation method; it has no adapter yet.',
      '- ACI latest open distribution and CC BY 4.0 terms were identified, but a verified RAR/ODS parser and current municipal crosswalk remain unimplemented. No vehicle statistics are claimed.',
      '- Most remaining catalogue items need a real distribution, specific reuse verification, a parser and coverage tests. In particular complete budgets, appalti, coesione, crop/livestock breakdowns, spatial environment indicators, climate, paritarie, housing and transit are not delivered as numerical datasets.','',
      'Acquisition metadata, hashes and per-indicator/per-period quality are in `data/snapshot.json`; immutable full response bytes remain in local `data/raw/archive/`. Each source retains its failed attempts separately from last-valid publication.'])
    path=ROOT/'docs/SOURCE_INVENTORY.md';path.write_text('\n'.join(lines)+'\n');return path


if __name__=='__main__':print(generate())
