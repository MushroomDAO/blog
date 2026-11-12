"""Read pinned public source evidence; does not execute LayerFS or benchmarks."""
from pathlib import Path
import urllib.request,json,hashlib
pin='2aaf2552ce21154928b9f9c83582e41a637f5910';root='https://raw.githubusercontent.com/Ephemeral-AI-Lab/layerfs/'+pin+'/'
checks={
'LICENSE':['MIT License'],
'sdk/js/README.md':['Linux only','ext4, xfs, btrfs','An Exec message describes that execution and creates','workspace.commit(ws'],
'dsh/README.md':['22.19','Docker'],
'benchmark/pjdfstest/records/20261019T224251Z.md':['707 assertions','432 as cascades','atime is not kept apart from mtime'],
'benchmark/fio/records/20261020T000148Z.md':['0.31×','Disposable fsync does not','6.9×'],
}
rows=[]
for path,needles in checks.items():
 data=urllib.request.urlopen(root+path).read();text=data.decode();assert all(x in text for x in needles),(path,needles);rows.append({'path':path,'url':root+path,'sha256':hashlib.sha256(data).hexdigest(),'statementsVerified':needles})
r={'pin':pin,'sourceReviewOnly':True,'noDockerAvailable':True,'runtimeTested':False,'performanceMeasuredByUs':False,'banner':'FLUX157; official assets reviewed were animated schematic SVG panels/logo, not photographic hero','sources':rows,'reportedRatioArithmeticOnly':{'fsBench':round(8.88/5.20,2),'dedup':round(1994.6/100.1,2)}}
Path(__file__).with_name('source-review.json').write_text(json.dumps(r,ensure_ascii=False,indent=2));print('Pinned source review PASS; no runtime or benchmark reproduction')
