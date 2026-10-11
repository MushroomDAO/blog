import json,time,urllib.request
from pathlib import Path
BASE='http://127.0.0.1:18973'
ROOT=Path(__file__).parent
weather={'type':'function','function':{'name':'get_weather','description':'Get current weather for a city.','parameters':{'type':'object','properties':{'city':{'type':'string'},'unit':{'type':'string','enum':['celsius','fahrenheit']}},'required':['city','unit'],'additionalProperties':False}}}
add={'type':'function','function':{'name':'add','description':'Add two integer values exactly.','parameters':{'type':'object','properties':{'a':{'type':'integer'},'b':{'type':'integer'}},'required':['a','b'],'additionalProperties':False}}}
tests=[
('single-add','Use the add tool to add 17 and 25.',[add],[('add',{'a':17,'b':25})]),
('single-weather-zh','请调用天气工具查询上海天气，单位用摄氏度。城市参数必须写 Shanghai。',[weather],[('get_weather',{'city':'Shanghai','unit':'celsius'})]),
('parallel-weather','Call the weather tool for Bangkok and Tokyo, both in celsius. Make both calls in one response.',[weather],[('get_weather',{'city':'Bangkok','unit':'celsius'}),('get_weather',{'city':'Tokyo','unit':'celsius'})]),
('parallel-mixed','In one response, call add for 12 and 30 and call get_weather for Paris in celsius.',[add,weather],[('add',{'a':12,'b':30}),('get_weather',{'city':'Paris','unit':'celsius'})])]
for i in range(90):
 try:
  with urllib.request.urlopen(BASE+'/health',timeout=3) as r:
   if json.load(r).get('status')=='ok':break
 except Exception:pass
 time.sleep(2)
else: raise RuntimeError('server not ready within 180s')
results=[]
for name,prompt,tools,expected in tests:
 payload={'model':'saluki','messages':[{'role':'user','content':prompt}],'tools':tools,'temperature':0,'max_tokens':256,'chat_template_kwargs':{'enable_thinking':False},'parallel_tool_calls':True,'stream':False}
 req=urllib.request.Request(BASE+'/v1/chat/completions',data=json.dumps(payload).encode(),headers={'Content-Type':'application/json'})
 started=time.monotonic()
 try:
  with urllib.request.urlopen(req,timeout=150) as r:response=json.load(r)
  msg=response['choices'][0]['message'];actual=[]
  for call in msg.get('tool_calls',[]):
   f=call['function'];actual.append((f['name'],json.loads(f['arguments'])))
  norm=lambda x: sorted(json.dumps(item,sort_keys=True,ensure_ascii=False) for item in x)
  passed=norm(actual)==norm(expected)
  result={'name':name,'passed':passed,'seconds':round(time.monotonic()-started,3),'request':payload,'expected':expected,'actual':actual,'response':response}
 except Exception as e:result={'name':name,'passed':False,'seconds':round(time.monotonic()-started,3),'error':str(e),'request':payload}
 results.append(result)
 ROOT.joinpath('smoke-results.json').write_text(json.dumps({'scope':'four synthetic schema/argument checks only; no real tool execution, no BFCL reproduction, no Bonsai comparison','results':results,'passed':sum(r['passed'] for r in results),'total':len(results)},ensure_ascii=False,indent=2))
 print(name,result['passed'],result.get('actual'),result['seconds'],flush=True)
