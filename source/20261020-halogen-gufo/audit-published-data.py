"""Validate published table consistency, not engine speed or underlying timing accuracy."""
from pathlib import Path
import json,re,hashlib
b=Path(__file__).resolve().parent
raw=b/'gufo--docs__models__qwen3.8-flash-next__artifacts__single-ar-gufo.json';doc=b/'gufo--docs__models__qwen3.8-flash-next__BENCHMARKS.md';d=json.loads(raw.read_text());section=doc.read_text().split('<!-- bench:single-ar -->')[1].split('<!-- /bench -->')[0]
parsed={}
for line in section.splitlines():
 fields=[x.strip()for x in line.strip().strip('|').split('|')]
 if fields and re.fullmatch(r'[0-9,]+',fields[0]):parsed[int(fields[0].replace(',',''))]={'pp':float(fields[1]),'tg':float(fields[4])}
checks=[]
for depth,row in sorted(d['rows'].items(),key=lambda x:int(x[0])):
 depth=int(depth);assert row['pp']==parsed[depth]['pp'] and row['tg']==parsed[depth]['tg'];assert row['samples']==len(row['counts'])
 for c in row['counts']:
  assert abs(c['prompt_n']-2048)<=max(32,2048*.005)
  assert abs(c['cache_n']-depth)<=max(32,depth*.005)
  assert c['predicted_n']==128 and c['draft_n']==0 and c['draft_n_accepted']==0
  checks.append({'nominalDepth':depth,'cachedTokens':c['cache_n'],'newPromptTokens':c['prompt_n'],'outputTokens':c['predicted_n'],'reportedPP':row['pp'],'reportedARDecode':row['tg'],'documentationMatchesJSON':True,'measuredSamples':row['samples']})
r={'sourceRevision':'877518953c153b2aac57f7b77fc904e8540b1fde','publisherMeasuredOn':d['measuredOn'],'sourceSHA256':hashlib.sha256(raw.read_bytes()).hexdigest(),'rowsChecked':len(checks),'rows':checks,'scope':'Published JSON/table/count consistency only. Full raw phase timings are not in this JSON. No engine execution, hardware, inference, correctness or latency reproduction.','illustrativeArithmetic':{'promptTokens':10000,'assumedPP':1800,'idealPrefillSeconds':10000/1800,'outputTokens':1000,'assumedDecode':40,'idealDecodeSeconds':1000/40,'scope':'Hypothetical rates for explanation, excludes all extra overhead and cache effects; not measured.'}}
assert len(checks)==8;(b/'published-data-audit.json').write_text(json.dumps(r,indent=2));print('8 published rows match; prefix/new-token counts distinguished. No inference executed.')
