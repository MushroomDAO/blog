"""Check pinned source statements and saved public result counts; not a benchmark."""
from pathlib import Path
import json,urllib.request,hashlib
b=Path(__file__).resolve().parent
sources={
 'onetake':{'cases/clawd-desktop-19s/README.md':['film only','not','126 BPM','571 frames']},
 'ondine':{'README.md':['210-byte','MIT'],'bench/comparison.md':['127','612 vectors','327.86','562.99','14 small types']},
 'live-panel-skill':{'README.md':['illustrative','not covered by the MIT grant','window.seek(t)']},
 'awesome-animation-datasets':{'README.md':['44 datasets','2,355 hours','45 human datasets','CC BY 4.0'],'docs/assets/quality.json':[]},
}
rows=[]
for name,files in sources.items():
 m=json.loads((b/(name+'-meta.json')).read_text())
 for file,needles in files.items():
  url='https://raw.githubusercontent.com/'+m['repo']+'/'+m['pin']+'/'+file;data=urllib.request.urlopen(url,timeout=30).read();text=data.decode();assert all(x in text for x in needles),(file,needles)
  if file.endswith('quality.json'):
   x=json.loads(text);assert len(x['datasets'])==45 and len(x['thresholds'])==9 and x['share']==0.25
  rows.append({'url':url,'sha256':hashlib.sha256(data).hexdigest(),'checked':needles})
(b/'source-recheck.json').write_text(json.dumps({'sourceReviewOnly':True,'sources':rows},ensure_ascii=False,indent=2));print('Pinned source statements PASS; no performance measurement')
