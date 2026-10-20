"""Fetch a fixed public revision and execute its existing targeted checks in a temp directory."""
from pathlib import Path
import concurrent.futures,json,subprocess,tempfile,urllib.request
pin='3499a60c6fc67ff8b7d86e4c41e7b7607b850b39';repo='Ethannju/ascii-portrait'
def get(url):return urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'MyceliumResearch'}),timeout=60).read()
tree=json.loads(get(f'https://api.github.com/repos/{repo}/git/trees/{pin}?recursive=1'))
with tempfile.TemporaryDirectory(prefix='ascii-portrait-check-')as d:
 root=Path(d)
 def fetch(entry):
  if entry['type']!='blob':return
  p=root/entry['path'];p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(get(f"https://raw.githubusercontent.com/{repo}/{pin}/{entry['path']}"))
 with concurrent.futures.ThreadPoolExecutor(max_workers=6)as pool:list(pool.map(fetch,tree['tree']))
 for name in ['motion-export','runtime-regressions','select-regressions','server-regressions']:
  subprocess.run(['node',str(root/'tests'/(name+'.mjs'))],cwd=root,check=True)
