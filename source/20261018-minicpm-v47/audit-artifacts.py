"""Inspect captured metadata and a 64KiB GGUF prefix; never loads model tensors."""
from pathlib import Path
import json,struct,hashlib
b=Path(__file__).resolve().parent;raw=(b/'gguf-prefix.bin').read_bytes();pos=0

def read(fmt):
 global pos
 n=struct.calcsize('<'+fmt)
 if pos+n>len(raw):raise EOFError()
 v=struct.unpack_from('<'+fmt,raw,pos);pos+=n;return v[0] if len(v)==1 else v

def string():
 global pos
 n=read('Q')
 if pos+n>len(raw):raise EOFError()
 out=raw[pos:pos+n].decode();pos+=n;return out

def value(t):
 formats={0:'B',1:'b',2:'H',3:'h',4:'I',5:'i',6:'f',7:'?',10:'Q',11:'q',12:'d'}
 if t in formats:return read(formats[t])
 if t==8:return string()
 if t==9:
  typ=read('I');n=read('Q');a=[]
  for _ in range(n):
   v=value(typ)
   if len(a)<4:a.append(v)
  return {'type':typ,'length':n,'first4':a}
 raise ValueError(t)
assert len(raw)==65536 and raw[:4]==b'GGUF';pos=4;version=read('I');nt=read('Q');nk=read('Q');meta={};done=0
try:
 for _ in range(nk):
  key=string();typ=read('I');v=value(typ);meta[key]=v;done+=1
except EOFError:pass
c=json.loads((b/'config.json').read_text())['text_config']
for key,other in [('expert_count','num_experts'),('expert_used_count','num_experts_per_tok'),('block_count','num_hidden_layers')]:assert meta['qwen35moe.'+key]==c[other]
out={'downloadedPrefixBytes':len(raw),'prefixSha256':hashlib.sha256(raw).hexdigest(),'version':version,'tensorCount':nt,'declaredMetadataEntries':nk,'parsedEntries':done,'partialHeaderOnly':True,'metadata':{k:v for k,v in meta.items() if not k.startswith('tokenizer.')},'crossCheckConfig':{'experts':c['num_experts'],'selectedPerToken':c['num_experts_per_tok'],'layers':c['num_hidden_layers'],'passed':True},'fullWeightsDownloaded':False,'fullWeightIntegrityVerified':False,'inferenceExecuted':False};(b/'gguf-header-verification.json').write_text(json.dumps(out,ensure_ascii=False,indent=2))
tree=json.loads((b/'gguf-tree.json').read_text());names=['MiniCPM-V-4_7-35B-A3B-Q4_K_M.gguf','MiniCPM-V-4_7-35B-A3B-mix_q3gud_im.gguf','mmproj-model-f16.gguf','mmproj-model-f16-4x.gguf','dspark-MiniCPM-V-4_7-35B-A3B-F16.gguf'];files=[{'file':r['path'],'bytes':r['size'],'decimalGB':r['size']/1e9} for r in tree if r['path'] in names];idx=json.loads((b/'weight-index.json').read_text());(b/'artifact-sizes.json').write_text(json.dumps({'standardTotalTensorBytes':idx['metadata']['total_size'],'standardShardCount':len(set(idx['weight_map'].values())),'ggufFiles':files,'units':'decimal GB not runtime memory'},indent=2));print('GGUF prefix/config agree; 40 layers,256experts,8selected. No inference.')
