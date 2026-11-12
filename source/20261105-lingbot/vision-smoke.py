from pathlib import Path
import sys,json,hashlib,platform
sys.path[:0]=['/tmp/lingbot-smoke-deps','/tmp/lingbot-vision-research']
import torch
from lingbot_vision import load_pretrained_backbone,extract_patch_tokens,load_image
j=Path('/Users/jason/.heinu1-bot/jobs/48e58ed8-e40a-411a-aa49-d0539f3bfe54');api=json.loads((j/'small-model-api.json').read_text());torch.set_num_threads(4)
b,e=load_pretrained_backbone(variant='small',device='cpu',dtype=torch.float32,revision=api['sha'],cache_dir='/tmp/lingbot-smoke-model-cache')
x,_,_=load_image('/tmp/lingbot-vision-research/examples/example.png',size=224,patch_size=b.patch_size,mode='square')
y,g=extract_patch_tokens(b,x,'cpu',torch.float32)
r={'sourceCommit':'151e46321bae4399f8568829f190c7bdec216b49','model':'robbyant/lingbot-vision-vit-small','modelRevision':api['sha'],'platform':platform.platform(),'torch':torch.__version__,'device':'cpu','dtype':'float32','inputShape':list(x.shape),'outputShape':list(y.shape),'patchGrid':list(g),'embedDim':e,'parameters':sum(p.numel()for p in b.parameters()),'finite':bool(torch.isfinite(y).all()),'scope':'one real pretrained backbone forward, not depth/robot/world evaluation'}
assert r['finite'] and list(y.shape)==[1,196,384];(j/'vision-smoke-result.json').write_text(json.dumps(r,indent=2));print(json.dumps(r))
