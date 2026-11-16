from pathlib import Path
import subprocess,json,os,http.server,threading,functools,time
s=Path(__file__).resolve().parent;root=Path('/tmp/deepseek-chat-demo-20261116/dist');logs=[]
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(http.server.SimpleHTTPRequestHandler,directory=str(root)));threading.Thread(target=server.serve_forever,daemon=True).start()
cli='/tmp/agent-browser-smoke-20261115/node_modules/.bin/agent-browser';base=[cli,'--session','mycelium-deepseek-chat-20261116','--executable-path','/Applications/Google Chrome.app/Contents/MacOS/Google Chrome','--json'];env={**os.environ,'AGENT_BROWSER_NO_VERSION_CHECK':'1','AGENT_BROWSER_DEFAULT_TIMEOUT':'10000'}
def run(*a,required=True):
 p=subprocess.run(base+list(a),capture_output=True,text=True,env=env,timeout=40);r={'args':a,'exit':p.returncode,'stdout':p.stdout,'stderr':p.stderr};logs.append(r)
 if required:assert p.returncode==0,r
 return json.loads(p.stdout) if p.returncode==0 else r
frames=[{'type':'message_start','message':{'id':'local-fixture','type':'message','role':'assistant','model':'local-test-fixture','content':[],'stop_reason':None,'stop_sequence':None,'usage':{'input_tokens':1,'output_tokens':0}}},{'type':'content_block_start','index':0,'content_block':{'type':'text','text':''}},{'type':'content_block_delta','index':0,'delta':{'type':'text_delta','text':'LOCAL TEST '}},{'type':'content_block_delta','index':0,'delta':{'type':'text_delta','text':'RESPONSE'}},{'type':'content_block_stop','index':0},{'type':'message_delta','delta':{'stop_reason':'end_turn','title':'Local fixture'},'usage':{'output_tokens':3}},{'type':'message_stop'}]
payload=['event: '+x['type']+'\ndata: '+json.dumps(x)+'\n\n' for x in frames]
mock="""(()=>{const native=window.fetch.bind(window);window.fixtureRequests=[];const chunks=CHUNKS;window.fetch=async(input,init={})=>{const u=new URL(input instanceof Request?input.url:String(input),location.href);if(u.origin===location.origin)return native(input,init);if(u.hostname!=='api.deepseek.com')throw new Error('External request blocked by local test');window.fixtureRequests.push({path:u.pathname,method:init.method||'GET'});if(u.pathname==='/models')return new Response(JSON.stringify({data:[{id:'deepseek-flash'}]}),{headers:{'Content-Type':'application/json'}});if(u.pathname==='/anthropic/v1/messages'){const enc=new TextEncoder();return new Response(new ReadableStream({start(c){let i=0;const pump=()=>{if(i===chunks.length){c.close();return}c.enqueue(enc.encode(chunks[i++]));setTimeout(pump,30)};pump()}}),{headers:{'Content-Type':'text/event-stream'}})}throw new Error('Unimplemented local fixture endpoint '+u.pathname)};return 'Synthetic API fixture installed; no remote service calls'})()""".replace('CHUNKS',json.dumps(payload))
try:
 run('network','route','https://**','--abort')
 run('open',f'http://127.0.0.1:{server.server_port}/index.html')
 initial=run('snapshot','-i');(s/'initial-snapshot.json').write_text(json.dumps(initial,ensure_ascii=False,indent=2))
 run('eval',mock)
 refs=initial['data']['refs'];settings=[k for k,v in refs.items() if v.get('role')=='button' and v.get('name','').lower() in ['settings','设置']]
 has_input=run('eval',"!!document.querySelector('input[type=password]')")['data']['result']
 if not has_input and settings:run('click','@'+settings[0])
 run('fill','input[type=password]','local-fixture-key')
 run('press','Enter');run('wait','500')
 run('press','Escape')
 snap=run('snapshot','-i');(s/'after-settings-snapshot.json').write_text(json.dumps(snap,ensure_ascii=False,indent=2))
 run('fill','textarea','LOCAL TEST PROMPT')
 run('press','Enter');run('wait','--text','LOCAL TEST RESPONSE')
 result=run('eval',"JSON.stringify({keyStored:localStorage.getItem('chat-demo:api-key')==='local-fixture-key',fixtureRequests:window.fixtureRequests,bodyHasResponse:document.body.innerText.includes('LOCAL TEST RESPONSE')})")
 run('screenshot',str(s/'local-fixture-screenshot.png'))
 run('reload');run('wait','500')
 persisted=run('eval',"(async()=>{const db=await new Promise((res,rej)=>{const r=indexedDB.open('chat-demo');r.onsuccess=()=>res(r.result);r.onerror=()=>rej(r.error)});const sessions=await new Promise((res,rej)=>{const r=db.transaction('sessions').objectStore('sessions').getAll();r.onsuccess=()=>res(r.result);r.onerror=()=>rej(r.error)});const found=JSON.stringify(sessions).includes('LOCAL TEST RESPONSE');db.close();return JSON.stringify({keyStored:localStorage.getItem('chat-demo:api-key')==='local-fixture-key',sessionCount:sessions.length,responseInIndexedDB:found})})()")
 a=json.loads(result['data']['result']);b=json.loads(persisted['data']['result']);assert a['keyStored'] and a['bodyHasResponse'] and b['keyStored'] and b['responseInIndexedDB']
 report={'scope':'Unmodified production build, isolated headless Chrome, local HTTP with synthetic fetch/SSE fixture and externalHTTPS blocked; no real API key/account/request, no actual DeepSeek response or CORS validation','result':result,'afterReload':persisted,'checks':{'keySavedThroughUI':True,'syntheticSSEDisplayed':True,'reloadPreservesIndexedDBResponse':True}}
finally:
 run('close',required=False);server.shutdown();(s/'browser-commands.json').write_text(json.dumps(logs,ensure_ascii=False,indent=2))
(s/'browser-smoke-results.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print(json.dumps(report,ensure_ascii=False))
