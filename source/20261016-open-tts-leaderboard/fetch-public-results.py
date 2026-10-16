import json,time
from urllib.request import urlopen,Request
from pathlib import Path
base='https://hf-audio-open-tts-leaderboard.hf.space/gradio_api/call/'
p=Path(__file__).resolve().parent
queries={'english':('_refresh_leaderboard',['09-10-2026','',['🇬🇧 English'],['Seed-TTS','CV3-Eval'],False]),'chinese':('_refresh_leaderboard',['09-10-2026','',['🇨🇳 Chinese'],['Seed-TTS','CV3-Eval'],False]),'clone-english':('_refresh_leaderboard',['09-10-2026','',['🇬🇧 English'],['Seed-TTS','CV3-Eval'],True]),'stream-a100':('_refresh_streaming',['A100','09-10-2026','']),'stream-cpu':('_refresh_streaming',['CPU','09-10-2026',''])}
for name,(api,data) in queries.items():
 r=json.load(urlopen(Request(base+api,json.dumps({'data':data}).encode(),{'Content-Type':'application/json'})))
 s=urlopen(base+api+'/'+r['event_id'],timeout=120).read().decode();(p/(name+'-response.txt')).write_text(s)
 print(name,s[:200],flush=True)
 for chunk in s.split('\n\n'):
  if 'event: complete' in chunk:
   v=json.loads(next(l[6:] for l in chunk.splitlines() if l.startswith('data: ')));(p/(name+'.json')).write_text(json.dumps(v,ensure_ascii=False,indent=2));print(str(v[0])[:650],flush=True)
