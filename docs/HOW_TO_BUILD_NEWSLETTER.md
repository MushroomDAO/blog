# 给你的博客搭一套邮件订阅系统——可复用集成方案

> 这不是"复制粘贴就能跑"的代码库说明书（那个是 [`NEWSLETTER_SYSTEM.md`](./NEWSLETTER_SYSTEM.md)，Mushroom Blog 专属，带真实资源 ID）。这是**方案**——技术选型的理由、每一步在解决什么问题、真实踩过的坑，让你能把同一套模式搬到自己的项目上，用不同的域名/账号重新走一遍。
>
> 背景：这套系统是 2026-07-29 到 2026-08-01 之间，在 Mushroom Research Blog（Astro 静态博客）上真实搭建、真实调试、真实发送成功的。下面每一条坑都是实际踩过的，不是"理论上可能"。

---

## 1. 你在解决什么问题

个人/小型博客想要邮件订阅，通常两条路：

- **上第三方平台**（Substack、ConvertKit、Beehiiv）：最快，但数据不在自己手里，读者名单是平台的，平台随时能抽成/限流/关停。
- **自己搭**：数据主权在自己手里，但要解决一堆容易踩坑的细节——双重确认（防止别人拿你邮箱恶意订阅）、退订令牌、防灌邮件骚扰、bounce/complaint 处理（不处理会拖累发信域名信誉，最后邮件全进垃圾箱）、邮件模板兼容各家客户端。

这套方案选的是第二条路，但**尽量不重新发明轮子**——核心思路是找一个已经把"最容易出错的部分"做完的开源工具，自己只负责拼起来和写内容。

---

## 2. 技术选型（和为什么）

| 环节 | 选了什么 | 为什么 |
|---|---|---|
| 邮件列表引擎 | **listmonk**（开源，自托管） | 双重确认、Altcha 防骚扰验证码、退订令牌、bounce 处理全部内置，自己不用再实现这些最容易出错的部分 |
| 托管 listmonk | **Fly.io** | 无状态部署，配 `auto_stop_machines`（空闲自动休眠、有请求自动唤醒）成本趋近于 0；曾经先尝试过 Cloudflare Container，跑起来发现内存档位不够便宜就放弃了——**这条路线切换本身就说明：先花小成本 spike 验证，比一开始就押注更划算** |
| 数据库 | **Neon**（外部托管 Postgres） | listmonk 本身无状态，数据全在这，不用管 Fly 卷备份这些运维细节 |
| 发信 | **AWS SES** | 按量计费，没有 Resend 免费层"每天 100 封"那种硬顶，订阅人数一多就会撞上 |
| 定时任务 | **GitHub Actions**（不是本地 crontab） | 不依赖某台机器是不是开着联网；免费额度对个人博客量级完全够用 |
| 前端集成 | **直接 `fetch()` POST**，不用 iframe，不用自建后端代理 | 见第 5 节，这是最容易想复杂的一步 |

---

## 3. 前置准备

- 一个你控制 DNS 的域名（Cloudflare、Route53 都行，示例用 Cloudflare）
- AWS 账号（开 SES）
- Fly.io 账号
- Neon（或任何托管 Postgres）账号
- 代码托管在 GitHub（用 Actions 做定时）

---

## 4. 分步搭建

### 4.1 部署 listmonk 到 Fly.io

```toml
# fly.toml
app = "your-listmonk-app"
primary_region = "sin"   # 选离你的读者近的区域

[build]
  image = "docker.io/listmonk/listmonk:v6.2.0"   # 官方镜像，不需要自己写 Dockerfile

[env]
  LISTMONK_app__address = "0.0.0.0:9000"
  LISTMONK_db__host = "your-neon-host.neon.tech"
  LISTMONK_db__port = "5432"
  LISTMONK_db__user = "neondb_owner"
  LISTMONK_db__database = "listmonk"
  LISTMONK_db__ssl_mode = "require"
  LISTMONK_db__max_open = "4"     # Neon 免费层并发连接数有限，小博客量级够用
  LISTMONK_db__max_idle = "2"
  LISTMONK_ADMIN_USER = "admin"

[http_service]
  internal_port = 9000
  force_https = true
  auto_stop_machines = "stop"    # 省钱的关键
  auto_start_machines = true
  min_machines_running = 0

[[vm]]
  size = "shared-cpu-1x"
  memory = "512mb"
```

