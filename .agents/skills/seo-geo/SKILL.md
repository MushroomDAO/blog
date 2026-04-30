---
name: seo-geo
description: |
  SEO + GEO (Generative Engine Optimization) 内容优化 skill。
  
  触发词: seo优化, geo优化, 优化文章, 让AI引用我
  
  使用场景:
  - 用户想提升文章被搜索引擎收录质量
  - 用户想让文章被 AI 引擎（ChatGPT/Perplexity/Claude/Gemini/Kimi）引用
  - blog-publisher skill 调用此 skill 进行发布前内容优化
  
  完整流程:
  1. 读取文章 markdown 文件
  2. 运行 SEO 24点检查清单
  3. 运行 GEO 10点优化检查
  4. 输出优化建议 + 自动修复（可选）
  5. 返回优化报告供 blog-publisher 使用
  
  研究来源:
  - Kevin Indig: 1.2M ChatGPT 响应分析（Ski Ramp Pattern, BLUF）
  - KDD 2024: FAQ Schema +20-40% 引用率
  - Ahrefs 75K 品牌研究: 品牌提及 0.664 相关系数（最强单一因子）
  - Mike King/iPullRank: Query Fan-Out 理论
  - GA4 误归因研究: 70.6% AI 来源流量被标为"直接"
---

# SEO + GEO 内容优化 Skill

> **核心目标**：让文章既能被搜索引擎收录（SEO），又能被 AI 引擎引用（GEO）。

## 研究背景

GEO（Generative Engine Optimization）是 2024 年以来的新兴领域：
- **44.2%** 的 AI 引用来自文章前 30% 内容（Kevin Indig，1.2M ChatGPT 响应分析）
- **品牌提及**是 AI 可见度最强单一因子，相关系数 **0.664**（Ahrefs 75K 研究）
- **FAQ Schema** 可将引用率提升 **+20-40%**（KDD 2024 论文验证）
- **原创数据/统计** 提升 AI 可见度 **+41%**
- **GA4 误归因**：70.6% 的 AI 来源流量被错误分类为"直接"流量

---

## Part 1: SEO 基础检查清单（24项）

### 1.1 Frontmatter SEO 字段

```bash
# 检查文章是否有必要的 SEO 字段
grep -E "^(title|description|titleEn|descriptionEn|tags|pubDate|category):" "$FILE"
```

**必须字段**:
- [ ] `title`: 中文标题，包含核心关键词，≤60字符
- [ ] `titleEn`: 英文标题，包含核心关键词，≤60字符（Google 截断点）
- [ ] `description`: 中文描述，150-160字符，包含关键词
- [ ] `descriptionEn`: 英文描述，150-160字符
- [ ] `tags`: 至少 3 个标签，覆盖核心话题
- [ ] `pubDate`: ISO 格式日期（新鲜度信号）
- [ ] `updatedDate`: 更新时间（告知搜索引擎内容已更新）
- [ ] `category`: 准确分类

### 1.2 内容结构检查

- [ ] H1 标题唯一（Astro 自动用 `title` 字段作 H1）
- [ ] H2/H3 层次清晰，不超过 3 级
- [ ] **标题包含关键词**（尤其是 H2）
- [ ] 文章开头 100 字内包含核心关键词
- [ ] 内链：引用本站其他相关文章（PageRank 分发）
- [ ] 外链：引用权威来源（增加可信度）

### 1.3 图片 SEO

- [ ] heroImage 已设置（社交分享预览）
- [ ] 图片文件名为英文描述性名称（非 `image1.jpg`）
- [ ] 文章内图片有 alt 文本

### 1.4 URL/Slug

- [ ] slug 为英文，包含关键词
- [ ] 使用连字符分隔（非下划线）
- [ ] 不含特殊字符或中文

### 1.5 长度与可读性

- [ ] 文章总长度 ≥ 800 字（SEO 最低门槛）
- [ ] 段落长度 40-120 字（GEO 最优区间）
- [ ] 中英双语覆盖（CN + EN 双引擎覆盖）

---

## Part 2: GEO 优化检查（10项）

### GEO 核心原理

AI 引擎（ChatGPT/Perplexity/Claude/Gemini/Kimi）在回答用户问题时：
1. 将问题分解为多个子查询（Query Fan-Out，Mike King/iPullRank）
2. 检索相关内容
3. 优先引用**结构清晰、答案在前、有权威来源**的内容

### GEO-1: BLUF（Bottom Line Up Front）— 最重要

