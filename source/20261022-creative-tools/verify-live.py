import re,json,subprocess
from pathlib import Path
base='https://blog.mushroom.cv';folder=Path('source/20261022-creative-tools')
checks=[('ondine-rust-mermaid-compiler','Ondine compiles Mermaid text into SVG','without rerunning performance','0b589ec34481856b4153526f10a0a35558a201a8'),('live-panel-skill-animated-architecture','live-panel turns a JSON system description','three tests passed','439c9addce7e7ac2b4e384aa847a351926c8f945'),('animation-datasets-motion-viewer','awesome-animation-datasets organizes motion resources','we did not download every dataset','4d4abf35b33f2b5a429671b668d83d9973da1750'),('onetake-envmanage-source-check','onetake uses a coding agent','The new description matches the official','013a61ac8d98883c73733f59c06e49e9ba444f14')]
def get(url,name):
 p=Path('/tmp/batch-current-live-'+name);s=subprocess.check_output(['curl','-LsS','--compressed','-o',str(p),'-w','%{http_code}',url],text=True);return int(s),p.read_bytes()
_,lb=get(base+'/blog/','list');links=list(dict.fromkeys(re.findall(r'/blog/[a-zA-Z0-9-]+/',lb.decode())));reports=[]
for slug,en,scope,pin in checks:
 s,b=get(base+'/blog/'+slug+'/','article');h=b.decode();assets=sorted(set(re.findall(r'(?:src|href)="([^" ]*'+slug+r'[^" ]*\.(?:webp|jpg|png))"',h)));r={'slug':slug,'url':base+'/blog/'+slug+'/','status':s,'images':[]}
 for i,a in enumerate(assets):
  u=base+a if a.startswith('/') else a;c,d=get(u,'asset'+str(i));r['images'].append({'url':u,'status':c,'bytes':len(d)})
 r['listPosition']=links.index('/blog/'+slug+'/')+1 if '/blog/'+slug+'/' in links else None;r['englishColumn']='language:en' in h and en.replace('’','&#39;') in h or ('language:en' in h and en in h);r['documentedScope']=scope in h;r['pinnedSourceInArticle']=pin in h
 assert s==200 and all(r[k] for k in ['englishColumn','documentedScope','pinnedSourceInArticle']) and (r['listPosition'] is not None or slug=='onetake-envmanage-source-check'),r
 assert slug=='onetake-envmanage-source-check' or r['listPosition']<=4,r
 assert len(r['images'])==4 and all(x['status']==200 for x in r['images']);reports.append(r);print(slug,'200,4assets200,list',r['listPosition'])
folder.joinpath('live-verification.json').write_text(json.dumps({'articles':reports},indent=2))
