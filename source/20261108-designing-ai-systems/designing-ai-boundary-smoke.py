import asyncio,json,shutil
from pathlib import Path
import httpx
from proto import tools_pb2
from services.tools.service import ToolServiceImpl
from services.data.service import DataService
from services.data.store import InMemoryVectorStore
class Context:
 def set_code(self,c):raise AssertionError(str(c))
 def set_details(self,s):raise AssertionError(s)
async def main():
 calls=[]
 def reply(req):
  calls.append({'url':str(req.url),'method':req.method});return httpx.Response(200,json={'synthetic':True})
 async with httpx.AsyncClient(transport=httpx.MockTransport(reply))as client:
  svc=ToolServiceImpl(http_client=client);tool=tools_pb2.ToolDefinition(name='fixture.write',endpoint='https://fixture.invalid/action');tool.behavior.requires_confirmation=True
  await svc.RegisterTool(tools_pb2.RegisterToolRequest(tool=tool),Context());r=await svc.ExecuteTool(tools_pb2.ExecuteToolRequest(tool_name='fixture.write',arguments_json='{}'),Context());assert r.success and len(calls)==1 and svc.registry.get('fixture.write').behavior.requires_confirmation
 data=DataService(vector_store=InMemoryVectorStore(),worker_count=0)
 try:
  a=data._embedding_generator.embed_query('synthetic question one','fixture');b=data._embedding_generator.embed_query('different synthetic question','fixture');assert a==b and all(v==0 for v in a)
 finally:
  data.close();p=Path(data._plugin_dir);assert p.name.startswith('data_plugins_');shutil.rmtree(p)
 report={'commit':'94dd7ecdd02de7c1289bb81765deeaaa23dffcee','syntheticChecksPassed':2,'directToolExecution':{'requiresConfirmationMetadata':True,'mockEndpointReachedWithoutApprovalArtifact':True,'requests':calls},'defaultDataServiceEmbedding':{'dimensions':len(a),'allZero':True,'differentQueriesEqual':True},'modelCalls':0,'externalHTTPRequests':0,'scope':'MockTransport only; isolated service objects. Not a full security audit or deployed-stack test. Approval may be enforced by separate callers; this verifies the direct ExecuteTool path only.'}
 Path('/tmp/designing-ai-boundary-result.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
asyncio.run(main())
