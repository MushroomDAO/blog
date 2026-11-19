from pathlib import Path
import torch,transformers,importlib.util,json,hashlib,platform
p=Path(__file__).parent;f=p/'research/model_minimind.py';spec=importlib.util.spec_from_file_location('minimind_pinned',f);mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
torch.manual_seed(42);torch.set_num_threads(4)
cfg=mod.MiniMindConfig();model=mod.MiniMindForCausalLM(cfg).cpu();count=sum(x.numel()for x in model.parameters());x=torch.randint(3,cfg.vocab_size,(2,16));checks={}
checks['tied_embeddings']=model.model.embed_tokens.weight is model.lm_head.weight
model.eval()
with torch.no_grad():
 full=model(x,use_cache=False);checks['forward_shape']=list(full.logits.shape)==[2,16,6400];checks['finite_logits']=bool(torch.isfinite(full.logits).all())
 prefix=model(x[:,:15],use_cache=True);step=model(x[:,15:],past_key_values=prefix.past_key_values,use_cache=True);err=(full.logits[:,-1]-step.logits[:,-1]).abs().max().item();checks['kv_cache_parity']=torch.allclose(full.logits[:,-1],step.logits[:,-1],atol=1e-5,rtol=1e-4)
 generated=model.generate(x[:1,:4],max_new_tokens=3,do_sample=False,eos_token_id=None);checks['greedy_generation_shape']=list(generated.shape)==[1,7]
 model.config.flash_attn=False
model.train();loss=model(x,labels=x).loss;checks['finite_loss']=bool(torch.isfinite(loss));loss.backward();checks['finite_gradients']=all(bool(torch.isfinite(t.grad).all())for t in model.parameters()if t.grad is not None)
before=model.lm_head.weight[0,0].item();opt=torch.optim.SGD(model.parameters(),lr=1e-3);opt.step();checks['optimizer_changed_weight']=model.lm_head.weight[0,0].item()!=before
print(json.dumps({'parameters':count,'checks':checks,'kv_max_abs_error':err,'loss':loss.item()}));assert all(checks.values()),checks
report={'revision':(p/'research/revision.txt').read_text().strip(),'sourceSha256':hashlib.sha256(f.read_bytes()).hexdigest(),'torch':torch.__version__,'transformers':transformers.__version__,'platform':platform.platform(),'device':'CPU','randomWeights':True,'pretrainedWeightsDownloaded':False,'realLanguageQualityEvaluated':False,'fullTrainingReplicated':False,'parameters':count,'kv_max_abs_error':err,'loss':loss.item(),'checks':checks,'passed':sum(checks.values())}
(p/'smoke-results.json').write_text(json.dumps(report,indent=2))
