from pathlib import Path
import urllib.request,json,concurrent.futures,re,hashlib
from html.parser import HTMLParser
s=Path('source/20261025-town-townie-research')
class Text(HTMLParser):
 def __init__(self):super().__init__();self.skip=0;self.out=[]
 def handle_starttag(self,t,a):
  if t in ['script','style','nav','header','footer']:self.skip+=1
  if not self.skip and t in ['p','div','h1','h2','h3','h4','li','tr','section','article','br']:self.out.append('\n')
 def handle_endtag(self,t):
  if t in ['script','style','nav','header','footer']:self.skip=max(0,self.skip-1)
  if not self.skip and t in ['p','div','h1','h2','h3','h4','li','tr','section','article']:self.out.append('\n')
 def handle_data(self,d):
  if not self.skip:self.out.append(d)
def parse(d):
 p=Text();p.feed(d);return re.sub(r'\n\s*\n+','\n',''.join(p.out)).strip()+'\n'
paths=['pricing','press/series-a','press/series-b','operate-at-the-speed-of-ai','why-we-built-town','town-redesign','group-text','text-town','how-a-townie-gets-to-know-you','trust','privacy-policy','terms-of-service','dpa','security-practices','subprocessors','ai-model-providers','docs/teams','docs/billing/plans','docs/billing/credits','docs/billing/trials','docs/safety/modes-approvals','docs/safety/security','docs/features/context-and-memory','docs/features/profiles','docs/features/wiki','docs/features/skills','docs/features/tasks','docs/features/routines','docs/features/decks','docs/features/recordings','docs/features/suggestions','docs/features/scheduling','docs/getting-started/reaching-your-townie','docs/integrations/mcp-servers','docs/routines/custom-routines/concepts/calling-agents','docs/routines/custom-routines/concepts/steps-and-caching','docs/routines/custom-routines/triggers','docs/routines/stock-routines/routine-sharing','docs/admin-setup/google-workspace','docs/admin-setup/microsoft-entra','docs/teams/billing','docs/using-town/ios','careers']
urls=['https://www.town.com/'+p for p in paths]+['https://menlovc.com/perspective/talk-of-the-town-menlo-is-co-leading-towns-108m-series-b/','https://a16z.com/announcement/investing-in-town/']
def fetch(u):
 n=u.split('://')[-1].replace('/','--').strip('-')
 try:
  r=urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':'Mozilla/5.0'}),timeout=35);d=r.read();t=parse(d.decode(errors='replace'));(s/(n+'.txt')).write_text(t);return {'url':u,'http':r.status,'finalUrl':r.url,'file':n+'.txt','htmlSHA256':hashlib.sha256(d).hexdigest(),'textBytes':len(t.encode())}
 except Exception as e:return {'url':u,'error':str(e)}
r=list(concurrent.futures.ThreadPoolExecutor(max_workers=8).map(fetch,urls));(s/'source-manifest.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n')
for a in r:print(a['url'],a.get('http',a.get('error')),a.get('textBytes',''))
