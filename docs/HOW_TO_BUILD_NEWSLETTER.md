# 给你的博客搭一套邮件订阅系统——从零开始、手把手的完整教程

> 这份文档假设你只有一样东西：**一个你能控制 DNS 的域名**。别的什么都没有——没有 Fly.io 账号，没有 AWS 账号，没有 Neon 账号。跟着下面的步骤一步步做，每一步都是"去哪个网址、点哪个按钮、跑哪条命令"，不是原理性的描述。
>
> 全程用示例域名 `yourdomain.com`，发信子域名用 `updates.yourdomain.com`，listmonk 域名用 `list.yourdomain.com`——替换成你自己的域名就行。
>
> 想看"这套系统内部是怎么设计的"（内容模块化架构、去重逻辑这些），看 [`NEWSLETTER_SYSTEM.md`](./NEWSLETTER_SYSTEM.md) 或者本文第 8 节之后的部分。这里第 1-7 节是纯粹的"从 0 部署到能收发邮件"操作步骤。
>
> 预计总耗时：2-4 小时（大部分时间花在等 DNS 生效、等 AWS SES 审核），不算写博客集成代码的时间。

---

## 0. 开始前，先申请这三个账号

现在就去注册，不用等看到对应章节再去申请，因为其中一个（AWS SES 生产权限）审核可能要等几小时到一天：

1. **Fly.io**：https://fly.io/app/sign-up ——需要绑信用卡（有免费额度，个人博客量级基本不花钱）
2. **AWS**：https://aws.amazon.com/ ——如果已经有 AWS 账号可以直接用
3. **Neon**（免费 Postgres）：https://neon.tech/ ——用 GitHub 账号登录最快

---

## 1. 建数据库（Neon）

1. 登录 https://console.neon.tech
2. 点 **Create a project**，起个名字（比如 `newsletter`），region 选离你部署 listmonk 的地方近的（比如 AWS `us-east-2`）
3. 建好之后，进项目 → **Connection Details**，拿到这几个值，先记下来：
   ```
   host:     ep-xxxxx-xxxxx.区域.aws.neon.tech
   database: neondb（默认库名，也可以自己新建一个叫 listmonk 的库）
   user:     neondb_owner（默认用户名）
   password: 点 "Show password" 才会显示
   ```
4. **在 Neon 控制台里手动新建一个名叫 `listmonk` 的数据库**（Tables 页或者 SQL Editor 里跑 `CREATE DATABASE listmonk;`）——listmonk 自己不会建库，得有一个已存在的空库给它初始化表结构。

---

## 2. 部署 listmonk 到 Fly.io

### 2.1 安装命令行工具

```bash
curl -L https://fly.io/install.sh | sh
flyctl auth login   # 会弹浏览器登录
```

### 2.2 建 fly.toml

新建一个空目录（比如 `~/listmonk-deploy/`），里面放这个文件：

```toml
# fly.toml
app = "your-listmonk-app"     # 全局唯一，起个不会撞名的
primary_region = "sin"         # 离你的读者近的区域，可选值见 flyctl platform regions

[build]
  image = "docker.io/listmonk/listmonk:v6.2.0"

[env]
  LISTMONK_app__address = "0.0.0.0:9000"
  LISTMONK_db__host = "你在第1步拿到的 Neon host"
  LISTMONK_db__port = "5432"
  LISTMONK_db__user = "neondb_owner"
  LISTMONK_db__database = "listmonk"
  LISTMONK_db__ssl_mode = "require"
  LISTMONK_db__max_open = "4"
  LISTMONK_db__max_idle = "2"
  LISTMONK_db__max_lifetime = "300s"
  LISTMONK_ADMIN_USER = "admin"

[http_service]
  internal_port = 9000
  force_https = true
  auto_stop_machines = "stop"     # 空闲自动休眠，省钱
  auto_start_machines = true
  min_machines_running = 0

[[vm]]
  size = "shared-cpu-1x"
  memory = "512mb"
```

