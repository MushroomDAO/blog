from pathlib import Path
import json,time,platform,re,sys,traceback
import torch,transformers
from transformers import AutoTokenizer,AutoModelForCausalLM
out=Path(__file__).parent;model_dir='/tmp/botpsy-research-20261112/model';revision='24561e9681643eaf807fc28b0875210cb17f89c1'
tools=[{'type':'function','function':{'name':'set_brightness','description':'Set the brightness of a simulated desk light. Only call if the requested level is explicitly provided.','parameters':{'type':'object','properties':{'level':{'type':'integer','minimum':0,'maximum':100}},'required':['level'],'additionalProperties':False}}}]
cases=[{'id':'explicit-argument','prompt':'Set the simulated desk light brightness to 55 percent.','expected':'call'},{'id':'missing-argument','prompt':'Change the simulated desk light brightness.','expected':'clarify'},{'id':'unavailable-tool','prompt':'What is the current weather in Bangkok?','expected':'no-call'}]
r={'modelRevision':revision,'device':'mps'if torch.backends.mps.is_available()else'cpu','dtype':'float32','torch':torch.__version__,'transformers':transformers.__version__,'platform':platform.platform(),'python':sys.version,'generation':{'do_sample':False,'max_new_tokens':1024,'enable_thinking':True,'use_cache':True},'scope':'Three synthetic English prompts; no real device, network tool or payment executed; not benchmark, latency comparison, quantized or phone test.','results':[]}
try:
 t=time.monotonic();tok=AutoTokenizer.from_pretrained(model_dir,local_files_only=True);model=AutoModelForCausalLM.from_pretrained(model_dir,dtype=torch.float32,local_files_only=True).to(r['device']).eval();r['loadSeconds']=time.monotonic()-t;print('model loaded',r['device'],flush=True)
 for c in cases:
  messages=[{'role':'system','content':'You are a tool-calling assistant. Use only the supplied tool. Ask for missing required information instead of inventing it. If no tool can answer, explain that limitation.'},{'role':'user','content':c['prompt']}];x=tok.apply_chat_template(messages,tools=tools,add_generation_prompt=True,enable_thinking=True,return_tensors='pt',return_dict=True).to(model.device);t=time.monotonic()
  with torch.inference_mode():y=model.generate(**x,max_new_tokens=1024,do_sample=False,use_cache=True)
  if r['device']=='mps':torch.mps.synchronize()
  text=tok.decode(y[0,x['input_ids'].shape[1]:],skip_special_tokens=False);final=text.split('</think>')[-1];names=re.findall(r'<function=([^>]+)>',final);vals=re.findall(r'<parameter=level>\s*(.*?)\s*</parameter>',final,re.S);complete='</think>'in text and y.shape[1]-x['input_ids'].shape[1]<1024
  check=complete and ((names==['set_brightness']and vals==['55'])if c['expected']=='call'else not names and '<tool_call>'not in final)
  row={**c,'inputTokens':x['input_ids'].shape[1],'outputTokens':y.shape[1]-x['input_ids'].shape[1],'seconds':time.monotonic()-t,'final':final,'toolNames':names,'argumentValues':vals,'completedWithinBudget':complete,'automatedStructuralCheck':check};r['results'].append(row);(out/'smoke-report.json').write_text(json.dumps(r,ensure_ascii=False,indent=2));print(json.dumps(row,ensure_ascii=False),flush=True)
except Exception as e:r['error']=repr(e);r['traceback']=traceback.format_exc();print(r['traceback'],flush=True)
(out/'smoke-report.json').write_text(json.dumps(r,ensure_ascii=False,indent=2))
