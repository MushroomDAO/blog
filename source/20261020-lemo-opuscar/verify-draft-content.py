from pathlib import Path
from html.parser import HTMLParser
import json,re
from urllib.parse import urlsplit
class Content(HTMLParser):
 def __init__(self):super().__init__();self.text=[];self.images=[]
 def handle_data(self,text):self.text.append(text)
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if tag=='img':self.images.append((a.get('alt'),a.get('data-src',a.get('src'))))
def image_key(pair):
 alt,url=pair;u=urlsplit(url);parts=u.path.rsplit('/',1)
 if u.hostname=='mmbiz.qpic.cn' and parts[-1] in ['0','640']:return alt,u.hostname,parts[0],u.query
 return alt,url
b=Path(__file__).resolve().parent;a=Content();a.feed(Path('/tmp/lemo-final-actual.html').read_text());e=Content();e.feed(Path('/tmp/lemo-final-expected.html').read_text());norm=lambda p:re.sub(r'\s+','', ''.join(p.text));assert len(norm(a))>3500;assert norm(a)==norm(e);assert list(map(image_key,a.images))==list(map(image_key,e.images)) and len(a.images)==3
p=b/'draft-update-verification.json';d=json.loads(p.read_text());d.update({'readBackAllNormalizedTextMatches':True,'allThreeImageAssetIdsAndAltsMatch':True,'normalizedTextCharacters':len(norm(a)),'normalization':'HTMLParser entity decoding, whitespace ignored for text; src/data-src normalized; WeChat CDN http-to-https and size0-to640 mapped by the identical CDN asset ID.'});p.write_text(json.dumps(d,indent=2));print('complete remote body text and3images match final local render')
