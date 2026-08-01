# Newsletter / 订阅系统 — 架构与运维手册

> 这是一份自包含的参考文档：假设读者（人类或未来某个 Claude 会话）**没有任何本项目的历史上下文**，只从这份文档出发就能理解整套系统、定位问题、做修改。
>
> 想看"为什么做这些决定、踩过什么坑"的完整故事，见 [`NEWSLETTER_SUBSCRIPTION_PROPOSAL.md`](./NEWSLETTER_SUBSCRIPTION_PROPOSAL.md)（按时间顺序的决策日志，很长，不是操作手册）。这份文档只讲"现在系统长什么样、怎么用、怎么改"。
>
> 最后核对时间：2026-08-01。核对方式：本文档里提到的每一个组件、每一条命令，当时都在真实环境里跑通过（不是照着代码推测写的）。

---

## 1. 系统概览

读者在博客底部填邮箱订阅 → 收确认邮件 → 点确认 → 每 2 天收一封"报纸风格"摘要邮件（本次发了哪些新文章/内容，banner+标题+摘要+链接）→ 随时可退订。

```
┌─────────────────┐       fetch() POST        ┌──────────────────────┐
│ blog.mushroom.cv │ ─────────────────────────>│ list.mushroom.cv     │
│ (Cloudflare      │   /subscription/form       │ (listmonk, Fly.io)   │
│  Pages, Astro)    │   直连，无 iframe/代理      │                       │
└─────────────────┘                            └──────────┬────────────┘
                                                             │
                                                    Postgres │ (Neon, 外部托管)
                                                             │
┌──────────────────────┐   GitHub Actions 每 2 天   ┌───────▼────────┐
│ pipeline/newsletter/  │ ─────────────────────────>│ listmonk 发信   │
│ build-digest.py       │  send-newsletter.sh 调用   │ (走 AWS SES)    │
│ + sources/ 内容源     │  listmonk campaign API     └────────────────┘
└──────────────────────┘
```

---

## 2. 关键资源清单（真实地址/ID，直接可用）

| 资源 | 值 | 说明 |
|---|---|---|
| 博客域名 | `blog.mushroom.cv` | Cloudflare Pages 项目名 `blog-mushroom` |
| listmonk 域名 | `list.mushroom.cv` | **不是**直接反代到 Fly.io app——中间有一层 Cloudflare Worker 路由白名单，见 2.1 节 |
| listmonk Fly app | `mushroom-listmonk`，region `sin` | `flyctl -a mushroom-listmonk` |
| listmonk 镜像 | `listmonk/listmonk:v6.2.0`（官方镜像，无自定义 Dockerfile） | 见 `pipeline/newsletter/listmonk-fly/fly.toml` |
| Postgres | Neon 项目 "blog"（`ep-wild-water-ax0wchad.c-4.us-east-2.aws.neon.tech`） | listmonk 本身无状态，数据全在这；Fly machine 可以空闲自动休眠不丢数据 |
| 发信域名 | `updates.mushroom.cv`（不是 `blog.mushroom.cv`） | listmonk 设置里 `app.from_email` 决定的，SPF/DKIM/DMARC 都配在这个子域名上 |
| SES SMTP | `email-smtp.us-east-1.amazonaws.com`，IAM 用户 `listmonk-ses` | 只有发信权限，没有 SNS/IAM 管理权限（刻意最小权限） |
| 订阅列表 | listmonk 内部 list id `2`，UUID `575531a8-2817-4787-aa78-df7338e1747d`，名字 "Opt-in list" | 双重确认（double opt-in），自带 Altcha 防灌邮件 |
| SNS bounce/complaint topic | `mushroom-ses-bounce` / `mushroom-ses-complaint`（AWS 账号 `463387446964`，us-east-1） | 已订阅到 `https://list.mushroom.cv/webhooks/service/ses`，已验证自动确认 |
| 订阅确认邮件 logo | `https://blog.mushroom.cv/logo.png` | listmonk `app.logo_url` 设置；**必须是 PNG，不能是 SVG**（大多数邮件客户端不渲染内联 SVG，但浏览器渲染没问题，这条坑踩过一次） |

