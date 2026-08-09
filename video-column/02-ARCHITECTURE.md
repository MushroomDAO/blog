# 02 · 系统架构与技术选型

> 设计约束（来自现状调研，不可回避）：
> 1. 博客是**纯静态 Astro + Cloudflare Pages**，无 SSR、无后端。
> 2. Mycelium 加密基建（AirAccount / SuperPaymaster v5 / SBT / aPNTs / CometENS）**目前全在 Sepolia / OP Sepolia 测试网**，主网 GA 未落地。
> 3. **链上不支持周期性扣款**（订阅需 Permit2，未建）——`research/fangpay/LITE_SCOPE.md` 明确 "❌ 不需要订阅合约"。
> 4. **"AI 发任务→评测→自动打分"闭环在生态里不存在**，需自建编排（基建部件齐全）。

这四条直接决定了下面的选型。

---

## 1. 全景架构

```
┌─────────────────────────────────────────────────────────────┐
│  博客（保持纯静态，零改造风险）                                  │
│  Astro + CF Pages  ──构建──▶ dist/  ──▶ blog.mushroom.cv       │
│  文章 frontmatter.video.streamId  ──▶ <VideoPaywall/> 岛组件    │
└───────────────┬─────────────────────────────────────────────┘
                │ 客户端 fetch（岛在浏览器里跑）
                ▼
┌─────────────────────────────────────────────────────────────┐
│  spore-api （新增：Cloudflare Worker 后端）                    │
│  ├─ /preview   免登录，签发 60s 预览 token                     │
│  ├─ /unlock    校验"已购/会员额度/aPNTs兑换"→签发完整版 token    │
│  ├─ /pay       校验链上 USDC/x402 付款 → 记账                   │
│  ├─ /auth      AirAccount WebAuthn 登录 → session              │
│  ├─ /membership 购买/查询月度 Pass（预付制，非订阅）             │
│  ├─ /tasks     领任务 / 提交 / 查状态                          │
│  └─ /grade     调 AI 评测 → mint aPNTs                         │
├─────────────────────────────────────────────────────────────┤
│  状态层                                                        │
│  D1 (SQLite)  用户/购买/会员Pass/积分账本/任务                  │
│  KV           session、支付 nonce、Stream token 缓存           │
│  Cloudflare Stream  视频托管 + 签名播放 + 服务端切预览          │
└───────────────┬─────────────────────────────────────────────┘
                │ 按需调用（P1/P2）
                ▼
┌─────────────────────────────────────────────────────────────┐
│  Mycelium 生态基建（复用，不重造）                              │
│  AirAccount @aastar/sdk   身份/登录（WebAuthn passkey）        │
│  x402 SDK / FangPay Relay  USDC gasless 微支付                │
│  SuperPaymaster v5        aPNTs mint/burn、SBT 校验、gasless    │
│  Agent24 eval + Claude    任务 AI 评测                         │
│  CometENS (可选)          member.mushroom.cv 身份页            │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. 为什么是 Cloudflare 全栈

| 决策 | 选型 | 理由 |
|------|------|------|
| 后端 | **Cloudflare Workers**（新建 `spore-api`） | 博客已在 CF Pages + wrangler；FangPay Relay 本身就是设计成 CF Worker；一个平台、一套 `wrangler` 部署、边缘低延迟、量小近乎免费 |
| 数据库 | **Cloudflare D1**（SQLite） | 关系型账本（购买/额度/积分/任务）天然适配；与 Worker 零延迟绑定 |
| 会话/临时态 | **Cloudflare KV** | session、支付 nonce、短时 Stream token |
| 视频托管 | **Cloudflare Stream** | **本产品的关键使能器**：原生**签名 URL**（完整版永不裸露）+ **服务端切片**生成 60s 预览（完整版不下发）+ 自适应码率 + 按分钟计费 |
| 前端付费墙 | **Astro island**（Preact/vanilla） | 博客保持静态，付费墙只是挂在文章下的客户端岛，运行时调 API；无视频的文章零影响 |
| 身份 | **AirAccount `@aastar/sdk`** | 生态现成、生产可用、WebAuthn 免助记词，对齐"数字主权" |
| 支付 | **x402 SDK（已发布）→ FangPay USDC 关道** | x402 已 `v0.29.x` 可用；FangPay Path A（EIP-3009 gasless）为目标态 |
| 积分 | **aPNTs（SuperPaymaster token ops）** | `mint`/`burn`/`transferAndCall` 已在 v5 生产可用 |
| 会员门槛/成员 | **SBT（SuperPaymaster v5 子系统）** | `safeMint`/`getUserSBT`/`setReputation` 现成 |

**一句话**：除了"付费墙业务逻辑 + 任务评测编排"这两块必须自建，其余全部复用生态现成件，把自研面积压到最小。

---

## 3. 三个最关键的技术决策（含现实妥协）

### 决策 A · 会员用"预付月票"，不做链上订阅

链上周期扣款未建（需 Permit2）。**不要等它**。

> **方案**：会员 = 一次性买一张**月票（Monthly Pass）**——付 $1 USDC，D1 里给该用户写一条 `pass`（10 个 credit，`expires_at = 当月底`）。看完整版时扣 credit。下月想续 = 再买一张。

这完全绕开订阅合约，用现成的一次性支付就实现了"$1/月/10 条"的体验。人民币/自动续费留到 P3 接支付宝再说。

### 决策 B · 支付校验与身份**解耦**，MVP 可先"钱包直付"

付费墙的最小问题只是"**这个人付过钱了吗**"。所以 P0 不必先上 AirAccount：

- **P0**：用户用任意钱包付 USDC（x402），后端验链上到账 → D1 记 `purchase(wallet, videoId)` → 放行。**无需登录系统**。
- **P1**：叠加 AirAccount 登录，把 `wallet` 关联到账户，支持会员额度、跨设备。
- 这样 P0 能在**最短路径**验证核心假设（有没有人愿意为 1 元视频付费），身份/会员/积分是增量。

### 决策 C · 测试网优先，主网就绪即切

生态基建（SuperPaymaster/AirAccount/SBT/aPNTs/CometENS）**当前在 Sepolia / OP Sepolia**。策略：

- **后端把链交互抽象成 `PaymentProvider` / `PointsProvider` / `IdentityProvider` 接口**，实现分 `testnet` / `mainnet` 两套。
- **P0/P1** 可在 **OP 测试网** 跑通全链路（含真实合约调用），或用 **OP 主网 Native USDC** 做真实收款（支付与身份解耦，见决策 B，支付可先上主网、身份/积分留测试网）。
- SuperPaymaster 主网 GA 落地 → 配置切换，不改业务代码。
- **结算链推荐 Optimism**：AirAccount/CometENS 已在 OP 系；Circle Native USDC 支持 OP；与生态一致。（备选 Base，看你偏好，列入 `07-OPEN-QUESTIONS.md`。）

---

## 4. 三条核心数据流

### 流 1 · 看完整版（付费墙判定）
```
浏览器岛 ──/unlock {videoId, wallet/session}──▶ spore-api
  spore-api 按序判定：
    已购此片? ──是──▶ 签发 Stream 完整版 token
    会员且本月 credit>0? ──是──▶ 扣1 credit，签发 token
    aPNTs 已兑换此片? ──是──▶ 签发 token
    否 ──▶ 返回 402 + 三选一（单片付费/开会员/用积分）
  浏览器拿 token ──▶ Cloudflare Stream 播放完整版
