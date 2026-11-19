from pathlib import Path
import json,itertools,hashlib,urllib.request,yaml
from jinja2 import Environment,nodes
from jinja2.ext import Extension
p=Path(__file__).parent;r=p/'research'; api=json.loads((r/'model-api.json').read_text());sha=api['sha']
assert sha=='a0c34287229103b706c670d70791683e34379732'
files=['README.md','config.json','processor_config.json','chat_template.jinja','tokenizer_config.json','LICENSE']
for name in files:
 data=urllib.request.urlopen(f'https://huggingface.co/Reson8/Rumble-2-Flash/resolve/{sha}/{name}',timeout=45).read()
 assert data==(r/('model-card.md' if name=='README.md'else name)).read_bytes(),name
class Generation(Extension):
 tags={'generation'}
 def parse(self,parser):
  token=next(parser.stream);body=parser.parse_statements(['name:endgeneration'],drop_needle=True)
  return nodes.Scope(body).set_lineno(token.lineno)
env=Environment(extensions=[Generation]);template=env.from_string((r/'chat_template.jinja').read_text());results=[]
for digits,filler,verbatim in itertools.product([False,True],repeat=3):
 for language in [None,'English']:
  for kind in ['audio','audio_url','input_audio']:
   kw=dict(messages=[{'role':'user','content':[{'type':kind,kind:'synthetic-placeholder'}]}],add_generation_prompt=True,digits=digits,filler=filler,verbatim=verbatim)
   if language:kw['language']=language
   s=template.render(**kw)
   markers=['<digits>'if digits else'<nodigits>','<filler>'if filler else'<nofiller>','<verbatim>'if verbatim else'<noverbatim>']
   assert all(x in s for x in markers)
   assert s.count('<|audio_start|><|audio_pad|><|audio_end|>')==1
   assert ('language English<asr_text>'in s)==bool(language)
   results.append({'options':[digits,filler,verbatim],'language':language,'audioType':kind,'passed':True})
s=template.render(messages=[{'role':'user','content':[{'type':'audio','audio':'synthetic'}]}],add_generation_prompt=True)
assert '<digits><nofiller><verbatim>'in s
card=yaml.safe_load((r/'model-card.md').read_text().split('---')[1]);config=json.loads((r/'config.json').read_text());processor=json.loads((r/'processor_config.json').read_text())
assert card['license']=='apache-2.0' and len(card['language'])==45 and len(config['support_languages'])==30
assert processor['feature_extractor']['sampling_rate']==16000
report={'revision':sha,'templateCases':len(results)+1,'passed':len(results)+1,'jinjaGenerationTag':'Transparent generation-block parser for template-only evaluation; no Transformers model execution','cardLanguages':45,'configLanguages':30,'realAudioInference':False,'weightsDownloaded':False,'cases':results,'sha256':{name:hashlib.sha256((r/('model-card.md'if name=='README.md'else name)).read_bytes()).hexdigest()for name in files}}
(p/'smoke-results.json').write_text(json.dumps(report,indent=2));print(json.dumps({k:v for k,v in report.items()if k not in ['cases','sha256']}))
