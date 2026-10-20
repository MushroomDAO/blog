"""Fetch pinned Rust workspace sources and rerun the tested configurations."""
from pathlib import Path
import concurrent.futures,json,subprocess,tempfile,urllib.request
pin='14b4e42d4972239eb86adfdc036ed78508d7ec30';repo='OriEra-engine/engine'
def get(url):return urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'MyceliumResearch'}),timeout=45).read()
tree=json.loads(get(f'https://api.github.com/repos/{repo}/git/trees/{pin}?recursive=1'));assert not tree.get('truncated')
with tempfile.TemporaryDirectory(prefix='oriera-v03-check-')as d:
 root=Path(d)
 def fetch(x):
  if x['type']!='blob'or not x['path'].endswith(('.rs','.toml','.lock')):return
  p=root/x['path'];p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(get(f"https://raw.githubusercontent.com/{repo}/{pin}/{x['path']}"))
 with concurrent.futures.ThreadPoolExecutor(max_workers=8)as ex:list(ex.map(fetch,tree['tree']))
 lock=Path(__file__).with_name('tested-Cargo.lock')
 if lock.exists():(root/'Cargo.lock').write_bytes(lock.read_bytes())
 for args in [['test','--workspace','--locked'],['test','-p','oriera-genai','--features','providers','--locked'],['run','-p','oriera-genai','--example','hotswap','--locked']]:subprocess.run(['cargo',*args],cwd=root,check=True)
