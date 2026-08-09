# 🎬 Video Column · 博客付费视频栏目（设计文档集）

> **一句话**：博客的付费视频栏目——每天一条 **5–7 分钟**的工具落地实操，**1 元起单片付费**或 **$1/月会员**，接入 **AirAccount + SBT + aPNTs** 的"做任务赚积分换视频"闭环。跑在 Mycelium 生态基建上，对齐数字主权。
>
> 代号建议：**Spore Cast（孢子课）**（命名待定，见 `07-OPEN-QUESTIONS.md` Q8）

这是一套**可分解执行**的设计文档：产品、架构、模块、数据、内容生产、路线图、待决策。你按此拆任务，我负责设计与选型已在文档内完成。

---

## 📐 核心设计一图流

```
博客文章（免费,SEO入口）
   └─落地讲解版─▶ 5-7min 视频（付费）
        ├─ 前 60s 免费预览（挂在文章下）
        └─ 看完整版：
             ├─ 单片付费  1元起 (USDC / aPNTs)
             ├─ 会员      $1/月，免费10条（预付月票，非订阅）
             └─ 社区成员(AirAccount+SBT)：领任务→AI评测→赚aPNTs→换视频
```

技术：**博客保持纯静态 Astro**，新增 **Cloudflare Worker (`spore-api`) + D1 + Stream**；加密件全部**复用生态**（AirAccount / SuperPaymaster v5 / SBT / aPNTs / x402）。

---

## 📚 文档索引

| 文档 | 内容 | 你用它来 |
|------|------|---------|
| [`01-PRODUCT-SPEC.md`](./01-PRODUCT-SPEC.md) | 产品规格：定位、三类用户、定价、付费墙、任务积分、MVP边界 | 对齐要做什么 |
| [`02-ARCHITECTURE.md`](./02-ARCHITECTURE.md) | 系统架构、技术选型、三个关键决策、数据流、安全 | 理解怎么搭 |
| [`03-MODULES.md`](./03-MODULES.md) | **模块拆分（开发 Backlog）** + 依赖拓扑 + 起步顺序 | **拆任务、派活** |
| [`04-DATA-MODEL.md`](./04-DATA-MODEL.md) | D1 表结构、API 契约、frontmatter 约定、链上抽象接口 | 写代码 |
| [`05-CONTENT-PRODUCTION.md`](./05-CONTENT-PRODUCTION.md) | 内容生产管线 + 工具选型 + 每日90min SOP + 成本 | 做视频 |
| [`06-ROADMAP.md`](./06-ROADMAP.md) | P0→P3 分阶段，每段独立上线验证一个假设 | 排期 |
| [`07-OPEN-QUESTIONS.md`](./07-OPEN-QUESTIONS.md) | **待你拍板的 10 个决策**（含推荐） | **先读这个** |

---

## ✅ 关键现实约束（已在设计中消化）

调研 Brood 生态后确认（详见各文档）：

- ✔️ **AirAccount**（身份，WebAuthn 免助记词）、**SuperPaymaster v5**（含 SBT / aPNTs mint-burn / gasless）、**x402 SDK**、**Cloudflare Stream** —— **现成可用**。
- ⚠️ 生态基建当前多在 **Sepolia / OP 测试网**，主网 GA 未落地 → 架构用接口隔离 testnet/mainnet。
- ⚠️ **链上不支持周期订阅**（需 Permit2）→ 会员改用**预付月票**绕开。
- ⚠️ **"AI 发任务→评测→打分"闭环生态里不存在** → 部件齐全，编排需自建（P2 关键工作量）。

---

## 🚀 最快启动路径（P0）

1. 读 `07-OPEN-QUESTIONS.md`，回**最小四问**（链 / 收款地址 / aPNTs定位 / 品牌名）。
2. 用 `05-CONTENT-PRODUCTION.md` 的产线**先攒 5–10 条视频**（从存量文章回填）。
3. 按 `03-MODULES.md` 起步顺序开发 P0 七个模块：`M-OP-1 → M-BE-1/3/4 → M-BE-2 → M-FE-1/2`。
4. 上线 = **能收第一笔 USDC + 用户能看完整版**。验证"有人愿为 1 元视频付费"。

> 先做的从来不是最全的功能，而是**能验证核心假设的最小闭环**。P0 过了，飞轮（P2）才值得建。
