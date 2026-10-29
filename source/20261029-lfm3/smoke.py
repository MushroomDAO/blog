"""A bounded text-only functional check, not an accuracy or throughput benchmark."""
import datetime,json,urllib.request
from pathlib import Path
URL='http://127.0.0.1:18788/v1/chat/completions'
cases=[
 {'id':'arithmetic','system':'Return only the final answer.','prompt':'What is 17 + 25? Reply with just the integer.','expected':'42'},
 {'id':'chinese-routing','system':'你只做分类。只输出 billing、shipping 或 technical 中的一个词。billing指扣费和退款，shipping指配送，technical指软件故障。','prompt':'这笔订单被重复扣款，请退还多收的钱。','expected':'billing'},
 {'id':'structured-extraction','system':'Return only a JSON object with keys name and quantity. Do not add explanations.','prompt':'Order: 3 notebooks. Extract name as notebooks and quantity as integer.','expected':{'name':'notebooks','quantity':3}},
]
results=[]
for case in cases:
 payload={'messages':[{'role':'system','content':case['system']},{'role':'user','content':case['prompt']}],'temperature':0.0,'top_k':50,'repeat_penalty':1.1,'max_tokens':96,'seed':42,'stream':False}
 req=urllib.request.Request(URL,data=json.dumps(payload,ensure_ascii=False).encode(),headers={'Content-Type':'application/json'})
 d=json.load(urllib.request.urlopen(req,timeout=90));text=d['choices'][0]['message'].get('content','').strip()
 try:observed=json.loads(text) if isinstance(case['expected'],dict) else text
 except Exception:observed=text
 ok=observed==case['expected'];result={'case':case,'request':payload,'output':text,'observed':observed,'matched':ok,'usage':d.get('usage'),'finishReason':d['choices'][0].get('finish_reason')};results.append(result);print(case['id'],repr(text),'matched',ok,flush=True)
out={'checkedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'purpose':'short text functional smoke only; three manually selected synthetic prompts; not a benchmark','contextConfigured':4096,'parallel':1,'results':results,'matched':sum(x['matched'] for x in results),'total':len(results)}
Path(__file__).with_name('smoke-results.json').write_text(json.dumps(out,ensure_ascii=False,indent=2))
