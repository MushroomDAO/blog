"""Inspect public bootstrap entries only; does not launch or download the game."""
import concurrent.futures, datetime, hashlib, json, re, urllib.request
from pathlib import Path
from urllib.parse import urljoin
BASE='https://littleprince.dev/'
b=Path(__file__).resolve().parent
req=urllib.request.Request(BASE,headers={'User-Agent':'Mozilla/5.0'})
with urllib.request.urlopen(req,timeout=30) as response:
 raw=response.read();status=response.status
s=raw.decode('utf-8');m=re.search(r'var buildUrl = "([^"]+)"',s)
if not m:raise RuntimeError('Build base changed; inspect the page before changing this parser')
names=list(dict.fromkeys(re.findall(r'/([a-f0-9]+\.(?:loader\.js|data\.br|framework\.js\.br|wasm\.br))',s)))
def head(name):
 url=urljoin(BASE,m[1].rstrip('/')+'/'+name)
 try:
  with urllib.request.urlopen(urllib.request.Request(url,method='HEAD',headers={'User-Agent':'Mozilla/5.0'}),timeout=25) as r:
   return {'url':url,'status':r.status,'headers':{k:v for k,v in r.headers.items() if k.lower() in ['content-type','content-length','content-encoding','last-modified']}}
 except Exception as error:return {'url':url,'error':str(error)}
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:files=list(executor.map(head,names))
out={'checkedAtUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'homepageStatus':status,'homepageSha256':hashlib.sha256(raw).hexdigest(),'webgpuMentioned':'WebGPU' in s,'bootstrapFiles':files,'gameplayExecuted':False,'unityOrBlenderBuildExecuted':False,'fullDataDownloaded':False}
(b/'site-verification.json').write_text(json.dumps(out,indent=2))
print(status,len(files),'bootstrap references; HEAD results:',[x.get('status',x.get('error')) for x in files]);print('No gameplay or engine build executed.')
