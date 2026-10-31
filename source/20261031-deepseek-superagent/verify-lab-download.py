from pathlib import Path
from zipfile import ZipFile
from io import BytesIO
import urllib.request,json,hashlib,datetime
p=Path(__file__).resolve().parent
manifest=json.loads((p/'lab-package.json').read_text())
u='https://blog.mushroom.cv'+manifest['download']
r=urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':'Mycelium-Publish-Verification','Cache-Control':'no-cache'}),timeout=45)
b=r.read();assert r.status==200;assert hashlib.sha256(b).hexdigest()==manifest['sha256']
with ZipFile(BytesIO(b)) as z:
 for name in manifest['files']:assert z.read('lab/'+name)==(p/'lab'/name).read_bytes()
report={'checkedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'url':u,'status':r.status,'bytes':len(b),'sha256':manifest['sha256'],'allFilesMatch':True}
(p/'lab-download-verification.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
