from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from html.parser import HTMLParser
from urllib.parse import urljoin
import urllib.request,json,hashlib,datetime,re
out=Path(__file__).parent;private=Path('/Users/jason/.heinu1-bot/jobs/f34863db-652b-4c32-9a3e-80d242301c4f/research')
urls={
'legacy':'https://fab.cba.mit.edu/classes/MAS.863/',
'course':'https://pub.cba.mit.edu/863.26/site/',
'application':'https://pub.cba.mit.edu/863.26/site/file/app.html',
'people':'https://pub.cba.mit.edu/863.26/site/people.html',
'principles':'https://academy.cba.mit.edu/classes/principles_practices/index.html',
'presentation':'https://academy.cba.mit.edu/classes/project_presentation/index.html',
'development':'https://academy.cba.mit.edu/classes/project_development/index.html',
'integration':'https://fabacademy.org/2026/classes/system_integration/index.html',
'ai-recitation':'https://pub.cba.mit.edu/863.26/site/recitations/AI/index.html'}
def read(pair):
 name,u=pair;r=urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':'Mycelium-Research-Verification'}),timeout=45);b=r.read();assert r.status==200;private.joinpath(name+'.html').write_bytes(b);s=b.decode('utf8');return name,{'url':u,'finalHttpUrl':r.url,'status':r.status,'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest(),'linkCount':len(re.findall(r'<a\b',s,re.I))}
reports=dict(ThreadPoolExecutor(max_workers=5).map(read,urls.items()))
legacy=(private/'legacy.html').read_text();assert 'http-equiv="refresh"'in legacy and 'https://pub.cba.mit.edu/863.26/site'in legacy
assert '2026'in (private/'course.html').read_text();assert 'Gershenfeld'in(private/'people.html').read_text();assert '80%'in(private/'application.html').read_text()and'20%'in(private/'application.html').read_text();assert 'AI Agents'in(private/'ai-recitation.html').read_text()
result={'checkedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'pages':reports,'legacyUsesMetaRefreshNotHttpRedirect':True,'verificationScope':'nine public HTML pages, source-link and key-field checks only; not hardware fabrication, lab access, full course completion or media playback'};(out/'source-verification.json').write_text(json.dumps(result,indent=2));print(json.dumps({'pages200':len(reports),'metaRefreshVerified':True,'keyFieldsVerified':True}))