### 2.1 `list.mushroom.cv` 前面有一层 Cloudflare Worker 路由白名单

`list.mushroom.cv` 这个自定义域名（Cloudflare Custom Domain for Workers）绑定的不是 listmonk 本身，而是一个 Cloudflare Worker，脚本名 **`mushroom-listmonk-proxy`**（账号里能看到，`wrangler deployments` 或 Cloudflare Dashboard → Workers）。这个 Worker 只转发一份**公开路由白名单**给真正的 Fly.io 后端（`https://mushroom-listmonk.fly.dev`），其余一律返回 404：

```
放行：/health、/robots.txt、/subscription/form（精确匹配）
      /api/public/*、/subscription/*、/link/*、/campaign/*、/public/*、/webhooks/service/*（前缀匹配）
其余：一律 404（包括 /admin、大部分管理 /api/*）
```

**这是故意的，不是 bug**——目的是把 `/admin` 后台和管理类 API 从公网自定义域名上完全隐藏掉，只留读者真正需要用到的订阅/确认/退订/追踪/webhook 这些公开端点可达。**管理员访问走 `https://mushroom-listmonk.fly.dev/admin`（Fly 原生域名），不是 `list.mushroom.cv/admin`**——第一次核对这份文档时曾经把这两个域名搞混，在错的域名上得到一个 404 还以为是系统坏了，其实是设计如此。

如果要调整白名单（比如以后要放行更多公开端点），改这个 Worker 的脚本（`ALLOWED_EXACT` / `ALLOWED_PREFIXES` 两个列表），部署方式是标准的 `wrangler deploy`（Worker 脚本本体目前没有进这个 git 仓库，只存在于 Cloudflare 账号里——如果要长期维护，值得后续把脚本拉下来存进版本库，比如 `pipeline/newsletter/listmonk-proxy-worker/`）。

---

## 3. 密钥在哪（本地开发 / 运维用）

**全局密钥文件是 `~/Dev/.env`（不是这个仓库自己的 `.env`）**——跨项目共享，里面有很多跟这个系统无关的密钥，下面只列相关的：

| 变量名 | 用途 |
|---|---|
| `LISTMONK_API_URL` | listmonk 的 admin API 地址（`https://mushroom-listmonk.fly.dev`，注意不是 `list.mushroom.cv`，是 Fly 原生域名） |
| `LISTMONK_API_TOKEN` | 格式 `username:token`，调 listmonk admin API 用 `Authorization: token <值>` |
| `LISTMONK_NEWSLETTER_LIST_UUID` | 同上面表格的订阅列表 UUID |
| `LISTMONK_ADMIN_PASSWORD` | 登录 `https://mushroom-listmonk.fly.dev/admin` 用（**不是** `list.mushroom.cv/admin`——见 2.1 节，自定义域名上 `/admin` 是故意 404 的） |
| `LISTMONK_NEON_PGPASSWORD` | Neon Postgres 密码 |
| `CLOUDFLARE_DNS_TOKEN` | 只有 DNS 编辑权限的 Cloudflare token（改 SPF/DKIM/DMARC 记录用）——注意区分：项目自己 `.env` 里的 `CLOUDFLARE_API_TOKEN` 权限范围不一样（只有 zone:read + worker），**不能**用来改 DNS |
| `AWS_SES_Access_Key_ID` / `AWS_SES_Secret_Access_Key` | IAM 用户 `listmonk-ses`，SES 发信用；如果要重新推导 SMTP 密码，用 AWS 官方 SigV4 算法（见第 8 节"常见操作"） |
| `SES_SMTP_PASSWORD` | 已经推导好的 SMTP 密码（跟上面那对 key 对应，理论上应该一致，改了 secret key 记得重新推导） |
| `FLY_IO_ORG_TOKEN` | 操作 Fly.io（重启 machine、查日志）用 |

**GitHub Actions 用的密钥**（存在仓库的 Settings → Secrets and variables → Actions，不在 `~/Dev/.env` 里）：

```
LISTMONK_API_URL
LISTMONK_API_TOKEN
LISTMONK_NEWSLETTER_LIST_UUID
```

