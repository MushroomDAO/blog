from pathlib import Path
import json,shutil
p=Path(__file__).parent;old=p.parent/'20261120-awesome-3d-coding';slug='aura-streaming-avatar-causal-distillation-guide';oldslug='awesome-3d-coding-research-map-evaluation-guide';job='f1eb66fd-32b5-4940-b57a-958cb418aa42'
for name in ['check.py','verify-public.py','verify-preserved.py','verify-wechat.cjs','wechat-content-canonical.py','remote-preflight.cjs','check-semantic.py','mine-kb.py','verify-kb.py','compress-figures.py','stage-source.py']:
 s=(old/name).read_text().replace(oldslug,slug).replace('2a394977-41d1-4814-b4d4-59dfdc13ec50',job).replace('source/20261120-awesome-3d-coding','source/20261121-aura')
 if name=='verify-preserved.py':s=s.replace('slugs=[','slugs=["'+oldslug+'",')
 if name=='remote-preflight.cjs':
  a=s.index('const matches=');b=s.index('const{data:p}',a);s=s[:a]+'const matches=items.filter(x=>/2611.26540|kyutai-labs\\/aura|aura-streaming-avatar-causal-distillation-guide/i.test(JSON.stringify(x)));'+s[b:]
 if name=='check-semantic.py':s=s.replace('Awesome-3D-Coding jweihe 3DCodeVerse CADTestBench StateProbe','AURA Kyutai 流式数字人 rolling KV cache H100 distillation')
 (p/name).write_text(s)
(p/'research').mkdir(exist_ok=True);(p/'slugs.json').write_text(json.dumps([slug]));shutil.copy2('/tmp/aura-dedup.log',p/'duplicate-check.log')
(p/'source-pin.json').write_text(json.dumps({'repo':'https://github.com/kyutai-labs/aura','revision':'c06aa7dc8b850405273345089da521454ffd607e','paper':'2611.26540v1','paperDate':'2026-11-19','codeLicense':'Snap Inc NonCommercial','model13':'53558287fd7c62d33fc4217f5f4e7b8d2d729526 CC BYNC4','model5':'4442f4e4d59eb912ac09b8d1cc9d52522ee9b0d4 SnapNonCommercial','dataset':'69b599373c24a49c8c7e8027143e7595f1afb5df CC BYNC4 partialrelease','privateSourceArchive':'/Users/jason/.heinu1-bot/jobs/'+job+'/research','dedup':'ExactpaperURLandAURA clear; genericarxivfalsepositives frombot.'},indent=2))
mem=Path('/Users/jason/.claude/projects/-Users-jason-Dev-mycelium-blog/memory');f=mem/f'project_{slug}.md';f.write_text(f'''---
name: AURA streaming avatar research
description: Kyutai causalavatar distillation speed and release/license boundaries.
type: project
---
# AURA streaming avatar
Sources https://arxiv.org/abs/2611.26540 and https://github.com/kyutai-labs/aura pin c06aa7dc8b850405273345089da521454ffd607e. Slug {slug}. Date2026-11-21. Exactdedupclear, botarxivgenericfalsepositives. Not AURA visualunderstanding2604.04184.
PaperH100 optimized20.7fps1.3B16Hz576p /9.7fps5B25Hz720p; referencecodecompiled~16/~8fps different. Endtoendexcludesloadwarmup, notTTFT. Fourlatentframes16video frames (~1s16Hz/.64s25Hz;first13frames), notzerobuffer. 1.3codebuckets576square/512x768; notalways16:9. Rollingcacheanchor+lastpast+current; repeateddenoisingoverwritescurrent,cachefixedRoPEbounded13Bonly. Stage1ODEteacherforcing,stage2DMDbackwardsimulation noGAN. CLIpre-encodesaudiofilebeforevideoloop, chunkyieldnotliveinputproof; livedemoUnmuteextra.
CodeSnapNoncommercial,1.3BweightsCCBYNC4,5BweightsSnapNC, dataCCBYNC4. Datasetpartial:1.3BODElatents30000train200validation,5BTalkVerse30Kdecodedvideoscomingsoon,referencepromptsimagesnotredistributed. 100syntheticCPUcacheiterations passed directupstreamclass, no realmodels/CUDA/render/latencytest. Torch2.14 outsideproject2.6to2.8, notfullruntimecompatibilityproof. Paper32pagesreviewmethod/results/stability/supplement, nofullproof/benchreplication.
Blog/WeChat/semantic pending.
''');i=mem/'MEMORY.md'
if f.name not in i.read_text():i.write_text(i.read_text()+f'\n- [AURA streaming avatar]({f.name}) — causaldistillation, H100speed andpartialresearchrelease.\n')
