"""Measure built static imports, not an end-to-end network benchmark."""
from pathlib import Path
import re,gzip,json,sys,subprocess
root=Path(sys.argv[1]if len(sys.argv)>1 else'/tmp/livliv-player-research').resolve();dist=root/'dist'
seen=set();external=set()
def visit(p):
 p=p.resolve()
 if p in seen:return
 seen.add(p)
 text=p.read_text()
 for name in re.findall(r'(?:from\s*|import\s*)[\"\']([^\"\']+)[\"\']',text):
  if name.startswith('.'):visit(p.parent/name)
  else:external.add(name)
visit(dist/'index.js')
files=[{'file':str(p.relative_to(dist)),'bytes':p.stat().st_size,'gzip9Bytes':len(gzip.compress(p.read_bytes(),compresslevel=9,mtime=0))}for p in sorted(seen)]
packages=[{'file':p.name,'bytes':p.stat().st_size}for p in sorted((root/'characters').glob('*.livliv'))]
r={'codeCommit':subprocess.check_output(['git','-C',str(root),'rev-parse','HEAD'],text=True).strip(),'coreStaticClosure':files,'externalCoreImports':sorted(external),'coreGzip9SumBytes':sum(x['gzip9Bytes']for x in files),'characterPackageCount':len(packages),'characterPackages':packages,'characterPackageTotalBytes':sum(x['bytes']for x in packages),'method':'gzip9 each required static JS module separately, mtime0; sum; excludes optional modules, models, images, face runtime and network headers; no FPS or memory benchmark'}
out=Path(__file__).with_name('bundle-audit.json');out.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
assert not external and len(packages)==21