### 2.3 建 app + 设密码 + 部署

```bash
cd ~/listmonk-deploy
flyctl apps create your-listmonk-app

# 数据库密码、管理员密码不要写进 fly.toml，走 secrets：
flyctl secrets set LISTMONK_db__password="你的Neon数据库密码" -a your-listmonk-app
flyctl secrets set LISTMONK_ADMIN_PASSWORD="给自己起一个强密码" -a your-listmonk-app

flyctl deploy -a your-listmonk-app
```

### 2.4 跑数据库初始化

listmonk 第一次部署，数据库表结构是空的，需要跑一次安装命令：

```bash
flyctl ssh console -a your-listmonk-app
# 进到容器里之后：
./listmonk --install --yes
exit
```

### 2.5 绑自定义域名

```bash
flyctl certs create list.yourdomain.com -a your-listmonk-app
flyctl certs show list.yourdomain.com -a your-listmonk-app
```

第二条命令会告诉你需要在 DNS 里加什么记录（通常是一条 `CNAME list.yourdomain.com` 指向 `your-listmonk-app.fly.dev`，或者一条 `A`/`AAAA` 记录）。去你的 DNS 服务商（Cloudflare/其他）控制台把这条记录加上，等几分钟到证书签发完成。

### 2.6 验证

浏览器打开 `https://list.yourdomain.com`，应该能看到 listmonk 的欢迎页/订阅表单相关内容。打开 `https://list.yourdomain.com/admin`，用 `admin` + 你在 2.3 步设置的密码登录，能进后台就说明部署成功了。

---

## 3. 配置发信域名（AWS SES）

### 3.1 验证发信子域名

**用一个专属子域名发信，不要用根域名**——这样万一发信信誉出问题，不会连累主站/其他邮箱。

1. 登录 AWS 控制台，搜索并进入 **SES**（Simple Email Service），右上角选一个区域（比如 `us-east-1`，后面所有配置都要在同一个区域）
2. 左侧菜单 **Verified identities** → **Create identity**
3. Identity type 选 **Domain**，输入 `updates.yourdomain.com`
4. 勾选 **Use a default DKIM signing key length** 保持默认（RSA 2048），点 **Create identity**
5. 创建后进入这个 identity 的详情页，**DKIM** 标签下会给你 **3 条 CNAME 记录**——记下来，格式类似：
   ```
   名称: xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx._domainkey.updates.yourdomain.com
   类型: CNAME
   值:   xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx.dkim.amazonses.com
   ```
   （3 条记录的 xxxx 部分各不相同，都要加）

### 3.2 把记录写进 DNS

去你的 DNS 服务商控制台，加下面这几条记录（都是加在 `updates.yourdomain.com` 这个子域名上）：

| 类型 | 名称 | 值 |
|---|---|---|
| CNAME | `token1._domainkey.updates.yourdomain.com` | AWS 给你的第 1 条 DKIM 值 |
| CNAME | `token2._domainkey.updates.yourdomain.com` | AWS 给你的第 2 条 DKIM 值 |
| CNAME | `token3._domainkey.updates.yourdomain.com` | AWS 给你的第 3 条 DKIM 值 |
| TXT | `updates.yourdomain.com` | `v=spf1 include:amazonses.com ~all` |
| TXT | `_dmarc.updates.yourdomain.com` | `v=DMARC1; p=none; rua=mailto:你的真实邮箱` |

加完等一会儿（几分钟到几小时不等），回 SES 控制台的 Verified identities 列表刷新，状态从 Pending 变成 **Verified** 就说明 DNS 生效了。

### 3.3 申请退出 Sandbox（这一步经常被漏掉，非做不可）

**新开的 SES 账号默认在 Sandbox 模式**——这个模式下你**只能给已经验证过的邮箱地址发信**，普通读者根本收不到。必须申请转正：

