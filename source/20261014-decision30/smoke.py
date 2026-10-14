"""Run the pinned d3-edge package on CPU; no timing benchmark or accuracy-score claim."""
import json, sys
from pathlib import Path
root=Path(sys.argv[1]).resolve(); out=Path(sys.argv[2]).resolve()
sys.path.insert(0,str(root))
import torch
from d3_runtime import D3, normalize_question, product_answer, video_sample_indices
# Contract checks use synthetic distributions, not model predictions.
checks={}
q=normalize_question({'type':'choice','criteria':{'returns':None,'billing':None}})
checks['choice_mapping']=product_answer(q,[.8,.2])['choice']=='returns'
q=normalize_question({'type':'noul'});checks['yes_probability']=product_answer(q,[.2,.8])['noul']==.8
q=normalize_question({'type':'score','criteria':['low','medium','high']});checks['score_expectation']=abs(product_answer(q,[.1,.2,.7])['score']-1.6)<1e-8
checks['ten_second_sampling']=len(video_sample_indices(300,30))==20
checks['long_video_cap']=len(video_sample_indices(3000,30))==32
try:normalize_question({'type':'score','criteria':['same','same']})
except ValueError:checks['invalid_score_rejected']=True
else:checks['invalid_score_rejected']=False
model=D3.from_pretrained(root,device='cpu',verify='full')
results={}
results['text']=model.system_one(state='The order arrived damaged. The customer has a receipt and asks for a replacement today.',questions={'route':{'type':'choice','instructions':'Which department should handle the request?','criteria':{'returns':'Refunds and replacements','billing':'Payments','technical':'Setup'}},'receipt':{'type':'noul','instructions':'Does the customer have a receipt?'},'urgency':{'type':'score','instructions':'How urgent is the request?','criteria':['Routine','Soon','Today']}})
results['image']=model.system_one(state='Read the attached receipt.',images=[str(root/'assets/example-receipt.png')],questions={'payment':{'type':'choice','instructions':'How was the order paid?','criteria':{'card':None,'cash':None,'gift card':None}}})
results['video']=model.system_one(state='A short clip from a test camera.',videos=[str(root/'assets/example-video.mp4')],questions={'direction':{'type':'choice','instructions':'Which way does the square move?','criteria':{'right':'Left to right','left':'Right to left','still':'Not moving'}},'color_change':{'type':'noul','instructions':'Does the square change color?'}})
report={'model':'vllm-sr/d3-edge','revision':'fe71f8e1dad1d0198386de78345b13f25c319b36','device':'cpu','torch':torch.__version__,'contract_checks':checks,'model_results':results,'benchmark_reproduction':False,'performance_measurement':False}
out.write_text(json.dumps(report,ensure_ascii=False,indent=2));print(json.dumps(report,ensure_ascii=False,indent=2))
