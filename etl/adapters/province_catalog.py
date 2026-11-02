"""Import licensed provincial lists without inventing municipal associations or dates."""
from collections import Counter
import hashlib
import json
from urllib.parse import quote
from etl.acquisition import Context
from etl.models import AdapterResult, Entity, Observation
from etl.adapters.municipal_keys import normalized_name

CATALOG_URL='https://www.dati.gov.it/opendata/api/3/action/package_search?fq=organization:provincia-di-avellino&rows=100'
TYPES={
 'province_castles':('Castelli','Castelli','castle'),
 'province_religious':('ComplessiReligiosi','Complessi Religiosi','religious place'),
 'province_libraries':('Biblioteche','Biblioteche','library'),
 'province_archaeology':('AreeArcheologiche','Aree Archeologiche','archaeological place'),
 'province_palaces':('PalazziStorici','Palazzi Storici','historic palace'),
 'province_schools':('IstitutiScolastici','Istituti Scolastici','school'),
 'province_roads':('ElencoStrade','Elenco Strade','road'),
 'province_works':('OrdinanzeeCantieri','Ordinanze e cantieri','road notice'),
}


def metadata(adapter:str) -> dict[str,object]:
    """Declare catalogue coverage honestly before running a licence or association check."""
    filename,title,_=TYPES[adapter]
    return {'id':adapter,'name':title,'publisher':'Provincia di Avellino',
      'landing_url':'https://provincia.avellino.it/cprvnvll/zf/index.php/servizi-aggiuntivi/index/index/idtesto/174',
      'download_url':f'https://www.provincia.avellino.it/cprvnvll/images/OpenData/{filename}/{filename}.json',
      'license':None,'license_url':None,'format':'JSON','geography':'Provincial catalogue; association coverage measured, not assumed',
      'period':'acquisition snapshot, observation date unknown','status':'blocked','blocker':'Reuse licence and record association have not been validated.',
      'notes':'The publisher supplies no observation date. Acquisition date is not a field survey date. Source listings may contain duplicates or partial addresses. No geocoding and no invented coordinates. Unmatched records remain visible in the section with a null municipality.',
      'indicators':[]}


def run(context:Context,municipalities:list[dict[str,str]],adapter:str,school_links:dict[str,str]) -> AdapterResult:
    """Require CC BY metadata for the exact distribution, then import original fields with explicit join methods."""
    meta=metadata(adapter);filename,title,kind=TYPES[adapter]
    catalog=json.loads(context.fetch(CATALOG_URL,'province_catalog_all.json').read_text())
    if not catalog['success']:raise ValueError('Provincial catalogue lookup failed')
    packages=[p for p in catalog['result']['results'] if p['title']==title]
    if len(packages)!=1:raise ValueError('No unique licensed provincial dataset in national catalogue')
    resources=[r for r in packages[0]['resources'] if r.get('url')==meta['download_url']]
    if len(resources)!=1 or resources[0].get('license')!='https://creativecommons.org/licenses/by/4.0/':
        raise ValueError('Provincial JSON distribution licence absent or changed')
    path=context.fetch(str(meta['download_url']),f'province_{filename}.json')
    rows=json.loads(path.read_text());period=str(context.artifacts[-1]['retrieved_at'])[:10]
    if not isinstance(rows,list) or not rows:raise ValueError('Expected a nonempty provincial list')
    names={normalized_name(m['name']):m['code'] for m in municipalities}
    if len(names)!=118:raise ValueError('Ambiguous normalized ISTAT names')
    entities=[];seen=set();counts=Counter();unmatched=[]
    for index,row in enumerate(rows):
        if not isinstance(row,dict):raise ValueError('Malformed provincial record')
        identity=hashlib.sha256(json.dumps(row,sort_keys=True,ensure_ascii=False).encode()).hexdigest()
        if identity in seen:continue
        seen.add(identity)
        name=row.get('Comune');code=names.get(normalized_name(str(name))) if name else None
        join_method='Exact normalized ISTAT municipality name' if code else 'Unresolved; no inferred municipality'
        if adapter=='province_schools':
            code=school_links.get(str(row.get('Codice Meccanografico','')).strip())
            if code:join_method='MIM institution code, linked to official ISTAT cadastral crosswalk'
        entity_title=row.get('Nome') or row.get('Denominazione') or row.get('Denominazione Istituto') or row.get('ITINERARIO')
        if not isinstance(entity_title,str) or not entity_title.strip():raise ValueError('Provincial record lacks a title')
        payload={**row,'join_method':join_method}
        entities.append(Entity(code,adapter,identity,entity_title,kind,payload,period))
        if code:counts[code]+=1
        else:unmatched.append({'row':index+1,'title':entity_title,'municipality':name})
    indicators=[];observations=[]
    if counts:
        metric=adapter+'_listed_records'
        indicators=[{'id':metric,'label':title+' — schede associate al comune','unit':'listed records',
          'definition':'Count of reconciled publisher catalogue rows, after exact duplicate removal. Partial catalogue; absent municipality is missing, never zero cultural assets.'}]
        observations=[Observation(m['code'],metric,period,float(counts[m['code']]) if m['code'] in counts else None,'observed' if m['code'] in counts else 'missing') for m in municipalities]
    meta.update({'status':'ready','blocker':None,'license':'CC BY 4.0','license_url':'https://creativecommons.org/licenses/by/4.0/',
                 'period':period,'indicators':indicators,'source_record_count':len(rows),'exact_duplicate_rows':len(rows)-len(entities),
                 'unmatched_records':unmatched,'metadata_modified':packages[0]['metadata_modified']})
    return AdapterResult(meta,observations,entities=entities)
