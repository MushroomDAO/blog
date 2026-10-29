"""Follow up a visible-answer truncation; retain the initial failure separately."""
from pathlib import Path
import json,urllib.request,datetime
initial=json.load(open(Path(__file__).with_name('smoke-results.json')))
payload=initial['results'][2]['request'].copy();payload['max_tokens']=512
req=urllib.request.Request('http://127.0.0.1:18788/v1/chat/completions',data=json.dumps(payload).encode(),headers={'Content-Type':'application/json'})
d=json.load(urllib.request.urlopen(req,timeout=90));m=d['choices'][0]['message'];text=m.get('content','').strip()
try:observed=json.loads(text)
except Exception:observed=text
out={'checkedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'reason':'Initial JSON prompt exhausted 96 generated tokens before a visible final answer. Only max_tokens changed, to 512. Initial failure retained.','request':payload,'response':d,'observed':observed,'matched':observed==initial['results'][2]['case']['expected']}
Path(__file__).with_name('budget-followup.json').write_text(json.dumps(out,ensure_ascii=False,indent=2));print(json.dumps({'message':m,'usage':d.get('usage'),'finishReason':d['choices'][0]['finish_reason'],'matched':out['matched']},ensure_ascii=False))
