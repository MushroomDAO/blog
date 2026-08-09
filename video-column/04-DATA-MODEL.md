# 04 · 数据模型与 API

> 后端 `spore-api`（Cloudflare Worker）+ D1（SQLite）+ KV。下表是 P0→P2 的完整 schema 与接口契约。P0 只需建 ★ 标记的表。

---

## 1. D1 表结构

### ★ videos —— 视频元数据（也可只存 frontmatter，此表做后端索引）
```sql
CREATE TABLE videos (
  video_id     TEXT PRIMARY KEY,        -- 与文章 slug 对应或独立 id
  slug         TEXT,                     -- 关联文章 slug
  stream_id    TEXT NOT NULL,            -- Cloudflare Stream UID
  title        TEXT,
  duration_sec INTEGER,
  preview_sec  INTEGER DEFAULT 60,
  price_usdc   REAL DEFAULT 0.15,        -- 1元起
  price_apnts  INTEGER DEFAULT 10,
  goal         TEXT,                     -- 一句话目标
  track        TEXT,                     -- efficiency | business | model-training
  created_at   INTEGER
);
```

### ★ purchases —— 单片购买（P0 无需登录即可记 wallet）
```sql
CREATE TABLE purchases (
  id         INTEGER PRIMARY KEY AUTOINCREMENT,
  wallet     TEXT NOT NULL,             -- 付款钱包地址（P1 后可关联 user_id）
  user_id    TEXT,                       -- 可空（P0 无账户）
  video_id   TEXT NOT NULL,
  method     TEXT NOT NULL,             -- usdc | apnts
  tx_hash    TEXT,                       -- 链上凭证
  nonce      TEXT,                       -- 防重放
  amount     REAL,
  created_at INTEGER,
  UNIQUE(video_id, wallet, nonce)        -- 防重复入账
);
```

### users —— 账户（P1）
```sql
CREATE TABLE users (
  user_id    TEXT PRIMARY KEY,          -- AirAccount 账户 id
  wallet     TEXT UNIQUE,               -- 智能账户地址
  passkey_id TEXT,                       -- WebAuthn 凭证 id
  has_sbt    INTEGER DEFAULT 0,         -- 缓存链上 SBT 校验结果
  created_at INTEGER
);
```

### passes —— 会员月票（P1，预付制替代订阅）
```sql
CREATE TABLE passes (
  id           INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id      TEXT NOT NULL,
  credits_total INTEGER DEFAULT 10,
  credits_used  INTEGER DEFAULT 0,
  price_usdc    REAL DEFAULT 1.0,
  tx_hash       TEXT,
  purchased_at  INTEGER,
  expires_at    INTEGER NOT NULL         -- 当月底
);
-- 有效额度 = SUM(credits_total - credits_used) WHERE expires_at > now
```

### points_ledger —— aPNTs 积分账本（P2，镜像链上）
```sql
CREATE TABLE points_ledger (
  id         INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id    TEXT NOT NULL,
  delta      INTEGER NOT NULL,          -- +赚 / -花
  reason     TEXT,                       -- task:<id> | redeem:<video_id>
  tx_hash    TEXT,                       -- 链上 mint/burn 凭证
  created_at INTEGER
);
-- 余额 = SUM(delta)（并与链上 balanceOf 对账）
```

### tasks / submissions —— 任务与提交（P2）
```sql
CREATE TABLE tasks (
  task_id     TEXT PRIMARY KEY,
  user_id     TEXT NOT NULL,
  video_id    TEXT,                      -- 配套视频
  prompt      TEXT NOT NULL,            -- AI 生成的任务描述
  rubric      TEXT NOT NULL,            -- 评测标准（JSON）
  reward_apnts INTEGER DEFAULT 20,
  state       TEXT DEFAULT 'claimed',   -- claimed|submitted|passed|failed
  claimed_at  INTEGER
);
CREATE TABLE submissions (
  id         INTEGER PRIMARY KEY AUTOINCREMENT,
  task_id    TEXT NOT NULL,
  payload    TEXT,                       -- 截图URL/仓库链接/命令输出
  score      INTEGER,
  passed     INTEGER,
  feedback   TEXT,
  graded_by  TEXT,                       -- ai | human
  created_at INTEGER
);
```

**KV**：`session:<token>`→userId；`nonce:<video>:<wallet>`→intent；`stream_token:<hash>`→短时缓存。

---

## 2. API 契约

### P0
| 方法 | 路径 | 入参 | 出参 | 说明 |
|------|------|------|------|------|
| GET | `/preview` | `videoId` | `{ previewToken }` | 免登录，60s 预览 |
| POST | `/unlock` | `{ videoId, wallet? , session? }` | `{ streamToken }` 或 `402 { options }` | **核心判定** |
| POST | `/pay/intent` | `{ videoId, wallet }` | `{ recipient, nonce, amount, chain }` | 发起单片付款 |
| POST | `/pay/confirm` | `{ videoId, wallet, txHash, nonce }` | `{ ok, purchaseId }` | 校验到账入账 |
| GET | `/stream-token` | `videoId`(+解锁态) | `{ streamToken }` | 完整版签名 token |

**`/unlock` 判定伪码：**
```
if purchased(wallet, videoId): return token
if session and passCredits(userId) > 0: consumeCredit(); return token
if session and redeemed(userId, videoId): return token
return 402 { options: [buy_single, buy_pass, redeem_apnts] }
```

### P1
| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/auth/register` · `/auth/login` | AirAccount WebAuthn |
| GET | `/me` | 额度/已购/积分概览 |
| POST | `/membership/buy` | 付 $1 → 建 pass(10 credit, 当月底过期) |

### P2
| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/tasks/claim` | 需 SBT；AI 依画像发任务 |
| POST | `/tasks/submit` | 交提交物 |
| POST | `/grade` | AI 评测 → 通过则 mint aPNTs |
| GET | `/points/balance` · POST `/points/redeem` | 查余额 / 用 aPNTs 兑换视频 |

---

## 3. 文章 frontmatter 契约（内容侧唯一约定）

```yaml
video:
  streamId: "<cloudflare-stream-uid>"   # 必填
  durationSec: 372
  previewSec: 60                         # 可选，默认 60
  priceUSDC: 0.15                        # 可选，默认 0.15
  priceAPNTs: 10
  track: "efficiency"                    # efficiency | business | model-training
  goal: "10 分钟接好 Trends MCP 并跑第一个查询"
```

Astro 构建时 `<VideoPaywall>` 岛读此块；**无此块的文章完全不受影响**。

---

## 4. 链上交互抽象（便于 testnet→mainnet 切换）

```ts
interface PaymentProvider {           // x402 / FangPay 两实现
  createIntent(videoId, wallet): Intent
  verify(txHash, nonce, amount, recipient): boolean
}
interface PointsProvider {            // SuperPaymaster aPNTs
  mint(userAddr, amount, reason): TxHash
  burn(userAddr, amount, reason): TxHash
  balanceOf(userAddr): number
}
interface IdentityProvider {          // AirAccount @aastar/sdk
  register(): Passkey
  authenticate(): Session
}
interface MembershipGate {            // SuperPaymaster SBT
  hasSBT(userAddr): boolean
}
```

配置 `env.NETWORK = testnet | mainnet` 切换实现；业务代码零改动。合约地址/ABI 从对应 GitHub 仓库获取（AAStarCommunity/SuperPaymaster、AirAccount、MushroomDAO/CometENS）。
