"""Exercise the released CLI against a deterministic loopback SSE fixture, no real LLM."""
import os,json,threading,subprocess,sys
from pathlib import Path
from http.server import ThreadingHTTPServer,BaseHTTPRequestHandler
root=Path(sys.argv[1]).resolve(); work=root/'gateway-smoke';work.mkdir(exist_ok=True);cfg=work/'config';cfg.mkdir(exist_ok=True);requests=[]
class Handler(BaseHTTPRequestHandler):
 def log_message(self,*args):pass
 def do_POST(self):
  body=json.loads(self.rfile.read(int(self.headers['Content-Length'])));requests.append(body)
  self.send_response(200);self.send_header('Content-Type','text/event-stream');self.send_header('Connection','close');self.end_headers()
  done=any(m.get('role')=='tool' for m in body['messages'])
  delta={'role':'assistant','content':'fixture complete'} if done else {'role':'assistant','tool_calls':[{'index':0,'id':'call_fixture','type':'function','function':{'name':'write','arguments':json.dumps({'path':'smoke.txt','content':'rpi deterministic tool round trip\n'})}}]}
  for item in [{'id':'fixture','object':'chat.completion.chunk','model':'fixture','choices':[{'index':0,'delta':delta,'finish_reason':None}]},{'id':'fixture','object':'chat.completion.chunk','model':'fixture','choices':[{'index':0,'delta':{},'finish_reason':'stop' if done else 'tool_calls'}]}]:self.wfile.write(('data: '+json.dumps(item)+'\n\n').encode())
  self.wfile.write(b'data: [DONE]\n\n');self.wfile.flush()
server=ThreadingHTTPServer(('127.0.0.1',0),Handler);thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
(cfg/'models.json').write_text(json.dumps({'providers':{'fixture':{'api':'openai-completions','baseUrl':f'http://127.0.0.1:{server.server_port}/v1','apiKey':'fixture-not-secret','models':[{'id':'fixture','name':'Local deterministic fixture','contextWindow':32768,'maxTokens':1024}]}}}))
env={k:v for k,v in os.environ.items()if not any(s in k for s in ['KEY','TOKEN','SECRET'])};env.update(RPI_CODING_AGENT_DIR=str(cfg),RPI_OFFLINE='1')
args=[str(root/'binary/rpi'),'--offline','--model','fixture/fixture','--no-extensions','--no-skills','--no-context-files','--no-prompt-templates','--no-session','--tools','write','--mode','json','-p','Write smoke.txt using the write tool.']
try:
 r=subprocess.run(args,env=env,cwd=work,capture_output=True,text=True,timeout=45)
 out={'exitCode':r.returncode,'requests':len(requests),'stdout':r.stdout,'stderr':r.stderr,'fileContent':(work/'smoke.txt').read_text()if(work/'smoke.txt').exists()else None,'hasToolResult':any(any(m.get('role')=='tool' for m in b['messages'])for b in requests),'scope':'deterministic local HTTP fixture, no real LLM quality or performance measured'}
 (root/'gateway-smoke.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,ensure_ascii=False))
 assert r.returncode==0 and out['fileContent']=='rpi deterministic tool round trip\n' and out['hasToolResult']
finally:server.shutdown();server.server_close()
