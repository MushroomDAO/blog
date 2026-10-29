"""Compare all visible text and ordered image identities after WeChat HTML rewrites."""
import json,sys,hashlib
from html.parser import HTMLParser
from urllib.parse import urlsplit
class Content(HTMLParser):
 def __init__(self):super().__init__(convert_charrefs=True);self.text=[];self.images=[]
 def handle_data(self,data):self.text.append(data)
 def handle_starttag(self,tag,attrs):
  if tag=='img':
   a=dict(attrs);u=urlsplit(a.get('data-src')or a.get('src')or '');p=u.path.rsplit('/',1)[0]
   self.images.append({'identity':u.netloc.lower()+p,'alt':a.get('alt','')})
d=json.load(sys.stdin);a=Content();b=Content();a.feed(d['local']);b.feed(d['remote']);x=''.join(a.text);y=''.join(b.text)
print(json.dumps({'fullTextMatches':x==y,'imageIdentitiesMatch':a.images==b.images,'imageCount':len(b.images),'localTextHash':hashlib.sha256(x.encode()).hexdigest(),'remoteTextHash':hashlib.sha256(y.encode()).hexdigest()}))