1. SES 控制台左侧 **Account dashboard**，能看到当前 Sending limits 显示"Sandbox"
2. 点 **Request production access**
3. 填表单：Mail type 选 Transactional 或 Marketing（订阅摘要邮件选 Marketing 更准确），Website URL 填你的博客地址，Use case description 老老实实写清楚"这是个人博客的邮件订阅系统，双重确认订阅，读者可以随时退订"，预估发送量填个保守数字（比如每天 100 封以内）
4. 提交后一般几小时到一天内会有结果邮件

**在批准之前**，第 5 节的"往自己邮箱发一封测试邮件"这一步用你自己已验证的邮箱地址是能跑通的（Sandbox 模式下，给自己发的已验证地址不受限），可以先测起来，不用干等审核结果。

### 3.4 建一个只有发信权限的 IAM 用户

不要用 root 账号的密钥发信，建一个权限最小化的专用用户：

1. AWS 控制台搜索进入 **IAM** → **Users** → **Create user**
2. 用户名起个能看出用途的，比如 `listmonk-ses`
3. **Attach policies directly**，创建一个自定义策略（Create policy → JSON），内容：
   ```json
   {
     "Version": "2012-10-17",
     "Statement": [
       {
         "Effect": "Allow",
         "Action": ["ses:SendEmail", "ses:SendRawEmail"],
         "Resource": "*"
       }
     ]
   }
   ```
4. 建好用户后，进用户详情 → **Security credentials** → **Create access key** → 用途选 "Application running outside AWS"，拿到 **Access Key ID** 和 **Secret Access Key**（这个 Secret 只显示一次，立刻复制保存好）

### 3.5 从 Secret Key 推导 SMTP 密码

AWS SES 的 SMTP 密码不是你上一步拿到的 Secret Access Key 本身，是用官方算法推导出来的：

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

print(derive_smtp_password("你的Secret Access Key", region="us-east-1"))
```

存下这个输出值，下一步要用。

### 3.6 在 listmonk 后台配置 SMTP

1. 登录 `https://list.yourdomain.com/admin`
2. **Settings → SMTP**，新建一条：
   ```
   Host:     email-smtp.us-east-1.amazonaws.com   （区域要跟 3.1 步一致）
   Port:     587
   Auth protocol: LOGIN
   Username: 你的 Access Key ID（第3.4步拿到的）
   Password: 第3.5步推导出来的 SMTP 密码
   TLS:      STARTTLS
   From address: hello@updates.yourdomain.com（随便起一个前缀）
   ```
3. Settings → General，把 **From email** 也设成同一个发信域名下的地址，比如 `Your Blog <updates@updates.yourdomain.com>`
4. 保存，点旁边的 **Send test email** 给自己已验证的邮箱发一封，收到就说明配置对了

---

## 4. 配置退信/投诉处理（AWS SNS）——不是可选项

**这是发送生产邮件前的硬性合规前置条件**：持续给失效/投诉过的邮箱发信，会拖累 SES 账号信誉，轻则限流重则封号。listmonk 自己已经实现了处理这类通知的 webhook（走 SNS 消息签名验证，不需要额外密钥），只需要把 AWS 那边接上：

先确认本地装好了 AWS CLI 并配置好了刚才那个 IAM 用户（如果 3.4 步的策略只给了发信权限，这里需要给这个用户临时加上 SNS 权限，或者用一个有更高权限的账号跑下面这几条命令）：

