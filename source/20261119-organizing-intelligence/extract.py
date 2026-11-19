from pathlib import Path
from html.parser import HTMLParser
import json,urllib.request,hashlib
p=Path(__file__).parent;r=p/'research'
class Extract(HTMLParser):
 def __init__(self):super().__init__();self.skip=0;self.text=[];self.images=[];self.meta={}
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if tag in ['script','style']:self.skip+=1
  if tag=='img':self.images.append(a)
  if tag=='meta':self.meta[a.get('property',a.get('name',''))]=a.get('content','')
 def handle_endtag(self,tag):
  if tag in ['script','style']:self.skip=max(0,self.skip-1)
 def handle_data(self,data):
  if not self.skip and data.strip():self.text.append(data.strip())
x=Extract();x.feed((r/'essay.html').read_text());(r/'essay.txt').write_text('\n'.join(x.text));(r/'essay-metadata.json').write_text(json.dumps({'meta':x.meta,'images':x.images},indent=2))
url=x.meta['og:image'];data=urllib.request.urlopen(url,timeout=45).read();f=Path('/Users/jason/.heinu1-bot/media/organizing-intelligence-20261119-official-cover.webp');f.write_bytes(data);(p/'saved-files.json').write_text(json.dumps([str(f)],indent=2));print(json.dumps({'cover':str(f),'images':[{'alt':i.get('alt'), 'src':i.get('src','')[:160]}for i in x.images]},ensure_ascii=False))
