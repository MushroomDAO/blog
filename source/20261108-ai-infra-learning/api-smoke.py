from pathlib import Path
import sys,importlib.util,json,platform,importlib.metadata
from fastapi.testclient import TestClient
root=Path(sys.argv[1] if len(sys.argv)>1 else '/tmp/ai-infra-learning-research');p=root/'projects/project-101-basic-model-serving/src/api.py';spec=importlib.util.spec_from_file_location('curriculum_api',p);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
responses=[]
with TestClient(module.app)as c:
 for method,path,kwargs in [('GET','/',{}),('GET','/health',{}),('GET','/metrics',{}),('POST','/predict',{'files':{'file':('fixture.png',b'synthetic test fixture','image/png')}}),('POST','/predict',{})]:
  r=c.request(method,path,**kwargs);responses.append({'method':method,'path':path,'status':r.status_code,'body':r.json(),'contentType':r.headers.get('content-type')})
 model_loaded=hasattr(module.app.state,'model')
assert responses[0]['status']==200
assert responses[1]['status']==200 and responses[1]['body']=={}
assert responses[2]['status']==200 and responses[2]['body']=={'message':'Metrics endpoint not implemented'}
assert responses[3]['status']==501 and responses[4]['status']==422 and not model_loaded
out={'python':platform.python_version(),'packages':{k:importlib.metadata.version(k)for k in ['fastapi','pydantic','httpx','python-multipart','starlette']},'requests':responses,'modelAttributeInitialized':model_loaded,'scope':'Five requests through TestClient against unmodified upstream project101 API with startup/shutdown; synthetic upload only, no socket server, model weights, Docker, Kubernetes, cloud, GPU, load benchmark or full dependency environment.'}
Path(__file__).with_name('api-smoke-result.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
