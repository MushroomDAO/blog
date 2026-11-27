"""Local released-weight smoke test. No speed, listening or ASR benchmark."""
from pathlib import Path
import sys,json,hashlib,platform,importlib.metadata
repo=Path(sys.argv[1]);out=Path(sys.argv[2]);out.mkdir(parents=True,exist_ok=True)
sys.path.insert(0,str(repo/'src'))
import torch,numpy as np,soundfile as sf,onnxruntime as ort
from tiny_voca.infer import load_model,speak_text
from tiny_voca.text import phonemize,NothingToPronounce

torch.set_num_threads(4)
model=load_model(repo/'release/qora-voca-zh.pt','cpu');parameter_count=sum(p.numel()for p in model.parameters())
assert parameter_count==4532299
opt=ort.SessionOptions();opt.intra_op_num_threads=4;opt.inter_op_num_threads=1
session=ort.InferenceSession(str(repo/'release/onnx/model.onnx'),opt,providers=['CPUExecutionProvider'])
text='今天天气真不错，我们一起去公园散步吧。';phones=phonemize(text);rows=[]
for idx,voice in enumerate(model.config.speakers):
 with torch.inference_mode():wave,_=speak_text(model,text,voice)
 a=wave.numpy();assert a.size>24000 and np.isfinite(a).all() and np.max(np.abs(a))<=.99001 and np.max(np.abs(a))>.01
 dest=out/f'{voice}-torch.wav';sf.write(dest,a,24000)
 feed={'tokens':np.array([phones.ids],dtype=np.int64),'stress':np.array([phones.stress],dtype=np.int64),'voice':np.array([idx],dtype=np.int64),'speed':np.array([1.],dtype=np.float32),'pitch_shift':np.array([0.],dtype=np.float32),'pitch_range':np.array([1.],dtype=np.float32)}
 audio,durations=session.run(None,feed);assert audio.size>24000 and np.isfinite(audio).all();assert audio.shape[1]==len(a)
 sf.write(out/f'{voice}-onnx.wav',np.clip(audio[0],-.99,.99),24000)
 rows.append({'voice':voice,'torchSamples':len(a),'onnxSamples':audio.shape[1],'sampleRate':24000,'torchPeak':float(np.abs(a).max()),'onnxRawPeak':float(np.abs(audio).max()),'sameLength':True,'durationFramesSum':int(np.sum(durations))})
front=[]
for x in ['Hello world','2026','你好AI世界','你好2026世界','你好世界']:
 try:
  ph=phonemize(x);row={'text':x,'symbols':ph.symbols,'stress':ph.stress,'unknown':ph.unknown}
 except NothingToPronounce:row={'text':x,'rejected':True}
 front.append(row)
assert front[0]['rejected'] and front[1]['rejected']
assert front[2]['symbols']==front[3]['symbols']==front[4]['symbols']
result={'platform':platform.platform(),'python':platform.python_version(),'packages':{x:importlib.metadata.version(x)for x in ['torch','numpy','soundfile','pypinyin','jieba','onnxruntime']},'parameterCount':parameter_count,'providers':session.get_providers(),'rows':rows,'frontEnd':front,'artifacts':{str(p.relative_to(repo)): {'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in [repo/'release/qora-voca-zh.pt',repo/'release/onnx/model.onnx']},'limits':['released weights actually synthesized on CPU','no timing or performance comparison','no listening panel ASR CER or prosody evaluation','ONNX raw samples may exceed PCM range; saved copies clipped for safety','frontend drops mixed latin and digits in these fixtures','equal waveform length does not establish waveform numerical parity']}
(out/'smoke-results.json').write_text(json.dumps(result,ensure_ascii=False,indent=2));print(json.dumps(result,ensure_ascii=False))
