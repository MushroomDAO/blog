from pathlib import Path
import tempfile,subprocess,threading,urllib.request,urllib.error,importlib.util,json
repo=Path('/tmp/shipmygame-research');spec=importlib.util.spec_from_file_location('ship_cors',repo/'skills/ship-my-game/scripts/serve_cors.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
with tempfile.TemporaryDirectory(prefix='shipmygame-fixture-')as d:
 p=Path(d).resolve();root=p/'public';root.mkdir();(root/'sample.txt').write_text('PUBLIC_TEST_ONLY');(p/'outside.txt').write_text('OUTSIDE_TEST_ONLY');(root/'outside-link.txt').symlink_to(p/'outside.txt')
 from http.server import ThreadingHTTPServer
 server=ThreadingHTTPServer(('127.0.0.1',0),m.make_handler(str(root),{'https://console.example.test'}));th=threading.Thread(target=server.serve_forever,daemon=True);th.start();url=f'http://127.0.0.1:{server.server_port}'
 results=[]
 try:
  for path,origin,status,cors in [('/sample.txt','https://console.example.test',200,True),('/sample.txt','https://other.example.test',200,False),('/outside-link.txt','https://console.example.test',404,True),('/','https://console.example.test',404,True)]:
   try:r=urllib.request.urlopen(urllib.request.Request(url+path,headers={'Origin':origin}));code=r.status
   except urllib.error.HTTPError as e:r=e;code=e.code
   body=r.read();has=r.headers.get('Access-Control-Allow-Origin')==origin;assert code==status and has==cors
   if code==200:assert body==b'PUBLIC_TEST_ONLY'
   results.append({'path':path,'status':code,'allowOriginPresent':has})
 finally:server.shutdown();server.server_close();th.join()
 gen=repo/'skills/ship-taptap-minigame/scripts/make_privacy_page.py';inp=p/'policy.txt';out=p/'index.html';inp.write_text('privacy_title={{GAME}}\nprivacy={{GAME}} policy\\n一、测试\\n<script>fixture</script>\n');r=subprocess.run(['python3',str(gen),str(inp),'--out',str(out)],capture_output=True,text=True);assert r.returncode!=0 and not out.exists();rejected=True
 inp.write_text('privacy_title=Fixture Game\nprivacy=Fixture Game policy\\n一、测试\\n<script>fixture</script>\n');r=subprocess.run(['python3',str(gen),str(inp),'--out',str(out)],capture_output=True,text=True);assert r.returncode==0 and '&lt;script&gt;fixture&lt;/script&gt;'in out.read_text()
 scan=p/'scan.txt';scan.write_text('contact: reviewer@fixture.invalid\n');r=subprocess.run(['python3',str(repo/'tools/privacy_scan.py'),str(scan)],capture_output=True,text=True);assert r.returncode==1 and 'email:'in r.stdout
 report={'http':results,'unresolvedPlaceholderRejected':rejected,'filledTemplateRenderedWithEscaping':True,'syntheticEmailDetected':True,'allDataSelfOwnedSynthetic':True,'noUnityNoBrowserNoAccountsNoUpload':True,'CORSnote':'disallowedOriginStillReceivesHTTP200Body;browserCORSrestrictionIsNotAuthentication'}
 Path('/tmp/shipmygame-smoke-result.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