三个都是上面表格里同名变量的值，设置方式：`gh secret set <NAME> --repo MushroomDAO/blog --body "<值>"`。

---

## 4. 前端订阅表单

### 4.1 设计原则：直连，不套壳

`src/components/subscribe/SubscribeForm.astro` 是唯一的真实表单实现——一个 `<form>`，JS 用 `fetch()` **直接** POST 到 `https://list.mushroom.cv/subscription/form`，不经过 iframe、不经过弹窗、不经过任何自建后端代理。

能这么做是因为 listmonk 已经把 `blog.mushroom.cv` 加进了它的 CORS 允许来源（这是当初实测确认的，如果哪天 listmonk 重装或 CORS 配置丢了，前端会开始报 CORS 错误，去 listmonk 的 Settings → General 里检查允许的来源）。

表单字段：
- `email`（真实输入）
- `l`（隐藏字段，值是订阅列表 UUID）
- `nonce`（隐藏字段，留空即可，listmonk 不校验这个值本身）
- `altcha`（由 `<altcha-widget>` 自动生成——listmonk 自带的无感工作量证明验证码，脚本从 `https://list.mushroom.cv/public/static/altcha.umd.js` 加载）

### 4.2 全站只有一处真表单

**教训**：最早的设计是 Header/首页横幅/首页底部/文章页各放一份完整表单，上线后被指出"看起来像好几个订阅框，很乱"。现在的正确模式：

- **`Footer.astro`**：唯一的真实表单实例，`id="subscribe"`。同时也是唯一加载 Altcha 脚本（`<script src=".../altcha.umd.js">`）的地方——因为 Footer 在每个页面都渲染一次，脚本只需要加载一次，重复加载会导致 web component 重复注册报错。
- **`Header.astro`**：一个纯锚点链接 `<a href="#subscribe">`，点击滚动到 Footer 的表单，不是自己的表单。
- **首页横幅**（`src/pages/index.astro`）：同样是锚点链接，不是表单。

如果以后想加新的订阅入口（比如某篇文章页单独强调），**不要**再嵌一份 `<SubscribeForm>`，用锚点链接指向 `#subscribe`。

### 4.3 前端如何判断提交成功/失败

listmonk 的响应是 HTML 页面，不是 JSON。判断逻辑（`SubscribeForm.astro` 里的 JS）：
- 响应里有 `<h2>Error</h2>` → 明确失败，把错误信息展示给用户
- 响应 `ok` 且有 `<h2>Subscribe</h2>` 且不含 `<form` → 明确成功
- 都不满足（比如 listmonk 后端 500 但返回体既不是标准错误页也不是确认页）→ **展示"状态不确定，请稍后查收邮件"，不瞎猜成功或失败**

这个"不确定态"不是过度设计——真实踩过坑：listmonk 的 SMTP 密码一度过期，返回 500 但订阅记录其实已经建好了，如果代码简单地把"非 2xx"当失败，会给用户看一个假的失败提示。

---

## 5. 内容生成：可插拔的内容源架构

### 5.1 目录结构

```
pipeline/newsletter/
├── sources/
│   ├── __init__.py     # 注册表：SOURCES = {"blog": blog, ...}
│   ├── base.py           # DigestItem 数据类（统一 schema）
│   └── blog.py            # 博客内容源（目前唯一实现）
├── templates.py            # HTML 渲染（卡片式 / 正文内嵌式两种）
├── notes/README.md         # "个人笔记" 内容源的约定文档（脚本还没写）
├── build-digest.py          # 编排层：调用每个已注册源，合并、排序、渲染
├── send-newsletter.sh        # 生成 + 调 listmonk campaign API 发送
├── requirements.txt           # Python 依赖：requests / python-dateutil / pyyaml
├── last-sent.json              # 运行时状态（gitignore，不进版本库）
└── last-sent.seed.json          # 状态的一次性引导种子（进版本库，见第 6.3 节）
```

### 5.2 `DigestItem`：所有内容源的统一数据格式

见 `sources/base.py`：

