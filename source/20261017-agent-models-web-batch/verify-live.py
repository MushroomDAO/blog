import re,json,subprocess
from pathlib import Path
base='https://blog.mushroom.cv';folder=Path('source/20261017-agent-models-web-batch')
checks=[('nemotron-35-super-vl-bolt-local-models','NVIDIA’s October 15 release','We downloaded no model weights','c6cc2e8ffa353403213d6b9b18aaf8eb684d705a'),('opengcua-generalist-computer-use-stack','OpenGCUA is an open stack','We installed no native driver','625b1cebde1f772328a238881121b76691b8895b'),('atticus-mac-voice-assistant','Atticus is a Mac','We tested no real speech session','0f4d8d79e3db4e9447a80deab847369423b295ad'),('indexnow-website-push-indexing-guide','IndexNow lets a website','We sent no example URLs','https://www.indexnow.org/searchengines.json')]
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
s,b=get(base+'/downloads/indexnow-payload.py','helper');assert s==200 and b==Path('public/downloads/indexnow-payload.py').read_bytes();folder.joinpath('live-verification.json').write_text(json.dumps({'articles':reports,'downloadArtifact':{'status':s,'bytes':len(b),'matchesSource':True}},indent=2))
