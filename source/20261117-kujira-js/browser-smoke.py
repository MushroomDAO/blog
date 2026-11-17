from pathlib import Path
import subprocess,os,json,http.server,threading,functools,time
out=Path(__file__).resolve().parent;root=Path('/tmp/kujira-js-20261117');logs=[]
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(http.server.SimpleHTTPRequestHandler,directory=str(root)));threading.Thread(target=server.serve_forever,daemon=True).start()
base=['/tmp/agent-browser-smoke-20261115/node_modules/.bin/agent-browser','--session','mycelium-kujira-20261117','--executable-path','/Applications/Google Chrome.app/Contents/MacOS/Google Chrome','--json'];env={**os.environ,'AGENT_BROWSER_NO_VERSION_CHECK':'1','AGENT_BROWSER_DEFAULT_TIMEOUT':'30000'}
def run(*args,required=True):
 p=subprocess.run(base+list(args),capture_output=True,text=True,env=env,timeout=60);r={'args':args,'exit':p.returncode,'stdout':p.stdout,'stderr':p.stderr};logs.append(r)
 if required:assert p.returncode==0,r
 return json.loads(p.stdout) if p.returncode==0 else r

def ev(js):
 r=run('eval',js);v=r.get('data');v=v.get('result',v) if isinstance(v,dict) else v
 return json.loads(v) if isinstance(v,str) else v
try:
 run('network','route','https://**','--abort')
 run('open',f'http://127.0.0.1:{server.server_port}/index.html?q=low&t=2.6')
 for _ in range(12):
  ready=ev('JSON.stringify({ready:!!window.FILM_READY})')
  if ready['ready']:break
  time.sleep(1)
 assert ready['ready']
 start=ev("JSON.stringify({ready:FILM_READY,fps:FILM.FPS,frames:FILM.FRAMES,label:document.querySelector('#lbl').textContent,canvas:[document.querySelector('#c').width,document.querySelector('#c').height],userAgent:navigator.userAgent})")
 assert start['fps']==24 and start['frames']==120 and start['canvas']==[1280,720]
 run('screenshot',str(out/'local-frame-62.png'))
 # Hash the same real WebGL canvas after visiting a different frame, within this browser only.
 frame=ev("""(async()=>{const hash=async()=>Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',new TextEncoder().encode(document.querySelector('#c').toDataURL())))).map(x=>x.toString(16).padStart(2,'0')).join('');FILM.renderFrame(62);let a=await hash();FILM.renderFrame(20);let b=await hash();FILM.renderFrame(62);let c=await hash();return JSON.stringify({frame62First:a,frame20:b,frame62Again:c,same:a===c,different:a!==b})})()""")
 assert frame['same'] and frame['different']
 run('press','ArrowRight');control=ev("JSON.stringify({label:document.querySelector('#lbl').textContent,frame:+document.querySelector('#scrub').value})");assert control['frame']==63
 audio=ev("""(async()=>{const b=await FILM.soundReady;let d=b.getChannelData(0),sum=0,finite=true;for(let i=0;i<d.length;i++){sum+=d[i]*d[i];finite=finite&&Number.isFinite(d[i]);}return JSON.stringify({duration:b.duration,sampleRate:b.sampleRate,channels:b.numberOfChannels,samples:b.length,checkedSampleChannel:0,nonzero:sum>0,finite})})()""")
 assert audio['duration']==5 and audio['sampleRate']==48000 and audio['channels']==2 and audio['nonzero'] and audio['finite']
 run('click','#play');play=ev("JSON.stringify({playing:document.body.classList.contains('playing')})");assert play['playing'];run('press',' ');pause=ev("JSON.stringify({playing:document.body.classList.contains('playing')})");assert not pause['playing']
 resources=ev("JSON.stringify(performance.getEntriesByType('resource').map(x=>x.name))")
 assert not any(x.startswith('https:') for x in resources)
 report={'scope':'Real local HTTP single HTML, isolated headless Chrome Low; no FPS/power/mobile/crossGPU/audio-listening benchmark','startup':start,'sameBrowserFrameCheck':frame,'arrowControl':control,'audioBuffer':audio,'playControl':play,'pauseControl':pause,'resourceEntries':resources,'passed':True}
finally:
 run('close',required=False);server.shutdown();(out/'browser-commands.json').write_text(json.dumps(logs,ensure_ascii=False,indent=2))
(out/'browser-smoke-results.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print(json.dumps(report,ensure_ascii=False))
