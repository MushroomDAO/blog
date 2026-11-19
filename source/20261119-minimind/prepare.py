from pathlib import Path
import urllib.request,json
p=Path(__file__).parent;root=p.resolve().parents[1];r=p/'research';sha=(r/'revision.txt').read_text().strip();slug='minimind-64m-llm-training-from-scratch-guide'
for src,name in [('README.md','README.md'),('model/model_minimind.py','model_minimind.py'),('trainer/train_full_sft.py','train_full_sft.py'),('trainer/train_pretrain.py','train_pretrain.py'),('dataset/lm_dataset.py','lm_dataset.py'),('LICENSE','LICENSE'),('requirements.txt','requirements.txt')]:
 data=urllib.request.urlopen(f'https://raw.githubusercontent.com/jingyaogong/minimind/{sha}/{src}',timeout=45).read();(r/name).write_bytes(data)
memory=Path('/Users/jason/.claude/projects/-Users-jason-Dev-mycelium-blog/memory');f=memory/f'project_{slug}.md'
if not f.exists():f.write_text(f'''---
name: MiniMind64M educational training pipeline
description: Main text MiniMind repo, separate from MiniMind-O; architecture smoke and cost boundaries.
type: project
---
# MiniMind64M
Source: https://github.com/jingyaogong/minimind
Revision: {sha}
Slug: {slug}
Date: 2026-11-19
Dedup: MiniMind-O113M multimodal repo is a different project; AI Agent book merely references bojieli/minimind fork. No dedicated primary text64M article or prior draft found; only incoming rawKB matches. Published API48001 unavailable.
Apache2.0. Current default8layers768hidden/vocab6400/GQA8q4kv/tiedembedding/RoPE/RMSNorm/SwiGLU;64M Dense separate198M-A64M MoE. GPT3 reference175B/64M~2734 parameter ratio, not ability/disk ratio. Header2h3yuan scoped SFT3090oneepoch; detailedtable pretrain1.21h+SFT1.10h=2.31h~3yuan estimates. No universal all-stage cost claim.
Blog pending. WeChat pending. Semantic pending. Random-weight CPU forward/backward/cache/generation smoke planned; no pretrained quality/fulltraining/3090timing replication.
''')
index=memory/'MEMORY.md';s=index.read_text()
if f.name not in s:index.write_text(s+f'\n- [MiniMind64M training](project_{slug}.md) — educational text model, cost boundaries and local smoke.\n')
(p/'slugs.json').write_text(json.dumps([slug]))
old=p.parent/'20261119-rumble-2-flash';oldslug='rumble-2-flash-small-asr-phone-call-benchmarks'
for name in ['check.py','verify-public.py','verify-preserved.py','verify-wechat.cjs','wechat-content-canonical.py','remote-preflight.cjs','check-semantic.py','mine-kb.py','verify-kb.py','compress-figures.py']:
 s=(old/name).read_text().replace(oldslug,slug).replace('00613c57-ed07-4b19-8cfd-1fe57eff41a9','38001a13-a161-45df-8675-d6e8e5326029')
 if name=='remote-preflight.cjs':s=s.replace('Reson8\\/Rumble-2-Flash|'+slug+'|Rumble-2-Flash：','jingyaogong\\/minimind(?:[/?"\\s]|$)|'+slug+'|MiniMind64M：')
 if name=='verify-preserved.py':s=s.replace("slugs=['cheetah", "slugs=['"+oldslug+"','cheetah")
 if name=='check-semantic.py':s=s.replace('Rumble-2-Flash Reson8 小模型 电话语音识别 H200 批处理','MiniMind64M jingyaogong 从零预训练 SFT 教学 参数量')
 (p/name).write_text(s)