`flyctl secrets set LISTMONK_ADMIN_PASSWORD=... LISTMONK_db__password=...`（密码类不要写进 fly.toml，走 secrets）。首次部署后访问 `/admin` 走一遍初始化。

### 4.2 配置发信域名——SES + DNS

1. AWS SES 控制台验证一个**专属发信子域名**（不要用根域名，隔离信誉——比如 `updates.yourdomain.com`，不是 `yourdomain.com`），拿到它给你的 DKIM CNAME 值（3 条）。
2. DNS 里加：
   - `TXT updates.yourdomain.com` → `v=spf1 include:amazonses.com ~all`
   - 3 条 DKIM CNAME（SES 控制台给你的原样抄）
   - `TXT _dmarc.updates.yourdomain.com` → `v=DMARC1; p=none; rua=mailto:你的邮箱`
3. **SMTP 密码不是 SES 控制台的密码，是从 Secret Access Key 用 AWS 官方算法推导出来的**：

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

4. listmonk 后台 Settings → SMTP，填 `email-smtp.<region>.amazonaws.com`，端口 587，用户名是 Access Key ID，密码是上面推导出来的值。

### 4.3 配置 bounce/complaint webhook（SNS）——不是可选项

**这是发送生产邮件前的硬性合规前置条件，不是"以后再补"**：持续往失效/投诉邮箱发信会直接拖累 SES 账号信誉，轻则限流重则封号。

listmonk 自己已经实现了处理这类通知的 webhook（`/webhooks/service/ses`），走 AWS SNS 消息签名验证，不需要额外密钥。要做的只是把 AWS 那边接上：

```bash
# 1. 建两个 SNS topic
aws sns create-topic --name your-app-ses-bounce --region us-east-1
aws sns create-topic --name your-app-ses-complaint --region us-east-1

# 2. topic policy 允许 SES 发布（替换成你自己的账号 ID / identity）
aws sns set-topic-attributes --topic-arn <topic-arn> --attribute-name Policy --attribute-value '{
  "Version": "2012-10-17",
  "Statement": [{
    "Sid": "AllowSESPublish", "Effect": "Allow",
    "Principal": {"Service": "ses.amazonaws.com"}, "Action": "SNS:Publish",
    "Resource": "<topic-arn>",
    "Condition": {
      "StringEquals": {"AWS:SourceAccount": "<你的账号ID>"},
      "StringLike": {"AWS:SourceArn": "arn:aws:ses:us-east-1:<账号ID>:identity/updates.yourdomain.com"}
    }
  }]
}'

# 3. 订阅 listmonk 的 webhook 地址
aws sns subscribe --topic-arn <bounce-topic-arn> --protocol https \
  --notification-endpoint https://your-listmonk.fly.dev/webhooks/service/ses
# listmonk 会自动确认这个订阅（收到 SNS 的 SubscriptionConfirmation 消息后自动回访确认链接）

# 4. 挂到 SES identity 上
aws ses set-identity-notification-topic --identity updates.yourdomain.com \
  --notification-type Bounce --sns-topic <bounce-topic-arn>
aws ses set-identity-notification-topic --identity updates.yourdomain.com \
  --notification-type Complaint --sns-topic <complaint-topic-arn>
```

**验证**：往 AWS 官方提供的模拟退信地址 `bounce@simulator.amazonses.com` 发一封测试邮件，走一遍真实触发流程，确认没有报错。

### 4.4 前端订阅表单——直连而不是套壳

**这是最容易一开始就想复杂的一步。** 第一反应通常是"listmonk 的确认页有 CSRF token/验证码，我没法自己模拟提交，只能 iframe 嵌进来或者自己写后端代理转发"——**先别急着下这个结论，去测一下 CORS**：

