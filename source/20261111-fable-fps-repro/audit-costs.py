from pathlib import Path
from decimal import Decimal,ROUND_HALF_UP
import csv,json,sys,tempfile,shutil,subprocess,os
root=Path(sys.argv[1] if len(sys.argv)>1 else '/tmp/fable-fps-research');rows=list(csv.DictReader((root/'data/metrics.tsv').open(),delimiter='\t'));out=[]
for r in rows:
 n=lambda k:int(r[k]);total=n('input_uncached')+n('write_5m')+n('write_1h')+n('write_other')+n('cache_read');assert total==n('input_total')
 cost=(Decimal(n('input_uncached'))*8+Decimal(n('write_5m')+n('write_other'))*10+Decimal(n('write_1h'))*16+Decimal(n('cache_read'))*Decimal('.2')+Decimal(n('output'))*40)/1000000
 no=(Decimal(total)*8+Decimal(n('output'))*40)/1000000
 rounded=lambda x:str(x.quantize(Decimal('.01'),rounding=ROUND_HALF_UP));assert rounded(cost)==r['cost_recalc']==r['cost_usd'];assert rounded(no)==r['cost_no_cache']
 out.append({'run':r['run'],'cost':rounded(cost),'uncachedCounterfactual':rounded(no),'inputTotal':total,'cacheHitPercent':round(n('cache_read')/total*100,1),'turns':n('turns'),'sec':n('sec')})
with tempfile.TemporaryDirectory(prefix='fps-metrics-audit-') as d:
 t=Path(d);(t/'scripts').mkdir();(t/'data').mkdir();shutil.copy(root/'scripts/metrics.py',t/'scripts/metrics.py');shutil.copy(root/'data/metrics.tsv',t/'data/metrics.tsv');subprocess.run([sys.executable,str(t/'scripts/metrics.py')],check=True,capture_output=True);empty=(t/'data/metrics.tsv').read_text().splitlines();assert len(empty)==1
 (t/'bin').mkdir();(t/'prompts').mkdir();(t/'prompts/probe.md').write_text('synthetic local probe');(t/'prompts/builder_system.md').write_text('synthetic local system');stub=t/'bin/claude';stub.write_text('#!/bin/sh\nprintf \'{"error":"synthetic"}\'\nexit 7\n');stub.chmod(0o700);shutil.copy(root/'scripts/run.sh',t/'scripts/run.sh')
 probe=subprocess.run(['/bin/zsh','scripts/run.sh','probe','prompts/probe.md','5m','1'],cwd=t,env={**os.environ,'PATH':str(t/'bin')+':'+os.environ['PATH']},capture_output=True,text=True);assert probe.returncode==0 and 'exit=7' in (t/'runs/wall.log').read_text()
 wrapper={'scope':'Fake claude executable in isolated temp PATH; no model call','wrapperExitCode':probe.returncode,'syntheticModelExitCode':7,'wallLogRecordsFailure':True}
print(json.dumps({'scope':'Arithmetic check of published aggregates using stated per-million prices8/10/16/.2/40; not actual invoices or a generation benchmark','rows':out,'rawRunJSONPublished':bool(list((root/'runs').glob('*.json'))),'metricsEmptyInputOverwritesWithHeader':len(empty)==1,'sourceTSVUnmodified':True,'wrapperProbe':wrapper},indent=2))