```python
@dataclass
class DigestItem:
    source: str              # 内容源名字，如 "blog"
    id: str                  # 该内容源内部唯一 id
    title: str
    summary: str
    pub_date: datetime
    banner_url: str | None = None   # 绝对 URL；留空则用邮件模板的兜底 banner
    link: str | None = None         # 外部链接（"阅读全文 →"）；留空则用 body_html
    body_html: str | None = None    # 已经是安全 HTML 的正文，直接内嵌进邮件（给没有外部链接的内容用）
```

**去重 key**（`dedup_key` 属性）：`source == "blog"` 时用裸 `id`（不加前缀，兼容已经写进 `last-sent.json` 的老数据）；其他内容源用 `f"{source}:{id}"`，避免和博客 slug 撞车。

### 5.3 现有内容源：`sources/blog.py`

扫 `src/content/blog/*.md`，逻辑：
1. 读文件名生成 slug，**必须**用 `slugify()` 函数处理（不能直接用文件名！Astro 生成路由 slug 的规则是"转小写 + 去掉所有非 `[a-z0-9-]` 字符"，跟文件名不一定一样——比如 `xxx-0.6b-...-dualAR.md` 的真实 URL 是 `xxx-06b-...-dualar`。这条踩过坑：一篇文章因为这个不一致，邮件里的链接和 banner 图都指向了错误地址，读者点了会跳到博客首页而不是文章）
2. 解析 frontmatter（YAML），取 `title`/`description`/`pubDate`
3. 抓文章线上页面的 `<meta property="og:image">` 作为 banner（抓不到就用兜底图 `favicon.svg`；只接受 `http(s)` 开头的 URL）
4. 按 `pubDate` 判断是否在时间窗口内、且还没发过（用 slug 去重，不是纯时间比较——博客的 `pubDate` 经常只写日期没写时间，纯时间比较会把"当天更晚发布的文章"误判成"已经发过同一天"从而永久漏发）

### 5.4 怎么加一个新内容源

以 jason 提到的两个具体场景为例：

**场景 A：Google Trends AI 研究分析**（有独立分析内容，值得配一篇专门的东西）
```python
# pipeline/newsletter/sources/trends.py
from datetime import datetime
from .base import DigestItem

def collect(window_start: datetime, sent_ids: set) -> list:
    items = []
    # 1. 调 Google Trends（官方没有正式 API，常见做法是 pytrends 库或第三方 SerpAPI）
    # 2. 生成本期的分析文字（可以是你自己写的，也可以是脚本生成后你 review 过再发）
    # 3. 每条包成一个 DigestItem：
    item_id = "2026-08-01-ai-adoption"  # 自己起一个稳定唯一的 id，比如"日期+主题"
    if f"trends:{item_id}" in sent_ids:
        return items
    items.append(DigestItem(
        source="trends",
        id=item_id,
        title="本周 AI 领域热度：...",
        summary="...",
        pub_date=datetime.now(...),
        body_html="<p>...</p>",  # 没有独立页面就用这个，直接把内容写进邮件
        # 或者 link="https://blog.mushroom.cv/trends/2026-08-01/"，如果决定单独发一篇博客
    ))
    return items
```

**场景 B：个人笔记/实验记录**（不打算上公开博客，只给订阅者看）——按 `notes/README.md` 里的约定，在 `pipeline/newsletter/notes/` 放 markdown 文件（frontmatter: `title`/`pubDate`/`summary`，正文是给订阅者看的内容），写一个 `sources/notes.py` 去扫这个目录、把 markdown 正文转成 HTML 塞进 `body_html`，`link` 留空（没有公开页面可以链接）。

**两种情况都一样的最后一步**：在 `sources/__init__.py` 里注册：
```python
from . import blog, trends  # 加上新模块
SOURCES = {
    "blog": blog,
    "trends": trends,
}
```
`build-digest.py`、`send-newsletter.sh`、`templates.py` **都不用改**。

### 5.5 渲染模板（`templates.py`）

`MAX_ITEMS = 7`——所有内容源合并后按 `pub_date` 倒序，最多放 7 条，超出的在邮件末尾提示"还有 N 条，去博客看全部"（这条提示目前假设溢出的都是博客内容，如果以后某个非博客内容源经常单独超过 7 条，这句话需要改得更通用，现在还没遇到这个情况）。

