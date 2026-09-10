#!/usr/bin/env bash
# ============================================================================
# bootstrap-machine.sh — 在一台新机器上把这个仓库装成「能真正干活」的状态
# ----------------------------------------------------------------------------
# 背景：git clone 下来只有代码。Claude Code 实际加载的 skill 在 .claude/skills/
# （被 .gitignore 忽略），出图能力在 ~/.claude/skills/ 和 ~/.codex/skills/
# （全局路径，不跟仓库走），项目记忆在 ~/.claude/projects/.../memory/。
# 这些不装，clone 下来的仓库是「代码有、跑不动」。
#
# 这个脚本负责把仓库里带着的那部分装好，并且**如实报告装不了的那部分**
# （凭据、几个 GB 的模型权重、绑定本机浏览器的登录态）—— 不假装成功。
#
# 用法：
#   scripts/bootstrap-machine.sh                # 安装 + 体检
#   scripts/bootstrap-machine.sh --claim-owner  # 顺便认领 24/7 运行权
#   scripts/bootstrap-machine.sh --install-cron # 顺便装定时任务（需先是 owner）
#   scripts/bootstrap-machine.sh --check-only   # 只体检，不改动任何东西
# ============================================================================
set -uo pipefail
cd "$(dirname "$0")/.."
REPO="$(pwd)"

CLAIM=false; INSTALL_CRON=false; CHECK_ONLY=false
for a in "$@"; do
  case "$a" in
    --claim-owner) CLAIM=true ;;
    --install-cron) INSTALL_CRON=true ;;
    --check-only) CHECK_ONLY=true ;;
    -h|--help) sed -n '2,22p' "$0"; exit 0 ;;
    *) echo "unknown arg: $a" >&2; exit 2 ;;
  esac
done

HOST=$(scutil --get LocalHostName 2>/dev/null || hostname -s 2>/dev/null || hostname)
echo "🍄 bootstrap-machine | host=$HOST repo=$REPO"
echo

BLOCKERS=0
warn() { echo "  ⚠️  $*"; }
fail() { echo "  ❌ $*"; BLOCKERS=$((BLOCKERS+1)); }
ok()   { echo "  ✓  $*"; }

# ---------------------------------------------------------------------------
# 1. .agents/skills/ → .claude/skills/（Claude Code 真正加载的路径）
# ---------------------------------------------------------------------------
echo "[1/6] 镜像 skill 到 .claude/skills/ …"
if $CHECK_ONLY; then
  [ -d .claude/skills ] && ok ".claude/skills/ 存在（$(ls .claude/skills | wc -l | tr -d ' ') 个）" \
                        || fail ".claude/skills/ 不存在 —— 所有 skill 加载不了"
else
  mkdir -p .claude/skills
  n=0
  for d in .agents/skills/*/; do
    name=$(basename "$d")
    rsync -a --delete "$d" ".claude/skills/$name/"
    n=$((n+1))
  done
  ok "已镜像 $n 个 skill（.agents/skills 是唯一真相源，改完重跑本脚本即可）"
  [ -d .agents/skills/lieflat-charts ] || warn "lieflat-charts 是第三方 skill（20MB，自带 LICENSE），按 .gitignore 的决定不进仓库 —— 新机器上没有，要用得单独装"
fi

# ---------------------------------------------------------------------------
# 2. 全局出图能力：banner-creator + codex 插图 skill
# ---------------------------------------------------------------------------
echo "[2/6] 安装全局出图 skill …"
if ! $CHECK_ONLY; then
  mkdir -p "$HOME/.claude/skills" "$HOME/.codex/skills"
  rsync -a .agents/skills/banner-creator/ "$HOME/.claude/skills/banner-creator/"
  for d in .agents/codex-skills/*/; do
    name=$(basename "$d")
    # 两边都装：Claude 侧和 Codex 侧都可能调用
    rsync -a "$d" "$HOME/.codex/skills/$name/"
    rsync -a "$d" "$HOME/.claude/skills/$name/"
  done
  ok "banner-creator + $(ls .agents/codex-skills | wc -l | tr -d ' ') 个插图 skill 已装到全局"
  warn "插图 skill 的 assets/examples/（每个 13MB 的示例图）没有进仓库 —— 按 SKILL.md 自己的说法它们「只作低频视觉校准，不进入默认生成路径」，缺了不影响生成"
fi

