"""Count root asset packages at the reviewed revision without fetching asset bytes."""
import json
import urllib.request
from urllib.parse import urlencode
REVISION='524747d9b5e1f21b5b18b56041788c01d745f1a1'
url='https://huggingface.co/api/datasets/nvidia/simready-assets/tree/'+REVISION+'?'+urlencode({'recursive':'false','limit':1000})
entries=[]
pages=0
while url:
    request=urllib.request.Request(url,headers={'User-Agent':'Mycelium-Research'})
    with urllib.request.urlopen(request,timeout=40) as response:
        entries.extend(json.load(response))
        link=response.headers.get('Link','')
    pages+=1
    url=link.split('<',1)[1].split('>',1)[0] if 'rel="next"' in link else None
print(json.dumps({'revision':REVISION,'rootDirectories':sum(x['type']=='directory' for x in entries),'rootEntries':len(entries),'pages':pages}))