```

### 流 2 · 单片付费（USDC）
```
浏览器 ──/pay/intent {videoId}──▶ 后端返回收款地址+nonce+金额
用户钱包签 EIP-3009 transferWithAuthorization（gasless）
  ──▶ FangPay/x402 Relay 代付 gas，USDC 直达收款钱包
后端监听/校验到账 ──▶ D1 写 purchase ──▶ 通知前端解锁
```

### 流 3 · 任务赚积分（需 SBT）
```
成员(持SBT) ──/tasks/claim──▶ AI 依据能力画像发任务
用户完成 ──/tasks/submit {截图/仓库/命令输出}──▶ D1 存 submission
后端 ──/grade──▶ 调 Claude/Agent24 按 rubric 评测 → 分数/通过与否
通过 ──▶ SuperPaymaster aPNTs.mint(userAddr, reward) ──▶ D1 记积分账本
用户 ──▶ 用 aPNTs 兑换视频（回到流1）
```

---

## 5. 安全要点（付费产品红线）

- **完整版 URL 绝不下发**：只发 Cloudflare Stream 短时效签名 token（分钟级过期）。预览用 Stream 服务端切片，完整版字节永不给未付费者。
- **支付防重放**：每笔 `/pay/intent` 发一次性 nonce，链上 tx 校验 `amount + recipient + nonce`，D1 唯一约束防重复入账。
- **额度扣减原子性**:会员扣 credit 用 D1 事务，防并发超扣。
- **任务防作弊**：AI 评测 rubric + 提交物需可验证（真实仓库/命令输出/带账户水印的截图）；同任务限领一次；异常提交人工复核队列。
- **积分即资产**：aPNTs 走 SuperPaymaster 合约 mint，链上可审计；后端只发起、不托管私钥。

---

## 6. 与现有发布流程的兼容

- `scripts/publish-blog.sh` **完全不动**。视频元数据只是文章 frontmatter 多了个 `video:` 块。
- 构建产物仍是纯静态 `dist/`。付费墙岛在客户端 hydrate 后才联网。
- `spore-api` Worker **独立部署**（独立 `wrangler.toml`），与博客 Pages 项目解耦，互不影响。

模块级拆分与开发顺序见 `03-MODULES.md`；表结构与接口见 `04-DATA-MODEL.md`。