# ---------------------------------------------------------------------------
# 3. 项目记忆：仓库 ↔ Claude Code memory 目录
# ---------------------------------------------------------------------------
echo "[3/6] 同步项目记忆 …"
# 记忆放在**另一个私有仓库**：本仓库是公开的，记忆里含 AWS 账号 ID、IAM 用户名、
# 私人邮箱、主密钥文件路径与变量名索引 —— 无密钥值，但打包公开就是踩点材料。
MEM_REPO="git@github.com:MushroomDAO/blog-memory.git"
MEM_VAULT="$REPO/.agents/memory"
MEM_LOCAL="$HOME/.claude/projects/$(echo "$REPO" | sed 's#/#-#g')/memory"
if $CHECK_ONLY; then
  [ -d "$MEM_VAULT/.git" ] && ok "记忆库已 clone（$(ls "$MEM_VAULT"/*.md 2>/dev/null | wc -l | tr -d ' ') 个 md）" \
                          || fail "没有 .agents/memory —— 跑一次不带 --check-only 的 bootstrap 来 clone"
  [ -d "$MEM_LOCAL" ] && ok "本机 Claude memory 目录有 $(ls "$MEM_LOCAL" 2>/dev/null | wc -l | tr -d ' ') 个文件" \
                      || fail "本机没有 Claude memory 目录 —— 偏好和教训全部缺失"
else
  if [ -d "$MEM_VAULT/.git" ]; then
    git -C "$MEM_VAULT" pull --ff-only -q 2>/dev/null && ok "记忆库已更新到最新" \
      || warn "记忆库 pull 失败（本地有未推送的改动？）—— 跑 scripts/sync-memory.sh 处理"
  elif git ls-remote "$MEM_REPO" >/dev/null 2>&1; then
    rm -rf "$MEM_VAULT"
    git clone -q "$MEM_REPO" "$MEM_VAULT" && ok "已 clone 私有记忆库到 .agents/memory/"
  else
    fail "访问不了 $MEM_REPO —— 私有仓库，需要这台机器的 SSH key 已加进 GitHub 账号（ssh -T git@github.com 自测）"
  fi

  if [ -d "$MEM_VAULT" ]; then
    mkdir -p "$MEM_LOCAL"
    before=$(ls "$MEM_LOCAL" 2>/dev/null | wc -l | tr -d ' ')
    # 只补本机没有的，绝不覆盖本机已有的 —— 本机那份可能比记忆库新
    rsync -a --ignore-existing --exclude='README.md' --include='*.md' --exclude='*' "$MEM_VAULT/" "$MEM_LOCAL/"
    after=$(ls "$MEM_LOCAL" 2>/dev/null | wc -l | tr -d ' ')
    ok "Claude memory: $before → $after 个文件（只补缺失，不覆盖本机已有）"
    echo "     日常双向对齐 + 推回私有库：scripts/sync-memory.sh"
  fi
fi

# ---------------------------------------------------------------------------
# 4. MemPalace：把仓库账本导进本机 palace
# ---------------------------------------------------------------------------
echo "[4/6] MemPalace 账本 …"
if command -v node >/dev/null 2>&1; then
  node .agents/skills/blog-publisher/sync-ledger.cjs status 2>&1 | sed 's/^/     /'
  # 这里**故意不自动 import**。查重根本不需要它 —— check-duplicate.cjs 同时读
  # chroma 和账本，别的机器写的条目照样查得到。而 import 走 `mempalace mine`，
  # 它会重排并切分文本，哈希对不上账本原文，所以 status 永远显示「只在仓库」，
  # 自动化跑就是每次重灌一遍（2026-09-10 实测：Mac mini palace 5 → 976 条）。
  # 想让本机语义搜索也能命中别的机器写的内容，再手动跑一次：
  #   node .agents/skills/blog-publisher/sync-ledger.cjs import
  if ! $CHECK_ONLY; then
    echo "     （不自动 import —— 查重不需要它，且 mempalace mine 会重排文本导致不收敛。"
    echo "       想补本机语义搜索：node .agents/skills/blog-publisher/sync-ledger.cjs import）"
  fi
else
  fail "没有 node，账本和发布流程都跑不了"
fi
$CHECK_ONLY || { git config core.hooksPath .githooks && ok "git hooks 已启用（提交时自动导出 MemPalace 到账本）"; }

# ---------------------------------------------------------------------------
# 5. 依赖体检 —— 这一段的价值在于「诚实」，缺什么直接说
# ---------------------------------------------------------------------------
echo "[5/6] 依赖体检 …"
need() { command -v "$1" >/dev/null 2>&1 && ok "$1" || { fail "缺 $1 —— $2"; }; }
need node    "brew install node（构建/发布/账本全靠它）"
need pnpm    "npm i -g pnpm（项目规定用 pnpm，不用 npm）"
need git     "xcode-select --install"
need magick  "brew install imagemagick（banner 和插图压缩）"
need ffmpeg  "brew install ffmpeg（视频线）"
if command -v gh >/dev/null 2>&1; then
  gh auth status >/dev/null 2>&1 && ok "gh（已登录）" || fail "gh 装了但没登录 —— forage 采不到 GitHub。跑 gh auth login"
