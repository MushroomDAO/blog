---
title: "Awesome Short Drama Skills：83 个短剧技能项目怎么选？"
titleEn: "Awesome Short Drama Skills: A Practical Selection Guide"
description: "Awesome Short Drama Skills 按创作阶段、视频模型和智能体整理短剧工具，附带选型助手与公开盲评。本文核查其83个技能项目、16个平台和CC0许可范围，复核两轮评测的文件指纹与提示词记录，说明如何从改编、剧本、分镜走到视频生成，以及安装范围、商用授权、成本和评测结论的实际边界。"
descriptionEn: "Explore a curated short-drama skills directory, its selector and public evaluations, with local verification, a practical workflow and clear licensing limits."
wechatTitle: "短剧Skill怎么选？这个开源目录有实测记录"
wechatDigest: "从83个技能项目中按创作阶段选工具，并核查公开评测的可信边界。"
pubDate: "2026-10-29"
updatedDate: "2026-10-29"
category: "Tech-News"
tags: ["Agent Skills", "AI Video", "Short Drama", "Open Source", "Creative Workflow"]
heroImage: "../../assets/images/awesome-short-drama-skills-guide-banner.jpg"
lastPublishedAt: "2026-10-29T11:08:46Z"
---

做 AI 短剧，先找出卡住的创作环节，再挑 Skill。Awesome Short Drama Skills 把改编、剧本、分镜和视频提示词分类整理，还提供一个帮助选工具的 Skill。它的价值是降低试错和筛选成本，视频生成能力仍由具体工具和模型提供。

仓库地址：https://github.com/UnderleveledBuilder/awesome-short-drama-skills

在线目录：https://shortdramaskills.com

维护账号为 UnderleveledBuilder，README 标注的 X 账号为 @UnderleveledDev。以下核查固定到提交 `4c3ba567a35325bd9041858d56116fc4ebbcdc43`，日期为 2026 年 10 月 29 日，避免后续目录变化影响结论。

## 83 个项目，究竟收录了什么？

固定版本及官网 `data.json` 都包含 99 条记录，元数据日期为 2026 年 10 月 26 日。其中 83 个属于 Skill 或提示词项目，另外 16 个是完整平台。83 是项目数量，不是技能文件总数；一个项目可能包含多个 Skill。

| 分类 | 项目数 | 用来解决什么问题 |
|---|---:|---|
| 全流程 | 23 | 串联改编、人物、剧本和后续视觉环节 |
| 编剧 | 10 | 聚焦剧本、改编和审稿 |
| 分镜与视觉 | 39 | 镜头、角色资产和图像／视频提示词 |
| 上游故事评估 | 3 | 判断原作与改编方向 |
| 创作方法 | 5 | 人物、结构和叙事方法 |
| 配套工具 | 3 | 支持制作中的专项需求 |
| 完整平台 | 16 | 应用层面的制作工作流 |

按格式统计，99 条中有 81 个标准 Skill 项目、2 个提示词项目、16 个应用。目录同时按创作阶段、适配视频模型和明确声明支持的智能体索引，适合从需求进入，而不是从星标榜单开始安装。

“人工核对”在这里有明确范围：检查仓库说明、目录和分类。它不表示每项效果都经过评测，也不表示每条安装命令都已逐一运行。作者在 README 中保留了这些限制。

固定版本数据：https://github.com/UnderleveledBuilder/awesome-short-drama-skills/blob/4c3ba567a35325bd9041858d56116fc4ebbcdc43/data/skills.toml

![小M按改编、剧本和分镜三个创作需求挑选工具，示意图](../../assets/images/awesome-short-drama-skills-guide-fig-01.png)

## 一条安装命令，会装进哪些能力？

仓库提供的入口是：

```bash
npx skills add UnderleveledBuilder/awesome-short-drama-skills
```

**装入的是 `short-drama-skill-finder` 选型助手，不是把 83 个项目全部安装。** 它读取官网的结构化列表，结合需求筛选；网站访问失败时，说明文件给出了回退到 GitHub README 的路径。

选型时，它会关注创作阶段、目标视频模型、正在使用的智能体、输出语言和许可证。匹配后优先看人工精选、明确的智能体支持、标准格式和更新状态，星标主要用于进一步排序。完整平台与技能包也会分别处理。

一个可直接借用的提问方式是：

> 将一篇已获改编授权的原创故事做成三集竖屏短剧。当前只需要分集大纲、人物设定与第一集剧本，使用支持 Skill 的编程助手，后续计划使用 Seedance。请推荐不超过三个项目，说明各自负责的环节、交接文件、许可证和目录数据日期，暂不安装。

