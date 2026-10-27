from pathlib import Path
import json,datetime
root=Path(__file__).resolve().parents[2]
src=Path(__file__).resolve().parent
slug='roboharness-v2-workspace'
job=Path('/Users/jason/.heinu1-bot/jobs/be1cdb1e-7a71-4631-a8c7-7b4e2b2a0453')
public=json.loads((src/'public-verification.json').read_text());article=public['articles'][0]
w=json.loads((src/'wechat-verification.json').read_text())['drafts'][0]
assert article['HTTP']==200 and article['carouselRank']==1
assert w['fullTextMatches'] and w['imageIdentitiesMatch'] and w['coverMatches']
r={'slug':slug,'blogUrl':article['url'],'mediaId':w['mediaId'],'archivedMediaId':'','wechatStatus':'draft','wechatError':''}
for p in [src/'publication-result.json',job/'publication-result.json']:
 p.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n')
(job/'results.json').write_text(json.dumps({'results':[r]},ensure_ascii=False,indent=2)+'\n')
(src/'.published').write_text(article['url']+'\n'+datetime.datetime.now(datetime.timezone.utc).isoformat()+'\n')
(src/'.state.json').write_text(json.dumps({'status':'published','wechatStatus':'draft','slug':slug,'blogUrl':article['url'],'mediaId':w['mediaId']},indent=2)+'\n')
mem=Path('/Users/jason/.claude/projects/-Users-jason-Dev-mycelium-blog/memory/project_'+slug+'.md')
mem.write_text('''---
name: RoboHarness V2 workspace robot harness
description: Published bilingual source audit and verified WeChat draft
type: project
---
Sources: https://github.com/BinceQu/RoboHarness and https://bincequ.github.io/RoboHarness/v2/
Published 2026-10-27. Exact URL/entity dedup found only raw KB, no existing Blog/M2/draft; no duplicate publication.
Source commit a0936867e0db7d0ef3eabe10688468edaea190d8. V2 open Oct25; design note explicitly says results later. V1 paper results do not validate V2. Self-contained R1 Pro / BEHAVIOR and ARX X5 / RoboDojo workspaces expose instructions, URDF/joints, Python actions, perception and call history. R1 27-value mixed-unit controller, X5 14 scalars. Editable code/skills are not model-weight learning. Direct joint control has no collision planner; independent physical safety layer is our recommendation, not supplied certification.
Official Linux x86-64 NVIDIA CUDA12.4 simulator path; Python3.11 evaluator versus Python3.10 V2 workspace; 48GB validated capacity is not minimum. ARX workspace CPU install does not prove whole simulator CPU operation. Mac M4 16GB selected unmodified upstream tests:16 passed (IPC4/receipt3/GPU config9), no GPU, model, sim, real-robot or performance validation.
'''+f'Blog: {article["url"]}\nWeChat current draft verified by draft/get: {w["mediaId"]}\nFull visible text, three image identities, title/author/digest/cover/canonical/comments match. Published API48001 unavailable; no existing old receipt was found.\nBanner local FLUX seed95, three XiaoM body illustrations. Official five images saved in bot media; source and proofs source/20261027-roboharness-v2.\n')
kb={'title':'RoboHarness V2机器人工作空间','summary':'RoboHarness V2 将机器人构型、关节手册、感知文件、Python 动作工具和任务技能放入可编辑的工作空间，供编程智能体检查、执行和改进动作。官方提供 R1 Pro 与 ARX X5 模板，V2 页面为设计说明，新成绩尚待发布，不能套用 V1 论文结果。本机16项CPU边界测试通过，未进行仿真或真机效果测试。','tags':['机器人','具身智能','Coding Agent','开源','工作空间'],'entities':['RoboHarness V2','Bince Qu','R1 Pro','ARX X5','BEHAVIOR','RoboDojo'],'content_type':'url','saved_files':sorted(str(x) for x in Path('/Users/jason/.heinu1-bot/media').glob('roboharness-v2-*'))}
(job/'kb-record.json').write_text(json.dumps(kb,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(r,ensure_ascii=False))