```bash
aws configure   # 填入 Access Key ID / Secret / region

# 1. 建两个 SNS topic
aws sns create-topic --name your-app-ses-bounce --region us-east-1
aws sns create-topic --name your-app-ses-complaint --region us-east-1
# 每条命令会返回一个 TopicArn，记下来

# 2. 允许 SES 往这两个 topic 发布消息（把下面的账号ID/ARN换成你自己的）
aws sns set-topic-attributes --topic-arn <bounce-topic-arn> --attribute-name Policy --attribute-value '{
  "Version": "2012-10-17",
  "Statement": [{
    "Sid": "AllowSESPublish", "Effect": "Allow",
    "Principal": {"Service": "ses.amazonaws.com"}, "Action": "SNS:Publish",
    "Resource": "<bounce-topic-arn>",
    "Condition": {
      "StringEquals": {"AWS:SourceAccount": "<你的AWS账号ID>"},
      "StringLike": {"AWS:SourceArn": "arn:aws:ses:us-east-1:<账号ID>:identity/updates.yourdomain.com"}
    }
  }]
}'
# complaint topic 同样操作一遍

# 3. 订阅 listmonk 的 webhook 地址
aws sns subscribe --topic-arn <bounce-topic-arn> --protocol https \
  --notification-endpoint https://list.yourdomain.com/webhooks/service/ses
aws sns subscribe --topic-arn <complaint-topic-arn> --protocol https \
  --notification-endpoint https://list.yourdomain.com/webhooks/service/ses
# listmonk 会在几秒到几十秒内自动确认这个订阅（不需要你手动点确认链接）

# 4. 挂到 SES identity 上
aws ses set-identity-notification-topic --identity updates.yourdomain.com \
  --notification-type Bounce --sns-topic <bounce-topic-arn>
aws ses set-identity-notification-topic --identity updates.yourdomain.com \
  --notification-type Complaint --sns-topic <complaint-topic-arn>
```

**验证**：

```bash
# 检查订阅是不是已经自动确认了（等 30 秒后跑，应该看到 SubscriptionsConfirmed: "1"）
aws sns get-topic-attributes --topic-arn <bounce-topic-arn> --region us-east-1

# 往 AWS 官方提供的模拟退信地址发一封测试邮件，走一遍真实触发流程（需要 SES 已经退出 sandbox，或者这个测试地址本身在 sandbox 下也能收）
aws ses send-email --region us-east-1 \
  --from "Your Blog <updates@updates.yourdomain.com>" \
  --destination "ToAddresses=bounce@simulator.amazonses.com" \
  --message "Subject={Data=test},Body={Text={Data=testing bounce webhook}}"
```

---

## 5. DNS 记录完整清单（汇总核对用）

走完第 2-4 节，你的 DNS 上应该有这些记录（域名替换成你自己的）：

| 类型 | 名称 | 值 | 用途 |
|---|---|---|---|
| CNAME 或 A/AAAA | `list.yourdomain.com` | Fly.io 给的地址 | listmonk 主域名 |
| CNAME ×3 | `token{1,2,3}._domainkey.updates.yourdomain.com` | SES 给的 DKIM 值 | 邮件签名验证 |
| TXT | `updates.yourdomain.com` | `v=spf1 include:amazonses.com ~all` | SPF |
| TXT | `_dmarc.updates.yourdomain.com` | `v=DMARC1; p=none; rua=mailto:...` | DMARC |

---

## 6. 前端订阅表单——直连，不套壳

**先测一下 listmonk 有没有把你的博客域名加进 CORS 允许来源**，再决定要不要用 iframe：

1. listmonk 后台 → Settings → General → 找 CORS/允许来源相关设置，把 `https://yourblog.com` 加进去
2. 验证：
   ```bash
   curl -s -D - "https://list.yourdomain.com/subscription/form" -H "Origin: https://yourblog.com" | grep -i access-control
   ```
   如果看到 `Access-Control-Allow-Origin: https://yourblog.com`，说明可以直接 `fetch()`，不需要 iframe、不需要自建后端代理。

3. listmonk 后台 → **Lists** → 建一个订阅列表（比如叫 "Newsletter"），Opt-in type 选 **Double**（双重确认），保存后从列表里拿到它的 UUID。

前端代码：