把交付物说清楚，比“推荐最强短剧 Skill”更容易得到可检查的答案。本次核查没有执行安装，也没有运行助手进行一轮新的模型选型；这里描述的是已读取的选型说明。

选型助手原文：https://github.com/UnderleveledBuilder/awesome-short-drama-skills/blob/4c3ba567a35325bd9041858d56116fc4ebbcdc43/skills/short-drama-skill-finder/SKILL.md

## 公开盲评值得信任到什么程度？

这个目录值得关注的一点，是作者把推荐与评测分开。第一轮比较剧本，第二轮比较选题；两轮都包含不装 Skill 的对照，记录参赛版本，多次运行，并公开匿名稿、评审记录和统计代码。

本次在固定提交上，用 Python 3.12.14 执行了目录校验、README 一致性检查，以及两轮 `evals/verify.py`。后者核对文件指纹、重建评审提示词并重算公开记录中的统计。

| 本地检查 | 结果 |
|---|---|
| `scripts/build.py --validate` | 99 个项目、4 个推荐组合，校验通过 |
| `scripts/build.py --check` | README 与数据一致 |
| 第一轮公开记录 | 636 个文件指纹匹配；120 次 Opus、121 次 GPT 提示词重建匹配 |
| 第二轮公开记录 | 1,011 个文件指纹匹配；397 次 Opus、397 次 GPT 提示词重建匹配 |

两轮合计核对 1,647 个文件和 1,035 次提示词重建，未出现不符。默认环境最初因 Python 版本缺少 `tomllib` 而失败，切换到满足项目要求的 Python 3.12 后通过；无需修改上游代码。

这些结果说明公开材料内部可以核对，不能证明当初每个运行条件都被独立见证，更不是重新调用模型重跑评测。本次没有生成新剧本、新评审或视频，也没有测播放量、完播率和付费转化。

评测还有几项会影响选型的限制：生成端只使用作者记录的一种模型；每个 Skill 的重复次数和输入种类有限；两位 AI 评审会有分歧；需要联网查榜的技能受离线沙箱影响。换了模型、题材、受众或工具权限，名次未必保持。

第一轮的部分参赛项目，按公开记录，在两位评审下都胜过对照；第二轮也有项目落在不装 Skill 的对照之后。合理的用法是阅读原稿与点评，缩小候选集，再用自己的同一份任务比较，而不是把一次排名推广到所有短剧。

评测方法：https://github.com/UnderleveledBuilder/awesome-short-drama-skills/blob/4c3ba567a35325bd9041858d56116fc4ebbcdc43/evals/README.md

第一轮：https://shortdramaskills.com/evals/round-1/

第二轮：https://shortdramaskills.com/evals/round-2/

![小M用放大镜核查评测档案，旁边的观众席代表仍需实际观众验证的效果](../../assets/images/awesome-short-drama-skills-guide-fig-02.png)

## 一个小团队应该怎样开始？

先做一集的小样，给每个环节设定可以验收的交付物。下面是一条建议流程，不是目录已经验证过的最佳组合。

| 环节 | 首轮交付 | 进入下一步前检查 |
|---|---|---|
| 改编与人物 | 一页故事梗概、人物目标、三集大纲 | 冲突能否通过行动表达，角色动机是否一致 |
| 单集剧本 | 第一集完整对白与动作 | 信息是否重复、转折是否成立、结尾是否有继续观看的理由 |
| 分镜与资产 | 镜头表、角色参考、场景清单 | 镜头能否连续，人物与关键物件是否一致 |
| 生成与剪辑 | 少量代表镜头、粗剪样片 | 实际生成成本、返工次数、视听连贯性 |

目录中的 `zenstory-ai/drama-skills` 可以作为全流程候选，`Shanyin-ai/shanyin-screenwriting-master` 可以作为人物与剧本方向的候选；这只是依据目录分类给出的比较起点，不是本次重跑后的效果推荐。选定后还要读各自说明。

协作时，比多装几个技能更重要的是交接约定。例如，全程使用同一份人物设定；镜头表中的角色 ID 与资产文件名一致；修改剧本后同步标记受影响的分镜。否则，上一个工具写出的关键细节，可能被下一个工具重新发明。

相关项目：https://github.com/zenstory-ai/drama-skills

https://github.com/Shanyin-ai/shanyin-screenwriting-master

关于视频制作 Skill 的另一条工作流，可参阅本站的既有调研：https://blog.mushroom.cv/blog/lemo-opuscar-code-video-skill/

![小M把统一人物设定依次交给剧本、分镜和生成环节，示意图](../../assets/images/awesome-short-drama-skills-guide-fig-03.png)

## 开源目录，是否意味着出片免费、素材可商用？

目录自身采用 CC0 1.0。这个声明不自动改变被收录项目的许可证，也不替代小说改编、音乐、字体、肖像或生成服务的使用授权。

