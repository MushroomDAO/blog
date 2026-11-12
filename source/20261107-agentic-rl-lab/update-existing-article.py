# Historical construction script, archived for review; do not rerun against finalized article.
from pathlib import Path
import json,datetime,shutil
s='agentic-rl-lab-grpo-vision-post-training-low-cost-geometry';o=Path('source/20261107-agentic-rl-lab');o.mkdir(exist_ok=True);j=Path('/Users/jason/.heinu1-bot/jobs/8c745da2-b954-4728-b381-b8a1792caf1c')
for n in ['README.md','LICENSE'] :shutil.copy(Path('/tmp/agentic-rl-lab-research')/n,o/('upstream-'+n))
for n in ['readme.md','train.py','start.md','analysis.py']:shutil.copy(Path('/tmp/agentic-rl-lab-research/experiments/vision-grpo')/n,o/('vision-'+n))
shutil.copy(j/'duplicate-check.json',o/'duplicate-check.json')
old=json.loads(Path('pipeline/m2/output',s+'.json').read_text());err='旧草稿draft/get返回40007，远程草稿箱11条中无此文章；已发布列表返回48001（无权限），当前状态未核验。保留旧创建凭证，未重复创建草稿；旧凭证不代表已同步本次修订。'
r=dict(slug=s,blogUrl='https://blog.mushroom.cv/blog/'+s+'/',mediaId='',archivedMediaId=old['mediaId'],wechatStatus='recorded',wechatError=err)
for p in [o/'publication-result.json',j/'publication-result.json']:p.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n')
old.update(wechatStatus='recorded',currentMediaId='',archivedMediaId=old['mediaId'],wechatError=err,currentStatusCheckedAt=datetime.datetime.now(datetime.timezone.utc).isoformat());Path('pipeline/m2/output',s+'.json').write_text(json.dumps(old,ensure_ascii=False,indent=2)+'\n')
remote=json.loads((j/'remote-verification.json').read_text());assert len(remote['draftBox']['item'])==remote['draftBox']['total_count'];(o/'wechat-current-status.json').write_text(json.dumps(dict(draftGetError=40007,publishedListError=48001,draftTotal=11,draftFetched=11,newDraftCreated=False),indent=2))
kb=Path('/Users/jason/.claude/projects/-Users-jason-Dev-mycelium-blog/memory');k=kb/f'project_{s}.md'
k.write_text('---\nname: agentic-rl-lab verification and correction\ndescription: Datawhale RL tutorials, cost and benchmark boundaries; existing article reused.\ntype: project\n---\n\nSource: https://github.com/datawhalechina/agentic-rl-lab\nPinned commit: 238bc688ca7d5c994c580f732ee9c2c92483bd20\nBlog: '+r['blogUrl']+'\n2026-11-07: existing 2026-08-10 article reused and corrected, no duplicate route. Apache-2.0 educational experiments using paid remote PyTRIO. Author 20-step session cost 5.06 yuan; NOT documented total cost of 100-step run. Author fixed100 GeoQA accuracy71 to87 percent, format75 to91; no per-sample JSON or remote checkpoint. Not independently reproduced. Current code experiments/vision-grpo.\nWeChat: recorded; current mediaId empty; archived creation credential '+old['mediaId']+'\n'+err+'\nBlog update/semantic verification pending.\n')
idx=kb/'MEMORY.md';t=idx.read_text();link=f'project_{s}.md'
if link not in t:idx.write_text(t.rstrip()+f'\n- [{s}]({link}) — revised RL tutorial verification.\n')
p=Path('src/content/blog',s+'.md');t=p.read_text();t=t.replace('5块钱让大模型学会看图做几何题：GRPO 后训练的低成本实验','agentic-rl-lab：从几何题入门Agent强化学习').replace('titleEn: "'+s+'"','titleEn: "agentic-rl-lab: A Practical Guide to Agent RL"').replace('updatedDate: "2026-08-10"','updatedDate: "2026-11-07"')
lines=t.splitlines();desc='agentic-rl-lab是Datawhale开源的Agent强化学习实验教程，使用PyTRIO远程训练服务拆解GRPO、蒸馏、搜索和工具调用。本篇核对源码，纠正约5元小规模会话与100步结果的混淆，解释固定100题测试、格式遵循和推理能力的区别，并给出从奖励函数、采样到独立评测的学习路径，避免把作者记录当作独立复现。'
en='Explore Datawhale’s agentic-rl-lab tutorials, PyTRIO training, GRPO rewards and evaluation limits, with corrected cost claims and a practical learning pathway.'
for i,l in enumerate(lines):
 if l.startswith('description:'):lines[i]='description: '+json.dumps(desc,ensure_ascii=False)
 if l.startswith('descriptionEn:'):lines[i]='descriptionEn: '+json.dumps(en)