**研究依据**：44.2% 的 AI 引用来自文章前 30% 内容

**检查**：
- [ ] 文章前 60 字内给出核心答案/结论
- [ ] 不要"铺垫式"开头（先讲背景再讲观点）
- [ ] 直接回答"这篇文章告诉你什么"

**示例**:
```markdown
❌ 差: "近年来，随着AI技术的飞速发展，越来越多的组织开始关注..."
✅ 好: "AI-native 组织的核心是三层能力：Skill（AI工具）→ Agent（自主体）→ 组织重构。
       本文提供可落地的 6 步转型路线。"
```

### GEO-2: 问题式标题（Question-Formatted Headings）

**检查**：
- [ ] 至少 2 个 H2/H3 标题使用问句格式
- [ ] 问句对应用户真实搜索意图

**示例**:
```markdown
❌ 差: "## 转型步骤"
✅ 好: "## 普通组织如何从 0 到 1 完成 AI-native 转型？"
```

### GEO-3: FAQ 结构

**研究依据**：FAQ Schema 可提升引用率 +20-40%（KDD 2024）

**检查**：
- [ ] 文章包含至少 3 个 Q&A 对（即使不是显式 FAQ 格式）
- [ ] 每个答案完整独立（AI 可直接截取）
- [ ] 可选：在文章末尾加显式 FAQ section

**FAQ 模板**:
```markdown
## 常见问题 / FAQ

**Q: [问题]?**  
A: [完整、独立的答案，40-80 字]

**Q: [问题]?**  
A: [完整、独立的答案，40-80 字]
```

### GEO-4: 原创数据与统计

**研究依据**：原创数据提升 AI 可见度 +41%

**检查**：
- [ ] 文章包含具体数字/百分比（哪怕是估算）
- [ ] 有原创观察或第一手经验
- [ ] 数据有来源标注

**示例**:
```markdown
❌ 差: "大多数组织还没有做到AI-native"
✅ 好: "据我们观察，目前 90% 的组织仍停留在「AI工具使用」阶段，
       真正完成 Agent 层重构的不足 5%"
```

### GEO-5: 权威来源引用

**研究依据**：引用权威来源提升被引用概率 +30%

**检查**：
- [ ] 引用了至少 2 个外部权威来源（论文、知名博主、研究机构）
- [ ] 来源有明确的超链接
- [ ] 引用内容具体（非泛泛的"某研究表明"）

### GEO-6: 品牌一致性提及（Brand Mentions）

**研究依据**：品牌提及相关系数 0.664（最强单一 AI 可见度因子，Ahrefs）

**检查**：
- [ ] 文章中自然提及品牌/作者名（Mycelium Protocol、MushroomDAO 等）
- [ ] 在"关于作者"或文末说明作者背景
- [ ] 跨文章保持品牌名称一致

### GEO-7: 内容分块（Chunking）

**检查**：
- [ ] 段落长度 40-120 字（AI 引擎最佳引用区间）
- [ ] 大段文字（>200字）拆分为多段
- [ ] 重要列表使用 markdown 列表格式（非连续文本）
- [ ] 关键结论单独成段

### GEO-8: 结构化数据（Schema）

**针对 Astro 博客**，在 frontmatter 中确保以下字段完整（Astro 会生成对应 meta 标签）：

**文章 ID（section anchor）**：
- [ ] 关键 H2/H3 标题有 anchor ID（`{#section-id}`）方便直接引用

**可选增强**：在文章末尾添加 FAQ 结构（机器可读）

### GEO-9: Ski Ramp Pattern（Kevin Indig）

**原理**：高权威性开场 → 引用量滚雪球增长（p<0.0001 统计显著）

**检查**：
- [ ] 文章开头引用了知名人物/研究/数据（建立权威感）
- [ ] 后续内容是对开场观点的深化（不是反转）
- [ ] 结尾有明确的行动建议或结论

### GEO-10: 双语平衡

**检查**：
- [ ] 英文版包含与中文版等价的 GEO 元素（BLUF、FAQ、引用）
- [ ] 英文关键词针对英语用户优化（不是直译）
- [ ] `<!--EN-->` 分隔清晰

---

## Part 3: 执行流程

### 3.1 分析模式（只报告，不修改）

```bash
# 读取文章并生成 SEO/GEO 报告
FILE="src/content/blog/SLUG.md"
cat "$FILE" | head -100  # 检查 frontmatter 和开头
```