Skill 可以产出文字流程、分镜与提示词。真正生成图像、配音和视频，仍需相应模型、服务或本地算力；生成失败、角色不一致与剪辑返工也会产生时间或调用成本。一个镜头写得漂亮，不等于选定的视频模型一定能够按描述执行。

本次还检查了官网分享图：它仍显示“82 skills + 14 platforms”，而固定版本数据与在线列表已是 83+16。该图已下载留存，文章统计采用数据文件，并标注日期。封面另按主题制作，避免把旧数字放进新文章。

目录许可：https://github.com/UnderleveledBuilder/awesome-short-drama-skills/blob/4c3ba567a35325bd9041858d56116fc4ebbcdc43/LICENSE

更适合把这个项目当作一套可维护的选型资料：先用分类找到候选，再检查公开产物与适用条件，最后让自己的小样决定是否继续投入。它能减少搜集资料的重复劳动，创作判断和最终验收仍留在团队手中。

## 常见问题

### 这是一个新的视频生成模型吗？

它是分类目录、选型助手和评测资料的组合。图像或视频生成来自后续选用的项目与服务。

### Mac 上需要独立显卡吗？

阅读目录、检查数据和使用文字类 Skill，没有这里统一规定的独显要求。若运行本地图像或视频模型，内存、显存和系统要求由那个项目决定；不能用目录本身很轻量推导整个出片流程都轻量。

### 推荐组合已经跑通成片了吗？

README 将推荐组合标为根据说明搭配的初版，尚未实测。公开的剧本、选题评测也不等于整条视频生产链路验收，应从一集小样验证交接和成本。

---

> © 2026 Author: Mycelium Protocol. 本文采用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.zh) 授权——欢迎转载和引用，须注明作者姓名及原文链接，不得去除署名后以原创发布。

<!--EN-->

For an AI short drama, identify the blocked production stage before installing more skills. Awesome Short Drama Skills organizes adaptation, scripts, storyboards and video prompts, with a separate selector skill. Its value is reducing discovery and selection work; actual generation still depends on the chosen tools and models.

Repository: https://github.com/UnderleveledBuilder/awesome-short-drama-skills

Website: https://shortdramaskills.com

The maintainer account is UnderleveledBuilder; the README links to @UnderleveledDev on X. This review pins commit `4c3ba567a35325bd9041858d56116fc4ebbcdc43`, inspected on October 29, 2026.

## What do the 83 projects contain?

The pinned source and live `data.json` both contain 99 entries, with metadata dated October 26. Of these, 83 are skill or prompt projects and 16 are platforms. Project count is distinct from individual skill-file count.

| Group | Projects | Purpose |
|---|---:|---|
| Pipeline | 23 | Connect adaptation, characters, scripts and visual stages |
| Writing | 10 | Scripts, adaptation and review |
| Visual | 39 | Shots, assets and image/video prompts |
| Source evaluation | 3 | Assess source stories and adaptation direction |
| Craft | 5 | Character, structure and storytelling methods |
| Companion | 3 | Supporting production tasks |
| Platforms | 16 | Application-level workflows |

Across all entries, the format breakdown is 81 standard skill projects, two prompt projects and 16 applications. Stage, target video model and explicitly declared agent support provide additional filters.

The maintainer's manual checks cover descriptions, structure and classification. They do not establish that every project, installation command or production result has been tested.

Pinned data: https://github.com/UnderleveledBuilder/awesome-short-drama-skills/blob/4c3ba567a35325bd9041858d56116fc4ebbcdc43/data/skills.toml

![XiaoM selects tools according to adaptation, scripting and storyboard needs; conceptual illustration](../../assets/images/awesome-short-drama-skills-guide-fig-01.png)

## What does the installation command install?

```bash
npx skills add UnderleveledBuilder/awesome-short-drama-skills
```

It installs the `short-drama-skill-finder` selector, rather than all 83 projects. The instructions fetch the site's structured list, with a GitHub README fallback.

Selection considers stage, video model, agent, language and licensing. Editorial picks, explicit agent support, standard format and maintenance inform matching; stars serve mainly as a tie-breaker. Full applications are distinguished from skills.

A useful request specifies an authorized source story, intended episodes, required deliverables, agent and video model. Ask for at most three candidates, their responsibilities, handoff files, licenses and data date, initially without installing them.

This review inspected the selector instructions but did not install or run the skill through a new model-based selection session.

Selector: https://github.com/UnderleveledBuilder/awesome-short-drama-skills/blob/4c3ba567a35325bd9041858d56116fc4ebbcdc43/skills/short-drama-skill-finder/SKILL.md

## How much does the public evaluation establish?

