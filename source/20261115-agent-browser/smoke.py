from pathlib import Path
import http.server,threading,subprocess,json,os,re
s=Path(__file__).resolve().parent
page='''<!doctype html><html><head><title>Local Agent Browser Fixture</title></head><body><h1>Demo registration</h1><form onsubmit="event.preventDefault();document.getElementById('result').textContent='Saved: '+document.getElementById('email').value"><label>Email<input id="email" type="email" required></label><button type="submit">Save demo</button></form><p id="result" role="status">Not saved</p><button disabled>Disabled action</button><button id="covered" style="position:absolute;left:20px;top:220px">Covered action</button><div id="overlay" style="position:absolute;left:0;top:200px;width:400px;height:120px;background:#ddd;z-index:10">Consent overlay</div></body></html>'''
class Handler(http.server.BaseHTTPRequestHandler):
 def do_GET(self):
  self.send_response(200);self.send_header('Content-Type','text/html');self.end_headers();self.wfile.write(page.encode())
 def log_message(self,*args):pass
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),Handler);threading.Thread(target=server.serve_forever,daemon=True).start()
cli='/tmp/agent-browser-smoke-20261115/node_modules/.bin/agent-browser'
base=[cli,'--session','mycelium-agent-browser-20261115','--executable-path','/Applications/Google Chrome.app/Contents/MacOS/Google Chrome','--json'];env={**os.environ,'AGENT_BROWSER_NO_VERSION_CHECK':'1','AGENT_BROWSER_DEFAULT_TIMEOUT':'2500'};logs=[]
def run(*args,ok=True):
 p=subprocess.run(base+list(args),capture_output=True,text=True,env=env,timeout=45);r={'args':args,'exit':p.returncode,'stdout':p.stdout,'stderr':p.stderr};logs.append(r)
 if ok:assert p.returncode==0,r
 return r
try:
 run('open',f'http://127.0.0.1:{server.server_port}')
 snap=json.loads(run('snapshot','-i')['stdout'])['data'];refs=snap['refs']
 def ref(name):return '@'+next(k for k,v in refs.items() if v['name']==name)
 run('fill',ref('Email'),'demo@example.test');run('click',ref('Save demo'));run('wait','--text','Saved: demo@example.test')
 full=run('snapshot')['stdout'];assert 'Saved: demo@example.test'in full
 disabled=run('click',ref('Disabled action'),ok=False);assert disabled['exit']!=0
 blocked=run('click',ref('Covered action'),ok=False);assert blocked['exit']!=0
 report={'package':'0.43.0','sourceCommit':'e0c121a96d3a5412e2078e0c8eba3f4d2db2b616','checks':{'interactiveSnapshotRefs':bool(refs),'fillAndSubmitLocalForm':True,'statusReadback':True,'disabledActionRejected':True,'coveredActionRejected':True},'scope':'Isolated headless Chrome, synthetic local fixture; no external account, LLM, benchmark or real business transaction.','commands':logs}
finally:
 run('close',ok=False);server.shutdown();(s/'smoke-log.json').write_text(json.dumps(logs,ensure_ascii=False,indent=2))
(s/'smoke-results.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print(json.dumps(report['checks']))
