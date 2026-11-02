"""Import annual demographic balances with dynamic published-year discovery."""
from copy import deepcopy
import csv
import io
import re
from urllib.parse import urljoin
from zipfile import ZipFile
from etl.acquisition import Context
from etl.models import AdapterResult, Observation
from etl.adapters.mef_income import parse_number

LANDING_URL = 'https://demo.istat.it/app/?i=P02&l=it'
FIELDS = {
 'births': ('Nati vivi - Totale', 'Nati vivi', False),
 'deaths': ('Morti - Totale', 'Decessi', False),
 'natural_balance': ('Saldo naturale - Totale', 'Saldo naturale', True),
 'domestic_immigrants': ('Immigrati da altro comune - Totale', 'Iscritti da altri comuni', False),
 'domestic_emigrants': ('Emigrati per altro comune - Totale', 'Cancellati per altri comuni', False),
 'domestic_migration_balance': ('Saldo migratorio interno - Totale', 'Saldo migratorio interno', True),
 'foreign_immigrants': ("Immigrati dall'estero - Totale", 'Iscritti dall’estero', False),
 'foreign_emigrants': ("Emigrati per l'estero - Totale", 'Cancellati per l’estero', False),
 'foreign_migration_balance': ("Saldo migratorio con l'estero - Totale", 'Saldo migratorio con l’estero', True),
 'year_end_population': ('Popolazione al 31 dicembre - Totale', 'Popolazione al 31 dicembre', False),
}
METADATA = {'id':'istat_balance','name':'Bilancio demografico annuale','publisher':'ISTAT',
 'landing_url':LANDING_URL,'download_url':None,'license':'CC BY 4.0 (ISTAT default)','license_url':'https://www.istat.it/note-legali/',
 'format':'ZIP / UTF-8 semicolon CSV','geography':'Municipality','period':'2021–latest published year',
 'status':'ready','blocker':None,'notes':'Event-year flows. 2025 has source flag p (provisional); 2021–2024 are census-adjusted. End-year figures are kept separate from 1 January population estimates. No backward imputation across municipal boundary changes.',
 'indicators':[{'id':key,'label':v[1],'unit':'persons','definition':f'ISTAT original {v[0]}; annual event counts, both sexes.','allow_negative':v[2]} for key,v in FIELDS.items()]}


def parse_balance(payload: bytes, year: int) -> list[Observation]:
    """Require exact geography and reconcile published natural and migration balances."""
    with ZipFile(io.BytesIO(payload)) as archive:
        names=[n for n in archive.namelist() if n.endswith('.csv')]
        if len(names)!=1:raise ValueError('Expected one balance CSV')
        lines=archive.read(names[0]).decode('utf-8-sig').splitlines()
    if str(year) not in lines[0]:raise ValueError('Balance year mismatch')
    reader=csv.DictReader(io.StringIO('\n'.join(lines[1:])),delimiter=';')
    columns={n.casefold():n for n in reader.fieldnames or []}
    result=[];seen=set()
    for row in reader:
        code=row['Codice comune']
        if code.startswith('Note: p = dato provvisorio.') and row['Comune'] is None:continue
        if not re.fullmatch(r'064\d{3}',code):raise ValueError('Unrecognised balance municipality')
        if code in seen:raise ValueError('Duplicate balance municipality')
        seen.add(code);values={}
        for key,(field,_,_) in FIELDS.items():
            source=columns.get(field.casefold())
            if key=='year_end_population' and source is None:
                source=columns.get('popolazione censita al 31 dicembre - totale')
            if source is None:raise ValueError(f'Balance schema changed: {field}')
            value,status=parse_number(row[source]);values[key]=value
            result.append(Observation(code,key,str(year),value,status))
        for left,right,total in [('births','deaths','natural_balance'),('domestic_immigrants','domestic_emigrants','domestic_migration_balance'),('foreign_immigrants','foreign_emigrants','foreign_migration_balance')]:
            if all(values[k] is not None for k in (left,right,total)) and values[left]-values[right]!=values[total]:
                raise ValueError('Published demographic balance does not reconcile')
    if len(seen)!=118:raise ValueError(f'Balance coverage {len(seen)}')
    return result


def run(context: Context, options: dict[str, object] | None = None) -> AdapterResult:
    """Discover the newest linked archive and acquire five annual balances from 2021."""
    landing=context.fetch(LANDING_URL,'demo_balance.html').read_text()
    matches=re.findall(r'href="([^\"]*P2_(\d{4})_it_064_Avellino\.zip)"',landing)
    if not matches:raise ValueError('No published Avellino balance archive')
    latest=max(int(year) for _,year in matches)
    if latest<2025:raise ValueError('Published balance regressed')
    metadata=deepcopy(METADATA);metadata['period']=f'2021–{latest}'
    metadata['period_notes']={str(y):('Provisional (p)' if y==2025 else 'See source information flag and release notes') for y in range(2021,latest+1)}
    observations=[]
    start_year=int((options or {}).get('start_year',2021))
    for year in range(start_year,latest+1):
        url=f'https://demo.istat.it/data/p2/P2_{year}_it_064_Avellino.zip'
        observations.extend(parse_balance(context.fetch(url,f'istat_balance_{year}.zip').read_bytes(),year))
    return AdapterResult(metadata,observations)
