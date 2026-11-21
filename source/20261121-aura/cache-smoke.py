from pathlib import Path
import importlib.util,json,hashlib,torch
repo=Path('/tmp/aura-20261121');file=repo/'aura/kv_cache.py';spec=importlib.util.spec_from_file_location('aura_cache_audit',file);mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
c=mod.KVCache(num_layers=2,num_heads=2,head_dim=3,tokens_per_frame=2,frames_per_block=4,window=2,segment_frames=20,ref_rope_offset=30,rope_max_block=3,device='cpu',dtype=torch.float32)
ptrs=[t.data_ptr() for t in c.k+c.v];shapes=[list(t.shape)for t in c.k+c.v];checks=0
for r in range(100):
 lo,hi=c.slot()
 for t in c.k:t[:,lo:hi]=r+1
 for t in c.v:t[:,lo:hi]=-(r+1)
 b=c.block_tokens
 assert torch.all(c.k[0][:,:b]==1) and torch.all(c.v[1][:,:b]==-1)
 if r>=2:assert torch.all(c.k[0][:,b:2*b]==r) and torch.all(c.v[0][:,b:2*b]==-r)
 assert torch.all(c.k[1][:,lo:hi]==r+1)
 assert [t.data_ptr()for t in c.k+c.v]==ptrs
 assert [list(t.shape)for t in c.k+c.v]==shapes
 if r>=3:
  assert c.query_frame_indices()==[12,13,14,15,30]
  assert c.key_frame_indices()==[0,1,2,3,8,9,10,11,12,13,14,15,30]
 checks+=1;c.advance()
result={'passed':True,'iterations':checks,'properties':['anchor retained','oldest nonanchor evicted/latest predecessor retained','current slot writable','K/V both correct','storage pointers and shapes fixed','bounded RoPE indices'],'torch':torch.__version__,'device':'CPU float32 synthetic tensors','scope':'Direct import of unmodified upstream KVCache only. No diffusion/VAE/audio/modelweights/GPU/speed/memorypeak or end-to-end audio streaming test. Torch2.14 outside project declared2.6to2.8; not fullruntimecompatibilityproof.','sourceRevision':'c06aa7dc8b850405273345089da521454ffd607e','sourceSHA256':hashlib.sha256(file.read_bytes()).hexdigest()};Path(__file__).with_name('cache-smoke-results.json').write_text(json.dumps(result,indent=2));print(json.dumps(result))
