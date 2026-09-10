# 换机 / 24-7 自动运行

这个仓库要在 Mac mini 上 24 小时跑，同时 MacBook Pro 保留完整能力做手动介入。
这份文档说清楚：**什么跟着 git 走、什么必须手动搬、两台机器怎么不打架。**

---

## 一、在新机器上开工

```bash
git clone git@github.com:MushroomDAO/blog.git
cd blog
pnpm install
scripts/bootstrap-machine.sh
```

`bootstrap-machine.sh` 做六件事，每件都幂等，随时可以重跑：

| 步骤 | 干什么 |
|---|---|
| 1 | `.agents/skills/*` → `.claude/skills/`（**Claude Code 实际加载的是后者**，前者才是真相源） |
| 2 | `banner-creator` + 3 个插图 skill 装到 `~/.claude/skills/` 和 `~/.codex/skills/` |
| 3 | clone 私有记忆库 `MushroomDAO/blog-memory` 到 `.agents/memory/`，再补到 `~/.claude/projects/<repo>/memory/`（只补缺失，不覆盖本机已有） |
| 4 | 仓库账本 → 本机 MemPalace（`sync-ledger.cjs import`），并启用 git hooks |
| 5 | 依赖体检，缺什么直接报，附修复命令 |
| 6 | 24/7 运行权归属检查 |

其他用法：

```bash
scripts/bootstrap-machine.sh --check-only    # 只体检，不改任何东西
scripts/bootstrap-machine.sh --claim-owner   # 认领 24/7 运行权
scripts/bootstrap-machine.sh --install-cron  # 装定时任务（需先是 owner）
```

---

## 二、bootstrap 装不了的四样东西

这四样**不可能**跟 git 走，必须手动处理。体检会明确报出来，不会假装成功。

### 1. `.env` —— 凭据

微信 AppID/Secret、Cloudflare token 都在里面。**这个文件永远不进 git。**

```bash
scp 旧机器:/path/to/blog/.env .
scp 旧机器:~/Dev/.env ~/Dev/.env     # 云基础设施凭据（listmonk / AWS SES / DNS）
```

注意 `~/Dev/.env` 是**全局**的那份，不是项目里的 —— 两份都要。

### 2. FLUX 模型 + mflux venv —— banner 生成

模型 4.3GB、venv 1.6GB，只能在新机器上装：

```bash
python3 -m venv ~/venvs/ml && source ~/venvs/ml/bin/activate
pip install mflux
mdt download Runpod/FLUX.2-klein-4B-mflux-4bit
```

装不上就没有 banner。仅 Apple Silicon 可用（走 MLX）。

### 3. 小红书登录态 —— forage 的小红书源

`scripts/refresh-xhs-cookie.sh` 从 **Chrome Profile 15** 提取登录态（账号 Mushroom.cv）。
新机器上没有那个 profile，编号也不会一样。要么用同一个 Chrome 账号登录后确认新的
profile 编号并改脚本，要么接受小红书源为 0（其余源不受影响）。

### 4. 8042 评审台 LaunchAgent

```bash
scp 旧机器:~/Library/LaunchAgents/cv.mushroom.forage.plist ~/Library/LaunchAgents/
# plist 里的路径要改成新机器上的仓库路径
launchctl load ~/Library/LaunchAgents/cv.mushroom.forage.plist
```

---

## 三、两台机器怎么不打架

### 归属锁

`config/runner.json` 的 `owner` 字段记着谁有 24/7 运行权，比对本机 `LocalHostName`。

有副作用的定时任务在入口 `source scripts/require-owner.sh`：

- `.agents/skills/forage/run-daily.sh` —— 防止同一批线索被采两遍
- `pipeline/newsletter/local-fallback.sh` —— **防止订阅者收到两封一样的邮件**

非 owner 机器上这两个脚本会打印一行「跳过，不执行」然后正常退出（退出码 0，
cron 不会报错刷屏）。手动要跑就 `FORCE_RUN=1`。

### 交接步骤（顺序不能反）

```bash
# 1. 新机器：认领
scripts/bootstrap-machine.sh --claim-owner
git add config/runner.json && git commit -m "chore: Mac mini 接管 24/7 运行" && git push

# 2. 旧机器：拉到新配置 + 删掉 cron
git pull
crontab -e            # 删掉所有 cd /path/to/blog 的行

# 3. 新机器：装 cron
scripts/bootstrap-machine.sh --install-cron
```

> ⚠️ **第 2 步不能省。** cron 不会自己 `git pull`，归属锁只挡住了有守卫的那两个脚本；
> `update-analytics.sh` 和 `refresh-xhs-cookie.sh` 没有守卫，旧机器上不删 cron 就会双跑。

### 「24/7 运行」到底是什么

**不是一个常驻守护进程。** 是两样东西：

**一、5 条 cron —— 被定时唤醒的一次性脚本，跑完就退出**

| 时间 | 脚本 | 装在哪台 | 有归属锁吗 |
|---|---|---|---|
| 21:00 | `scripts/update-analytics.sh` | 仅 owner | 否（幂等，双跑只是浪费） |
| 21:10 | `.agents/skills/forage/run-daily.sh` | 仅 owner | ✅ 有 |
| 21:15 | `scripts/refresh-xhs-cookie.sh` | 仅 owner | 否（只写本机 cookie 文件） |
| 21:30 | `pipeline/newsletter/local-fallback.sh` | 仅 owner | ✅ 有 |
| 21:45 | `scripts/sync-memory.sh` | **两台都装** | 否（双向合并，两边都跑才同步） |

