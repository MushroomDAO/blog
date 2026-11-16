from pathlib import Path
import subprocess,os,json,http.server,threading,time,functools
s=Path(__file__).resolve().parent;root=Path('/tmp/abyssal-garden-20261116');logs=[]
handler=functools.partial(http.server.SimpleHTTPRequestHandler,directory=str(root))
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),handler);threading.Thread(target=server.serve_forever,daemon=True).start()
cli='/tmp/agent-browser-smoke-20261115/node_modules/.bin/agent-browser';base=[cli,'--session','mycelium-abyssal-20261116','--executable-path','/Applications/Google Chrome.app/Contents/MacOS/Google Chrome','--json'];env={**os.environ,'AGENT_BROWSER_NO_VERSION_CHECK':'1','AGENT_BROWSER_DEFAULT_TIMEOUT':'15000'}
def run(*a,required=True):
 p=subprocess.run(base+list(a),capture_output=True,text=True,env=env,timeout=45);r={'args':a,'exit':p.returncode,'stdout':p.stdout,'stderr':p.stderr};logs.append(r)
 if required:assert p.returncode==0,r
 return json.loads(p.stdout) if p.returncode==0 else r
try:
 run('open',f'http://127.0.0.1:{server.server_port}/index.html')
 run('eval',"localStorage.setItem('abyssal','2'); localStorage.removeItem('abyssalLoad'); 'Low selected in isolated profile'")
 run('reload')
 state=None
 for _ in range(18):
  state=run('eval',"JSON.stringify({body:document.body.className,status:document.getElementById('s').textContent,webgpu:!!navigator.gpu,canvas:[document.getElementById('c').width,document.getElementById('c').height],userAgent:navigator.userAgent,resources:performance.getEntriesByType('resource').map(x=>x.name)})")
  d=state['data'];d=d.get('result',d) if isinstance(d,dict) else d
  if isinstance(d,str):d=json.loads(d)
  if d['body']=='m' or 'e' in d['body'].split():break
  time.sleep(2)
 report={'scope':'Isolated local HTTP page, headless installed Chrome, Low detail, no FPS benchmark or hardware comparison','startup':d,'logs':logs}
 if d['body']=='m':
  run('click','#d');run('press','6');run('press','m');run('screenshot',str(s/'local-browser-smoke.png'))
  after=run('eval',"JSON.stringify({body:document.body.className,selected:localStorage.abyssal,resources:performance.getEntriesByType('resource').map(x=>x.name)})")
  report['afterControls']=after;report['started']=True
 else:
  run('screenshot',str(s/'local-browser-smoke.png'));report['started']=False
finally:
 run('close',required=False);server.shutdown();(s/'browser-commands.json').write_text(json.dumps(logs,ensure_ascii=False,indent=2))
(s/'browser-smoke-results.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print(json.dumps({k:v for k,v in report.items() if k not in ['logs']},ensure_ascii=False))
