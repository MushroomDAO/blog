from pathlib import Path
import json,hashlib,importlib.metadata
from jsonschema import Draft202012Validator
from referencing import Registry,Resource
out=Path(__file__).parent;schema=json.loads((out/'research/schema.json').read_text());registry=Registry().with_resource(schema['$id'],Resource.from_contents(schema));Draft202012Validator.check_schema(schema)
event=Draft202012Validator(schema,registry=registry);inputv=Draft202012Validator({'$ref':schema['$id']+'#RunAgentInput'},registry=registry)
def close(outcome):return {'type':'RUN_FINISHED','threadId':'t1','runId':'r1','outcome':outcome}
cases=[
('valid-run-start',event,{'type':'RUN_STARTED','threadId':'t1','runId':'r1','protocolVersion':'1.0'},True),
('missing-run-id',event,{'type':'RUN_STARTED','threadId':'t1'},False),
('valid-success',event,close({'type':'success'}),True),
('legacy-implicit-success',event,{'type':'RUN_FINISHED','threadId':'t1','runId':'r1'},True),
('valid-cancelled',event,close({'type':'cancelled'}),True),
('wrong-outcome-shape',event,close('cancelled'),False),
('valid-interrupt',event,close({'type':'interrupt','interrupts':[{'id':'approval-1','reason':'approval','message':'Approve this draft?'}]}),True),
('empty-interrupts',event,close({'type':'interrupt','interrupts':[]}),False),
('valid-frontend-pending',event,close({'type':'success','pendingToolCallIds':['tool-1']}),True),
('invalid-frontend-pending-id',event,close({'type':'success','pendingToolCallIds':[7]}),False),
('valid-text-start',event,{'type':'TEXT_MESSAGE_START','messageId':'m1'},True),
('end-without-prior-start-structurally-valid',event,{'type':'TEXT_MESSAGE_END','messageId':'never-opened'},True),
('resume-input',inputv,{'threadId':'t1','runId':'r2','messages':[],'resume':[{'interruptId':'approval-1','status':'resolved','payload':{'approved':True}}]},True),
('invalid-resume-status',inputv,{'threadId':'t1','runId':'r2','messages':[],'resume':[{'interruptId':'approval-1','status':'yes'}]},False)]
rows=[]
for name,v,obj,expected in cases:
 errors=list(v.iter_errors(obj));actual=not errors;assert actual==expected,(name,errors[:1]);rows.append({'case':name,'expectedValid':expected,'actualValid':actual})
r={'cases':len(rows),'passed':len(rows),'schemaSha256':hashlib.sha256((out/'research/schema.json').read_bytes()).hexdigest(),'jsonschemaVersion':importlib.metadata.version('jsonschema'),'results':rows,'scope':'Strict schema-shape checks only. Lone end event passes by design; no lifecycle or interoperability conformance claimed. No provider calls/network during validation.'};(out/'schema-smoke-result.json').write_text(json.dumps(r,indent=2));print(json.dumps(r))
