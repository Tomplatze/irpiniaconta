"""Verify original municipal boundary attributes before enabling spatial climate publication."""
import csv
import io
import json
import struct
from zipfile import ZipFile
from etl.acquisition import Context
from etl.pipeline import ROOT,replay_snapshot,utc_now
from etl.quality import validate_registry

URL='https://www.istat.it/storage/cartografia/confini_amministrativi/generalizzati/2026/Limiti01012026_g.zip'
LANDING='https://www.istat.it/notizia/confini-delle-unita-amministrative-a-fini-statistici-al-1-gennaio-2018-2/'


def dbf_records(payload:bytes) -> list[dict[str,str]]:
    """Read source DBF attributes only; geometry and CRS transformations are not inferred."""
    count=struct.unpack_from('<I',payload,4)[0]
    header_length,row_length=struct.unpack_from('<HH',payload,8)
    fields=[];offset=32
    while payload[offset]!=13:
        descriptor=payload[offset:offset+32]
        fields.append((descriptor[:11].split(b'\0')[0].decode('ascii'),descriptor[16]));offset+=32
    if sum(length for _,length in fields)+1!=row_length:raise ValueError('Unexpected DBF row layout')
    records=[]
    for index in range(count):
        row=payload[header_length+index*row_length:header_length+(index+1)*row_length]
        if len(row)!=row_length or row[:1] not in {b' ',b'*'}:raise ValueError('Truncated/invalid DBF record')
        if row[:1]==b'*':continue
        values={};position=1
        for field,length in fields:
            values[field]=row[position:position+length].decode('utf-8').strip();position+=length
        records.append(values)
    return records


def execute() -> dict[str,object]:
    """Replay an actually downloaded archive and reconcile the full current 118-code universe."""
    municipalities,_,_=replay_snapshot(ROOT/'data/snapshot.json');codes=validate_registry(municipalities)
    context=Context(ROOT/'data/raw',offline=True)
    path=context.fetch(URL,'istat_boundaries_2026.zip')
    with ZipFile(path) as archive:
        files=[name for name in archive.namelist() if name.startswith('Com01012026_g/') and name.endswith('.dbf')]
        if len(files)!=1:raise ValueError('Ambiguous municipal boundary file')
        records=[row for row in dbf_records(archive.read(files[0])) if row['PRO_COM_T'] in codes]
        if len(records)!=118 or {row['PRO_COM_T'] for row in records}!=codes:raise ValueError('Boundary/registry coverage mismatch')
        projection=archive.read(files[0].replace('.dbf','.prj')).decode('utf-8')
        encoding_file=files[0].replace('.dbf','.cpg')
        encoding=archive.read(encoding_file).decode('utf-8') if encoding_file in archive.namelist() else 'UTF-8 (publisher documentation; no CPG file in actual ZIP)'
        if encoding_file in archive.namelist() and encoding.strip().upper()!='UTF-8':raise ValueError('Unexpected DBF text encoding')
    filtered=ROOT/'data/boundary-attributes-2026.csv'
    with filtered.open('w',newline='') as stream:
        writer=csv.DictWriter(stream,fieldnames=list(records[0]));writer.writeheader();writer.writerows(records)
    report={'checked_at':utc_now(),'mode':'offline-raw','source_url':URL,'landing_url':LANDING,'original_archive':context.artifacts,
            'municipality_count':118,'identifier_field':'PRO_COM_T','projection':projection,'encoding':encoding,'attributes_file':filtered.name,
            'publication_status':'Collected and code-verified; geometry validation, representative points and climate aggregation are not implemented'}
    (ROOT/'data/geography-verification.json').write_text(json.dumps(report,indent=2)+'\n');return report


if __name__=='__main__':print(json.dumps(execute(),indent=2))
