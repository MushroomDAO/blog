# Mycelium Blog 立项调研 — research

> 范围：本轮规划只覆盖「语义检索 / 智能推荐」这一个功能，不是整个 blog 仓库的通用规划。
> 记录日期：2026-08-20

## 五步框架

1. **要解决的问题** — 博客已积累几百篇中英双语技术文章，读者/粉丝靠分类、标签浏览难以定位内容。
   用户提出的诉求：输入一段自然语言描述，系统返回若干篇相关文章，并对每篇给出一句话说明——
   这篇文章解决诉求里的哪个环节/子问题。
2. **现有方案全景** — 见下表。
3. **差异化立足点** — 不是要做一个通用搜索引擎，而是贴合"个人技术博客、中英双语、几百篇规模"
   这个具体场景：起步零成本（静态检索），只有证明语义检索确实带来提升时才引入在线向量检索，
   避免过度工程化。
4. **可复用 vs 要自建** — Pagefind（构建时索引）、Cloudflare Vectorize（向量存储）、
   Workers AI（embedding/推理）全部复用现成托管服务；需要自建的只是检索编排逻辑（分片策略、
   文章级聚合去重、双语路由、增量索引触发）。
5. **License / 合规边界** — Pagefind：MIT，构建时依赖，不影响博客本身的授权。
   Cloudflare Vectorize / Workers AI：商业托管服务，按量计费，无 License 冲突，
   费用直接走用户已有的 Cloudflare 账号（Workers Paid $5/月套餐 + 按量超额）。

## 开源全景表

| 项目 | 能力 | 可借鉴 | License |
|:---|:---|:---|:---|
| Pagefind | 构建时静态全文索引，浏览器端检索 | 直接使用，零运维 | MIT |
| Cloudflare Vectorize | 托管向量数据库，原生 Workers 绑定 | 直接使用 | 商业托管（按量计费） |
| Cloudflare Workers AI (`bge-m3`) | 多语言 embedding 模型托管推理 | 直接使用 | 商业托管（按量计费） |
| Cloudflare Workers AI (`bge-reranker-base`) | 重排序模型 | Phase 2 可选使用 | 商业托管（按量计费） |
| D1 FTS5 | SQLite 全文检索 | 评估过，未采用（中文分词不如 Pagefind 直接） | Cloudflare 托管 SQLite |

## 结构性空白（差异化）

个人技术博客规模（几百篇文章）下，市面上的方案要么是重量级企业搜索（Algolia/Elasticsearch，
成本和运维超出需要），要么是直接上向量库不做基线对比（容易出现"跑通了但不知道好不好"）。
本方案的立足点是：**先证明价值，再加复杂度**——用 Codex 对抗评审确认这条路径后拍板（详见
`semantic-search/CODEX_REVIEW.md`）。

## 结论

做。第一个里程碑（M1）只做「语义检索/智能推荐」这一个功能，从 Phase 0A 的静态关键词检索基线切入，
Phase 0B 离线验证向量检索是否值得做，再决定要不要进入 Phase 1（在线语义检索）。
详细方案见 `semantic-search/PLAN.md`（v1.0，已经过 Codex 评审 + 裁定）。
