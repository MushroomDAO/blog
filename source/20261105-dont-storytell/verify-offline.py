from pathlib import Path
import json,subprocess,sys,importlib.util,collections,hashlib,copy
r=Path('/tmp/dont-storytell-research');out=Path('/Users/jason/.heinu1-bot/jobs/e631f0be-5f05-4971-a55b-1ab968dce657');out.mkdir(parents=True,exist_ok=True)
rows=json.loads((r/'references/casebook.json').read_text());report={'sourceRevision':'d4840723dac3234e901aed94192b43f98b4c40eb','caseCount':len(rows),'uniqueIDs':len({x['id']for x in rows}),'subjects':len({x['subject']for x in rows}),'signCounts':dict(collections.Counter(x['sign']for x in rows)),'checks':[]}
assert len(rows)==112 and len({x['id']for x in rows})==112
report['checks'].append('112 unique case IDs and source/limitation fields present')
assert all(x.get('url','').startswith(('http://','https://')) and x.get('locator') and x.get('limit')for x in rows)
for args,expected in [(['--tag','治理','--sign','反例','--limit','3'],0),(['--id','E001'],0),(['--limit','0'],2),(['--id','NO-SUCH-CASE'],2)]:
 p=subprocess.run([sys.executable,str(r/'scripts/find_cases.py'),*args],text=True,capture_output=True);assert p.returncode==expected;(out/('case-cli-'+str(len(report['checks']))+'.txt')).write_text(p.stdout+p.stderr);report['checks'].append({'cliArgs':args,'expectedExit':expected,'actualExit':p.returncode})
p=subprocess.run([sys.executable,str(r/'scripts/render_strategy.py'),str(r/'examples/neighborhood-magazine.json'),str(out/'official-example.html')],text=True,capture_output=True);assert p.returncode==0
s=(out/'official-example.html').read_text();assert '虚构示范' in s and '街区杂志' in s and '@media print' in s
report['checks'].append('Official schema-3 example renders with fiction label and print CSS')
spec=importlib.util.spec_from_file_location('render_strategy',r/'scripts/render_strategy.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);sample=json.loads((r/'examples/neighborhood-magazine.json').read_text());sample['title']='<script>alert(1)</script>';html=m.render(sample);assert '<script>alert(1)</script>'not in html and '&lt;script&gt;alert(1)&lt;/script&gt;'in html;report['checks'].append('Synthetic title HTML escaped')
bad=copy.deepcopy(sample);bad['sources']=[{'label':'synthetic link','url':'javascript:alert(1)'}]
try:m.render(bad)
except ValueError:report['checks'].append('Synthetic javascript source URL rejected')
else:raise AssertionError('unsafe scheme accepted')
bad=copy.deepcopy(sample);bad['schema']=99
try:m.render(bad)
except ValueError:report['checks'].append('Unknown renderer schema rejected')
else:raise AssertionError('unknown schema accepted')
report.update(checkGroups=len(report['checks']),modelCalled=False,browserRenderingTested=False,consultingQualityTested=False,outputSha256=hashlib.sha256(s.encode()).hexdigest());Path('source/20261105-dont-storytell/offline-verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps(report,ensure_ascii=False))
