import sys,json,time,platform,hashlib
from pathlib import Path
import torch
from transformers import AutoModel, AutoProcessor
from nemotron_parse.inference import DocumentParser,GenerationSettings,TransformersBackend
from bs4 import BeautifulSoup
out=Path('/Users/jason/Dev/mycelium/blog/source/20261112-openthai-my-office');model_dir=Path('/tmp/openthai-research-20261112');assert torch.backends.mps.is_available()
t=time.perf_counter();model=AutoModel.from_pretrained(model_dir,trust_remote_code=True,dtype=torch.float32,local_files_only=True).to('mps').eval();processor=AutoProcessor.from_pretrained(model_dir,trust_remote_code=True,local_files_only=True);load=time.perf_counter()-t
class Backend(TransformersBackend):
 def __call__(self,image,*,prompt,**kwargs):return super().__call__(image,prompt='\n'+prompt,**kwargs)
parser=DocumentParser(backend=Backend(model,processor),fullpage=GenerationSettings(temperature=0,max_tokens=4096))
with parser:
 t=time.perf_counter();doc=parser.parse('/tmp/openthai-smoke-page.png',mode='single');torch.mps.synchronize();elapsed=time.perf_counter()-t
(out/'smoke-document.json').write_text(json.dumps(doc,ensure_ascii=False,indent=2,default=str));md=doc['markdown'];(out/'smoke-output.md').write_text(md)
soup=BeautifulSoup(md,'html.parser');report={'modelRevision':'7a153712e5b50fac7e4a9d42ccf9ec41fb4202f0','device':'mps','dtype':'float32','torch':torch.__version__,'system':platform.platform(),'pageCount':1,'fixture':'self-authored synthetic Thai/English purchase summary with rowspan/colspan','fixtureSHA256':hashlib.sha256(Path('/tmp/openthai-smoke-page.png').read_bytes()).hexdigest(),'generationTemperature':0,'maxTokens':4096,'loadSeconds':load,'singleParseSeconds':elapsed,'errors':0,'markdownCharacters':len(md),'checks':{'thaiTitle':'รายงานการจัดซื้อ'in md,'englishTitle':'Purchase summary'in md,'paperRow':'กระดาษ'in md,'penRow':'ปากกา'in md,'total':'550'in md,'table':bool(soup.find('table')),'rowspan':bool(soup.find(attrs={'rowspan':'2'})),'colspan':bool(soup.find(attrs={'colspan':'2'}))},'scope':'Single synthetic page on local MPS, not a speed benchmark, CER estimate, real scanned-document evaluation or reproduction of H100 results. Model loading excluded from singleParseSeconds; first parse includes warmup.'};(out/'smoke-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print(json.dumps(report,ensure_ascii=False),flush=True);print(md,flush=True)