```bash
curl -s -D - "https://your-listmonk.fly.dev/subscription/form" -H "Origin: https://yourblog.com" | grep -i access-control
```

如果 listmonk 的 Settings → General 里把你的博客域名加进了允许来源，这个请求会带 `Access-Control-Allow-Origin` 头——意味着你可以**直接从浏览器 `fetch()` POST**，不需要 iframe，也不需要自建后端代理。这个方案原本以为"工程量和不确定性明显更高"，实测后发现只是一个 CORS 配置的事。

核心代码模式：

```html
<form id="subscribe-form">
  <input type="email" name="email" required />
  <input type="hidden" name="l" value="你的订阅列表UUID" />
  <input type="hidden" name="nonce" value="" />  <!-- 留空，listmonk 不校验这个值本身 -->
  <div><altcha-widget challengeurl="https://your-listmonk.fly.dev/api/public/captcha/altcha"></altcha-widget></div>
  <button type="submit">订阅</button>
</form>
<script src="https://your-listmonk.fly.dev/public/static/altcha.umd.js" async defer></script>
```

```js
form.addEventListener('submit', async (e) => {
  e.preventDefault();
  const res = await fetch('https://your-listmonk.fly.dev/subscription/form', {
    method: 'POST',
    body: new URLSearchParams(new FormData(form)),
  });
  const text = await res.text();
  // listmonk 返回的是 HTML 不是 JSON——按内容判断状态：
  if (/<h2>Error<\/h2>/.test(text)) {
    // 明确失败，提取错误信息
  } else if (res.ok && /<h2>Subscribe<\/h2>/.test(text) && !/<form/.test(text)) {
    // 明确成功
  } else {
    // 都不满足——不要瞎猜，展示"状态不确定，请稍后查收邮件"
    // 真实踩过：listmonk SMTP 密码过期时返回 500，但订阅记录其实已经建好了，
    // 如果这里简单地把"非 2xx"当失败，会给用户看一个误导性的假失败提示
  }
});
```

**另一个容易犯的错**：如果打算在网站多处放订阅入口（页头、页脚、文章页），**只在一处放真实表单**，其余地方用锚点链接 `<a href="#subscribe">` 跳过去。最早的设计是每处都嵌一份完整表单，上线后被读者吐槽"看起来像好几个订阅框，很乱"。

### 4.5 内容生成——做成可插拔的内容源

如果邮件内容只来自"新发布的博客文章"，一个脚本扫目录、拼 HTML 就够了。但如果以后想加其他内容（比如一份定期的行业趋势分析、只给订阅者看不上公开博客的笔记），从一开始就做成插件模式，后面加新内容源不用碰核心逻辑：

```python
@dataclass
class DigestItem:
    source: str              # "blog" / "trends" / "notes"...
    id: str                  # 该内容源内部唯一 id，用于去重
    title: str
    summary: str
    pub_date: datetime
    banner_url: str | None = None
    link: str | None = None       # 有公开页面就填这个
    body_html: str | None = None  # 没有公开页面（订阅者专属内容）就把正文直接塞这个字段内嵌进邮件
```

每个内容源是一个模块，实现 `collect(window_start, sent_ids) -> list[DigestItem]`，注册进一个字典，编排层依次调用、合并、按时间排序、渲染。加新内容源 = 写一个新模块 + 注册一行，其他文件都不用改。

### 4.6 幂等发送——別让"重试"变成"重复发送"

发送脚本的状态机不能只有"成功/失败"两态，还要有"**建好了 campaign、还没确认发送完成**"这个中间态：

```
1. 检查上次是否有"pending_campaign_id"没确认完 —— 有就先处理这个，不建新的
2. 没有才生成新内容、调 API 建 campaign
3. 把 campaign_id + 这次要发的条目 id 写进状态文件的 pending 字段（在真正触发发送之前）
4. 触发发送、短暂轮询确认状态
5. 确认 finished → 把 pending 转正，更新"已发送"集合
   没确认到 → 不当错误处理，直接退出，状态留着，下一次运行接着确认
```

