# mushroom-listmonk — 方案 C 可行性验证

把 [listmonk](https://github.com/knadh/listmonk) 跑在 Cloudflare Container 上（无状态），数据库放外部免费 Postgres（Neon）。见 `../../../docs/NEWSLETTER_SUBSCRIPTION_PROPOSAL.md` 第 3.5 节的背景。

**这是一次可行性验证（spike），不是正式生产部署**——目的是回答一个问题：listmonk 能不能塞进 Cloudflare Container 最便宜的 `lite` 档位（256MiB）。

## 前置条件（需要 jason 完成）

1. **Neon 免费 Postgres 项目**：去 [neon.com](https://neon.com) 建一个免费项目，拿到连接信息（host / user / password / database）。
2. **listmonk 管理员密码**：自己定一个，待会儿设成 secret。

## 部署步骤

```bash
cd pipeline/newsletter/listmonk-container
npm install

# 改 wrangler.jsonc 里的 vars.PGHOST 为你的 Neon host
# （PGUSER/PGDATABASE 如果 Neon 给的不是 "listmonk"，也要改）

# 设置 secrets（不要写进 wrangler.jsonc）
npx wrangler secret put PGPASSWORD
npx wrangler secret put LISTMONK_ADMIN_PASSWORD

# 先跑一次数据库迁移（本地临时跑一次 listmonk --install，指向 Neon）
# 或者直接用 psql 连 Neon 跑 listmonk 仓库里的 schema.sql：
#   psql "$NEON_CONNECTION_STRING" -f ~/Dev/tools/listmonk/schema.sql

npm run dev     # 本地验证 wrangler.jsonc/Container 配置能跑起来
npm run deploy  # 部署到 Cloudflare
```

## 验证清单（对应 docs/NEWSLETTER_SUBSCRIPTION_PROPOSAL.md 任务 #7/#8）

- [ ] 打开部署后的 URL，能看到 listmonk 登录页
- [ ] 用 admin 账号登录，创建一个测试 list
- [ ] 通过公开订阅 API 订阅一个自己的邮箱，收到确认邮件
- [ ] 点确认链接，订阅状态变成 confirmed
- [ ] 发一次测试 campaign（先随便配一个 SMTP，比如临时用 Mailtrap 沙箱测，不需要等 SES 配好）
- [ ] 点退订链接，确认状态变成 unsubscribed
- [ ] 等 10 分钟以上（`sleepAfter`）让容器休眠，再点一次此前邮件里的链接，确认冷启动后依然正常（预期 1-3 秒延迟，不应该报错）
- [ ] 观察 Cloudflare 后台的容器资源使用，判断 `lite`（256MiB）是否够用，还是需要升到 `basic`

## 已知要留意的点

- Cloudflare Containers **只支持 amd64**，listmonk 的 Docker Hub 镜像两种架构都发布，`wrangler.jsonc` 里已指定拉 amd64（Cloudflare 默认按此架构拉取）。
- 数据库连接池已经从 listmonk 默认的 25/25 调小到 4/2（`LISTMONK_db__max_open` / `max_idle`），因为 Neon 免费层并发连接数有限，而且我们这个流量根本用不到 25 个连接。
- listmonk 的媒体上传功能（Settings → Media）默认写本地磁盘——**容器磁盘是临时的，重启会清空**。我们不打算用这个功能（邮件里的 banner 图直接引用博客自己的绝对 URL），如果以后要用，需要另外配 S3/R2 存储后端。
