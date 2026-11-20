from pathlib import Path
import json,shutil
p=Path(__file__).parent;r=p/'research';slug='linger-polystrata-local-moe-agent-engineering-guide';job='e2b82b3c-b1c5-498d-912e-ed168ce750a4';old=p.parent/'20261119-organizing-intelligence';oldslug='organizing-intelligence-ai-jobs-wages-coordination'
for base,files,prefix in [(Path('/tmp/linger-20261120'),['README.md','LICENSE','NOTICE','docs/local-inference.md','docs/model-scheduling.md','docs/wiki-and-memory.md'],'linger'),(Path('/tmp/polystrata-20261120'),['README.md','LICENSE','docs/HOW_IT_WORKS.md','docs/models/qwen38.md','bench/results/2026-10-09-community-rtx-3060-0141/README.md'],'polystrata')]:
 for f in files:shutil.copy2(base/f,r/(prefix+'-'+f.replace('/','--')))
(p/'slugs.json').write_text(json.dumps([slug]))
for name in ['check.py','verify-public.py','verify-preserved.py','verify-wechat.cjs','wechat-content-canonical.py','remote-preflight.cjs','check-semantic.py','mine-kb.py','verify-kb.py','compress-figures.py']:
 s=(old/name).read_text().replace(oldslug,slug).replace('4124913f-d640-4580-9065-ef75c531f32e',job)
 if name=='check.py':s=s.replace("'https://arxiv.org/'in cn and 'https://arxiv.org/'in en","'https://github.com/'in cn and 'https://github.com/'in en")
 if name=='verify-preserved.py':s=s.replace('slugs=[','slugs=[\"'+oldslug+'\",')
 if name=='remote-preflight.cjs':
  a=s.index('const matches=');b=s.index('const{data:p}',a);s=s[:a]+f'const matches=items.filter(x=>/simplexai-labs\\/linger|simplexai-labs\\/PolyStrata|PolyStrata|{slug}/i.test(JSON.stringify(x)));'+s[b:]
 if name=='check-semantic.py':s=s.replace('Organizing Intelligence Imas Koh Legg 工资 协调 组织重构','Linger PolyStrata local MoE GPU RAM SSD inference license')
 (p/name).write_text(s)
saved=[]
for name in ['feature-local-computer.jpg','feature-local-engine.jpg','feature-local-stack.jpg','feature-local-moe.webp']:
 f=Path('/Users/jason/.heinu1-bot/media')/('linger-20261120-'+name);shutil.copy2(Path('/tmp/linger-20261120/assets')/name,f);saved.append(str(f))
(p/'saved-files.json').write_text(json.dumps(saved,indent=2));(p/'source-pin.json').write_text(json.dumps({'linger':'8b8aea78820f52e687d3e709dbb56da3e8b982aa','polystrata':'3e1642161198c50ff1abed4046f4e4f476099dbb','date':'2026-11-20','dedup':'OnlyincomingrawKB forPolyStrata, noarticle/receipt/remotedraft. PublishedAPI48001 unavailable.','license':'Linger modifiedApache2 withhostedservice/frontendbrandingconditions; PolyStrataMIT; modelseparate.'},indent=2))
mem=Path('/Users/jason/.claude/projects/-Users-jason-Dev-mycelium-blog/memory');f=mem/f'project_{slug}.md'
f.write_text(f'''---
name: Linger PolyStrata local agent and MoE inference
description: CPU GPU expert placement, benchmarkconditions and separate product licenses.
type: project
---
# Linger and PolyStrata
Source: https://github.com/simplexai-labs/linger and https://github.com/simplexai-labs/PolyStrata
Pins: Linger8b8aea78,PolyStrata3e164216. Date2026-11-20. Slug: {slug}
Dedup: incomingrawKB only exactPolyStrata; noexistingarticle/localreceipt/remotedraft;publishedAPI48001unavailable.
License: Linger modifiedApache2, restrictions onhostedmanagedserviceforoutsideorg andfrontendlogo/copyright; notplainApache2. PolyStrataMIT;engine/model/assetsownlicenses.
MoEoffload includesCPUcomputationofRAMexperts concurrently withGPUcachedexperts, notalleachexpertmustmovetoGPU. QwenengineunchangedStrata; other11strata-polyseparate. SSD normalQwenngram28.8GBtable plusOSfilecache; oversizedweights/lowRAMexpertpoolmaypagedisk. 125Btotal notallactive token;39GB2bitfile notVRAMallocation/qualityguarantee.
45.5/179 areLingerREADMEwritingclaims, incompletesametablesettings. SeparatecommunityOct9 Strata0.1.41 RTX3060+i7-12700/64GBWin11 IQ2_XS4Kprompt45.5median,32K40.8 TTFT35.4s; don'tassumesamesourceprotocol. Linger simulated12GB+32GB on96GBcard gives21.3short/34.1after62KTTFT3min, notphysical3060. Mac16GBrecommend4B, not125B; AutopilotqualityscoresnotproofequalClaude. Local/BYOK/subscription changewherebackgroundmemorycallsgo. NoNVIDIAspeed/125Bweights/LoCoMofullagentreplication.
Blog pending. WeChat pending. Semantic pending.
''')
i=mem/'MEMORY.md';s=i.read_text()
if f.name not in s:i.write_text(s+f'\n- [Linger PolyStrata]({f.name}) — localagent, expert placement andbenchmarklicenseboundaries.\n')
print(json.dumps({'slug':slug,'savedImages':len(saved)}))
