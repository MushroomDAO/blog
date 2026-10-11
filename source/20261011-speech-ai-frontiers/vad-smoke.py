from pathlib import Path
import wave,time,json,hashlib,platform,subprocess
import numpy as np
import onnxruntime as ort
ROOT=Path(__file__).parent
with wave.open(str(ROOT/'fixture.wav'))as w:
 assert w.getframerate()==16000 and w.getnchannels()==1 and w.getsampwidth()==2
 audio=np.frombuffer(w.readframes(w.getnframes()),dtype=np.int16).astype(np.float32)/32768
rng=np.random.default_rng(42);noise=rng.normal(0,1,len(audio)).astype(np.float32);noise*=np.sqrt(np.mean(audio**2))/np.sqrt(np.mean(noise**2))
cases={'synthetic-speech-clean':audio,'speech-white-noise-20dB':audio+noise/10,'speech-white-noise-0dB':audio+noise,'silence':np.zeros_like(audio)}
opts=ort.SessionOptions();opts.intra_op_num_threads=1;opts.inter_op_num_threads=1
start=time.perf_counter();session=ort.InferenceSession(str(ROOT/'silero-vad.onnx'),sess_options=opts,providers=['CPUExecutionProvider']);load_ms=(time.perf_counter()-start)*1000
results=[]
for name,samples in cases.items():
 state=np.zeros((2,1,128),np.float32);context=np.zeros((1,64),np.float32);probs=[];times=[];start=time.perf_counter()
 for n in range(0,len(samples),512):
  chunk=np.pad(samples[n:n+512],(0,max(0,512-len(samples[n:n+512]))))[None].astype(np.float32)
  joined=np.concatenate([context,chunk],axis=1);t=time.perf_counter()
  pred,state=session.run(None,{'input':joined,'state':state,'sr':np.array(16000,dtype=np.int64)})
  times.append((time.perf_counter()-t)*1000);probs.append(float(pred[0,0]));context=joined[:,-64:]
 elapsed=time.perf_counter()-start
 results.append({'case':name,'secondsAudio':len(samples)/16000,'chunks':len(probs),'elapsedSeconds':elapsed,'RTF':elapsed/(len(samples)/16000),'chunkMsP50':float(np.percentile(times[1:],50)),'chunkMsP95':float(np.percentile(times[1:],95)),'firstChunkMs':times[0],'fractionChunksAbove05':float(np.mean(np.array(probs)>=0.5)),'probMax':max(probs),'probMean':float(np.mean(probs)),'probabilities':probs})
summary={'modelCommit':'1e261b036686cd0017d500ee96acd1c4ba572a9d','modelBytes':(ROOT/'silero-vad.onnx').stat().st_size,'modelSha256':hashlib.sha256((ROOT/'silero-vad.onnx').read_bytes()).hexdigest(),'hardware':subprocess.check_output(['sysctl','-n','machdep.cpu.brand_string'],text=True).strip(),'RAM':'16GiB','runtime':ort.__version__,'provider':'CPUExecutionProvider','threads':1,'sampleRate':16000,'chunkSamples':512,'chunkAudioMs':32,'contextSamples':64,'sessionLoadMs':load_ms,'fixture':'macOS say synthesizedEnglish, resampled16kmono; deterministic whiteGaussian noise and silence; no cloned real voice','scope':'one pass percase; no AEC/network/playback/end-to-end conversation or semantic interruption test; threshold fractions are not detectionaccuracy','results':results}
(ROOT/'vad-smoke-result.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2))
for r in results:print(r['case'],{k:round(r[k],5)for k in ['RTF','chunkMsP50','chunkMsP95','fractionChunksAbove05']})
print('loadMs',load_ms)
