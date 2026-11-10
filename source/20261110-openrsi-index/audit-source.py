from pathlib import Path
import json,hashlib,sys,tomllib
from rsi_harness.task.compiler import HarborTaskCompiler
from rsi_harness.models import CompileOptions
root=Path(sys.argv[1]);out=Path(__file__).parent
files=list(root.joinpath('rsi-tasks').rglob('task.toml'));compiled=[]
for name in ['gemm-h100-refined','minference-sparse-prefill','signature-tasks/post-training-qwen-122B-rl']:
 d=HarborTaskCompiler().compile(root/'rsi-tasks'/name,CompileOptions());compiled.append({'path':name,'taskId':d.task_id,'workdir':str(d.workdir),'gpus':d.gpu_requirement.count,'taskDigest':d.source_digest})
assets=[]
expected={'shared_base':(29406658,'ca6df1b9b9791e8509c87da0314350a05867e5fd647fddc4ccb3813494134990'),'anchor_intervention':(28972820,'946affd59232b7d6bcf7db55965e580c0b2561234c1f36b8c85b434345a90467')}
for name in ['shared_base','anchor_intervention']:
 p=root/'rsi-tasks/signature-tasks/post-training-qwen-122B-rl/environment/assets/data'/f'{name}.jsonl';b=p.read_bytes();rows=[json.loads(l)for l in b.splitlines()if l.strip()];assets.append({'file':name+'.jsonl','rows':len(rows),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()});assert len(rows)==2560;assert (len(b),hashlib.sha256(b).hexdigest())==expected[name]
r={'commit':'8d170deed4591fc7e4306f2d86ff4d9bcffd1288','taskManifestCount':len(files),'manifestCountIsNotPortableTaskCount':True,'compiledOnlyNoContainers':compiled,'qwenDataFiles':assets,'scope':'Read-only TOML/JSONL/hash audit plus actual HarborTaskCompiler; no Docker/GPU/model/network or full Judge execution.'};(out/'source-audit.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r))
