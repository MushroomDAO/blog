"""Exercise upstream task validation only; does not load a speech model."""
import sys,json,importlib.util
from pathlib import Path
root=Path(sys.argv[1]);sys.path.insert(0,str(root))
from tts_tasks import build_task_generation_kwargs as build
out=[]
valid=[('plain',dict(task='TTS',text='Hello.')),('freeform',dict(task='FREEFORM',text='Hello.',instruction='Speak softly.')),('japanese',dict(task='MULTILINGUAL',text='こんにちは',language_id='Japanese'))]
for name,args in valid:
 result=build(**args);out.append({'case':name,'accepted':True,'fields':list(result)})
invalid=[('missing-language',dict(task='MULTILINGUAL',text='Hallo')),('mixed-freeform',dict(task='FREEFORM',text='Hello',instruction='Softly',controls={'emotion':'高兴'})),('conflicting-speaker-mode',dict(task='TTS',text='Hello',use_spk_emb=True,use_zero_spk_emb=True)),('missing-reference',dict(task='TTS',text='Hello',use_spk_emb=True)),('empty-text',dict(task='TTS',text=' '))]
for name,args in invalid:
 try:build(**args)
 except ValueError as e:out.append({'case':name,'rejected':True,'reason':str(e)})
 else:raise AssertionError(name)
print(json.dumps({'scope':'8 upstream task-input checks, no model loading/audio generation/benchmark','results':out},ensure_ascii=False,indent=2))
