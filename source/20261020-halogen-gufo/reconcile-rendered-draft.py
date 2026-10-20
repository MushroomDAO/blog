"""Compare local render with the read-back draft, allowing WeChat HTML normalization."""
from html.parser import HTMLParser
from pathlib import Path
import re,json,hashlib
class Content(HTMLParser):
 def __init__(self):super().__init__();self.text=[];self.images=[]
 def handle_data(self,data):self.text.append(data)
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if tag=='img':self.images.append((a.get('alt'),a.get('data-src',a.get('src'))))
b=Path(__file__).resolve().parent;root=b.parents[1];slug='strix-halo-halogen-gufo-prefill'
actual=Path('/tmp/halogen-draft-actual.html').read_text();expected=Path('/tmp/halogen-draft-expected.html').read_text();a=Content();a.feed(actual);e=Content();e.feed(expected)
norm=lambda obj:re.sub(r'\s+','', ''.join(obj.text))
assert norm(a)==norm(e) and a.images==e.images and len(a.images)==3
v=json.loads((b/'draft-verification.json').read_text());assert v['errcode']==0 and v['coverPresent'] and v['bodyImageCount']==3
p=root/'pipeline/m2/output'/f'{slug}.json';receipt=json.loads(p.read_text());assert receipt['mediaId']==v['mediaId']
receipt['updateReason']='Added cached-prefix figure via draft/update, retaining the original media_id; read back and compared all rendered text and three image URLs/alts. WeChat normalizes entities and image attributes.'
p.write_text(json.dumps(receipt,ensure_ascii=False,indent=2));(p.with_suffix('.html')).write_text(actual)
proof={'mediaId':receipt['mediaId'],'operation':'draft/update','createdNewDraft':False,'updateErrcode':0,'readBackAllNormalizedTextMatches':True,'imageURLsAndAltsMatch':True,'bodyImageCount':3,'coverPresent':v['coverPresent'],'actualHTMLSHA256':hashlib.sha256(actual.encode()).hexdigest(),'normalization':'HTMLParser entity decoding; whitespace ignored for text; img src/data-src mapped; attribute order ignored.'}
(b/'draft-update-verification.json').write_text(json.dumps(proof,indent=2));print(proof)