```html
<form id="subscribe-form">
  <input type="email" name="email" required />
  <input type="hidden" name="l" value="你的订阅列表UUID" />
  <input type="hidden" name="nonce" value="" />
  <div><altcha-widget challengeurl="https://list.yourdomain.com/api/public/captcha/altcha"></altcha-widget></div>
  <button type="submit">订阅</button>
</form>
<script src="https://list.yourdomain.com/public/static/altcha.umd.js" async defer></script>
```

```js
document.getElementById('subscribe-form').addEventListener('submit', async (e) => {
  e.preventDefault();
  const form = e.target;
  const res = await fetch('https://list.yourdomain.com/subscription/form', {
    method: 'POST',
    body: new URLSearchParams(new FormData(form)),
  });
  const text = await res.text();
  if (/<h2>Error<\/h2>/.test(text)) {
    // 明确失败：从 text 里提取错误信息展示
  } else if (res.ok && /<h2>Subscribe<\/h2>/.test(text) && !/<form/.test(text)) {
    // 明确成功：提示"请查收确认邮件"
  } else {
    // 都不满足——展示"状态不确定，请稍后查收邮件"，不要瞎猜成功或失败
  }
});
```

**Logo 用 PNG，不要用 SVG**：listmonk 后台 Settings → General 里的 Logo URL，如果填 SVG，网页显示没问题，但大多数邮件客户端不渲染内联 SVG，邮件里会是空的。

---

## 7. 内容生成 + 定时发送

### 7.1 最简单能跑起来的版本

一个 Python 脚本：扫你的文章列表 → 生成一段 HTML → 调 listmonk 的 Campaign API 创建并发送：

```bash
# 建 campaign
curl -X POST "https://list.yourdomain.com/api/campaigns" \
  -H "Authorization: token 你的用户名:你的API Token" \
  -H "Content-Type: application/json" \
  --data '{"name":"Digest 2026-08-01","subject":"本期更新","lists":[你的列表数字ID],"content_type":"html","body":"<p>...</p>","template_id":1,"type":"regular","messenger":"email"}'
# 返回里有 campaign id，记下来

# 触发发送
curl -X PUT "https://list.yourdomain.com/api/campaigns/<campaign id>/status" \
  -H "Authorization: token 你的用户名:你的API Token" \
  -H "Content-Type: application/json" \
  --data '{"status":"running"}'
```

（`API Token` 在 listmonk 后台 Settings → Users，给你的账号新建一个 API Token）

### 7.2 幂等发送——別让"重试"变成"重复发送"

发送脚本不能只有"成功/失败"两态，必须有"**建好了 campaign、还没确认发送完成**"这个中间态，否则超时重试会导致真实订阅者收到重复邮件（这个坑三个不同厂商的 AI 审查模型独立跑一遍代码 review，都标记成了 blocking 问题）：

```
1. 检查上次是否有"pending_campaign_id"没确认完 —— 有就先处理这个，不建新的
2. 没有才生成新内容、调 API 建 campaign
3. 把 campaign_id 写进本地状态文件的 pending 字段（在真正触发发送之前）
4. 触发发送、轮询确认状态
5. 确认 finished → 把 pending 转正，记录"已发送"
   没确认到 → 不当错误处理，直接退出，状态留着，下次运行接着确认
```

配合一个进程锁（用 `mkdir` 做原子锁，不要用 `flock`——macOS 默认不带这个命令，如果开发机是 Mac 但只在 Linux CI 测过，部署到本机跑定时任务会直接失效）。

### 7.3 内容源做成可插拔的（可选，但强烈建议）

如果只发博客新文章，一个脚本够了。但只要有一点点可能以后加别的内容（行业分析、订阅者专属笔记），从一开始就抽象出一个统一格式：

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
    body_html: str | None = None  # 没有公开页面（订阅者专属内容）就把正文直接塞这个字段
```

每个内容源实现 `collect(window_start, sent_ids) -> list[DigestItem]`，注册进一个字典，编排层依次调用、合并、排序、渲染。加新内容源 = 写一个新模块 + 注册一行。

### 7.4 用 GitHub Actions 定时，不用本地 crontab

```yaml
# .github/workflows/newsletter.yml
on:
  schedule:
    - cron: '0 14 */2 * *'   # 每 2 天 14:00 UTC，改成你想要的时间/频率
  workflow_dispatch:          # 支持手动触发测试

