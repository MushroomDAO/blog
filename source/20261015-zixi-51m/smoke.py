import json, pathlib, platform, sys, traceback, hashlib
import numpy as np
import soundfile as sf
import torch
from zixi.api import TTS
OUT=pathlib.Path(__file__).resolve().parent
CKPT=pathlib.Path.home()/'.cache/huggingface/hub/models--NoesisLab--zixi-51m/snapshots/3f66b777ff7d498310215939f98dd29598945d28'
report={'sourceCommit':'2cfebd74b6b84db2f83a40604e3a11fcbb750cee','modelRevision':CKPT.name,'platform':platform.platform(),'python':sys.version.split()[0],'torch':torch.__version__,'mpsAvailable':torch.backends.mps.is_available(),'checkpointBytes':(CKPT/'pytorch_model.bin').stat().st_size,'checkpointSHA256':hashlib.sha256((CKPT/'pytorch_model.bin').read_bytes()).hexdigest(),'scope':'Actual local inference only, no training or listening/MOS/ASR quality evaluation; no speed benchmark.','runs':[]}
for device in ['mps','cpu']:
 r={'device':device,'samples':[]}
 try:
  torch.manual_seed(42)
  model=TTS(language='ZH',device=device,config_path=str(CKPT/'config.json'),ckpt_path=str(CKPT/'pytorch_model.bin'))
  r['parameters']=sum(p.numel() for p in model.model.parameters())
  for i,text in enumerate(['你好，世界。','这是一段本地语音合成测试。今天我们检查模型能否正常生成声音。']):
   fn=OUT/f'{device}-sample-{i+1}.wav'
   model.tts_to_file(text,model.hps.data.spk2id['zixi'],str(fn),quiet=True)
   y,sr=sf.read(fn);info=sf.info(fn)
   x={'text':text,'file':fn.name,'sampleRate':sr,'channels':info.channels,'subtype':info.subtype,'frames':len(y),'durationSeconds':len(y)/sr,'finite':bool(np.isfinite(y).all()),'nonSilent':bool(np.max(np.abs(y))>0.001),'peak':float(np.max(np.abs(y))),'bytes':fn.stat().st_size}
   assert sr==44100 and info.channels==1 and x['finite'] and x['nonSilent'];r['samples'].append(x)
  r['ok']=True
  del model
 except Exception as e:
  r.update(ok=False,error=repr(e),traceback=traceback.format_exc())
 report['runs'].append(r)
 (OUT/'inference-verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps(r,ensure_ascii=False),flush=True)
assert any(x.get('ok') for x in report['runs']), 'No inference backend succeeded'