**二、1 个 LaunchAgent —— 唯一真正常驻的进程**

`cv.mushroom.forage.plist` 跑 `python3 .agents/skills/forage/server.py`，
就是 8042 端口那个评审台的 web 服务。`RunAtLoad`（开机自启）+ `KeepAlive`（挂了自动重拉）。

```bash
scp 旧机器:~/Library/LaunchAgents/cv.mushroom.forage.plist ~/Library/LaunchAgents/
# 把 plist 里的 /Users/jason/Dev/mycelium/blog 改成本机路径
launchctl load ~/Library/LaunchAgents/cv.mushroom.forage.plist
```

### ⚠️ 它**不会**自动写文章

这一点必须说清楚，免得期望错位。`run-daily.sh` 的注释里自己写了：

> 这个脚本只做**机械部分**：采集 → 三层去重 → 拉协议和 README → 装库。
> 它做不了的：写「核心增量」和「延展角度」——那是判断，需要 Claude 在会话里做。

所以早上打开 8042 看到的条目会标着「待判断」。**24 小时跑的是采集和待命，
不是 24 小时自动产出文章** —— 写稿、配图、发布仍然要你开一个会话。

---

## 四、记忆怎么跨机器

两套记忆，机制不同：

### Claude Code 项目记忆（34 条）—— 在**私有**仓库里

Claude Code 真正读写的位置是 `~/.claude/projects/<repo-path>/memory/`。
跟着 git 走的那一份在 **`MushroomDAO/blog-memory`（private）**，
被 clone 到本仓库的 `.agents/memory/`（该路径在本仓库 `.gitignore` 里）。

**为什么不放在本仓库**：`MushroomDAO/blog` 是公开的。记忆文件里没有任何密钥值，
但含 AWS 账号 ID、IAM 用户名、私人邮箱、主密钥文件路径与完整变量名索引 ——
单条都不是凭据，打包公开就是一份现成的踩点材料。

```bash
scripts/sync-memory.sh          # 拉取 → 双向对齐 → 自动提交并推回私有库
scripts/sync-memory.sh --dry    # 只看会动什么
```

提交和推送是脚本自动做的 —— 靠人记得提交迟早会漏，另一台机器就读不到。
`--install-cron` 会把它装成**每天 21:45 跑一次**，而且**两台机器都装** ——
它是双向的，只有两边都跑记忆才真正同步。

**`MEMORY.md` 是特殊处理的**：它是两边都会追加的索引，按「新的赢」整文件覆盖
会静默抹掉另一台新加的行（Mac mini 上实测有 4 条会丢）。所以先用
`scripts/merge-memory-index.py` 取并集，去重键是链接目标而不是整行文本。
其余每个 `.md` 各是一条记忆、通常只有一台在改，「新的赢」是对的。

**cron 环境的坑**：非交互 shell 里 push 到私有仓库，SSH key 必须无 passphrase
或已加进钥匙串，否则会静默失败。看 `/tmp/blog-memory-sync.log`。

**新机器需要 SSH key**：私有仓库走 `git@github.com:`，clone 不下来的话先
`ssh -T git@github.com` 自测。bootstrap 会明确报这一条，不会静默跳过。

不用软链接是因为 Claude Code 会在那个目录里增删文件，软链接一旦失效是**静默**的 ——
记忆会安静地写到别处，等你发现已经丢了一批。

### MemPalace（发布查重）

`~/.mempalace/palace/chroma.sqlite3` 是 7MB 二进制，不进 git（每次全量重写，
一年膨胀几百 MB 且没法 review）。跟着 git 走的是文本账本
`.agents/skills/blog-publisher/published-ledger.jsonl`。

```bash
node .agents/skills/blog-publisher/sync-ledger.cjs status   # 看两边差多少
node .agents/skills/blog-publisher/sync-ledger.cjs export   # 本机 → 账本（pre-commit 自动跑）
node .agents/skills/blog-publisher/sync-ledger.cjs import   # 账本 → 本机（bootstrap 自动跑）
```

**查重本身不依赖 import** —— `check-duplicate.cjs` 同时读 chroma 和这份 JSONL，
所以另一台机器写的条目在这台机器上照样查得到。`import` 是为了让本机 palace 补全，
这样 `mempalace search` 和 MCP 的语义搜索也能命中，而不只是精确文本查重能命中。

---

## 五、不跟 git 走的东西（一览）

| 东西 | 为什么 | 怎么办 |
|---|---|---|
| `.env` / `~/Dev/.env` | 凭据 | 手动 scp |
| FLUX 模型 + venv | 5.9GB | 新机器上装 |
| `radar/forage.db` | 二进制、每晚全量重写、两边写会冲突 | 丢了不致命：`store.py sync` 每晚从 `src/content/blog/` 重新播种 seen 表，对已发文章的查重照常；丢的只是评审台的 write/skip 历史 |
| `.claude/skills/` | 生成物 | bootstrap 重新生成 |
| `.agents/memory/` | 它是私有仓库 `MushroomDAO/blog-memory` 的 clone，本仓库公开 | bootstrap 自动 clone（需 SSH key） |
| 插图 skill 的 `assets/examples/` | 39MB，且 SKILL.md 自己说「只作低频视觉校准，不进入默认生成路径」 | 不需要 |
| `.agents/skills/lieflat-charts/` | 第三方 20MB，自带 LICENSE | 要用单独装 |
| Chrome Profile 15 登录态 | 绑定本机浏览器 | 见上文第二节 |
