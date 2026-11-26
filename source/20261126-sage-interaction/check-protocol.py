"""Read-only fixture checks against pinned upstream protocol.py; no model/API calls."""
import asyncio, importlib.util, json, os, sys, unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch, AsyncMock
root=Path(sys.argv[1] if len(sys.argv)>1 else '/tmp/sage-interaction-research-20261126')
sys.argv=sys.argv[:1]
spec=importlib.util.spec_from_file_location('sage_protocol',root/'demo/sage_demo/protocol.py');p=importlib.util.module_from_spec(spec);spec.loader.exec_module(p)
class Protocol(unittest.TestCase):
 def test_delegate_trim(self):self.assertEqual(p.delegate_query('{"query":"  check fixtures  "}'),'check fixtures')
 def test_delegate_missing(self):
  with self.assertRaises(ValueError):p.delegate_query('{}')
 def test_delegate_extra(self):
  with self.assertRaises(ValueError):p.delegate_query('{"query":"x","tool":"shell"}')
 def test_delegate_type(self):
  with self.assertRaises(ValueError):p.delegate_query('{"query":9}')
 def test_delegate_empty(self):
  with self.assertRaises(ValueError):p.delegate_query('{"query":" "}')
 def test_delegate_oversize(self):
  with self.assertRaises(ValueError):p.delegate_query(json.dumps({'query':'x'*6001}))
 def test_headers_key(self):
  with patch.dict(os.environ,{'SAGE_BACKEND_API_KEY':'fixture-key'}):self.assertEqual(p.backend_headers(),{'Authorization':'Bearer fixture-key'})
 def test_headers_missing(self):
  with patch.dict(os.environ,{'SAGE_BACKEND_API_KEY':''}):
   with self.assertRaises(ValueError):p.backend_headers()
 def test_headers_control(self):
  with patch.dict(os.environ,{'SAGE_BACKEND_API_KEY':'x\ny'}):
   with self.assertRaises(ValueError):p.backend_headers()
 def test_timer_english(self):self.assertEqual(p.parse_timer_request('Remind me in two minutes'),120)
 def test_timer_half(self):self.assertEqual(p.parse_timer_request('TimeSpeak task: remind me after half a minute'),30)
 def test_timer_ordinary(self):self.assertIsNone(p.parse_timer_request('What is the weather?'))
 def test_timer_chinese(self):self.assertIsNone(p.parse_timer_request('两分钟后提醒我'))
 def test_event_roundtrip(self):
  payload,e=p.tool_event('fixture','x','中文');self.assertEqual(json.loads(e.split('\n',1)[1].removesuffix('<|im_end|>')),payload)
class Response:
 def __init__(self,content='{"content":"fixture answer"}',finish='stop'):self.content=content;self.finish=finish
 def raise_for_status(self):pass
 def json(self):return {'choices':[{'message':{'content':self.content},'finish_reason':self.finish}],'model':'fixture-local'}
class Client:
 def __init__(self,response=None):self.calls=[];self.response=response or Response()
 async def post(self,url,**kw):self.calls.append((url,kw));return self.response
class Backend(unittest.IsolatedAsyncioTestCase):
 async def asyncSetUp(self):
  self.tmp=TemporaryDirectory();self.prompt=Path(self.tmp.name)/'prompt';self.prompt.write_text('Answer in {{MAX_CHARS}} chars')
  self.cfg=json.loads((root/'demo/config.example.json').read_text());self.cfg.update(backend_prompt=str(self.prompt),backend_base_url='http://127.0.0.1:9999/v1',backend_model_name='fixture-local')
 async def asyncTearDown(self):self.tmp.cleanup()
 async def call(self,c,q='fixture request'):
  with patch.dict(os.environ,{'SAGE_BACKEND_API_KEY':'fixture-key'}):return await p.ask_backend(c,self.cfg,'fixture-task',q)
 async def test_local_endpoint_contract(self):
  c=Client();r=await self.call(c);self.assertEqual(c.calls[0][0],'http://127.0.0.1:9999/v1/chat/completions');self.assertEqual(c.calls[0][1]['json']['response_format']['type'],'json_schema');self.assertEqual(r['payload']['content'],'fixture answer')
 async def test_length_exhaustion(self):
  with self.assertRaises(ValueError):await self.call(Client(Response(finish='length')))
 async def test_wrong_answer_schema(self):
  with self.assertRaises(ValueError):await self.call(Client(Response('{"text":"x"}')))
 async def test_long_answer(self):
  with self.assertRaises(ValueError):await self.call(Client(Response(json.dumps({'content':'x'*181}))))
 async def test_timer_no_http(self):
  c=Client()
  with patch('asyncio.sleep',new_callable=AsyncMock) as wait:r=await self.call(c,'Remind me in two seconds')
  wait.assert_awaited_once_with(2.0);self.assertEqual(c.calls,[]);self.assertTrue(r['scheduled']);self.assertEqual(r['payload']['event'],'time_up')
 async def test_timer_too_far(self):
  c=Client();r=await self.call(c,'Remind me in fifteen minutes');self.assertEqual(r['error'],'reminder_too_far');self.assertEqual(c.calls,[])
unittest.main(verbosity=2)
