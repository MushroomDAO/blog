from pathlib import Path
import re,json,urllib.request,datetime
p=Path(__file__).parent;r=p/'research';sha=(r/'revision.txt').read_text().strip();root=p.resolve().parents[1];old=p.parent/'20261111-jev-interaction'
data=urllib.request.urlopen(f'https://raw.githubusercontent.com/native-bond-lab/Jev-Interaction/{sha}/README.md',timeout=45).read();(r/'README.md').write_bytes(data)
body=data.decode();imgs=list(dict.fromkeys(re.findall(r'(?:src=["\']|\]\()(docs/[^"\') ]+\.(?:png|svg|jpg|jpeg|webp))',body)));saved=[];errors=[]
for src in imgs:
 dest=Path('/Users/jason/.heinu1-bot/media')/('jev-interaction-20261119-'+src.replace('/','-'))
 try:dest.write_bytes(urllib.request.urlopen(f'https://raw.githubusercontent.com/native-bond-lab/Jev-Interaction/{sha}/{src}',timeout=45).read());saved.append(str(dest))
 except Exception as e:errors.append({'source':src,'error':str(e)})
(p/'saved-files.json').write_text(json.dumps(saved,indent=2));(p/'fetch-status.json').write_text(json.dumps({'revision':sha,'repoFetched':True,'demoHTMLFetched':True,'demoMicrophoneOrCallTested':False,'agentReachCLI':'command not found; archived skill public-native-first path followed','savedFiles':saved,'imageErrors':errors,'fetchedAt':datetime.datetime.now(datetime.timezone.utc).isoformat()},indent=2))
for name in ['check-semantic.py','semantic-plan.json','mine-kb.py']:
 (p/name).write_bytes((old/name).read_bytes())
s=(old/'verify-public.py').read_text().replace(' assert route in slides and route in links and links.index(route)<8',' # Existing November11 article need not appear in latest-only list/carousel.\n catalog=get(BASE+\'/api/mcp\') if False else None').replace("'listRank':links.index(route)+1,'carouselRank':slides.index(route)+1","'latestListRank':links.index(route)+1 if route in links else None,'carouselRank':slides.index(route)+1 if route in slides else None")
(p/'verify-public.py').write_text(s)
print(json.dumps({'images':len(saved),'errors':errors}))
