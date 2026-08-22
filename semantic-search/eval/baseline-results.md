# Phase 0A 关键词检索基线结果

> 针对 `queries.md` 的 24 条查询，直接调用 Pagefind 的浏览器端 JS API（跳过 UI，拿原始结果），
> 对每条查询的 top5 结果做人工相关性判断。用于 T1.2.1 离线向量实验时对比"关键词 vs 向量"。
> 测试方式：`pnpm build && pnpm preview`，Playwright 打开 `/search/`，在页面里 `import('/pagefind/pagefind.js')`
> 直接跑 `pagefind.search(query)`，记录每条查询的命中数与 top5 标题/URL。
> 记录日期：2026-08-21

## 逐条结果

| # | 查询 | 命中数 | Top5 相关性判断 |
|---|---|---:|---|
| 1 | Pagefind | 75 | **不相关**——博客里没有文章讨论 Pagefind 这个工具本身（我们只是刚把它接进构建流程），75 条命中都是弱模糊匹配噪音 |
| 2 | Cloudflare Vectorize | 1 | 弱相关——命中一篇 Cloudflare Workers AI 模型文章，博客目前确实没有专门讲 Vectorize 的内容（符合预期，语义检索功能本身还没做） |
| 3 | MCP Model Context Protocol | 62 | **强相关**——top5 全部是真正的 MCP 相关文章（Google Trends MCP、Seeder、FastMCP、Agentic AI 指南、PipesHub） |
| 4 | LoRA 训练 | 27 | **强相关**——top5 中 4/5 是 LoRA 训练/适配器相关文章 |
| 5 | Claude Code Skill | 129 | **强相关**——top5 全部精确匹配 Claude Code Skill 主题 |
| 6 | WebGPU | 5 | 部分相关——top5 中 3/5 真正与 WebGPU/3D 渲染相关 |
| 7 | 我想本地部署一个 AI 视频编辑工具 | 1 | **未命中**——唯一结果（Cursor CTO 异步 Agent）完全不相关，而博客里明明有 video-use/ChatCut/FireRed-OpenStoryline 等视频编辑 Agent 文章（见 #20） |
| 8 | 怎么给 Claude Code 装技能包 | 3 | 弱相关——3 条结果都只是沾边（Codex 技能市场、手绘配图 Skill、LobsterAI），没有命中真正讲"如何安装 Skill"的内容 |
| 9 | local-first sync AI agent | 36 | **强相关**——第一条 Neo Chat（本地优先加密跨设备同步）精确命中 |
| 10 | 有没有讲 Agent 循环设计的文章 | 3 | 弱相关——awesome-agent-architecture（Harness 工程地图）算是相关，其余偏泛 |
| 11 | 脑仿真 大脑连接组 | 0 | **未命中/真实缺口**——博客里其实有 `brain-emulation-worm-to-human-scaling`（中文标题「从线虫到人类：全脑模拟的规模化之路」）、`brain-connectome-data-size-fly-human-mouse`（中文标题「脑子的数据量：从果蝇 20TB 到人脑 1.4PB…」）两篇文章，**两篇都有中文标题也都有英文标题，且页面上两种语言都会渲染**（见 `BlogPost.astro` 的 `titleEn` 展示逻辑），Pagefind 索引的是两种语言的文本，不是只有英文——真正的缺口是"脑仿真""大脑连接组"这两个具体措辞在全库任何语言版本里都不出现（同义词是"全脑模拟""连接组"），是**同语言内的措辞/同义词鸿沟**，不是跨语言桥接缺失 |
| 12 | MLX Apple Silicon guide | 18 | **强相关**——top5 全部精确命中 MLX/Apple Silicon 主题 |
| 13 | AI Agent 记忆系统 | 86 | **强相关**——top5 全部是 Agent 记忆系统相关文章（Wiki Memory、Dense-Mem、TencentDB Agent Memory 等） |
| 14 | 递归自我改进 RSI | 1 | 弱相关——只命中 1 条（awesome-rsi），而同主题的英文查询 #16 命中 9 条且全部相关，说明中文短语召回明显更弱 |
| 15 | 浏览器自动化 Agent | 73 | **强相关**——top5 中 3/5 高度相关（BrowserAct、browser-harness、ego-lite） |
| 16 | 3D 可视化工具 | 11 | 弱相关——只有 img2threejs 算真正命中，其余偏离主题（游戏开发、深度估计） |
| 17 | recursive self improvement | 9 | **强相关**——top5 全部精确命中，与 #14 同主题的中文查询形成鲜明对比 |
| 18 | terminal AI coding tool | 27 | **强相关**——top5 全部是终端/IDE 类 AI 编程工具文章 |
| 19 | 微信机器人远程控制 Claude Code | 6 | **强相关**——top5 中 4/5 高度相关（Heinu1、kimi-bridge、Proma、LobsterAI） |
| 20 | open source video editing agent | 17 | **强相关**——top5 全部精确命中视频编辑 Agent 主题，与 #7 同主题的中文自然语言提问形成鲜明对比 |
| 21 | 菜谱 家常菜做法 | 0 | **正确的无结果**——博客确实没有美食内容 |
| 22 | 报税指南 个人所得税 | 2 | 轻微噪音——2 条弱模糊匹配的不相关结果（应为 0），但数量很少 |
| 23 | 育儿经验分享 | 0 | **正确的无结果** |
| 24 | Kubernetes 集群运维 | 2 | 轻微噪音——2 条弱相关（容器相关但非 K8s）结果 |

