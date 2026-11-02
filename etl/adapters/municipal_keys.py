"""Explicit identifier crosswalks derived from the authoritative ISTAT registry."""
from pathlib import Path
import re
import unicodedata
from openpyxl import load_workbook


def normalized_name(value:str) -> str:
    """Normalize case, accents and punctuation, without fuzzy matching or inference."""
    return re.sub(r'[^a-z0-9]','',unicodedata.normalize('NFKD',value.casefold()).encode('ascii','ignore').decode())


def cadastral_crosswalk(path:Path,codes:set[str]) -> dict[str,str]:
    """Map published cadastral codes to current ISTAT codes, requiring a bijection."""
    workbook=load_workbook(path,read_only=True,data_only=True)
    try:
        rows=workbook.active.iter_rows(values_only=True);headers=next(rows)
        cat=headers.index('Codice Catastale del Comune');code=headers.index('Codice Comune formato alfanumerico')
        result={str(row[cat]):str(row[code]).zfill(6) for row in rows if str(row[code]).zfill(6) in codes}
        if len(result)!=118 or set(result.values())!=codes:raise ValueError('Incomplete/ambiguous cadastral crosswalk')
        return result
    finally:workbook.close()


def reconcile_legacy_code(code:str,name:str,period:str,current_codes:set[str]) -> tuple[str,str]:
    """Apply only reviewed, dated official code changes to current-location records."""
    if code in current_codes:return code,'Original current ISTAT code'
    import json
    rows=json.loads((Path(__file__).resolve().parents[2]/'config/municipality-crosswalks.json').read_text())['code_changes']
    matches=[row for row in rows if row['source_code']==code and normalized_name(row['source_name'])==normalized_name(name)
             and period>=row['effective_from'] and row['target_code'] in current_codes]
    if len(matches)!=1:raise ValueError(f'No reviewed current-location crosswalk for {code}/{name}')
    return matches[0]['target_code'],'Reviewed official municipal fusion crosswalk; original source code retained'
