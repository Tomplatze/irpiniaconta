"""Import AgID IPA authority records by their published municipal identifiers."""
from collections import Counter
import json
from openpyxl import load_workbook
from etl.acquisition import Context
from etl.models import AdapterResult, Entity, Observation

CATALOG_URL='https://indicepa.gov.it/ipa-dati/api/3/action/package_show?id=enti'
METADATA={'id':'ipa_entities','name':'Anagrafe enti IPA','publisher':'AgID','landing_url':'https://indicepa.gov.it/ipa-dati/dataset/enti',
 'download_url':None,'license':'CC BY 4.0','license_url':'https://creativecommons.org/licenses/by/4.0/',
 'format':'CKAN JSON / XLSX','geography':'Authority location, exact municipal ISTAT code','period':'acquisition snapshot','status':'ready','blocker':None,
 'notes':'IPA includes public administrations, service providers and private contracting authorities. Their registered location is not their service area. Personal names and contact mailboxes are not imported.',
 'indicators':[{'id':'ipa_entity_count','label':'Enti con sede nel comune iscritti in IPA','unit':'entities','definition':'Count of IPA identifiers with Codice_comune_ISTAT equal to the municipality; includes all IPA entity types.'}]}


def run(context:Context,codes:set[str]) -> AdapterResult:
    """Discover the current licensed spreadsheet and retain identifier/type/source update date."""
    catalog=json.loads(context.fetch(CATALOG_URL,'ipa_catalog.json').read_text())
    if not catalog['success'] or catalog['result']['license_id']!='CC-BY-4.0':raise ValueError('IPA catalogue or licence changed')
    resources=[r for r in catalog['result']['resources'] if r['format']=='XLSX']
    if len(resources)!=1:raise ValueError('Ambiguous IPA spreadsheet')
    path=context.fetch(resources[0]['url'],'ipa_entities.xlsx');period=str(context.artifacts[-1]['retrieved_at'])[:10]
    workbook=load_workbook(path,read_only=True,data_only=True)
    entities=[];counts=Counter();seen=set()
    try:
        rows=workbook.active.iter_rows(values_only=True);headers=next(rows)
        required={'Codice_IPA','Denominazione_ente','Codice_comune_ISTAT','Tipologia','Codice_Categoria','Data_aggiornamento'}
        if not required.issubset(headers):raise ValueError('IPA schema changed')
        for values in rows:
            row=dict(zip(headers,values));code=str(row['Codice_comune_ISTAT']).zfill(6)
            if not code.startswith('064'):continue
            if code not in codes:raise ValueError('Unreconciled IPA municipality')
            identity=str(row['Codice_IPA'])
            if identity in seen:raise ValueError('Duplicate IPA ID')
            seen.add(identity);counts[code]+=1
            payload={k:row[k] for k in ('Codice_IPA','Tipologia','Codice_Categoria','Indirizzo','Data_aggiornamento')}
            entities.append(Entity(code,'ipa_entities',identity,str(row['Denominazione_ente']),'authority',payload,period))
    finally:workbook.close()
    if not entities:raise ValueError('No Avellino IPA entities')
    observations=[Observation(c,'ipa_entity_count',period,float(counts[c])) for c in sorted(codes)]
    return AdapterResult({**METADATA,'download_url':resources[0]['url'],'period':period},observations,entities=entities)
