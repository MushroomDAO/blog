import importlib.util,json,tempfile,subprocess
from pathlib import Path
p=Path('public/downloads/indexnow-payload.py');spec=importlib.util.spec_from_file_location('payload',p);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
h='www.example.com';k='0123456789abcdef0123456789abcdef';good='https://'+h+'/post/'
r=m.build_payload(h,k,[good,good]);assert len(r['urlList'])==1 and r['keyLocation']==f'https://{h}/{k}.txt'
checks=['dedup/root-key']
cases=[('scheme-host','https://www.example.com',k,[good]),('empty-key',h,'',[good]),('wrong-host',h,k,['https://other.example.com/']),('userinfo',h,k,['https://user@www.example.com/']),('port',h,k,['https://www.example.com:443/']),('fragment',h,k,[good+'#a']),('ftp',h,k,['ftp://www.example.com/']),('whitespace',h,k,[good+' ']),('empty-list',h,k,[]),('over-limit',h,k,[f'https://{h}/{i}' for i in range(10001)])]
for name,host,key,urls in cases:
 try:m.build_payload(host,key,urls)
 except ValueError:checks.append(name)
 else:raise AssertionError(name)
r=m.build_payload(h,k,[f'https://{h}/{i}' for i in range(10000)]);assert len(r['urlList'])==10000;checks.append('10000-boundary')
with tempfile.TemporaryDirectory() as d:
 target=Path(d)/'payload.json';subprocess.run(['python3',str(p),'--host',h,'--key',k,'--output',str(target),good],check=True);assert json.loads(target.read_text())['urlList']==[good];checks.append('CLI-file-output')
Path('source/20261017-agent-models-web-batch/indexnow-offline-verification.json').write_text(json.dumps({'checks':checks,'passed':len(checks),'networkRequests':0,'liveIndexingMeasured':False},indent=2));print(len(checks),'offline checks passed; no HTTP requests')
