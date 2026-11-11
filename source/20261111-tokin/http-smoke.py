"""Exercise the real HTTP gateway with a synthetic, deliberately non-roundtripping tokenizer."""
import asyncio,json,socket,sys
from pathlib import Path
import httpx2,uvicorn
repo=Path(sys.argv[1] if len(sys.argv)>1 else '/tmp/tokin-research');sys.path.insert(0,str(repo/'tests'))
from conftest import ChatML,FakeTokenizer,Engine,END
from tokin import Gateway,Session
from tokin.rollout import Generation,FinishReason
from tokin.server import Server

SPECIAL=900001
class NonRoundtripTokenizer(FakeTokenizer):
 def decode(self,ids,skip_special_tokens=False):return ''.join('ok' if i==SPECIAL else chr(i) for i in ids)

async def main():
 tok=NonRoundtripTokenizer();engine=Engine(Generation([SPECIAL,ord(END)],FinishReason.STOP,[-.1,-.2]),Generation([ord('a'),ord(END)],FinishReason.STOP,[-.3,-.4]),Generation([ord('b'),ord(END)],FinishReason.STOP,[-.5,-.6]))
 app=Server(Gateway(ChatML(tok),engine)).app
 sock=socket.socket();sock.bind(('127.0.0.1',0));sock.listen();port=sock.getsockname()[1]
 server=uvicorn.Server(uvicorn.Config(app,log_level='error'));task=asyncio.create_task(server.serve(sockets=[sock]))
 try:
  for _ in range(100):
   if server.started:break
   await asyncio.sleep(.01)
  assert server.started
  async with httpx2.AsyncClient(base_url=f'http://127.0.0.1:{port}') as c:
   sid=(await c.post('/sessions',json={'params':{'return_logprobs':True}})).raise_for_status().json()['id'];ep=f'/sessions/{sid}/v1/chat/completions'
   start=[{'role':'user','content':'hi'}];r=(await c.post(ep,json={'model':'fake','messages':start})).raise_for_status().json();msg=r['choices'][0]['message'];assert msg['content']=='ok'
   probe=await c.post(ep,json={'model':'fake','messages':start+[msg,{'role':'user','content':'probe'}]});assert probe.status_code==400 and 'tool_calls' in probe.text
   msg={k:v for k,v in msg.items() if v is not None}
   for question in ['again','branch']:
    (await c.post(ep,json={'model':'fake','messages':start+[msg,{'role':'user','content':question}]})).raise_for_status()
   prefix=engine.calls[0][0]+[SPECIAL,ord(END)];assert all(ids[:len(prefix)]==prefix for ids,_ in engine.calls[1:]);assert tok.encode(tok.decode([SPECIAL]))!=[SPECIAL]
   session=await Session.collect(c,sid);rollouts=session.rollouts;assert len(rollouts)==2
   for r in rollouts:
    pos=r.token_ids.index(SPECIAL);assert r.loss_mask[pos]==1 and abs(r.logprobs[pos]+.1)<1e-6
    assert len(r.token_ids)==len(r.loss_mask)==len(r.logprobs)
   assert (await c.get(f'/sessions/{sid}')).status_code==404
   report={'scope':'Actual localhost HTTP/FastAPI/uvicorn pipeline; fake tokenizer and engine; no model inference','httpTurns':3,'assistantNullToolCallsRejected400':True,'unusedNullFieldsRemovedForSuccessfulContinuation':True,'rolloutLeaves':len(rollouts),'nonRoundtripSampledIDPreserved':True,'branchPrefixPreserved':True,'tokenMaskLogprobAligned':True,'collectedSessionDeleted':True,'trainingOrPerformanceMeasured':False};print(json.dumps(report,indent=2))
 finally:
  server.should_exit=True;await task
asyncio.run(main())
