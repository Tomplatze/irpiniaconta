"""Acquire real API examples and policy evidence without publishing unreviewed municipal weather."""
import argparse
from datetime import date,timedelta,datetime,timezone
from urllib.parse import parse_qsl,urlencode,urlsplit,urlunsplit
import json
import math
from etl.acquisition import Context
from etl.pipeline import ROOT,utc_now


def validate(provider_id:str,payload:dict[str,object],expected:list[str]|None=None) -> dict[str,object]:
    """Reject error/HTML responses, missing days, nonfinite values and changed weather units."""
    expected=expected or [(date(2025,1,1)+timedelta(days=offset)).isoformat() for offset in range(7)]
    if provider_id=='open_meteo_archive':
        daily=payload['daily'];units=payload['daily_units']
        if daily['time']!=expected:raise ValueError('Historical day coverage changed')
        if units['temperature_2m_mean']!='°C' or units['precipitation_sum']!='mm':raise ValueError('Weather units changed')
        parameters={'temperature':daily['temperature_2m_mean'],'precipitation':daily['precipitation_sum']}
    else:
        source=payload['properties']['parameter'];units=payload['parameters']
        if set(source['T2M'])!={day.replace('-','') for day in expected}:raise ValueError('Historical day coverage changed')
        if units['T2M']['units']!='C' or units['PRECTOTCORR']['units']!='mm/day':raise ValueError('NASA units changed')
        parameters={'temperature':list(source['T2M'].values()),'precipitation':list(source['PRECTOTCORR'].values())}
    for values in parameters.values():
        if len(values)!=7 or any(value is None or not math.isfinite(value) or value==-999 for value in values):raise ValueError('Incomplete/invalid meteorological values')
    if any(value<0 for value in parameters['precipitation']):raise ValueError('Negative rainfall')
    return {'validated_days':7,'parameters':list(parameters),'temporal_scope':f'{expected[0]} to {expected[-1]}','municipal_coverage_verified':False}


def execute(offline:bool=False) -> dict[str,object]:
    """Test configured public endpoints independently, preserving acquisition evidence and blockers."""
    configuration=json.loads((ROOT/'config/weather-candidates.json').read_text())
    context=Context(ROOT/'data/raw',offline);checks=[]
    for provider in configuration['providers']:
        first=len(context.artifacts)
        try:
            context.fetch(provider['documentation_url'],provider['id']+'_documentation.html')
            context.fetch(provider['terms_url'],provider['id']+'_policy.html')
            response=json.loads(context.fetch(provider['probe_url'],provider['filename']).read_text())
            check={'id':provider['id'],'status':'sample_verified',**validate(provider['id'],response)}
            end=datetime.now(timezone.utc).date()-timedelta(days=10)
            recent=[(end-timedelta(days=6-offset)).isoformat() for offset in range(7)]
            url=urlsplit(provider['probe_url']);query=dict(parse_qsl(url.query))
            if provider['id']=='open_meteo_archive':query.update(start_date=recent[0],end_date=recent[-1])
            else:query.update(start=recent[0].replace('-',''),end=recent[-1].replace('-',''))
            recent_url=urlunsplit((url.scheme,url.netloc,url.path,urlencode(query),url.fragment))
            recent_payload=json.loads(context.fetch(recent_url,provider['id']+'_recent_'+end.isoformat()+'.json').read_text())
            check['recent_probe']=validate(provider['id'],recent_payload,recent)
            check['updateability']='Historical and recent sample dates both returned complete data; future availability is not guaranteed'
        except Exception as error:
            check={'id':provider['id'],'status':'blocked','blocker':f'{type(error).__name__}: {error}'}
        checks.append({**check,'artifacts':context.artifacts[first:],'municipal_publication':'Not integrated: reviewed points/boundaries and aggregation method are still required'})
    report={'checked_at':utc_now(),'mode':'offline-raw' if offline else 'live','reference_point':configuration['reference_point'],'providers':checks}
    (ROOT/'data/weather-verification.json').write_text(json.dumps(report,indent=2)+'\n')
    return report


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--offline',action='store_true')
    arguments=parser.parse_args();print(json.dumps(execute(arguments.offline),indent=2))
