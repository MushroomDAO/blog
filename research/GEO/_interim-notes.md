# GEO 调研临时笔记（agents 完成前的零散发现）

## 关键发现摘要

### 中国 GEO 市场比预想成熟得多
- **36.5% 中国网民已使用生成式 AI 搜索**（2025 数据，奇赞）
- **AIDSO (爱搜)** 已是国内头部 GEO 工具：**126 元/月起**（vs SEMrush 700 元，Profound 3500 元起）
- 服务模式以「人工精修代运营」为主，SaaS 自助工具相对稀缺

### 中国 vs 美国 GEO 差异
| 维度 | 中国 | 美国 |
|------|------|------|
| 主导引擎 | 豆包、文心、通义、DeepSeek、Kimi、元宝 | ChatGPT、Perplexity、Claude、Gemini |
| 商业模型 | 直接电商导流（豆包→抖音、通义→夸克） | 品牌曝光增强 |
| 主流引用源 | 头条/抖音、CSDN、知乎、人民日报、行业论坛 | Reddit、Wikipedia、官方文档 |
| 服务模式 | 人工代运营 + 监测工具 | SaaS 自助 + 代理 |
| 价格区间 | 100-500 元/月（AIDSO） | $30-$3500/月 |

### 中国引擎的引用偏好（实测案例）
来源：navyum 博客园（2026），一周让豆包/DeepSeek/Kimi 推荐其 Chrome 插件
- **豆包优先抓取 CSDN**（占比很高），其次抖音/头条生态
- **Kimi/DeepSeek** 也大量引用 CSDN、博客园、知乎、掘金
- 战术：在 CSDN 发布标题含关键词 + 总结部分优化的测评文章
- 时间：1 周从无排名到稳定第 2 名

### 关键洞察："平台溯源" 是中国 GEO 核心方法论
不同于美国主要靠站内优化（Schema、BLUF、引用），中国 GEO 的杠杆点是：
1. 识别 "目标查询 → AI 引用源平台" 的映射
2. 在那些源平台发布优化内容
3. 站内 GEO 是辅助

这意味着产品功能要包括：**"为查询 X 推荐应该在哪些平台发布"**

---

## Cloudflare 平台能力清单（产品化基础）

### 价格友好 / 免费层充足的产品
| 产品 | 免费层 | 付费起步 | GEO 用途 |
|------|--------|---------|---------|
| **Workers** | 100k req/day | $5/月含 10M req | API 后端 |
| **Workers AI** | 10k Neurons/day | $0.011/1k Neurons | LLM 改写、Schema 生成、内容评分 |
| **Pages** | 无限静态站 | $20/月 Pro | SaaS 前端 |
| **D1** | 5GB 存储免费 | 用量计费 | 用户数据、审计历史 |
| **R2** | 10GB 免费 | $0.015/GB/月 | 截图、原始页面归档 |
| **KV** | 100k reads/day | 用量 | 缓存 AI 响应 |
| **Vectorize** | 5M 向量免费 | 用量 | 语义搜索竞品内容 |
| **Browser Rendering** | 10 min/day（免费）/ 10 hr/月（付费） | $0.09/小时 | 抓取竞品页面、AI 引擎 SERP |
| **Queues** | 1M msg/月免费 | 用量 | 异步审计任务 |
| **Cron Triggers** | 含在 Workers 内 | 免费 | 定时引用追踪 |

### 关键模型可用（Workers AI）
- Llama 3.2 1B：$0.027/M input, $0.201/M output（用于内容评分、轻改写）
- Llama 3.1 70B：$0.293/M input, $2.253/M output（用于深度重写、Schema 生成）
- Mistral 7B（性价比中文不一定好）
- FLUX.2（图像生成 — 用于 OG 图、社交分享卡片）
- bge-* 系列嵌入模型（向量化用，配合 Vectorize）

### 中文模型缺口
Workers AI 自带模型对中文表现一般。GEO 产品里的「中文内容改写」需要外接：
- DeepSeek API（最便宜：~¥1/M tokens）
- Kimi API（context 长，适合长文章重写）
- 通义千问 API（对中国 SEO 关键词理解好）

可以走"Workers 调用外部中文 LLM API"的混合架构：英文用 Workers AI，中文用 DeepSeek/Kimi。

---

## Cloudflare 已有竞品基础设施（要避开重复造轮子）
- Cloudflare Web Analytics — 流量分析（免费）
- Cloudflare Workers AI Marketplace — 集成 Replicate、Hugging Face
- Wrangler CLI — 部署工具

---

## 产品定位假设（待 agents 验证后修正）

### 一句话
**给独立内容创作者和小商家用的 GEO Copilot：覆盖中英 AI 引擎，从审计到改写到追踪一站式，价格 ¥99-299/月（$15-45）**

### 差异化
1. **覆盖中英双语 AI 引擎** — 多数美国工具不覆盖豆包/Kimi/DeepSeek，AIDSO 不覆盖海外引擎
2. **平台溯源功能** — 揭示 AI 在引用哪些来源平台（CSDN/Reddit/etc），告诉用户去哪发布
3. **自动改写 + 多平台分发** — 不只监测，还动手帮你
4. **价格在 AIDSO 和 Profound 之间** — 个人创作者付得起，又比 AIDSO 多了海外覆盖

### MVP 功能清单（候选）
- [ ] **GEO 审计**：粘 URL → 24 分评分 + 具体改进项（参考用户已有的 24 分清单）
- [ ] **引用追踪**：每天用 Workers Cron 跑 N 个查询，看品牌/网站是否被引用
- [ ] **平台溯源**：对每个查询，告诉你 AI 引用了哪些 source（CSDN/Reddit/Wikipedia 等）
- [ ] **Schema 自动生成**：粘 URL → 生成 BlogPosting/FAQ/HowTo Schema
- [ ] **AI 改写**：粘文章 → 输出 BLUF + 表格 + 数据引用版本
- [ ] **多平台一键分发**（用户已有 xiaoheishu 桌面应用基础）：发到 CSDN/知乎/Reddit/小红书

### 商业模式
- **免费层**：1 个域名监测、5 次审计/月、3 次改写/月（吸引尝鲜）
- **个人 ¥99/月**：3 个域名、50 次审计、20 次改写、每日追踪 50 条查询
- **小商家 ¥299/月**：10 个域名、200 次审计、100 次改写、每日 200 查询、API 访问
- **代理 ¥999/月**：白标、子账号、批量处理

成本估算（Workers AI Llama 3.1 70B 改写一篇 2000 词文章 ≈ $0.005，海量轻量）

---

## 待 agents 完成后补充

- [ ] YouTube top 视频清单 + 共识/分歧
- [ ] 完整工具生态图（Profound/Athena/Otterly 详细功能与定价）
- [ ] 8-12 个真实案例数据（不仅来自 KDD/Yext）
- [ ] 小商家专项痛点和需求

---

*建立时间：2026-04-26*
