import json,subprocess,struct,shutil
from pathlib import Path
from jinja2 import Environment
p=Path(__file__).parent
MODEL_REV='92ddae9fc7665e9f801d141d2e5a6b2caf2460c4'
GGUF_REV='20b439426f1e997ba575eaccaf4856ac0f76f5d5'
model='JetBrains/Mellum2.1-12B-A2.5B-Thinking'
urls={
 'model-api.json':f'https://huggingface.co/api/models/{model}/revision/{MODEL_REV}',
 'gguf-api.json':f'https://huggingface.co/api/models/{model}-GGUF/revision/{GGUF_REV}',
 'gguf-tree.json':f'https://huggingface.co/api/models/{model}-GGUF/tree/{GGUF_REV}?recursive=true&expand=false',
 'config.json':f'https://huggingface.co/{model}/resolve/{MODEL_REV}/config.json',
 'chat_template.jinja':f'https://huggingface.co/{model}/resolve/{MODEL_REV}/chat_template.jinja',
 'modelscope-api.json':f'https://modelscope.cn/api/v1/models/{model}',
}
for name,url in urls.items():
 if not (p/name).exists():subprocess.run(['curl','-fLsS','--max-time','60',url,'-o',str(p/name)],check=True)
assert json.loads((p/'model-api.json').read_text())['sha']==MODEL_REV
assert json.loads((p/'gguf-api.json').read_text())['sha']==GGUF_REV
meta=json.loads((p/'gguf-api.json').read_text());rev=meta['sha']
files=json.loads((p/'gguf-tree.json').read_text());rows=[]
for f in files:
 if not f['path'].endswith('.gguf'):continue
 rows.append({'file':f['path'],'bytes':f['size'],'GB':round(f['size']/1e9,4),'GiB':round(f['size']/2**30,4),'sha256':f['lfs']['oid']})
f=next(x for x in rows if 'Q4_K_M' in x['file']);url=f'https://huggingface.co/JetBrains/Mellum2.1-12B-A2.5B-Thinking-GGUF/resolve/{rev}/{f["file"]}'
header=p/'q4-header.bin';code=subprocess.check_output(['curl','-LsS','--max-time','60','--max-filesize','65536','-H','Range: bytes=0-63','-D',str(p/'q4-range-headers.txt'),'-o',str(header),'-w','%{http_code}',url],text=True)
b=header.read_bytes();magic,version,tensors,kvs=struct.unpack('<4sIQQ',b[:24]);assert code=='206' and len(b)==64 and magic==b'GGUF' and version==3
config=json.loads((p/'config.json').read_text());assert config['num_experts']==64 and config['num_experts_per_tok']==8 and config['max_position_embeddings']==131072
ms=json.loads((p/'modelscope-api.json').read_text());assert ms['Code']==200 and ms['Data']['Name']==meta['cardData']['base_model'].split('/')[-1]
env=Environment();template=env.from_string((p/'chat_template.jinja').read_text())
def render(messages,**kw):return template.render(messages=messages,add_generation_prompt=True,**kw)
tool={'type':'function','function':{'name':'read_file','parameters':{'type':'object','properties':{'path':{'type':'string'}},'required':['path']}}}
cases=[]
def check(name,ok):assert ok,name;cases.append({'name':name,'passed':True})
r=render([{'role':'user','content':'Explain this patch.'}]);check('assistant generation prefix',r.endswith('<|im_start|>assistant\n'))
r=render([{'role':'user','content':'hi'}],enable_thinking=False);check('no-thinking prefix',r.endswith('<think>\n\n</think>\n\n'))
r=render([{'role':'system','content':'Only read.'},{'role':'user','content':'Inspect a.py'}],tools=[tool]);check('tool schema and system included','read_file' in r and 'Only read.' in r and '<tools>' in r)
r=render([{'role':'user','content':'Inspect a.py'},{'role':'assistant','content':'','tool_calls':[{'function':{'name':'read_file','arguments':{'path':'a.py'}}}]},{'role':'tool','content':'def add(a,b):return a-b'}],tools=[tool]);check('tool call JSON', '{"name": "read_file", "arguments": {"path": "a.py"}}' in r);check('tool result delimiter','<tool_response>\ndef add(a,b):return a-b\n</tool_response>' in r)
r=render([{'role':'user','content':[{'type':'text','text':'hello'},{'type':'text','text':' world'}]}]);check('multipart text normalized','hello world' in r)
result={'date':'2026-10-13','modelRevision':json.loads((p/'model-api.json').read_text())['sha'],'ggufRevision':rev,'modelScopeApiStatus':ms['Code'],'BF16SafetensorBytes':sum(x['size'] for x in ms['Data']['ModelInfos']['safetensor']['files']),'files':rows,'rangeVerification':{'status':int(code),'downloadedBytes':len(b),'magic':magic.decode(),'version':version,'tensorCount':tensors,'metadataCount':kvs,'scope':'first64bytes only, no full-file hash verification'},'templateChecks':cases,'passed':len(cases),'freeDiskBytes':shutil.disk_usage(p).free,'inferenceRun':False,'reason':'Insufficient working disk headroom for responsible complete model download; no speed, correctness, tool execution or benchmark claim.'}
(p/'artifact-verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2));print(json.dumps(result,ensure_ascii=False,indent=2))
