"""Discover official soil workbooks and retain annual/multi-year net changes separately."""
from copy import deepcopy
import re
from urllib.parse import urljoin
from openpyxl import load_workbook
from etl.acquisition import Context
from etl.models import AdapterResult, Observation
from etl.adapters.ispra_soil import LANDING_URL,LICENSE_EVIDENCE_URL,METADATA,measurement


def parse_series(path) -> AdapterResult:
    """Read real workbook dimensions and source-defined interval headers before normalization."""
    workbook=load_workbook(path,read_only=True,data_only=True)
    try:
        sheets=[name for name in workbook.sheetnames if re.fullmatch(r'Comuni_\d{4}_\d{4}',name)]
        if len(sheets)!=1:raise ValueError('Ambiguous municipal soil worksheet')
        sheet=workbook[sheets[0]];sheet.reset_dimensions();rows=sheet.iter_rows(values_only=True);headers=next(rows)
        columns={str(value):i for i,value in enumerate(headers)}
        total_fields=[name for name in columns if re.fullmatch(r'Suolo consumato \d{4} \[ettari\]',name)]
        if len(total_fields)!=1:raise ValueError('Ambiguous total soil year')
        year=re.search(r'\d{4}',total_fields[0]).group()
        pct=f'Suolo consumato {year} [%]'
        if pct not in columns or not {'PRO_COM','Nome_Provincia'}.issubset(columns):raise ValueError('Soil schema changed')
        net=[(field,*re.search(r'(\d{4})-(\d{4})',field).groups()) for field in columns if re.fullmatch(r'Incremento netto \d{4}-\d{4} \[ettari\]',field)]
        if not net:raise ValueError('No net-change intervals')
        observations=[];seen=set();period_notes={}
        for row in rows:
            code=str(row[columns['PRO_COM']]).removesuffix('.0').zfill(6)
            if not code.startswith('064'):continue
            if row[columns['Nome_Provincia']]!='Avellino' or code in seen:raise ValueError('Invalid/duplicate soil geography')
            seen.add(code)
            for field,metric in [(total_fields[0],'soil_consumed_ha'),(pct,'soil_consumed_pct')]:
                observations.append(Observation(code,metric,year,*measurement(row[columns[field]])))
            for field,start,end in net:
                metric='soil_net_change_ha' if int(end)-int(start)==1 else 'soil_net_multiyear_ha'
                period_notes[end]=f'Net change over {start}–{end}; interval length {int(end)-int(start)} years.'
                observations.append(Observation(code,metric,end,*measurement(row[columns[field]])))
        if len(seen)!=118:raise ValueError('Soil municipal coverage changed')
    finally:workbook.close()
    metadata=deepcopy(METADATA)
    metadata['indicators'][2]['definition']='Source net consumed land minus restored land over one year ending in the explicit observation year. Signed values are allowed.'
    metadata['indicators'].append({'id':'soil_net_multiyear_ha','label':'Consumo netto su intervallo pluriennale','unit':'ha','allow_negative':True,
      'definition':'Source net change over the original multi-year interval; observation period is its end year. Never compare with annual net change without accounting for interval duration.'})
    metadata.update({'period':f'2006–{year}','period_notes':period_notes,'notes':'Official workbook cells; annual and multi-year changes are separate metrics. Only the latest year has consumed-stock hectares/percentage in this extract. Signed restoration values are preserved; no synthetic past stock is reconstructed.'})
    return AdapterResult(metadata,observations)


def run(context:Context) -> AdapterResult:
    """Use the currently linked definitive workbook and independently check licence evidence."""
    landing=context.fetch(LANDING_URL,'ispra_landing.html').read_text()
    links=re.findall(r'href="([^\"]*consumo_di_suolo_estratto_dati_(\d{4})_anni_\d{4}_(\d{4})\.xlsx)"',landing)
    if not links:raise ValueError('Official linked soil workbook discovery failed')
    link,edition,year=max(links,key=lambda item:int(item[2]));url=urljoin(LANDING_URL,link)
    license_text=context.fetch(LICENSE_EVIDENCE_URL,'ispra_license.html').read_text()
    if 'CC BY 3.0 IT' not in license_text:raise ValueError('ISPRA reuse licence changed')
    result=parse_series(context.fetch(url,f'ispra_soil_edition_{edition}.xlsx'))
    result.metadata['download_url']=url
    return result
