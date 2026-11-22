from pathlib import Path
import json,urllib.request,datetime
p=Path(__file__).parent
old=json.loads((p/'catalog-before.json').read_text())['posts'];before={x['url']for x in old}
local=json.loads(Path('dist/agent-feed-index.json').read_text())['posts'];missing=sorted(before-{x['url']for x in local});assert not missing,missing
r=urllib.request.urlopen(urllib.request.Request('https://blog.mushroom.cv/agent-feed-index.json',headers={'User-Agent':'Mycelium-Publish-Verification','Cache-Control':'no-cache'}),timeout=45);live=json.load(r)['posts'];missing=sorted(before-{x['url']for x in live});assert not missing,missing
s={'checkedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'priorLiveRoutes':len(before),'localRoutes':len(local),'liveRoutes':len(live),'missingPriorRoutes':missing};(p/'catalog-preservation.json').write_text(json.dumps(s,indent=2));print(s)
