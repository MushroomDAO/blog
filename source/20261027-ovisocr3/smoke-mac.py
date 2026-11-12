"""Bounded local smoke test, not an accuracy or throughput benchmark.
Usage: PYTORCH_ENABLE_MPS_FALLBACK=1 HF_HUB_OFFLINE=1 python smoke-mac.py MODEL_DIR OUTPUT_DIR
Requires torch, transformers, Pillow and their usual runtime dependencies.
"""
import os,sys,json,time,hashlib,platform,traceback
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
out=Path(sys.argv[2]);out.mkdir(parents=True,exist_ok=True)
modelpath=Path(sys.argv[1]);report={'sourceRevision':'4833d5d2afa6e769ee933f024504d67ace80a24c','platform':platform.platform(),'scope':'Two synthetic clean English document cases only. No benchmark, multilingual, difficult image, caption or crosspage evaluation.','cases':[]}
try:
 import torch,transformers
 from transformers import AutoProcessor,Qwen3_5ForConditionalGeneration
 report.update(torch=torch.__version__,transformers=transformers.__version__,device=os.environ.get('OVIS_TEST_DEVICE', 'mps' if torch.backends.mps.is_available() else 'cpu'),dtype='float32',fallback=os.environ.get('PYTORCH_ENABLE_MPS_FALLBACK'),weightBytes=(modelpath/'model.safetensors').stat().st_size)
 device=report['device'];torch.set_num_threads(4)
 image=Image.new('RGB',(640,480),'white');draw=ImageDraw.Draw(image)
 font=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf',32)
 lines=['INVOICE','Invoice No: INV-1042','Date: 2026-10-27','Total: USD 128.50']
 for i,line in enumerate(lines):draw.text((40,40+i*80),line,font=font,fill='black')
 image.save(out/'synthetic-invoice.png');report['imageSha256']=hashlib.sha256((out/'synthetic-invoice.png').read_bytes()).hexdigest()
 processor=AutoProcessor.from_pretrained(str(modelpath),local_files_only=True,min_pixels=448*448,max_pixels=640*640)
 model=Qwen3_5ForConditionalGeneration.from_pretrained(str(modelpath),local_files_only=True,dtype=torch.float32,attn_implementation='sdpa').to(device).eval()
 print('MODEL_LOADED',device,flush=True)
 for task in os.environ.get('OVIS_TEST_TASKS','plain_ocr,kie_fields').split(','):
  prompt=(modelpath/'prompts'/f'{task}.txt').read_text()
  if task=='kie_fields':prompt=prompt.replace('{keys_json}',json.dumps(['Invoice No','Total','Purchase Order']))
  messages=[{'role':'user','content':[{'type':'image','image':image},{'type':'text','text':prompt}]}]
  inputs=processor.apply_chat_template(messages,tokenize=True,add_generation_prompt=True,enable_thinking=False,return_dict=True,return_tensors='pt').to(device)
  print('GENERATING',task,'inputTokens',inputs['input_ids'].shape[-1],flush=True)
  t=time.monotonic()
  with torch.inference_mode():ids=model.generate(**inputs,max_new_tokens=128,max_time=float(os.environ.get('OVIS_TEST_MAX_TIME','120')),do_sample=False,use_cache=True)
  if device=='mps':torch.mps.synchronize()
  output=processor.decode(ids[0][inputs['input_ids'].shape[-1]:],skip_special_tokens=True)
  (out/f'{task}-raw.txt').write_text(output)
  case={'task':task,'prompt':prompt,'inputTokens':inputs['input_ids'].shape[-1],'generatedTokens':ids.shape[-1]-inputs['input_ids'].shape[-1],'generationWallSeconds':time.monotonic()-t,'output':output}
  eos=model.generation_config.eos_token_id
  eos=eos if isinstance(eos,list) else [eos]
  case['lastTokenId']=int(ids[0,-1]);case['endedWithEos']=int(ids[0,-1]) in eos
  case['maxTimeSeconds']=float(os.environ.get('OVIS_TEST_MAX_TIME','120'))
  if task=='plain_ocr':case['expectedStringsPresent']=all(s in output for s in ['INV-1042','2026-10-27','128.50'])
  else:
   try:
    obj=json.loads(output);case['jsonValid']=True;case['fieldsCorrect']=obj=={'Invoice No':'INV-1042','Total':'USD 128.50','Purchase Order':''}
   except Exception as exc:case['jsonValid']=False;case['parseError']=str(exc)
  report['cases'].append(case);(out/'smoke-result.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print(json.dumps(case,ensure_ascii=False),flush=True)
 report['completed']=True
except Exception as exc:
 report['completed']=False;report['error']=repr(exc);report['traceback']=traceback.format_exc();print(report['traceback'],flush=True)
finally:
 (out/'smoke-result.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))

checks_ok = report.get('completed', False) and bool(report.get('cases')) and all(
    case.get('expectedStringsPresent', False) if case['task'] == 'plain_ocr' else case.get('fieldsCorrect', False)
    for case in report.get('cases', [])
)
raise SystemExit(0 if checks_ok else 1)
