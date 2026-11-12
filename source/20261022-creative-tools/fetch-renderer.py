"""Fetch only pinned upstream files needed for renderer checks, without installing a skill."""
import urllib.request,json,concurrent.futures
from pathlib import Path
pin='439c9addce7e7ac2b4e384aa847a351926c8f945';repo='ythx-101/live-panel-skill';dst=Path('/tmp/creative-live-panel')
tree=json.load(urllib.request.urlopen('https://api.github.com/repos/'+repo+'/git/trees/'+pin+'?recursive=1'))
paths=[v['path'] for v in tree['tree'] if v['type']=='blob' and (v['path'].startswith(('scripts/','tests/')) and v['path'].endswith('.py') or v['path'].startswith('assets/') and v['path'].endswith(('.html','.js','.css')) or v['path']=='examples/minimal/config.json')]
def fetch(p):
 q=dst/p;q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(urllib.request.urlopen('https://raw.githubusercontent.com/'+repo+'/'+pin+'/'+p).read())
list(concurrent.futures.ThreadPoolExecutor(6).map(fetch,paths));print(len(paths),'files at',pin,'to',dst)
