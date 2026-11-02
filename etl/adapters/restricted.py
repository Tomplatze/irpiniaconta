"""Executable verification adapter for a source whose reuse/access conditions block publication."""
import re
from html import unescape
from etl.acquisition import Context
from etl.models import AdapterResult


def run(context:Context,options:dict[str,object]) -> AdapterResult:
    """Acquire current policy evidence and stop before importing protected measurements."""
    path=context.fetch(str(options['evidence_url']),str(options['evidence_filename']))
    text=path.read_text(encoding='utf-8',errors='replace')
    normalized=' '.join(unescape(re.sub(r'<[^>]+>', ' ', text)).split())
    if ' '.join(str(options['expected_policy_text']).split()) not in normalized:
        raise ValueError('Restriction evidence changed; a manual licence review is required before import')
    return AdapterResult({'id':options['dataset_id'],'name':options['title'],'publisher':options['publisher'],
      'landing_url':options['landing_url'],'download_url':None,'license':None,'license_url':options['evidence_url'],
      'format':options['format'],'geography':options['geography'],'period':'unavailable','status':'blocked',
      'blocker':options['blocker'],'notes':'Current official restriction evidence acquired; no protected measurements imported.','indicators':[]})