else
  fail "缺 gh —— brew install gh && gh auth login（forage 采 GitHub）"
fi
need python3 "系统自带；缺了说明 PATH 有问题"

# codex：装了不等于能用 —— 没登录时 codex exec 会失败，而正文插图全靠它。
# 这一条是实测踩到的：Mac mini 上 codex --version 正常但 login status 是 Not logged in。
if command -v codex >/dev/null 2>&1; then
  # 先把输出收进变量再判断，不要用管道 —— `set -o pipefail` 下 grep -q 一匹配就
  # 关管道，上游进程收到 SIGPIPE 退出非零，整条管道被判为失败，结果是
  # 「没登录」被误判成「已登录」。这个假 ✓ 比没有检查更糟，实测踩到过。
  _codex_login=$(codex login status 2>&1 || true)
  if printf '%s' "$_codex_login" | grep -qi "not logged in"; then
    fail "codex 装了但**没登录** —— 正文插图会生成失败。跑一次交互式 \`codex login\`（需要浏览器）"
  else
    ok "codex（正文插图生成，已登录）"
  fi
else
  fail "缺 codex CLI —— 正文插图生成不了。npm 装的版本可能缺平台二进制，最稳的是直接下 release：
         gh release download rust-v0.154.0 --repo openai/codex --pattern 'codex-aarch64-apple-darwin.tar.gz' -D /tmp/codexdl
         tar -xzf /tmp/codexdl/*.tar.gz -C /tmp/codexdl && cp /tmp/codexdl/codex-aarch64-apple-darwin ~/.local/bin/codex && chmod +x ~/.local/bin/codex"
fi
command -v mempalace >/dev/null 2>&1 && ok "mempalace"                 || warn "缺 mempalace —— 查重会退化为只读仓库账本（仍可用）。装：pipx install mempalace"
command -v xhs       >/dev/null 2>&1 && ok "xhs（小红书采集）"          || warn "缺 xhs CLI —— forage 的小红书源会为 0。装：pipx install xiaohongshu-cli（还需要浏览器里有小红书登录态）"
command -v wrangler  >/dev/null 2>&1 || npx wrangler --version >/dev/null 2>&1 && ok "wrangler（部署）" || warn "wrangler 走 npx，首次会现装"

# 凭据
if [ -f .env ]; then ok ".env 存在"; else
  fail ".env 不存在 —— 微信草稿、Cloudflare 部署全部会失败。这个文件**不能**进 git，必须手动从旧机器拷：scp 旧机器:$REPO/.env ."
fi
[ -f "$HOME/Dev/.env" ] && ok "~/Dev/.env 存在（云基础设施凭据）" || warn "缺 ~/Dev/.env —— newsletter/DNS 相关脚本会拿不到凭据"

# FLUX：几个 GB，不可能进 git
FLUX_MODEL="${FLUX_MODEL_PATH:-$HOME/.omlx/models/FLUX.2-klein-4B-mflux-4bit}"
FLUX_VENV="${FLUX_VENV:-$HOME/venvs/ml/bin/activate}"
if [ -d "$FLUX_MODEL" ] && [ -f "$FLUX_VENV" ]; then
  ok "FLUX 模型 + mflux venv（banner 生成可用）"
else
  fail "banner 生成不可用 —— 模型 4.3GB + venv 1.6GB，不可能进 git，必须在本机装：
         python3 -m venv ~/venvs/ml && source ~/venvs/ml/bin/activate
         pip install mflux
         mdt download Runpod/FLUX.2-klein-4B-mflux-4bit"
fi

# 只在 Apple Silicon 上有意义
[ "$(uname -m)" = "arm64" ] || warn "非 Apple Silicon —— FLUX(MLX) banner 生成跑不了"

# ---------------------------------------------------------------------------
# 6. 运行权 + 定时任务
# ---------------------------------------------------------------------------
echo "[6/6] 24/7 运行权 …"
OWNER=$(python3 -c "import json;print(json.load(open('config/runner.json')).get('owner',''))" 2>/dev/null || echo "")
if $CLAIM && ! $CHECK_ONLY; then
  python3 - "$HOST" <<'PY'
import json, sys, datetime
p = 'config/runner.json'
d = json.load(open(p))
d['owner'] = sys.argv[1]
d['ownerNote'] = f"由 bootstrap-machine.sh --claim-owner 在 {sys.argv[1]} 上认领"
d['claimedAt'] = datetime.date.today().isoformat()
json.dump(d, open(p, 'w'), ensure_ascii=False, indent=2)
open(p, 'a').write('\n')
PY
  ok "本机（${HOST}）已认领 24/7 运行权"
  echo "     ⚠️  必须 commit + push config/runner.json，否则旧机器不知道自己该让位："
  echo "        git add config/runner.json && git commit -m 'chore: $HOST 接管 24/7 运行' && git push"
  echo "     ⚠️  然后去旧机器上 crontab -e 删掉 blog 相关的行 —— cron 不会自己 pull，"
  echo "        光改 runner.json 只能挡住有守卫的两个脚本，analytics 和 cookie 刷新仍会双跑。"
  OWNER="$HOST"
elif [ "$OWNER" = "$HOST" ]; then
  ok "本机就是 owner（${OWNER}）"
else
  warn "运行权归 ${OWNER:-<无>}，本机不是 —— 有副作用的定时任务会自动让路。要接管加 --claim-owner"
fi

if $INSTALL_CRON && ! $CHECK_ONLY; then
  P="$HOME/.bun/bin:$HOME/Library/pnpm:$HOME/.local/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin"
  TMPC=$(mktemp)
  crontab -l 2>/dev/null | grep -v "$REPO" > "$TMPC" || true

  # ---- 仓库对齐：两台机器都装，每 15 分钟一次 ----
  # 这条是给 Heinu1 微信 bot 兜底的：它在这个目录里 spawn claude，但**完全不碰 git**。
  # 没有这条，那台机器的树会一直漂（实测漂过 14 个提交），bot 就会在过时的
  # src/content/blog/ 和过时的账本上查重，把已经发过的选题判成没发过。
  echo "*/15 * * * * cd $REPO && PATH=$P ./scripts/sync-repo.sh >> /tmp/blog-repo-sync.log 2>&1" >> "$TMPC"

  # ---- 记忆同步：两台机器都装 ----
  # 它是双向的（rsync 按 mtime 新的赢 + MEMORY.md 取并集），两边同时跑不会互相
  # 覆盖，所以**不受运行权归属限制** —— 恰恰相反，只有两边都跑，记忆才真正同步。
  echo "45 21 * * * cd $REPO && PATH=$P ./scripts/sync-memory.sh >> /tmp/blog-memory-sync.log 2>&1" >> "$TMPC"

  # ---- 有副作用的任务：只有 owner 装 ----
  if [ "$OWNER" = "$HOST" ]; then
    cat >> "$TMPC" <<EOF