两种卡片样式：
- `CARD_TPL`：banner 图 + 标题 + 摘要 + "阅读全文 →" 链接（`item.link` 有值时用这个）
- `INLINE_TPL`：标题 + 直接内嵌的正文 HTML，没有外部链接（`item.link` 为空、`item.body_html` 有值时用这个）

---

## 6. 发送流程与幂等性

### 6.1 `send-newsletter.sh` 做了什么

```
1. mkdir 原子锁（防止并发/重叠运行）——不用 flock，因为 macOS 默认不带这个命令
2. 从 ~/Dev/.env 精确解析出需要的 3 个变量（不整个 source，因为那个文件里有些变量名
   带连字符、有些值带 $ 符号，不是合法 bash 语法，整个 source 会崩）
3. 检查 last-sent.json 里有没有"pending_campaign_id"（上一轮建好了 campaign 但还没
   确认发送完成）——有的话先处理这个，不建新 campaign
4. 没有 pending 才跑 build-digest.py 生成本期内容
5. 调 listmonk API 建 campaign、写入 pending 状态、触发发送
6. 短暂轮询（最多 30 秒）确认是否 finished
   - finished → 把 pending 转正，更新 last-sent.json 的 sent_slugs
   - 没 finished（列表大、发送慢）→ 不当错误处理，直接退出，状态留着，
     下一轮运行会接着确认，绝不会因为等太久就重复建一个新 campaign
```

### 6.2 为什么不能简单地"超时就报错重试"

这是 PR review（Codex + 两个独立模型审查）抓到的真实 blocking 问题：如果超时就报错、不记录任何状态，下一次运行会把这批文章当成"从没发过"，重新建一个新 campaign 再发一次——真订阅者会收到重复邮件。"pending campaign" 状态设计就是为了解决这个。

### 6.3 状态文件：`last-sent.json` vs `last-sent.seed.json`

- **`last-sent.json`**：真实运行时状态（`.gitignore` 排除，不进 git）。本地跑就是这个文件；GitHub Actions 里靠 `actions/cache` 跨 run 保存（cache key 前缀 `newsletter-last-sent-`）。
- **`last-sent.seed.json`**：**进版本库**的一次性引导种子。GitHub Actions 第一次跑、还没有任何 cache 的时候，会把这个文件复制成 `last-sent.json` 起步——这是为了避免"本地已经手动发过的内容，Actions 第一次跑时不知道，又重新发一遍"。**这个文件之后不会自动更新**，只在类似"本地手动发了一批、Actions 还没跑过一次"这种引导场景下手动更新一次，平时不用管它。

---

## 7. 定时任务：GitHub Actions

`.github/workflows/newsletter.yml`：

```yaml
on:
  schedule:
    - cron: '0 14 */2 * *'   # 每 2 天 14:00 UTC = 21:00 曼谷时间
  workflow_dispatch:          # 支持手动触发
    inputs:
      since_days:              # 手动触发时可以覆盖回溯窗口天数
```

**关键点**：定时触发器（`schedule`）只认仓库**默认分支**（`main`）上的 workflow 文件——如果这个文件只存在于某个 feature 分支，GitHub 根本不会注册这个定时任务，等到时间点也不会触发。之前 PR 没合并的时候就踩过这个坑。

改发送频率（比如改成每周一次）：改 `cron` 表达式那一行。改内容回溯窗口：改 `since_days` 默认值，或者 `workflow_dispatch` 手动触发时传参。

---

## 8. 常见操作

### 8.1 本地手动跑一次（不会真的发送，除非真有新内容且 API key 有效）

```bash
cd /path/to/blog
bash pipeline/newsletter/send-newsletter.sh
```

### 8.2 只生成 HTML 看看效果，不发送

```bash
python3 pipeline/newsletter/build-digest.py --since-days 3 --out /tmp/preview.html
open /tmp/preview.html
```

### 8.3 手动触发 GitHub Actions 上的定时任务

```bash
gh workflow run "Send newsletter digest" --repo MushroomDAO/blog
gh run list --repo MushroomDAO/blog --workflow="Send newsletter digest" --limit 1
```

### 8.4 查订阅者状态（listmonk API）

