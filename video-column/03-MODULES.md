# 03 · 模块拆分（开发 Backlog）

> 用法：这是你"分解执行"的施工图。每个模块含**边界、依赖、验收标准、可用的生态件**。按 `06-ROADMAP.md` 的阶段（P0→P3）取用。
> 图例：🟢 自建纯逻辑 · 🔵 复用生态件 · 🟡 自建+生态编排 · ⬜ 前端

---

## 模块地图

```
前端         ⬜ M-FE-1 付费墙岛   ⬜ M-FE-2 播放器   ⬜ M-FE-3 会员/任务面板
             ────────────────────────────────────────────────────
后端 spore-api 🟢 M-BE-1 视频与token   🟢 M-BE-2 付费墙判定   🟢 M-BE-3 记账/账本
             🔵 M-BE-4 支付(USDC/x402) 🔵 M-BE-5 身份(AirAccount) 🟢 M-BE-6 会员Pass
             🟡 M-BE-7 任务   🟡 M-BE-8 AI评测   🔵 M-BE-9 aPNTs积分   🔵 M-BE-10 SBT门槛
             ────────────────────────────────────────────────────
内容/运营     🟢 M-OP-1 视频上架工具   🟢 M-OP-2 选题看板   🟢 M-OP-3 数据看板
```

---

## P0 · MVP（能收第一笔钱、能看完整版）

### ⬜ M-FE-1 付费墙岛组件 `<VideoPaywall>`
- **做什么**：Astro island，读文章 frontmatter `video`，渲染预览播放器 + "看完整版"按钮；点按调 `/unlock`，402 时弹三选一浮层。
- **依赖**：M-BE-2、Cloudflare Stream 播放 SDK。
- **验收**：无视频的文章零渲染；有视频的文章显示预览 + 付费引导；付款后无刷新解锁。

### ⬜ M-FE-2 播放器
- **做什么**：封装 Stream `<stream>` 播放器，接收后端签名 token 播完整版 / 预览。
- **验收**：完整版 URL 不出现在 DOM/network 明文；token 过期后自动降级回预览。

### 🟢 M-BE-1 视频与 token 服务
- **做什么**：`GET /preview` 签发 60s 预览 token；`GET /stream-token` 校验解锁态后签完整版 token。管理 videoId ↔ streamId 映射。
- **依赖**：Cloudflare Stream 签名密钥。
- **验收**：预览 token 只能播前 60s；完整版 token 分钟级过期。

### 🟢 M-BE-2 付费墙判定引擎
- **做什么**：`/unlock` 按序判定 已购→会员额度→积分兑换→拒绝（返回 402 + 可选项）。**产品核心逻辑**。
- **依赖**：M-BE-3、M-BE-6、M-BE-9。
- **验收**：四条判定路径全覆盖单测；并发解锁不超扣。

### 🟢 M-BE-3 记账与账本
- **做什么**：D1 读写 `purchases`（单片购买）；防重放唯一约束；查询"某 wallet 是否已购某片"。
- **验收**：同一 tx 不能重复入账；查询 O(1)。

### 🔵 M-BE-4 支付模块（USDC / x402）
- **做什么**：`/pay/intent` 发收款地址+nonce+金额；校验链上 EIP-3009 到账；抽象成 `PaymentProvider` 接口（testnet/mainnet 两实现）。
- **复用**：**x402 SDK `@aastar/sdk`（已发布 v0.29.x）**；目标态接 **FangPay Path A**（USDC + `transferWithAuthorization` + CF Worker Relay，gasless）。
- **验收**：一笔真实 OP USDC 付款能被校验并触发解锁；nonce 防重放。
- ⚠️ FangPay 目前是设计稿——MVP 可先用 x402 SDK 或"直转 USDC + 后端轮询校验"，Relay gasless 作为增强。

### 🟢 M-OP-1 视频上架工具
- **做什么**：CLI/脚本：上传 `full.mp4` 到 Stream → 拿 streamId → 写回文章 frontmatter `video` 块。
- **验收**：一条命令完成"上传+挂载"，接上 `05-CONTENT-PRODUCTION.md` 的产线。

---

## P1 · 身份与会员