**输出报告格式**:
```
=== SEO/GEO 优化报告 ===
文件: SLUG.md
日期: YYYY-MM-DD

[SEO 问题] ×项通过，×项需改进
- ❌ description 缺失
- ⚠️ 标题过长（72字 > 60字上限）
- ✅ tags 完整

[GEO 问题] ×项通过，×项需改进
- ❌ 开头段未给出核心结论（BLUF 缺失）
- ⚠️ 无问句式标题
- ✅ 包含原创数据

[优先修复]
1. 补充开头 BLUF（预计 +15% AI 引用率）
2. 添加 FAQ section（预计 +20-40% 引用率）
3. 缩短 titleEn 到 60字内
```

### 3.2 优化模式（自动修复）

当 blog-publisher 调用此 skill 时，执行：

1. **检查 frontmatter**：补全缺失的 `descriptionEn`、`updatedDate`
2. **检查开头 BLUF**：如前 3 段没有核心结论，在开头添加摘要块
3. **检查 FAQ**：如文章 >1000 字且无 FAQ，在末尾（`<!--EN-->` 前）追加 FAQ section
4. **检查标题格式**：标注需要改为问句的 H2/H3
5. **检查品牌提及**：确认文章末尾有版权声明（含品牌名）

### 3.3 集成到 blog-publisher

blog-publisher SKILL.md 的 Step 2.5（创建 Markdown 后、M1 发布前）：

```
Step 2.5: SEO/GEO 优化
- 调用 .agents/skills/seo-geo/SKILL.md
- 运行分析模式，生成报告
- 自动修复高优先级问题（BLUF、FAQ、frontmatter）
- 如有改动，更新 updatedDate
```

---

## Part 4: 快速参考卡片

| 优化项 | 预期提升 | 难度 | 优先级 |
|--------|---------|------|--------|
| BLUF（前60字给结论）| +44% AI 引用率 | 低 | P0 |
| FAQ Section | +20-40% 引用率 | 低 | P0 |
| 原创数据/统计 | +41% AI 可见度 | 中 | P1 |
| 权威来源引用 | +30% 引用概率 | 低 | P1 |
| 品牌一致性提及 | 最强单一因子 0.664 | 低 | P1 |
| 问句式 H2/H3 | 提升 Query Fan-Out 命中率 | 低 | P2 |
| 段落分块 40-120字 | 提升引用可读性 | 中 | P2 |
| 双语平衡 | 中英双 AI 引擎覆盖 | 中 | P2 |
| Schema 结构化数据 | 机读信号 | 高 | P3 |

---

## Part 5: 测量与追踪

**AI 流量追踪**（解决 GA4 误归因问题）：

GA4 中 70.6% 的 AI 来源流量被错标为"直接"。改善方法：
- 在分享链接时添加 UTM 参数：`?utm_source=chatgpt&utm_medium=ai`
- 监控 Referrer 中 `perplexity.ai`、`chat.openai.com`、`gemini.google.com` 的直接来源
- Cloudflare Analytics 可看到更原始的 Referrer 数据（不受浏览器隐私模式影响）

**成效基线**（建立后 30 天测量）：
- 文章被 Perplexity 引用次数
- ChatGPT 搜索引用次数（可手动测试：问 ChatGPT 相关问题）
- Cloudflare Analytics AI referrer 流量

---

## 研究来源

- Kevin Indig: [Growth Memo](https://www.kevinindig.com/) — 1.2M ChatGPT 响应分析，Ski Ramp Pattern
- Ahrefs: 75,000 品牌研究 — 品牌提及 AI 可见度相关系数
- KDD 2024: "Generative Engine Optimization" 论文 — FAQ Schema 效果验证
- Mike King/iPullRank: Query Fan-Out 理论
- Lily Ray: [Amsive](https://www.amsive.com/) — 企业 GEO 实践
- Brian Dean/Backlinko: 权威链接建设与 GEO 结合

---

## 已知局限

1. **Astro 不原生支持 FAQPage Schema 注入**：需手动在文章末尾添加 JSON-LD，或在 `BaseHead.astro` 中按 frontmatter 条件注入
2. **GEO 效果测量滞后**：AI 引擎爬取和更新索引通常有 1-4 周延迟
3. **中文 GEO 主要针对 Kimi/DeepSeek/Gemini**：ChatGPT 对中文内容的引用权重低于英文

---

*Skill version: 1.0.0 | 研究基准: 2025-Q1 | 作者: Mycelium Protocol + Claude*
