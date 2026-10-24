"""Short local ASR functional check, not a benchmark or real-meeting evaluation."""
import os,sys,json,hashlib,platform
from pathlib import Path
os.environ['HF_HUB_OFFLINE']='1';os.environ['TRANSFORMERS_OFFLINE']='1'
sys.path.insert(0,'/tmp/bark-3-model')
import soundfile as sf
from bark_mlx import load_model,transcribe
s=Path(__file__).resolve().parent
wave,sr=sf.read(s/'smoke-speech.wav',dtype='float32',always_2d=True)
model=load_model('/tmp/bark-3-model/model.bark',bits=16,cache_dir='/tmp/bark-3-model/bark_mlx_fp16')
text=transcribe(model,wave.mean(1),sr)
assert text and 'meeting' in text.lower() and 'report' in text.lower(),text
r={'model':'ConwayResearch/Underdog-Bark-3.0','revision':'85db2ad18ab41e534a222ee253c29191d77ed919','runtime':'public bark_mlx.py FP16, mlx-audio0.5.3','host':platform.platform(),'audio':'Apple say Samantha synthetic English, mono16kHz WAV','reference':'The meeting starts at nine. Please send the report tomorrow.','transcript':text,'audioFrames':len(wave),'sampleRate':sr,'modelDownloadBytes':Path('/tmp/bark-3-model/model.bark').stat().st_size,'audioSha256':hashlib.sha256((s/'smoke-speech.wav').read_bytes()).hexdigest(),'scope':'one synthetic short clip, not natural meeting quality, benchmark WER, speed or Clean evaluation. HF_HUB_OFFLINE=1, TRANSFORMERS_OFFLINE=1 during local load/inference.'}
(s/'smoke-results.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(r))
