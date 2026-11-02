"""Discover and import state-school registries through cadastral-to-ISTAT keys."""
from collections import Counter
from copy import deepcopy
import csv
import re
from etl.acquisition import Context
from etl.models import AdapterResult, Entity, Observation
from etl.adapters.municipal_keys import cadastral_crosswalk

LANDING_URL='https://dati.istruzione.it/opendata/opendata/catalog/SCUANAGRAFESTAT'
METADATA={'id':'mim_schools','name':'Anagrafe scuole statali','publisher':'Ministero dell’Istruzione e del Merito',
 'landing_url':LANDING_URL,'download_url':None,'license':'IODL 2.0','license_url':'https://www.dati.gov.it/content/italian-open-data-license-v20',
 'format':'UTF-8 comma CSV','geography':'School record, cadastral municipality code crosswalk to ISTAT',
 'period':'latest two school years','status':'ready','blocker':None,
 'notes':'A school code is an administrative school unit, not necessarily a distinct building. Count includes source-listed units; sede scolastica SI is also reported separately. School year is displayed in metadata; observation year is the start year. No inferred school closure from absence in a historic file.',
 'indicators':[{'id':'state_school_units','label':'Unità scolastiche statali censite','unit':'school units','definition':'Count of distinct CODICESCUOLA in the published school-year registry.'},{'id':'state_school_sites','label':'Unità indicate come sede scolastica','unit':'school units','definition':'Count of distinct CODICESCUOLA with SEDESCOLASTICA=SI; not a count of distinct buildings.'}]}


def parse_school_file(path,crosswalk:dict[str,str],year:str) -> AdapterResult:
    """Reject HTML responses, duplicate school IDs, inconsistent periods and unmatched cadastral codes."""
    reader=csv.DictReader(path.open(encoding='utf-8-sig',newline=''))
    required={'ANNOSCOLASTICO','PROVINCIA','CODICESCUOLA','CODICECOMUNESCUOLA','DENOMINAZIONESCUOLA','SEDESCOLASTICA'}
    if not required.issubset(reader.fieldnames or []):raise ValueError('School CSV schema changed or download returned HTML')
    counts=Counter();sites=Counter();entities=[];seen=set()
    for row in reader:
        if row['PROVINCIA']!='AVELLINO':continue
        if row['ANNOSCOLASTICO']!=year:raise ValueError('School-year mismatch')
        code=crosswalk.get(row['CODICECOMUNESCUOLA'])
        if code is None:raise ValueError('Unreconciled school cadastral code')
        school=row['CODICESCUOLA']
        if school in seen:raise ValueError('Duplicate school identifier')
        if row['SEDESCOLASTICA'] not in {'SI','NO'}:raise ValueError('Unrecognised school-site status')
        seen.add(school);counts[code]+=1;sites[code]+=row['SEDESCOLASTICA']=='SI'
        payload={k:row[k] for k in ('CODICESCUOLA','CODICEISTITUTORIFERIMENTO','INDIRIZZOSCUOLA','DESCRIZIONETIPOLOGIAGRADOISTRUZIONESCUOLA','SEDESCOLASTICA','ANNOSCOLASTICO','CODICECOMUNESCUOLA')}
        payload['join_method']='ISTAT cadastral code crosswalk'
        entities.append(Entity(code,'mim_schools',school,row['DENOMINAZIONESCUOLA'],'school',payload,year[:4]))
    if not seen:raise ValueError('No Avellino school records')
    observations=[Observation(c,i,year[:4],float(v)) for c in sorted(crosswalk.values()) for i,v in [('state_school_units',counts[c]),('state_school_sites',sites[c])]]
    return AdapterResult(deepcopy(METADATA),observations,entities=entities)


def run(context:Context,codes:set[str]) -> AdapterResult:
    """Use the actual root download route, never the relative catalogue route returning HTML."""
    landing=context.fetch(LANDING_URL,'mim_catalog.html').read_text()
    if 'IODL 2.0' not in landing:raise ValueError('School registry reuse licence changed')
    files=sorted(set(re.findall(r'SCUANAGRAFESTAT(\d{6})(\d{8})\.csv',landing)),reverse=True)[:2]
    if len(files)!=2:raise ValueError('School-year discovery failed')
    crosswalk=cadastral_crosswalk(context.raw_dir/'istat_registry_2026.xlsx',codes)
    observations=[];latest_entities=[];period_labels={}
    for index,(year,release) in enumerate(files):
        url=f'https://dati.istruzione.it/opendata/SCUANAGRAFESTAT{year}{release}.csv'
        result=parse_school_file(context.fetch(url,f'mim_school_registry_{year}.csv'),crosswalk,year)
        observations.extend(result.observations)
        if index==0:latest_entities=result.entities
        period_labels[year[:4]]=year[:4]+'/'+year[4:]
    return AdapterResult({**METADATA,'period':', '.join(period_labels.values()),'period_notes':period_labels},observations,entities=latest_entities)
