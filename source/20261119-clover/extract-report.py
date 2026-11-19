from pathlib import Path
import json,re,urllib.request,pymupdf
p=Path(__file__).parent;r=p/'research';html=(r/'report.html').read_text();saved=[]
for src in re.findall(r'<object[^>]+data="([^"]+)"',html):
 if not src.endswith('.svg'):continue
 dest=Path('/Users/jason/.heinu1-bot/media')/('clover-report-20261119-'+src.rsplit('/',1)[-1]);url=urllib.request.urljoin('https://arxiv.org/html/2611.24636v1',src);dest.write_bytes(urllib.request.urlopen(url,timeout=45).read());saved.append(str(dest))
sha=(r/'revision.txt').read_text().strip();dest=Path('/Users/jason/.heinu1-bot/media/clover-benchmark-20261119.png');dest.write_bytes(urllib.request.urlopen(f'https://raw.githubusercontent.com/DiffuSpace/Clover-35B-A3B-Preview/{sha}/benchmark.png',timeout=45).read());saved.append(str(dest));(p/'saved-files.json').write_text(json.dumps(saved,indent=2))
doc=pymupdf.open(r/'report.pdf');(r/'report.txt').write_text('\n'.join(page.get_text()for page in doc))
rows=[]
for n in [3,9,10,11,12,13,14,15]:
 page=doc[n];f=r/f'report-page-{n+1:02d}.png';page.get_pixmap(matrix=pymupdf.Matrix(1.3,1.3)).save(f);rows.append({'page':n+1,'file':str(f)})
(r/'page-screenshots.json').write_text(json.dumps(rows,indent=2));print(json.dumps({'pages':len(doc),'savedFiles':saved}))
