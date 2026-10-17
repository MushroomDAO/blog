import re,json,subprocess
from pathlib import Path
base='https://blog.mushroom.cv';folder=Path('source/20261017-d2r-kinex-glimpse')
checks=[('d2r-mobile-build-ios-macos','d2r-mobile-build packages Apple-platform','We did not download game resources','e92853236714bbf96642faadd781dccf29da9c9c'),('kinex-coding-agents-robot-harness','Kinex connects coding agents','We did not install native drivers','15207927c6669fe98f1213a3fd05148e0fe938d3'),('glimpse-visual-reasoning-game-bug-review','Glimpse is worth examining','We did not call its paid API','https://elorian.ai/blog/introducing-glimpse')]
def get(url,name):
 p=Path('/tmp/batch-current-live-'+name);s=subprocess.check_output(['curl','-LsS','--compressed','-o',str(p),'-w','%{http_code}',url],text=True);return int(s),p.read_bytes()
_,lb=get(base+'/blog/','list');links=list(dict.fromkeys(re.findall(r'/blog/[a-zA-Z0-9-]+/',lb.decode())));reports=[]
for slug,en,scope,pin in checks:
 s,b=get(base+'/blog/'+slug+'/','article');h=b.decode();assets=sorted(set(re.findall(r'(?:src|href)="([^" ]*'+slug+r'[^" ]*\.(?:webp|jpg|png))"',h)));r={'slug':slug,'url':base+'/blog/'+slug+'/','status':s,'images':[]}
 for i,a in enumerate(assets):
  u=base+a if a.startswith('/') else a;c,d=get(u,'asset'+str(i));r['images'].append({'url':u,'status':c,'bytes':len(d)})
 r['listPosition']=links.index('/blog/'+slug+'/')+1 if '/blog/'+slug+'/' in links else None;r['englishColumn']='language:en' in h and en.replace('’','&#39;') in h or ('language:en' in h and en in h);r['documentedScope']=scope in h;r['pinnedSourceInArticle']=pin in h
 assert s==200 and all(r[k] for k in ['englishColumn','documentedScope','pinnedSourceInArticle']) and r['listPosition'] is not None,r
 assert len(r['images'])==4 and all(x['status']==200 for x in r['images']);reports.append(r);print(slug,'200,4assets200,list',r['listPosition'])
folder.joinpath('live-verification.json').write_text(json.dumps({'articles':reports},indent=2))
