"""Import funded digital applications, preserving withdrawals and current status."""
from collections import Counter,defaultdict
from datetime import datetime,timezone
import csv
import hashlib
import math
from pathlib import Path
from etl.acquisition import Context
from etl.models import AdapterResult, Observation, Entity

BASE='https://raw.githubusercontent.com/teamdigitale/padigitale2026-opendata/main/'
DOWNLOAD_URL=BASE+'data/candidature_comuni_finanziate.csv'
METADATA={'id':'pa_digitale','name':'PA Digitale 2026 — candidature dei comuni','publisher':'Dipartimento per la trasformazione digitale',
 'landing_url':'https://padigitale2026.gov.it/open-data','download_url':DOWNLOAD_URL,
 'license':'CC BY 4.0','license_url':BASE+'LICENSE','format':'UTF-8 comma CSV','geography':'Municipal authority, exact ISTAT code',
 'period':'acquisition snapshot','status':'ready','blocker':None,
 'notes':'Current application status, not accounting cash expenditure. A=assigned, E=disbursed after verification, R=withdrawn. Summaries exclude R. A funded application is not necessarily a distinct investment project or unique CUP. Acquisition-date snapshots do not represent annual flows.',
 'indicators':[{'id':'digital_applications','label':'Candidature digitali assegnate o erogate','unit':'applications','definition':'Count of municipal applications with status A or E at acquisition date.'},{'id':'digital_allocated_eur','label':'Voucher digitali assegnati o erogati','unit':'EUR','definition':'Sum of requested voucher amounts with current status A or E; not municipal cash expenditure.'}]}


def parse_applications(path:Path,codes:set[str],period:str) -> AdapterResult:
    """Reject duplicate application identities and retain source status rather than infer progress."""
    reader=csv.DictReader(path.open(encoding='utf-8-sig',newline=''))
    required={'cod_comune','cod_provincia','codice_ipa','avviso','codice_cup','importo_finanziamento','stato_candidatura','data_invio_candidatura'}
    if not required.issubset(reader.fieldnames or []):raise ValueError('PA Digitale schema changed')
    counts=Counter();totals=defaultdict(float);entities=[];seen=set()
    for row in reader:
        code=row['cod_comune']
        if not code.startswith('064'):continue
        if code not in codes or row['cod_provincia']!='064':raise ValueError('PA Digitale geography mismatch')
        amount=float(row['importo_finanziamento']);status=row['stato_candidatura']
        if not math.isfinite(amount) or amount<0 or status not in {'A','E','R'}:raise ValueError('Invalid funding amount/status')
        identity='|'.join(row[k] for k in ('codice_ipa','avviso','codice_cup','data_invio_candidatura'))
        if identity in seen:raise ValueError('Duplicate funded application')
        seen.add(identity)
        payload={k:row[k] for k in ('codice_ipa','codice_cup','avviso','data_finanziamento','stato_candidatura','data_stato_candidatura','decreto_finanziamento')}
        payload['amount_eur']=amount
        entities.append(Entity(code,'pa_digitale',hashlib.sha256(identity.encode()).hexdigest(),row['avviso'],'application',payload,period))
        if status in {'A','E'}:counts[code]+=1;totals[code]+=amount
    if not entities:raise ValueError('No Avellino funded applications')
    observations=[Observation(c,k,period,float(v)) for c in sorted(codes) for k,v in [('digital_applications',counts[c]),('digital_allocated_eur',totals[c])]]
    return AdapterResult({**METADATA,'period':period},observations,entities=entities)


def run(context:Context,codes:set[str]) -> AdapterResult:
    """Verify repository licence and parse the publicly downloaded complete national file."""
    license_text=context.fetch(BASE+'LICENSE','pad_license.txt').read_text()
    if 'Attribution 4.0 International' not in license_text:raise ValueError('Funding licence changed')
    context.fetch(BASE+'format/format-pad26-candidature-comuni-finanziate.md','pad_format.md')
    path=context.fetch(DOWNLOAD_URL,'pad_candidatures.csv')
    period=str(context.artifacts[-1]['retrieved_at'])[:10]
    return parse_applications(path,codes,period)