t='\n'.join(lines)+'\n';t=t.replace('pubDate:','wechatTitle: "agentic-rl-lab：低门槛学强化学习"\nwechatDigest: "核对训练代码与实验记录，分清小规模费用、格式改善与真实能力提升。"\npubDate:',1)
t=t.replace('https://github.com/KMnO4-zx/agentic-rl-lab','https://github.com/datawhalechina/agentic-rl-lab').replace('| ⭐ 147 |','| 2026-11-07 核对 |').replace('147 stars, ','')
t=t.replace('用这个方式，他在 Qwen3.5-4B 上做了一次几何图形问答的 Vision GRPO 后训练，花了 5 块钱，100 步，准确率从 71% 升到了 87%。','作者记录了两组不同信息：20步小规模会话花费约5.06元；100步 checkpoint 在固定100道题上的准确率从71%提高到87%。仓库没有给出100步正式实验的可核验总费用，不能把两者拼成“5元训练100步”。')
t=t.replace('100 步，5 块钱，+16pp。','这是作者在固定100题子集上的单次对照，提升16个百分点。仓库没有提交逐题评测JSON与远端checkpoint，本文也没有复跑训练。100步正式实验总费用未核验。')
t=t.replace('Using this approach, he ran Vision GRPO post-training on Qwen3.5-4B for geometric visual QA — ¥5, 100 steps, accuracy up from 71% to 87%.','Two records must be separated: a 20-step session cost about ¥5.06, while the 100-step checkpoint scored 87% versus 71% on a fixed 100-question subset. The repository does not establish the total cost of the 100-step run. This article did not reproduce training.')
t=t.replace('100 steps. ¥5. +16pp.','The author reports a 16 percentage-point increase on a fixed 100-question subset, not the complete test set. Per-example evaluation JSON and the remote checkpoint are not included. The total cost of the 100-step run is unverified.')
t=t.replace('## ¥5 to Teach a Vision Model Geometry: Low-Cost Post-Training with GRPO','## agentic-rl-lab: Learning Agent Reinforcement Learning Through Experiments')
t=t.replace('cd 09-vision-grpo','cd experiments/vision-grpo').replace('# Chapter 9: see 09-vision-grpo/start.md','# Vision chapter: see experiments/vision-grpo/start.md')
cn='''agentic-rl-lab是一套把奖励、采样、训练和评测串起来的Agent强化学习实验教程，适合已经会写Python、希望理解后训练的人。它采用Apache-2.0协议，目前由Datawhale仓库维护；训练示例依赖PyTRIO远端服务，开源代码不等于免费算力。

## 2026年11月更新：应该怎样读这个仓库？

仓库现已把实验统一放到`experiments/`，包含GRPO、GSPO、DAPO、OPD、OPSD、Search-R1、ReTool、ALFWorld，以及TEMPO、AgentOPSD、Spec-o3等章节。它定位是实验记录和教程；README把更友好、轻量的训练框架列为未来方向，不能当作已交付的通用生产框架。

![小M沿数据、奖励、采样和参数更新读懂强化学习闭环](../../assets/images/SLUG-fig-01.png)

最值得学的是边界如何拆开：数据模块定义题目和答案，rollout生成多条轨迹，reward给轨迹打分，训练脚本构造优势并调用远端更新，eval再用固定数据验证。可验证答案任务容易写规则奖励；搜索、代码执行或长任务则还需要环境反馈、工具权限、超时和轨迹归因。不要把“接入工具”直接等同于“Agent已经学会可靠使用工具”。

## 71%到87%，具体改善了什么？

Vision GRPO记录的格式正确率同时从75%升到91%。在格式正确的回答内部，正确率分别为71/75≈94.7%与87/91≈95.6%。这说明总分增长与更稳定地遵循可解析输出格式紧密相关，不能仅凭总分就断言几何推理发生了同等幅度跃迁。两个checkpoint的格式正确样本集合不同，这个条件比值也不能单独证明因果。

![小M分开小规模费用与100步评测，避免把两份记录合成一次实验](../../assets/images/SLUG-fig-02.png)

独立评测应保留逐题输出、解析失败、正确选项、token数和耗时，扩大到完整测试集，并做多个seed与不参与调参的留出集。固定100题每题就是1个百分点；反复查看同一子集再选checkpoint，会增加选择偏差。项目中的`analysis.py`绘制预先写入的汇总数字，不会自动读取新评测JSON；运行绘图脚本不是复现实验结果。

## 从哪一章开始最有效？

先读Loss Function与文本GRPO，用几道人工检查过的样本走一遍奖励与组内优势：一组全对或全错时，相对奖励通常提供不了区分信号。随后看Vision GRPO，检查图片token对齐与答案解析；最后再进入Search-R1、ReTool或ALFWorld，处理多轮环境反馈。先明确预算、凭证与可停止条件，再启动会产生费用的远端训练；不要把README中的一次花销当作自己的费用上限。

建议先冻结一份base评测，再做小规模训练与独立复测。自定义任务还应加入长度、工具调用次数和实际费用指标，防止模型通过冗长回答或无效调用“刷奖励”。业务任务应先明确什么叫成功，再选择RL，而非先训练再寻找目标。

![小M在训练之外保留独立评测和预算检查](../../assets/images/SLUG-fig-03.png)

## 常见问题

### 普通电脑能本地训练这些模型吗？

本地主要编排实验，重计算由PyTRIO服务承担。这降低本机显存门槛，但不意味着权重训练在普通电脑上完成，也不意味着没有网络与服务费用。

### 约5元能保证获得87%准确率吗？

不能。5.06元是作者20步会话截图；87%来自100步checkpoint的固定100题评测，两者不是同一次成本和效果的对应关系。

### 这是可以直接上线的Agent平台吗？

它首先是实验教程。生产系统仍需要独立评测、凭证保护、工具隔离、失败恢复和监控；本次核对没有运行远端训练，也没有测量新的准确率或费用。

原始仓库：https://github.com/datawhalechina/agentic-rl-lab
Vision实验与成本边界：https://github.com/datawhalechina/agentic-rl-lab/tree/main/experiments/vision-grpo
在线手册：https://datawhalechina.github.io/agentic-rl-lab/

以下保留早期实验的算法讲解；章节数量与历史star数不代表当前仓库规模。

'''.replace('SLUG',s)
enintro='''agentic-rl-lab is an educational collection that connects rewards, rollouts, parameter updates and evaluation for LLM agents. Datawhale maintains the Apache-2.0 repository. Its examples use remote PyTRIO training: open-source code does not make compute free.

### November 7 update: how should this repository be used?

Experiments now live under `experiments/`, covering GRPO, GSPO, DAPO, distillation, Search-R1, ReTool, ALFWorld and newer topics such as TEMPO, AgentOPSD and Spec-o3. The README describes a more friendly training framework as a possible future direction. The repository is primarily a tutorial and experiment log, rather than evidence of a completed production platform.

![Little M follows the data, reward, rollout and update loop](../../assets/images/SLUG-fig-01.png)

Read the boundaries between modules: data defines questions and answers; rollouts produce trajectories; rewards score them; training constructs advantages and requests remote updates; evaluation checks a fixed dataset. Search and tool-use tasks additionally need environment feedback, timeouts and attribution across turns. Exposing a tool is not evidence that an agent reliably learned to use it.

### What does the 71% to 87% increase establish?

The author also reports format compliance increasing from 75% to 91%. Conditional accuracy among parseable responses is 71/75, about 94.7%, versus 87/91, about 95.6%. The aggregate improvement is closely associated with more reliable answer formatting; it cannot establish an equally large gain in geometry reasoning. The two sets of parseable responses also differ, so these ratios alone do not establish causation.

![Little M separates a small-session bill from the 100-step evaluation](../../assets/images/SLUG-fig-02.png)

Retain individual outputs, parsing failures, labels, token counts and latency. Evaluate the full test split, multiple seeds and a holdout excluded from checkpoint selection. Each example in a 100-question subset contributes one percentage point. Repeatedly selecting checkpoints against the same subset risks selection bias. `analysis.py` plots hard-coded summary values rather than loading a newly generated evaluation file; drawing the chart is not reproduction.

### Where should learners start?

Start with loss functions and text GRPO. Manually verify a few rewards and group advantages: all-correct or all-incorrect groups generally provide no relative discrimination. Continue with image-token alignment and answer parsing in Vision GRPO, then tackle multi-turn feedback in Search-R1, ReTool or ALFWorld. Define a budget and stopping conditions before invoking paid remote services. A historical invoice does not cap a future bill.

Freeze a base evaluation first, run a small experiment and then evaluate independently. Add output length, tool-call counts and real costs for custom tasks so reward improvement cannot hide wasteful behavior. Choose reinforcement learning only after defining success for the intended task.

![Little M keeps independent evaluation and budget checks outside training](../../assets/images/SLUG-fig-03.png)

### FAQ

#### Does training happen on an ordinary laptop?

The laptop orchestrates the experiment; PyTRIO performs expensive training remotely. This reduces local memory requirements but introduces network and paid-service dependencies.

#### Does ¥5 guarantee an 87% score?

No. ¥5.06 refers to a 20-step session, whereas 87% refers to the 100-step checkpoint on a fixed 100-question subset. These are different records.

#### Is this a production agent framework?

Its primary role is education. Deployment still requires evaluation, credential management, tool isolation, recovery and monitoring. This review did not run training or independently measure accuracy or cost.

Repository: https://github.com/datawhalechina/agentic-rl-lab
Vision experiment: https://github.com/datawhalechina/agentic-rl-lab/tree/main/experiments/vision-grpo
Manual: https://datawhalechina.github.io/agentic-rl-lab/

The following retains the earlier algorithm explanation; historical chapter counts do not describe the current repository.

'''.replace('SLUG',s)
pos=t.index('*by Mycelium Protocol*');t=t[:pos]+cn+t[pos:];pos=t.index('## agentic-rl-lab: Learning');t=t[:pos]+enintro+t[pos:]
cccn='> © 2026 Author: Mycelium Protocol. 本文采用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.zh) 授权——欢迎转载和引用，须注明作者姓名及原文链接，不得去除署名后以原创发布。'
t=t.replace('<!--EN-->',cccn+'\n\n<!--EN-->');t=t.replace('© 2026 Mycelium Protocol. All rights reserved.','> © 2026 Author: Mycelium Protocol. Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) — free to share and adapt with attribution. You must credit the author and link to the original; removing attribution and republishing as original is not permitted.')
p.write_text(t);print('Updated existing route, description lengths',len(desc),len(en))
