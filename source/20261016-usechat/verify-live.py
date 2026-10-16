import re,json,subprocess
from pathlib import Path
base='https://blog.mushroom.cv'
pairs=[('usechat-wechat-agent-runtime','20261016-usechat','UseChat exposes a visible local','We did not install the native Helper','485c8080a0594d1fda5194556ac6da73a5e209a0'),('h3c-minimax-h3-metal-inference','20261016-h3c','h3.c is a native MiniMax-H3','We did not download MiniMax-H3 weights','8974cc055ea9c02fcd14cc27dfda3e1027c05153')]
def get(url,name):
 p=Path('/tmp/current-live-'+name);s=subprocess.check_output(['curl','-LsS','--compressed','-o',str(p),'-w','%{http_code}',url],text=True);return int(s),p.read_bytes()
for slug,folder,en,scope,pin in pairs:
 s,b=get(base+'/blog/'+slug+'/','article');h=b.decode();assets=sorted(set(re.findall(r'(?:src|href)="([^" ]*'+slug+r'[^" ]*\.(?:webp|jpg|png))"',h)));r={'url':base+'/blog/'+slug+'/','status':s,'images':[]}
 for i,a in enumerate(assets):
  u=base+a if a.startswith('/') else a;c,d=get(u,'asset'+str(i));r['images'].append({'url':u,'status':c,'bytes':len(d)})
 _,l=get(base+'/blog/','list');links=list(dict.fromkeys(re.findall(r'/blog/[a-zA-Z0-9-]+/',l.decode())));r['listPosition']=links.index('/blog/'+slug+'/')+1 if '/blog/'+slug+'/' in links else None;r['englishColumn']='language:en' in h and en in h;r['documentedScope']=scope in h;r['pinnedSourceInArticle']=pin in h;Path('source',folder,'live-verification.json').write_text(json.dumps(r,indent=2));print(json.dumps(r));assert r['status']==200 and all(r[k] for k in ['englishColumn','documentedScope','pinnedSourceInArticle']);assert len(r['images'])==4 and all(x['status']==200 for x in r['images']) and r['listPosition'] is not None
