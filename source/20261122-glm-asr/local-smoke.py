"""Run pinned GLM-ASR on official recordings, an attenuated recording and silence.
No benchmark/latency/whisper-generalization claim. Requires torch/transformers/numpy.
"""
import os,json,time,hashlib,subprocess,sys
from pathlib import Path
import numpy as np
import torch,transformers
from transformers import AutoProcessor,GlmAsrForConditionalGeneration
MODEL=Path(os.environ.get('GLM_ASR_MODEL','/tmp/glm-asr-model-20261122'))
REPO=Path(os.environ.get('GLM_ASR_REPO','/tmp/glm-asr-research-20261122'))
OUT=Path(os.environ.get('GLM_ASR_OUT','/Users/jason/.heinu1-bot/jobs/85ae7a54-bb41-4790-96c3-9d504c3e1f45/research/local-smoke.json'))
report={'torch':torch.__version__,'transformers':transformers.__version__,'device':'mps','dtype':'float16','revision':'61ba4e0b3309b6656edea3e93e419f7bd5c61957','samples':[],'scope':'2 official clips, one amplitude variant, silence; not actual-whisper/Cantonese benchmark'}
try:
 processor=AutoProcessor.from_pretrained(MODEL,local_files_only=True)
 model=GlmAsrForConditionalGeneration.from_pretrained(MODEL,local_files_only=True,dtype=torch.float16).to('mps').eval()
 report['actualParameters']=sum(p.numel() for p in model.parameters())
 for name,filename,gain in [('official_zh','example_zh.wav',1),('official_en','example_en.wav',1),('zh_minus30db','example_zh.wav',10**(-30/20)),('silence','example_zh.wav',0)]:
  f=REPO/'examples'/filename
  raw=subprocess.check_output(['ffmpeg','-v','error','-i',str(f),'-f','f32le','-ac','1','-ar','16000','pipe:1'])
  arr=np.frombuffer(raw,dtype='<f4').copy()*gain
  if name=='silence':arr=np.zeros(16000*3,dtype=np.float32)
  item={'name':name,'sourceSha256':hashlib.sha256(f.read_bytes()).hexdigest(),'seconds':len(arr)/16000,'gain':gain,'inputRms':float(np.sqrt(np.mean(arr**2)))}
  try:
   inputs=processor.apply_transcription_request(arr,return_tensors='pt')
   inputs=inputs.to('mps',dtype=torch.float16)
   with torch.inference_mode():output=model.generate(**inputs,do_sample=False,max_new_tokens=128)
   item['text']=processor.batch_decode(output[:,inputs.input_ids.shape[1]:],skip_special_tokens=True)[0]
   item['generatedTokens']=output.shape[1]-inputs.input_ids.shape[1]
  except Exception as e:item['error']=repr(e)
  report['samples'].append(item);OUT.write_text(json.dumps(report,ensure_ascii=False,indent=2));print(json.dumps(item,ensure_ascii=False),flush=True)
except Exception as e:
 report['startupError']=repr(e);OUT.write_text(json.dumps(report,ensure_ascii=False,indent=2));print(json.dumps(report,ensure_ascii=False),flush=True);raise
OUT.write_text(json.dumps(report,ensure_ascii=False,indent=2))
