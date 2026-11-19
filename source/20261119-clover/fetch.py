from pathlib import Path
import json,urllib.request,concurrent.futures,re
p=Path(__file__).parent;r=p/'research';sha=(r/'revision.txt').read_text().strip();tree=json.loads((r/'tree.json').read_text());vendor=Path('/tmp/clover-20261119');vendor.mkdir(exist_ok=True)
paths=[x['path']for x in tree['tree']if x['type']=='blob'and(x['path'].startswith('sft/')or x['path']=='README.md')]
def one(src):
 data=urllib.request.urlopen(f'https://raw.githubusercontent.com/DiffuSpace/Clover-35B-A3B-Preview/{sha}/{src}',timeout=45).read();dest=vendor/src;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(data);return {'path':src,'bytes':len(data)}
with concurrent.futures.ThreadPoolExecutor(max_workers=6)as ex: rows=list(ex.map(one,paths))
(r/'source-files.json').write_text(json.dumps(rows,indent=2));(r/'README.md').write_bytes((vendor/'README.md').read_bytes());(r/'sft-README.md').write_bytes((vendor/'sft/README.md').read_bytes());saved=[]
for src in list(dict.fromkeys(re.findall(r'<img[^>]+src="([^"]+)"',(r/'report.html').read_text()))):
 if not re.search(r'\.(png|jpg|jpeg|svg|webp)$',src):continue
 url=urllib.request.urljoin('https://arxiv.org/html/2611.24636v1/',src);dest=Path('/Users/jason/.heinu1-bot/media')/('clover-report-20261119-'+src.rsplit('/',1)[-1]);dest.write_bytes(urllib.request.urlopen(url,timeout=45).read());saved.append(str(dest))
(p/'saved-files.json').write_text(json.dumps(saved,indent=2));print(json.dumps({'sourceFiles':len(rows),'savedImages':saved,'revision':sha}))