**为什么这一步不能省**：如果超时就简单报错、不记录任何状态，下一次运行会把这批内容当成"从没发过"，重新建一个新 campaign 再发一次——真订阅者会收到重复邮件。这是三个独立 AI 审查模型（不同厂商）在 code review 里唯一一致标记为 blocking 的问题，说明这个坑足够隐蔽，容易被忽略。

配合一个进程锁（`mkdir` 做原子锁，别用 `flock`——macOS 默认不带这个命令，如果开发机是 Mac 但只测过 Linux CI，上线到本机跑定时任务会直接失效）。

### 4.7 定时任务——GitHub Actions，不是本地 crontab

```yaml
on:
  schedule:
    - cron: '0 14 */2 * *'   # 每 2 天 14:00 UTC
  workflow_dispatch:          # 支持手动触发测试
```

**两个坑**：
1. `schedule` 触发器**只认仓库默认分支**（通常是 `main`）上的 workflow 文件——如果这个 workflow 文件还在某个 feature 分支没合并，GitHub 根本不会注册这个定时任务，等到时间点也不会触发。
2. `*/2` 在 day-of-month 字段是"日历日期是不是奇数"，不是"从某个起点开始每隔 48 小时"——大部分时候等于"每 2 天"，但跨月边界如果上个月有 31 天，最后一天到下个月 1 号只隔 1 天不是 2 天。这是 cron 语法本身的特性。

状态文件（记录"发过什么"）如果不进 git（运行时状态，符合直觉），第一次在 GitHub Actions 上跑的时候会没有历史——**准备一个一次性的种子文件进版本库**，避免"本地已经手动发过的内容，Actions 第一次跑时不知道，又重新发一遍"。之后状态靠 CI 平台自己的缓存机制（比如 GitHub Actions 的 `actions/cache`）跨 run 保存，种子文件不需要持续更新。

---

## 5. 验收清单

- [ ] 真实订阅一次（自己的邮箱）→ 收到确认邮件 → logo/图片正常显示（**用 PNG，不要用 SVG**——浏览器渲染 SVG 没问题，但大多数邮件客户端不渲染内联 SVG，这条坑会导致"网页正常、邮件里空白"这种诡异的不一致表现）→ 点确认 → 状态变成 confirmed
- [ ] 往 `bounce@simulator.amazonses.com` 发测试邮件，确认 webhook 链路通
- [ ] 手动触发一次真实内容发送，检查邮件里的图片/链接是不是当前最新的（**不要复用之前生成的旧 HTML 文件做测试**——如果内容后来改过，内容生成脚本必须重新跑一遍才会抓到最新状态，复用旧文件会让你看到过时的内容却误以为是新 bug）
- [ ] 检查邮件在暗色模式 / 手机端渲染是否正常
- [ ] 确认 `List-Unsubscribe` header 存在（大多数邮件列表引擎会自动加，抓一封真实邮件的原始 header 确认一下）

---

## 6. 這次真实踩过的坑（完整清单，供参考）

- 从 GET 接口读回来的打码密钥字段（`••••`），改别的字段做 PUT 请求时如果原样传回去，会把真实密钥覆盖成打码字符串——改任何字段前，被打码的字段要么显式重新赋值真实值，要么用支持"只改一个字段"的 PATCH 接口
- 静态站点框架（Astro 等）生成的路由 slug 不一定等于源文件名——文件名里的大写字母/特殊符号可能被规范化，直接用文件名当 URL 会产生一个"看起来正常、实际指向别处"的死链接（HTTP 200 但内容是首页，不是 404，很难第一时间发现）
- Python `str.format()` 会把 `{{ }}` 当成转义后的单花括号，如果模板里需要保留给下游模板引擎（比如 Go template）的双花括号占位符，要用 `{{{{ }}}}` 四花括号
- 全局共享的密钥文件（比如一个跨项目的 `.env`）不一定是合法的 shell 语法——变量名带连字符、值里带 `$` 符号，直接 `source` 整个文件会崩，要精确解析需要的变量
- `VAR=value command | other_command` 这种写法，`VAR` 只在管道左边的 `command` 里生效，右边的 `other_command` 拿不到
