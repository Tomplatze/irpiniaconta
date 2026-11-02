"""Import the current public pharmacy registry with explicit validity intervals."""
from collections import Counter
from datetime import datetime
import csv
import re
from urllib.parse import urljoin
from etl.acquisition import Context
from etl.models import AdapterResult, Entity, Observation
from etl.adapters.municipal_keys import reconcile_legacy_code

LANDING_URL='https://www.dati.salute.gov.it/it/dataset/farmacie/'
METADATA={'id':'health_pharmacies','name':'Farmacie e sedi farmaceutiche','publisher':'Ministero della Salute',
 'landing_url':LANDING_URL,'download_url':None,'license':'IODL 2.0','license_url':'https://www.dati.gov.it/iodl/2.0/',
 'format':'UTF-8 semicolon CSV','geography':'Location record, exact municipal ISTAT code','period':'export snapshot',
 'status':'ready','blocker':None,'notes':'Counts pharmacy location records whose source validity interval includes the export date. Includes ordinary pharmacies, branches, dispensaries and seasonal dispensaries. Coordinates are excluded because the publisher notes that some coordinates originate from OpenStreetMap. Counts do not measure opening hours or actual seasonal availability.',
 'indicators':[{'id':'pharmacy_location_count','label':'Sedi farmaceutiche con validità corrente','unit':'locations','definition':'Count of distinct ministry pharmacy/location identifiers with validity interval including the source export date; includes seasonal dispensaries.'}]}


def date_value(token:str):
    """Read the documented date format without inferring missing start dates."""
    if token.strip() in {'','-'}:return None
    return datetime.strptime(token,'%d/%m/%Y').date()


def run(context:Context,codes:set[str]) -> AdapterResult:
    """Discover the daily CSV and preserve current location identifiers and source validity fields."""
    landing=context.fetch(LANDING_URL,'health_pharmacy_landing.html').read_text()
    if 'Italian Open Data Licence v2.0' not in landing:raise ValueError('Pharmacy reuse licence changed')
    links=re.findall(r'href="([^\"]*FRM_FARMA_5_(\d{8})\.csv)"',landing)
    if len(links)!=1:raise ValueError('Ambiguous current pharmacy export')
    link,stamp=links[0];url=urljoin(LANDING_URL,link);date=datetime.strptime(stamp,'%Y%m%d').date();period=date.isoformat()
    path=context.fetch(url,f'health_pharmacies_{stamp}.csv')
    reader=csv.DictReader(path.open(encoding='utf-8-sig',newline=''),delimiter=';')
    required={'cod_farmacia','localizzazione','cod_comune','cod_provincia','data_inizio_validita','data_fine_validita','descrizione_farmacia'}
    if not required.issubset(reader.fieldnames or []):raise ValueError('Pharmacy schema changed or HTTP returned HTML')
    entities=[];seen=set();counts=Counter();unknown_start=[]
    for row in reader:
        code=row['cod_comune']
        if not code.startswith('064'):continue
        start=date_value(row['data_inizio_validita']);end=date_value(row['data_fine_validita'])
        if start is None:unknown_start.append(row['cod_farmacia']);continue
        if start>date or (end is not None and end<date):continue
        code,join_method=reconcile_legacy_code(code,row['comune'],period,codes)
        if row['cod_provincia']!='064':raise ValueError('Current pharmacy province mismatch')
        identity=row['cod_farmacia']+':'+row['localizzazione']
        if identity in seen:raise ValueError('Overlapping active pharmacy/location records')
        seen.add(identity);counts[code]+=1
        payload={k:row[k] for k in ('cod_farmacia','localizzazione','indirizzo','descrizione_tipologia','data_inizio_validita','data_fine_validita')}
        payload.update({'source_municipal_code':row['cod_comune'],'join_method':join_method})
        entities.append(Entity(code,'health_pharmacies',identity,row['descrizione_farmacia'],'pharmacy',payload,period))
    if not entities:raise ValueError('No Avellino current pharmacy records')
    observations=[Observation(c,'pharmacy_location_count',period,float(counts[c])) for c in sorted(codes)]
    return AdapterResult({**METADATA,'crosswalk_evidence':'config/municipality-crosswalks.json','period':period,'download_url':url,'unresolved_start_dates':unknown_start},observations,entities=entities)