jobs:
  send:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - run: pip install -r requirements.txt
      - env:
          LISTMONK_API_URL: ${{ secrets.LISTMONK_API_URL }}
          LISTMONK_API_TOKEN: ${{ secrets.LISTMONK_API_TOKEN }}
          LISTMONK_LIST_UUID: ${{ secrets.LISTMONK_LIST_UUID }}
        run: bash send-newsletter.sh
```

在 GitHub 仓库 **Settings → Secrets and variables → Actions** 加上这 3 个 secret（值来自 listmonk 后台 Settings → Users 生成的 API Token，和第 6 节拿到的列表 UUID）。也可以用命令行：

```bash
gh secret set LISTMONK_API_URL --repo yourname/yourrepo --body "https://list.yourdomain.com"
gh secret set LISTMONK_API_TOKEN --repo yourname/yourrepo --body "你的用户名:你的Token"
gh secret set LISTMONK_LIST_UUID --repo yourname/yourrepo --body "你的列表UUID"
```

**两个容易踩的坑**：
1. `schedule` 触发器**只认仓库默认分支**（通常是 `main`）上的 workflow 文件——文件还在 feature 分支没合并的话，GitHub 根本不会注册这个定时任务。
2. `*/2` 在 day-of-month 字段是"日历日期是不是奇数"，不是"从某个起点开始每隔 48 小时"——大部分时候等于"每 2 天"，跨月边界（上个月是 31 天）会偶尔挤成隔 1 天。

**首次在 CI 上跑之前**，如果你已经手动发过一轮内容，记得把"已发送"的状态文件也提交进仓库当种子（不然 CI 第一次跑不知道这些内容已经发过，会重新发一遍）。

---

## 8. 验收清单

- [ ] 真实订阅一次（自己的邮箱）→ 收到确认邮件，logo 正常显示 → 点确认 → listmonk 后台看到状态变成 confirmed
- [ ] 往 `bounce@simulator.amazonses.com` 发测试邮件，确认 SNS webhook 链路通（listmonk 日志里没有报错）
- [ ] 手动触发一次真实内容发送，检查邮件里的图片/链接是不是当前最新（**不要复用之前生成的旧 HTML 文件做测试**，内容变过就要重新跑一遍生成脚本）
- [ ] 邮件在暗色模式 / 手机端渲染正常
- [ ] 邮件带 `List-Unsubscribe` header（抓一封真实邮件的原始 header 确认）
- [ ] SES 已经退出 Sandbox（不然只有已验证邮箱能收到）

---

## 9. 常见故障排查

| 症状 | 大概率原因 | 怎么查 |
|---|---|---|
| 订阅表单提交报 CORS 错误 | listmonk 没把博客域名加进允许来源 | listmonk 后台 Settings → General 检查 |
| 确认邮件一直收不到 | SES 还在 Sandbox，或者 SMTP 密码错 | 查 listmonk 容器日志 `flyctl logs -a your-listmonk-app`，看有没有 `535 Authentication Credentials Invalid`（密码错）或者其他 SES 拒绝的报错 |
| SMTP 密码改了但还是报错 | listmonk 只在启动时初始化 SMTP 连接，改完设置要重启 | `flyctl machine restart <machine-id> -a your-listmonk-app` |
| 邮件进了对方垃圾箱 | SPF/DKIM/DMARC 没配全，或者 bounce/complaint webhook 没接 | 用 mail-tester.com 之类的工具发一封测试邮件，看具体哪项没过 |
| 定时任务到点没跑 | workflow 文件还在非默认分支 | 确认已经合并到 `main`，`gh api repos/OWNER/REPO/actions/workflows` 能看到这个 workflow 且 `state: active` |
