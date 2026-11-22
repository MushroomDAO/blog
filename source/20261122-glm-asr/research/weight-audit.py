"""Read tensor metadata and verify the pinned model hash without loading the model."""
import sys,json,struct,math,collections,hashlib
from pathlib import Path
f=Path(sys.argv[1] if len(sys.argv)>1 else '/tmp/glm-asr-model-20261122/model.safetensors')
with f.open('rb')as r:h=json.loads(r.read(struct.unpack('<Q',r.read(8))[0]))
g=collections.Counter()
for k,v in h.items():
 if k!='__metadata__':g['.'.join(k.split('.')[:2])]+=math.prod(v['shape'])
with f.open('rb')as r:sha=hashlib.file_digest(r,'sha256').hexdigest()
print(json.dumps({'bytes':f.stat().st_size,'totalElements':sum(g.values()),'byPrefix':dict(g),'sha256':sha},indent=2))
