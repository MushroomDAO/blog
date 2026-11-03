"""Read-only artifact checks; no model inference or checkpoint hash verification.
Usage: /path/to/numpy/python verify-artifacts.py /path/to/lm_understand-logs
"""
import json,sys
from pathlib import Path
import numpy as np
p=Path(sys.argv[1]);m=json.loads((p/'exp8_math/runs/p50c/edit/manifest.json').read_text());z=np.load(p/'exp8_math/runs/p50c/edit/edit.npz')
results=[]
for i,t in enumerate(m['tensors']):
 idx=z[f't{i}_idx']; vals=z[f't{i}_val'];rows,cols=t['shape']
 assert len(idx)==len(set(idx.tolist()))==t['changed_entries']==len(vals)
 assert len(np.unique(idx%cols))==64
 assert len(np.unique(idx//cols))==t['changed_rows']
 assert idx.min()>=0 and idx.max()<rows*cols
 results.append({'tensor':t['name'],'patch_entries':len(idx),'columns':len(np.unique(idx%cols)),'rows':len(np.unique(idx//cols))})
assert sum(r['patch_entries'] for r in results)==130188
# A deliberately simple exact rank-one update with no zero entries.
u=np.array([1.,2.,3.,4.]);k=np.array([1.,1.,1.,1.]);target=np.array([4.,8.,12.,16.]);W=np.zeros((4,4));d=np.outer(target,k)/(k@k)
assert np.linalg.matrix_rank(d)==1 and np.count_nonzero(d)==16
assert np.array_equal((W+d)@k,target)
control=np.array([1.,-1.,0.,0.]);assert np.array_equal((W+d)@control,W@control)
related=np.array([1.,0.,0.,0.]);assert np.count_nonzero(d@related)==4
print(json.dumps({'patch_index_checks':results,'addressed':64*1024*2,'actual_patch_entries':130188,'algebra':{'rank':1,'nonzero_entries':16,'target_exact':True,'orthogonal_control_unchanged':True,'correlated_input_changed':True},'scope':'No full checkpoint bytes, model generation, independent benchmark scoring, or timing measured'},indent=2))
for n in ['unedited','p50c']:
 data=json.loads((p/f'exp8_math/eval/{n}/merged.json').read_text())
 print(n,json.dumps(data)[:2500])
for name in ['unedited','p50c']:
 rows=[]
 for f in sorted((p/f'exp8_math/eval/{name}/parts').glob('math500*/math500_per_problem.json')):rows.extend(json.loads(f.read_text()))
 assert len(rows)==len({r['id'] for r in rows})==500
 assert all(len(r['correct'])==4 and set(r['correct'])<={0,1} for r in rows)
 scores=[x for r in rows for x in r['correct']];acc=sum(scores)/len(scores)
 merged=json.loads((p/f'exp8_math/eval/{name}/merged.json').read_text())['math500']['acc']
 assert abs(acc-merged)<1e-12
 print(json.dumps({'release':name,'questions':500,'sample_flags':len(scores),'correct_flags':sum(scores),'mean_accuracy':acc,'any_of_four_correct':sum(any(r['correct']) for r in rows)/500,'scope':'Reaggregated author correctness flags, did NOT independently regrade answers or regenerate outputs'}))
