from pathlib import Path
import importlib.util,json,hashlib
root=Path('/tmp/heinu1-paperswithcode-research')
spec=importlib.util.spec_from_file_location('upstream_github_utils',root/'backend/utils/github_utils.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
cases=[('https://github.com/HuggingFace/PapersWithCode','https://github.com/huggingface/paperswithcode'),('github.com/huggingface/paperswithcode','https://github.com/huggingface/paperswithcode'),('https://github.com/huggingface/paperswithcode.git','https://github.com/huggingface/paperswithcode'),('https://github.com/huggingface/paperswithcode/tree/main/backend','https://github.com/huggingface/paperswithcode'),('https://github.com/huggingface/paperswithcode?tab=readme','https://github.com/huggingface/paperswithcode'),('https://example.org/huggingface/paperswithcode',None),('',None),('https://github.com/huggingface',None)]
rows=[]
for input,expected in cases:
 actual=m.normalize_github_url(input);assert actual==expected,(input,actual,expected);rows.append({'input':input,'expected':expected,'actual':actual})
print(json.dumps({'checks':len(rows),'passed':True,'scope':'Direct upstream normalize_github_url function; no full deployment, database, search benchmark or model test','cases':rows},indent=2))