The repository separates editorial checking from testing. Its first round compares scripts; the second compares topics. Both include a no-skill baseline, repeated runs, pinned contestant versions, anonymized outputs and public judging records.

Local verification used Python 3.12.14:

| Check | Result |
|---|---|
| Catalogue validation | 99 projects and four suggested stacks passed |
| README consistency | Generated content matches data |
| Round one | 636 file hashes matched; 120 Opus and 121 GPT judging prompts reconstructed successfully |
| Round two | 1,011 file hashes matched; 397 Opus and 397 GPT judging prompts reconstructed successfully |

That totals 1,647 files and 1,035 prompt reconstructions without mismatches. The default Python initially lacked `tomllib`; using the project's required modern Python resolved the issue without changing upstream code.

The scripts also recompute statistics from the published records. These checks establish internal consistency, not independent observation of the original runs. No new script generation, judging, video production, retention measurement or conversion test was performed.

The published comparison uses one generation model, limited input diversity and repetitions, and two AI judges whose preferences sometimes diverge. An offline sandbox disadvantages tools that require online research. Changing models, genres, audiences or tool access can change outcomes.

Some contestants beat the baseline in the recorded comparisons, while others ranked below it. Read the outputs and critique, shortlist candidates, then compare them using the same brief from an actual project.

Method: https://github.com/UnderleveledBuilder/awesome-short-drama-skills/blob/4c3ba567a35325bd9041858d56116fc4ebbcdc43/evals/README.md

Round one: https://shortdramaskills.com/evals/round-1/

Round two: https://shortdramaskills.com/evals/round-2/

![XiaoM verifies evaluation records while audience seats represent the separate need for real viewer testing](../../assets/images/awesome-short-drama-skills-guide-fig-02.png)

## How should a small team begin?

Start with one episode and explicit acceptance criteria. The following is a proposed workflow, not a stack already validated by this catalogue.

| Stage | First deliverable | Acceptance question |
|---|---|---|
| Adaptation and characters | Synopsis, character goals, three-episode outline | Are motives coherent and conflicts visible through action? |
| Script | Complete first-episode dialogue and action | Does it avoid repetition and earn its turns and ending? |
| Shots and assets | Shot list, character references, scene inventory | Do shots connect and identities remain consistent? |
| Generation and editing | Representative generated shots and a rough cut | What are actual costs, revision counts and continuity problems? |

The catalogue lists `zenstory-ai/drama-skills` as a pipeline candidate and `Shanyin-ai/shanyin-screenwriting-master` for character and script development. These are classification-based starting points, not fresh quality recommendations from this review.

Shared handoffs matter: retain a common character sheet, match character IDs to asset filenames, and mark which shots a script revision changes. Otherwise separate tools may reinvent details that should remain fixed.

Project links: https://github.com/zenstory-ai/drama-skills

https://github.com/Shanyin-ai/shanyin-screenwriting-master

Related production workflow research: https://blog.mushroom.cv/blog/lemo-opuscar-code-video-skill/

![XiaoM carries a shared character reference through script, storyboard and generation handoffs](../../assets/images/awesome-short-drama-skills-guide-fig-03.png)

## Does an open catalogue make production free?

The directory's CC0 dedication does not relicense linked projects, source novels, music, fonts, likenesses or generation services. Check the components actually used.

Skills can produce plans and prompts. Images, speech and video still require compatible services or local compute, and retries and editing consume resources. A strong written shot description does not establish that a video model can execute it reliably.

The official social image still says 82 skills plus 14 platforms; both pinned data and the live list say 83 plus 16. The image was downloaded for the record, while the article uses dated data and a separately prepared thematic cover.

License: https://github.com/UnderleveledBuilder/awesome-short-drama-skills/blob/4c3ba567a35325bd9041858d56116fc4ebbcdc43/LICENSE

Use the repository as maintainable selection material: find candidates by stage, inspect public artifacts and constraints, then let a small production sample determine further investment. It reduces repeated research while leaving creative decisions and acceptance with the team.

## FAQ

### Is this a video generation model?

It combines a directory, a selector and evaluation materials. Selected downstream projects and services provide generation.

### Does a Mac need a discrete GPU?

Reading the catalogue, checking its data and using text skills have no shared discrete-GPU requirement here. Local image or video generation inherits the selected project's hardware requirements; a lightweight directory does not make the entire production workflow lightweight.

### Have the suggested stacks been validated end to end?

The README labels them initial combinations based on project descriptions, not tested stacks. Script and topic comparisons do not establish finished-video pipeline reliability. Verify handoffs and costs with one episode first.

---

> © 2026 Author: Mycelium Protocol. Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) — free to share and adapt with attribution. You must credit the author and link to the original; removing attribution and republishing as original is not permitted.
