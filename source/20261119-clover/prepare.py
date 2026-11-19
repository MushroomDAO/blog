from pathlib import Path
import json,hashlib
p=Path(__file__).parent;root=p.resolve().parents[1];slug='clover-diffusion-llm-sft-engineering-guide';old=p.parent/'20261119-minimind';oldslug='minimind-64m-llm-training-from-scratch-guide'
memory=Path('/Users/jason/.claude/projects/-Users-jason-Dev-mycelium-blog/memory');f=memory/f'project_{slug}.md'
if not f.exists():f.write_text(f'''---
name: Clover block diffusion SFT engineering review
description: Paper2611.24636 and public SFT scope, native CPU tests and speed/evaluation boundaries.
type: project
---
# Clover35B-A3B Preview
Sources: https://arxiv.org/abs/2611.24636 ; https://github.com/DiffuSpace/Clover-35B-A3B-Preview/tree/main/sft
Date:2026-11-19
Slug: {slug}
Repo revision: {(p/'research/revision.txt').read_text().strip()}
Dedup: only incoming rawKB exists; no prior article/localdraft/currentremote match. Published API48001 unavailable.
35Btotal3Bactive textMoE adaptedfromQwen3.6, recurrent cleanhistory + blockbidirectional denoising, selfspecdraft/causalverification. ReportGB300680tok/s BF16batch1 internal64prefixreplay is not task success orconsumerGPU speed. RTX5070Ti16GB+host64GB INT4expert split96GPU160CPU top8optimized97.52tok/s97.6%MATH500 vsapproximate top6 106.25/96.0 authorreport, excludesprefill/includesthinking. PublicSFT singleturn/nonthinkingtemplate/fixed4096/block32, diffusionno-shiftCE+routeraux, no packing/multiturn/CP or auxiliaryARobjective documented inpublicpackage. RequiresHopper/BlackwellQuack forGPUfulltrain; default8GPUFSDP2. LoRAfrozenexperts/basefitrequired. Weights-onlycheckpointsnotfulloptimizerresume.
Local26 selectedoriginalCPUtests/5files passed3.65s, torch2.14.0outsideGPU2.11pin, Transformers5.19.0; scope/hashes/Python3.10syntaxcheckpassed. No35Bweights, GPUtraining, fullSFT, SGLang/llama.cppacceptance, taskbenchmark orspeedreproduction.
Blog pending. WeChat pending. Semantic pending.
''')
index=memory/'MEMORY.md';s=index.read_text()
if f.name not in s:index.write_text(s+f'\n- [Clover diffusion SFT](project_{slug}.md) — paper, public SFT scope and CPU evidence.\n')
(p/'slugs.json').write_text(json.dumps([slug]))
for name in ['check.py','verify-public.py','verify-preserved.py','verify-wechat.cjs','wechat-content-canonical.py','remote-preflight.cjs','check-semantic.py','mine-kb.py','verify-kb.py','compress-figures.py']:
 s=(old/name).read_text().replace(oldslug,slug).replace('38001a13-a161-45df-8675-d6e8e5326029','e87ef8e5-8623-49a7-9a94-00ad3a756676')
 if name=='remote-preflight.cjs':s=s.replace('jingyaogong\\/minimind(?:[/?"\\s]|$)|'+slug+'|MiniMind64M：','DiffuSpace\\/Clover-35B-A3B-Preview|2611\\.24636|'+slug+'|Clover：')
 if name=='verify-preserved.py':s=s.replace("slugs=['minimind-o", "slugs=['"+oldslug+"','minimind-o")
 if name=='check-semantic.py':s=s.replace('MiniMind64M jingyaogong 从零预训练 SFT 教学 参数量','Clover DiffuSpace 扩散语言模型 双流 SFT 掩码 并行验证')
 (p/name).write_text(s)
(p/'smoke-results.json').write_text(json.dumps({'passed':26,'selectedFiles':['test_data.py','test_loss.py','test_gdn_semantics.py','test_moe.py','test_model.py'],'seconds':3.65,'scopeCheckPassed':True,'device':'CPU','torch':'2.14.0','torchOutsideDocumentedGPUConstraint':True,'transformers':'5.19.0','pretrainedWeightsDownloaded':False,'fullTrainingOrBenchmarkReplicated':False,'sourceSha256':hashlib.sha256(Path('/tmp/clover-20261119/sft/clover_sft/model.py').read_bytes()).hexdigest()},indent=2))