```bash
# 不要整个 source ~/Dev/.env——那个文件不是合法 bash 语法（见 3 节），
# 用 shlex.quote 精确解析需要的变量，跟 send-newsletter.sh 里的做法一致
eval "$(python3 <<'PYEOF'
import shlex
from pathlib import Path
keys = {"LISTMONK_API_URL", "LISTMONK_API_TOKEN"}
for line in (Path.home() / "Dev/.env").read_text().splitlines():
    line = line.strip()
    if "=" not in line or line.startswith("#"):
        continue
    k, _, v = line.partition("=")
    if k.strip() in keys:
        print(f"export {k.strip()}={shlex.quote(v.strip().strip(chr(34)).strip(chr(39)))}")
PYEOF
)"
curl -s "$LISTMONK_API_URL/api/subscribers?per_page=all" -H "Authorization: token $LISTMONK_API_TOKEN" | python3 -m json.tool
```

### 8.5 SMTP 密码过期了怎么办（症状：日志里 `535 Authentication Credentials Invalid`）

如果 `AWS_SES_Secret_Access_Key` 被轮换过，listmonk 里存的 SMTP 密码需要重新推导（AWS 官方 SigV4 算法，region 填 `us-east-1`）：

```python
import hmac, hashlib, base64

def sign(key, msg):
    return hmac.new(key, msg.encode(), hashlib.sha256).digest()

def derive_smtp_password(secret_key, region="us-east-1"):
    k = sign(("AWS4" + secret_key).encode(), "11111111")
    k = sign(k, region)
    k = sign(k, "ses")
    k = sign(k, "aws4_request")
    k = sign(k, "SendRawEmail")
    return base64.b64encode(bytes([0x04]) + k).decode()
```

推导出来后，**必须**通过 listmonk API（`GET`/`PUT /api/settings`）更新 `smtp[].password` 字段，**并重启 Fly machine**（`flyctl machine restart <id> -a mushroom-listmonk`）——listmonk 只在启动时初始化 SMTP 连接，改完设置不重启不会生效。

**⚠️ 高危坑**：`GET /api/settings` 返回的密码字段是打码的 `••••••••`。如果因为改别的字段（比如 `app.logo_url`）而做了"GET 整个对象 → 改一个字段 → PUT 整个对象"这种操作，**千万不要把打码字符串原样 PUT 回去**——会把真实密码覆盖成打码字符串，导致刚才这个问题重新出现。改任何字段之前，先把 `smtp[].password` 显式重新赋值成真实密码（用上面的算法重新推导）。

### 8.6 检查 SES bounce/complaint webhook 是否还活着

```bash
curl -s -o /dev/null -w "%{http_code}\n" -X POST https://list.mushroom.cv/webhooks/service/ses
# 应该返回 400（缺 SNS 签名），不是 404
```

---

## 9. 已知未完成事项

- **Campaign 没配 `reply_to`**：读者回复摘要邮件，会发到没人盯的 `from_email`（`updates@updates.mushroom.cv`）。改动很小：`send-newsletter.sh` 创建 campaign 那个 JSON payload 加一个 `reply_to` 字段。
- ~~`/admin` 后台没有路由级隔离~~ **已解决**（2026-08-01 核对时发现，之前的记录是错的）：`list.mushroom.cv` 前面有一层 Cloudflare Worker 路由白名单（见 2.1 节），`/admin` 在这个域名上是故意 404 的，管理员只能通过 Fly 原生域名访问。这个 Worker 脚本目前不在 git 仓库里，只存在于 Cloudflare 账号里，是唯一的风险点——建议后续把脚本拉下来存进版本库。
- **`Deploy to Cloudflare Pages` 这个（跟 newsletter 无关的）GitHub Action 一直失败**：根因是仓库 secrets 里没有 `CLOUDFLARE_API_TOKEN`。跟这份文档描述的系统无关，只是顺手发现，需要人工去 Cloudflare 控制台生成一个有 Pages 部署权限的 token 补上。
- **`notes` 内容源还没实现**：目录和约定文档（`notes/README.md`）已经在，脚本还没写，等真的有内容再补 `sources/notes.py`。