### 🔵 M-BE-5 身份模块（AirAccount）
- **做什么**：`/auth` WebAuthn 注册/登录 → 签发 session（KV）；把 `wallet ↔ userId` 绑定。抽象 `IdentityProvider`。
- **复用**：**`@aastar/sdk` `AirAccount.create({provider:'webauthn'})`**；KMS API `POST /webauthn/register|authenticate`。
- **验收**：邮箱/passkey 登录成功，跨设备可续；无助记词。

### 🟢 M-BE-6 会员 Pass 模块（预付月票，非订阅）
- **做什么**：`/membership/buy` 一次性付 $1 → D1 写 `passes(userId, credits=10, expires_at=当月底)`；`/unlock` 扣 credit。
- **依赖**：M-BE-4、M-BE-3。
- **验收**：买票得 10 credit；看片扣 1；月底失效；并发扣减原子。
- 💡 绕开链上订阅缺口的关键设计（见架构决策 A）。

### ⬜ M-FE-3 会员/任务面板
- **做什么**：登录后展示 会员额度、已购列表、aPNTs 余额、可领任务。
- **验收**：数据实时；未登录引导注册。

---

## P2 · 积分飞轮（SBT + 任务 + AI 评测 + aPNTs）

### 🔵 M-BE-10 SBT 门槛
- **做什么**：`requireSBT` 中间件——校验用户地址持有社区 SBT 才放行任务系统。
- **复用**：**SuperPaymaster v5 `getUserSBT`**；成员发放用 `safeMint`。
- **验收**：无 SBT 领任务返回 403；持 SBT 放行。

### 🟡 M-BE-7 任务模块
- **做什么**：`/tasks/claim`（AI 依用户能力画像/已看视频发任务）、`/tasks/submit`（存提交物）、`/tasks/status`。任务与视频配套（例："用今天视频的工具跑出 X 并截图"）。
- **依赖**：M-BE-10、M-BE-8。
- **验收**：领取限一次；提交物落库；状态机 claimed→submitted→graded。

### 🟡 M-BE-8 AI 评测模块 ⭐ **最大自研点**
- **做什么**：`/grade` 按每任务的 **rubric** 调 Claude/Agent 评测提交物（截图/仓库/命令输出），产出 通过/分数/理由；不通过给反馈可重交。
- **复用**：Agent24 eval 能力 + Claude API；提交物可验证性设计（真实仓库链接、命令输出、带账户水印截图）。
- **验收**：同一达标提交稳定判过；明显不达标判否；有防作弊与人工复核队列。
- ⚠️ 生态里**无现成"AI 发+评任务"闭环**，此模块是 greenfield 编排，是 P2 的核心工作量。

### 🔵 M-BE-9 aPNTs 积分模块
- **做什么**：评测通过 → 给 AirAccount `mint` aPNTs；`/points/balance`、`/points/redeem`（用 aPNTs 兑换视频→写解锁态）。D1 记积分账本镜像链上。
- **复用**：**SuperPaymaster v5 token ops `mint`/`burn`/`transferAndCall`**（aPNTs，ERC-20 兼容）。
- **验收**：通过任务后链上到账且 D1 对账一致；兑换后可看完整版；余额不为负。

---

## P3 · 规模化

### 🟢 M-OP-3 数据看板
- 付费解锁数（北极星）、单片转化率、会员数、任务完成率、aPNTs 流通、日更达成。

### 🟢 法币支付接入
- 微信/支付宝 → 映射到 credit/aPNTs（off-chain 记账 + 后台对账）。

### 🔵 CometENS 身份页（可选）
- 每个成员发 `member.mushroom.cv` 身份页（`registerSubdomain`）。

---

## 依赖拓扑（先做谁）

```
M-BE-1 ─┬─▶ M-BE-2 ─┬─▶ M-FE-1 ─▶ M-FE-2      ← P0 闭环
M-BE-3 ─┘           │
M-BE-4 ─────────────┘
M-OP-1（并行，随时可做）

M-BE-5 ─▶ M-BE-6 ─▶ M-FE-3                     ← P1
M-BE-10 ─▶ M-BE-7 ─▶ M-BE-8 ─▶ M-BE-9          ← P2（M-BE-8 是关键路径）
```

**建议起步顺序**：`M-OP-1`（先能上架）→ `M-BE-1/3/4`（能收钱能发 token）→ `M-BE-2`（判定）→ `M-FE-1/2`（用户能看）。P0 五个后端 + 两个前端模块即可上线收第一笔钱。
