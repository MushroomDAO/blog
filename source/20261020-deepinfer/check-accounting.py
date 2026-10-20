"""Run the pinned upstream plotting helpers on synthetic records; no inference benchmark."""
from pathlib import Path
import hashlib,importlib.util,json,tempfile,urllib.request
b=Path(__file__).resolve().parent;pin='774ce244b87cc0eb8d4b94ab9f5de2ab22049f01';p=b/'examples__sweep__plot_pareto.py'
if not p.exists():p.write_bytes(urllib.request.urlopen(f'https://raw.githubusercontent.com/deepseek-ai/DeepInfer/{pin}/examples/sweep/plot_pareto.py',timeout=40).read())
assert hashlib.sha256(p.read_bytes()).hexdigest() == '13249bd8fd328ea6d59436e8a54360f53fbfcee6ec60a32f2ffb64e881ff6c56', 'Source differs from reviewed pinned version'
spec=importlib.util.spec_from_file_location('upstream_deepinfer_plot',p);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
base={'model_name':'deepseek-ai/DeepSeek-V4.1-Flash-1017','ep_size':64,'dp_size':64,'cp':1,'context_length':32768,'nextn':5,'mtp_varlen':False,'num_extra_experts':32,'decode_num_requests':64,'decode_avg_sps':10.,'decode_tokens_per_s_per_gpu':3840.};checks=[]
assert m.decode_tau([base],1.)==6.;checks.append('Full acceptance tau=6 for nextn5')
tau=m.decode_tau([base],.75);assert tau==4.75;xs,ys,_=m.decode_axes([base],tau);assert xs==[47.5]and ys==[3040.];checks.append('Synthetic10steps/s,64requests,cp1,a0.75 ->47.5tokens/s/user,3040tokens/s/GPU;not measured')
try:m.decode_tau([{**base,'mtp_varlen':True}],.75)
except AssertionError:checks.append('VARLEN records reject a second acceptance multiplier')
else:raise AssertionError('VARLEN guard missing')
with tempfile.TemporaryDirectory(prefix='deepinfer-metric-audit-')as d:
 q=Path(d)/'points.jsonl';q.write_text('\n'.join(json.dumps(x)for x in [base,{**base,'decode_avg_sps':11.}])+'\n');assert m.load_points(q,'decode')[0]['decode_avg_sps']==11.;checks.append('Repeated sweep parameter keeps latest record')
 q.write_text('\n'.join(json.dumps(x)for x in [base,{**base,'decode_num_requests':128,'context_length':65536}])+'\n')
 try:m.load_points(q,'decode')
 except AssertionError:checks.append('Mixed context lengths are rejected from one sweep curve')
 else:raise AssertionError('mixed-configuration guard missing')
xs,ys,_=m.prefill_axes([{'prefill_window_seconds':.5,'prefill_window_steps':5,'prefill_tokens_per_s_per_gpu':100.,'prefill_batch_size':4096}]);assert xs==[100.]and ys==[100.];checks.append('Prefill latency uses actual window seconds/steps, not full-batch inference')
out={'pin':pin,'source':'examples/sweep/plot_pareto.py','sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'checksPassed':len(checks),'checks':checks,'scope':'Unmodified plotting helper functions on synthetic records only. No GPU/NPU, model download, token generation, hardware throughput or latency measurement.'};(b/'accounting-verification.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
