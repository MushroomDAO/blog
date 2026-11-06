import os,subprocess,time,urllib.request,json,tempfile,pathlib
repo='/tmp/namidsh-research'; fixture=tempfile.TemporaryDirectory(prefix='nami-fixture-');p=pathlib.Path(fixture.name);(p/'fixture.txt').write_text('MYCELIUM_OFFLINE_FIXTURE')
env=os.environ.copy();env.update(PORT='13761',WORKSPACE=str(p));env.pop('API_KEY',None);env.pop('DEEPSEEK_API_KEY',None)
f=open('/tmp/namidsh-server.log','w');proc=subprocess.Popen(['npm','start'],cwd=repo,env=env,stdout=f,stderr=f)
try:
 for i in range(50):
  try: r=urllib.request.urlopen('http://127.0.0.1:13761/',timeout=1);break
  except Exception:time.sleep(.2)
 assert r.status==200
 results=[]
 for msg,tool,expected in [('现在几点？','get_time','工具返回了结果'),('项目里有哪些文件','list_dir','fixture.txt')]:
  req=urllib.request.Request('http://127.0.0.1:13761/api/chat',json.dumps({'message':msg}).encode(),headers={'Content-Type':'application/json'})
  body=urllib.request.urlopen(req,timeout=20).read().decode();events=[]
  for block in body.split('\n\n'):
   lines=block.splitlines()
   if len(lines)>=2: events.append({'event':lines[0][7:],'data':json.loads(lines[1][6:])})
  text=''.join(e['data'].get('text','')for e in events if e['event']=='delta');assert expected in text and any(e['event']=='tool'and e['data']['name']==tool for e in events)and events[-1]['event']=='done'
  results.append({'message':msg,'tool':tool,'text':text,'eventCount':len(events),'done':True})
 pathlib.Path('/tmp/namidsh-http-result.json').write_text(json.dumps({'node':subprocess.check_output(['node','--version'],text=True).strip(),'homeStatus':200,'APIKeyAbsent':True,'mockOnly':True,'results':results},ensure_ascii=False,indent=2))
 print(json.dumps(results,ensure_ascii=False))
finally:
 proc.terminate();proc.wait(timeout=10);f.close();fixture.cleanup()
