from pathlib import Path
import json,subprocess,shutil
p=Path(__file__).parent;old=p.parent/'20261120-linger';slug='heretic-model-behavior-editing-evaluation-guide';oldslug='linger-polystrata-local-moe-agent-engineering-guide';job='a7873a12-b8ae-44c2-a56f-3f57814b0245'
for name in ['check.py','verify-public.py','verify-preserved.py','verify-wechat.cjs','wechat-content-canonical.py','remote-preflight.cjs','check-semantic.py','mine-kb.py','verify-kb.py','compress-figures.py','stage-source.py']:
 s=(old/name).read_text().replace(oldslug,slug).replace('e2b82b3c-b1c5-498d-912e-ed168ce750a4',job)
 if name=='verify-preserved.py':s=s.replace('slugs=[','slugs=["'+oldslug+'",')
 if name=='remote-preflight.cjs':
  a=s.index('const matches=');b=s.index('const{data:p}',a);s=s[:a]+'const matches=items.filter(x=>/p-e-w\\/heretic|heretic-model-behavior-editing-evaluation-guide/i.test(JSON.stringify(x)));'+s[b:]
 if name=='check-semantic.py':s=s.replace('Linger PolyStrata local MoE GPU RAM SSD inference license','Heretic model behavior ARA terse sycophancy evaluation')
 (p/name).write_text(s)
(p/'slugs.json').write_text(json.dumps([slug]));shutil.copy2('/tmp/heretic-dedup-20261120.log',p/'duplicate-check.log')
repo=Path('/tmp/heretic-20261120');sha=subprocess.check_output(['git','-C',str(repo),'rev-parse','HEAD'],text=True).strip()
for f in ['README.md','LICENSE','pyproject.toml','config.terse.toml','config.nosyco.toml','docs/migration_v1_to_v2.md']:
 shutil.copy2(repo/f,p/'research'/f.replace('/','--'))
(p/'source-pin.json').write_text(json.dumps({'revision':sha,'version':'2.2.0.dev0','license':'AGPL-3.0-or-later','dedup':'Exact URL none; Heretic only a passing mention in a different DeepSeek model article, plus incoming raw KB. No dedicated article/local receipt/draft.'},indent=2))
mem=Path('/Users/jason/.claude/projects/-Users-jason-Dev-mycelium-blog/memory');f=mem/f'project_{slug}.md';f.write_text(f'''---
name: Heretic model behavior editing
description: ARA and evaluation limits, local open-weight model modification.
type: project
---
# Heretic
Source https://github.com/p-e-w/heretic pin {sha}; 2026-11-20.
Slug {slug}. Dedicated tool article distinct from existing DeepSeek model analysis. Exact source no previous match; only raw KB and passing Heretic mention. License AGPL3orlater; base model separate. Current checkout2.2dev, notstable release. General local model behavior editing, scorer/modifier plugins, ARA default, Optuna; no full pretrained/GPU optimization reproduction. Local CPU math/config checks scoped separately. Training-free does not mean zero optimization: ARA uses L-BFGS adapter-level fitting. Terse/nosyco benign examples, no refusal removal deployment recipe. Blog/WeChat/semantic pending.
''');idx=mem/'MEMORY.md'
if f.name not in idx.read_text():idx.write_text(idx.read_text()+f'\n- [Heretic]({f.name}) — model behavior editing and evaluation.\n')