## 汇总指标

- **Success@5（含弱相关，20 条非负样本查询）**：16/20 = 80%
- **Success@5（仅算强相关）**：12/20 = 60%
- **无结果查询的精确率（4 条负样本）**：2/4 完全干净（0 结果），2/4 有 1-2 条弱噪音但数量很少，
  没有出现"完全跑题却排在高位"的误导性结果

## 关键发现（供 T1.2.1/T1.2.2 决策参考）

1. **中文自然语言提问明显弱于关键词/英文查询，且是同一主题下的直接对比**：
   - #7「我想本地部署一个 AI 视频编辑工具」→ 0 相关 vs #20「open source video editing agent」→ 5/5 相关
   - #14「递归自我改进 RSI」→ 1 条 vs #16「recursive self improvement」→ 9 条全相关
   - 这正是 `semantic-search/PLAN.md` 里预期向量检索能带来提升的场景，值得在 T1.2.1 重点验证。
2. **真实的措辞/同义词鸿沟（订正：不是跨语言）**：#11「脑仿真 大脑连接组」命中 0，但博客里确实
   有对应内容的文章（`brain-emulation-worm-to-human-scaling`、
   `brain-connectome-data-size-fly-human-mouse`）——两篇都同时有中文和英文标题，Pagefind 两种
   语言都索引了。真正的缺口是"脑仿真""大脑连接组"这两个具体措辞在全库任何语言版本里都不出现
   （全库检索显示"全脑模拟"1 篇、"连接组"3 篇），纯词法检索桥接不了"措辞不同但语义相同"这类
   同义词差距，这才是向量检索最该证明自己价值的地方（而不是此前误记的"跨语言桥接"）。
3. **覆盖充分的技术主题（MCP、Claude Code Skill、LoRA、Agent 记忆、MLX）关键词检索本身已经很好**，
   不需要靠向量检索才能用——语义检索的增益应该集中在自然语言/跨语言场景，而不是全面替代关键词检索。
4. **负样本表现总体健康**，没有出现"博客里没有对应内容却给出高置信度错误推荐"的情况，
   符合 Phase 0A 阶段"宁可无结果也不要乱推荐"的验收要求。
5. **单独查询"Pagefind"本身噪音很大（75 条弱匹配）**——不是 bug，只是博客里确实没有文章讨论
   这个工具，作为反面例子提醒：常见但博客未覆盖的词，词法检索容易"硬凑"出一堆弱相关结果，
   向量检索在这类场景下需要有相关性阈值/无结果判定，而不是照样返回一堆结果。

## 下一步（T1.2.1 判断门槛，摘自 PLAN.md）

只有满足以下任一条件，Phase 1（上线语义检索）才值得做：
- 跨语言查询（如本次 #11）的 Recall@5 相对本基线有明显提升
- 整体质量不低于本基线（60% 强相关 / 80% 含弱相关），且自然语言/宽泛问题的召回有可感知改善
- 精确技术名词类查询（如 #3/#5/#12/#13，本基线已经很强）没有因为引入向量检索而变差
