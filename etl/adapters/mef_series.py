"""Full municipal IRPEF numeric tables, with explicit historical aggregate derivation."""
from copy import deepcopy
import csv
import hashlib
import io
import re
from urllib.parse import urljoin
from zipfile import ZipFile
from etl.acquisition import Context
from etl.models import AdapterResult, Observation
from etl.adapters.mef_income import LANDING_URL,METADATA,parse_number

BANDS=['minore o uguale a zero euro','da 0 a 10000 euro','da 10000 a 15000 euro','da 15000 a 26000 euro',
       'da 26000 a 55000 euro','da 55000 a 75000 euro','da 75000 a 120000 euro','oltre 120000 euro']
ALIASES={'Numero contribuenti':'irpef_taxpayers','Reddito complessivo - Frequenza':'irpef_income_declarants',
         'Reddito complessivo - Ammontare in euro':'irpef_income_total'}


def metric_id(field:str) -> str:
    """Keep field identities stable across catalogue years and punctuation-safe for APIs."""
    return ALIASES.get(field,'irpef_'+hashlib.sha256(field.encode()).hexdigest()[:16])


def combined(values:list[tuple[float|None,str]]) -> tuple[float|None,str]:
    """Sum only an exhaustive, unsuppressed set of source-defined income bins."""
    if any(status=='suppressed' for _,status in values):return None,'suppressed'
    if any(value is None for value,_ in values):return None,'missing'
    return sum(value for value,_ in values if value is not None),'observed'


def parse_year(payload:bytes,year:str) -> tuple[list[Observation],dict[str,dict[str,object]],bool]:
    """Import every frequency/amount column while keeping original suppression tokens."""
    with ZipFile(io.BytesIO(payload)) as archive:
        members=[name for name in archive.namelist() if name.lower().endswith('.csv')]
        if len(members)!=1:raise ValueError('Expected one municipal MEF CSV')
        text=archive.read(members[0]).decode('utf-8-sig')
    reader=csv.DictReader(io.StringIO(text),delimiter=';')
    reader.fieldnames=[field.strip() for field in reader.fieldnames or []]
    required={'Anno di imposta','Codice Istat Comune','Sigla Provincia','Numero contribuenti'}
    if not required.issubset(reader.fieldnames):raise ValueError('MEF identifiers changed')
    numeric=[field for field in reader.fieldnames if field=='Numero contribuenti' or field.endswith(' - Frequenza') or field.endswith(' - Ammontare in euro')]
    has_total='Reddito complessivo - Ammontare in euro' in reader.fieldnames
    if not has_total:
        if not all(f'Reddito complessivo {band} - {kind}' in numeric for band in BANDS for kind in ['Frequenza','Ammontare in euro']):
            raise ValueError('MEF exhaustive income bins unavailable')
    definitions={metric_id(field):{'id':metric_id(field),'label':field,'unit':'EUR' if field.endswith('Ammontare in euro') else 'persons',
       'definition':f'MEF original municipal column: {field}; explicit tax year, nominal euros where applicable.',
       'allow_negative':field.endswith('Ammontare in euro')} for field in numeric}
    definitions.update({i['id']:deepcopy(i) for i in METADATA['indicators']})
    observations=[];seen=set()
    for row in reader:
        code=row['Codice Istat Comune']
        if not code.startswith('064'):continue
        if not re.fullmatch(r'064\d{3}',code) or row['Sigla Provincia']!='AV' or row['Anno di imposta']!=year:raise ValueError('MEF period/geography mismatch')
        if code in seen:raise ValueError('Duplicate MEF municipality')
        seen.add(code);values={field:parse_number(row[field]) for field in numeric}
        for field,(value,status) in values.items():observations.append(Observation(code,metric_id(field),year,value,status))
        if has_total:
            total=values['Reddito complessivo - Ammontare in euro'];frequency=values['Reddito complessivo - Frequenza']
        else:
            total=combined([values[f'Reddito complessivo {band} - Ammontare in euro'] for band in BANDS])
            frequency=combined([values[f'Reddito complessivo {band} - Frequenza'] for band in BANDS])
            observations.extend([Observation(code,'irpef_income_total',year,*total),Observation(code,'irpef_income_declarants',year,*frequency)])
        amount,amount_status=total;count,count_status=frequency
        if amount is not None and count is not None and count>0:mean=amount/count;status='observed'
        else:mean=None;status='suppressed' if 'suppressed' in {amount_status,count_status} else 'missing'
        observations.append(Observation(code,'irpef_income_mean',year,mean,status))
    if len(seen)!=118:raise ValueError(f'MEF geography coverage changed: {len(seen)}')
    return observations,definitions,not has_total


def run(context:Context,options:dict[str,object]) -> AdapterResult:
    """Discover all configured years and preserve historical source schema differences."""
    landing=context.fetch(LANDING_URL,'mef-catalog.html').read_text()
    if 'creativecommons.org/licenses/by/3.0/it/' not in landing:raise ValueError('MEF licence changed')
    links={year:urljoin(LANDING_URL,url) for url,year in re.findall(r'href="([^\"]*Redditi_e_principali_variabili_IRPEF_su_base_comunale_CSV_(\d{4})[^\"]*)"',landing)}
    years=sorted(year for year in links if int(year)>=int(options.get('start_year',2020)))
    if not years:raise ValueError('No configured tax-year archives')
    observations=[];definitions={};derivations={}
    for year in years:
        cells,metrics,derived=parse_year(context.fetch(links[year],f'mef-income-{year}.zip').read_bytes(),year)
        observations.extend(cells);definitions.update(metrics)
        derivations[year]='Overall total/frequency derived only when all eight mutually exclusive official income-bin values are present; otherwise null.' if derived else 'Original overall-income total and frequency; mean derived from their ratio.'
    metadata=deepcopy(METADATA)
    for key in ['irpef_income_declarants','irpef_income_total','irpef_income_mean']:
        definitions[key]['definition']=str(definitions[key]['definition'])+' Historical archives without an overall column use the exhaustive eight source income bins; missing/suppressed bins propagate to null.'
    metadata.update({'period':f'{years[0]}–{years[-1]}','period_notes':derivations,'indicators':list(definitions.values()),'download_url':links[years[-1]],
      'notes':['All published frequency and euro-amount columns are imported, with stable field-derived identities. Tax years, declaration years and release dates are distinct.',
       'Nominal euros; no inflation adjustment. Historical totals are explicitly derived from the exhaustive official income bins only if every input is observed.',
       'Frequency denominators refer to declarations, not residents. Original small-count suppression and blank fields remain null.']})
    return AdapterResult(metadata,observations)