0 21 * * * cd $REPO && PATH=$P ./scripts/update-analytics.sh >> /tmp/blog-analytics-update.log 2>&1
10 21 * * * cd $REPO && PATH=$P ./.agents/skills/forage/run-daily.sh >> /tmp/forage-daily.log 2>&1
15 21 * * * cd $REPO && PATH=$P ./scripts/refresh-xhs-cookie.sh >> /tmp/xhs-cookie-refresh.log 2>&1
30 21 * * * cd $REPO && PATH=$P ./pipeline/newsletter/local-fallback.sh >> /tmp/newsletter-local.log 2>&1
EOF
  fi

  crontab "$TMPC" && rm -f "$TMPC"

  if [ "$OWNER" = "$HOST" ]; then
    ok "已装 6 条 cron（*/15 仓库对齐 / 21:00 analytics / 21:10 forage / 21:15 xhs cookie / 21:30 newsletter / 21:45 记忆同步）"
    warn "8042 评审台是常驻进程，走 LaunchAgent 不是 cron：拷 ~/Library/LaunchAgents/cv.mushroom.forage.plist 过来，把里面的路径改成本机的，再 launchctl load"
    warn "refresh-xhs-cookie.sh 从 Chrome Profile 15 提取登录态 —— 新机器没有那个 profile，得先用同一个 Chrome 账号登录小红书并确认 profile 编号"
  else
    ok "已装 2 条 cron（*/15 仓库对齐 / 21:45 记忆同步）—— 本机不是 owner，有副作用的 4 条没装"
  fi
  warn "cron 用的是非交互 shell：记忆同步要 push 到私有仓库，SSH key 必须无 passphrase 或已加进钥匙串，否则会静默失败（看 /tmp/blog-memory-sync.log）"
fi

echo
if [ $BLOCKERS -eq 0 ]; then
  echo "✅ 全部就绪。"
else
  echo "⚠️  完成，但有 $BLOCKERS 项阻塞（上面 ❌ 的），修完再跑 --check-only 复验。"
fi
