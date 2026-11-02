"""Import original administration spending after reconciling official authority identifiers."""
import csv
import json
from openpyxl import load_workbook
from etl.acquisition import Context
from etl.models import AdapterResult, Observation

LANDING_URL='https://www.opencivitas.it/portale/open-data'
BASE='https://www.opencivitas.it/portale/documents/20118/0/'
DATA=BASE+'2023_Ind_AMMINISTR_01_IT.csv/45e7ec1b-d282-278d-de7b-73af1b374255'
RDF=BASE+'2023_FC90_AMMINISTR_1_IT.rdf/8c19dffa-bcf4-b7e0-1268-1065c8c89c0f'
KEYS=BASE+'Metadati_Enti_2023_IT.xlsx/9af2749a-d3a5-cc6f-c78d-08593c7dbc32'
DICTIONARY=BASE+'2023_Metadati_Ind_FC90_AMMINISTR_01_IT.xlsx/9e1fd560-98c5-bad0-2d77-55c8018d8a02'
FIELDS={'SPESA_STORICA':('admin_historic_spending','Spesa storica — amministrazione','EUR'),
 'SPESA_STORICA_PROAB':('admin_historic_spending_per_person','Spesa storica per abitante — amministrazione','EUR/person'),
 'FST_RIPROPORZIONATO_BI':('admin_standard_spending','Spesa standard — amministrazione','EUR'),
 'FST_RIPROPORZIONATO_BI_PROAB':('admin_standard_spending_per_person','Spesa standard per abitante — amministrazione','EUR/person')}
METADATA={'id':'opencivitas','name':'OpenCivitas — amministrazione generale 2023','publisher':'Sogei / MEF',
 'landing_url':LANDING_URL,'download_url':DATA,'license':'CC BY 4.0 (specific dataset RDF)','license_url':RDF,
 'format':'CSV / XLSX crosswalk and definitions / RDF licence','geography':'Municipality','period':'2023','status':'ready','blocker':None,
 'notes':'Specific RDF declares CC BY 4.0 although general website terms are restrictive. Only four administration-function monetary indicators are imported. Standard spending is not an appropriation or a payment; historic spending follows OpenCivitas function definitions. The adapter pins the verified 2023 schema; discovery of a new release requires review and is signalled by the monthly catalogue check.',
 'indicators':[{'id':v[0],'label':v[1],'unit':v[2],'definition':f'OpenCivitas AMMINISTRAZIONE 2023, original {k}; see acquired indicator workbook.'} for k,v in FIELDS.items()]}


def run(context:Context,codes:set[str]) -> AdapterResult:
    """Respect suppression/privacy flags and reject a broken authority crosswalk."""
    license_rdf=context.fetch(RDF,'civitas_admin.rdf').read_text()
    if '<ccorg:licenses rdf:resource="http://creativecommons.org/licenses/by/4.0/deed.it"/>' not in license_rdf:
        raise ValueError('Specific OpenCivitas dataset licence changed')
    path=context.fetch(KEYS,'civitas_entities.xlsx');workbook=load_workbook(path,read_only=True,data_only=True)
    try:
        workbook.active.reset_dimensions()
        rows=workbook.active.iter_rows(values_only=True);headers=next(rows);mapping={}
        for values in rows:
            row=dict(zip(headers,values));code=str(row['COMUNE_ISTAT_COD']).zfill(6)
            if code in codes and row['TIPOLOGIA_ENTE']=='COMUNE':mapping[str(row['USERNAME'])]=code
        if set(mapping.values())!=codes or len(mapping)!=118:raise ValueError('OpenCivitas authority crosswalk incomplete')
    finally:workbook.close()
    dictionary=context.fetch(DICTIONARY,'civitas_indicators.xlsx');workbook=load_workbook(dictionary,read_only=True,data_only=True)
    try:
        workbook.active.reset_dimensions()
        definitions={str(row[0]):str(row[1]) for row in workbook.active.iter_rows(values_only=True) if len(row)>1}
        if not set(FIELDS).issubset(definitions):raise ValueError('OpenCivitas indicator definitions changed')
        for key,(_,_,unit) in FIELDS.items():
            if 'Euro' not in definitions[key] or ('per abitante' in definitions[key])!=(unit=='EUR/person'):
                raise ValueError('OpenCivitas units changed')
    finally:workbook.close()
    data=context.fetch(DATA,'civitas_admin.csv');reader=csv.DictReader(data.open(encoding='utf-8-sig',newline=''),delimiter=';')
    if reader.fieldnames!=['USERNAME','Indicatore/Determinante','Valore','Anomalia','Privacy']:raise ValueError('OpenCivitas CSV schema changed')
    observations=[];seen=set()
    for row in reader:
        code=mapping.get(row['USERNAME']);field=row['Indicatore/Determinante']
        if code is None or field not in FIELDS:continue
        key=(code,field)
        if key in seen:raise ValueError('Duplicate OpenCivitas observation')
        seen.add(key);token=row['Valore'].strip();status='observed'
        if row['Privacy'].strip() not in {'','0'} or token in {'*','..','...'}:value=None;status='suppressed'
        elif row['Anomalia'].strip() not in {'','0'} or not token:value=None;status='missing'
        else:value=float(token.replace(',','.'))
        observations.append(Observation(code,FIELDS[field][0],'2023',value,status))
    if not observations:raise ValueError('No Avellino OpenCivitas observations')
    return AdapterResult(dict(METADATA),observations)
