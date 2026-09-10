#!/usr/bin/env bash
# ============================================================================
# sync-repo.sh — 让多入口写同一个仓库时不至于在过时的树上工作
# ----------------------------------------------------------------------------
# 这个仓库现在有三个入口会往里写：
#   1. MacBook 上的手动会话
#   2. Mac mini 的 cron（forage 采集）
#   3. Mac mini 上的 Heinu1 微信 bot —— 你发条微信，它就在这个目录里 spawn claude
#
# 第 3 个是最危险的：**Heinu1 完全不碰 git**。它只管在配置好的 workspace 里
# 起 claude，不 pull 也不 push。所以只要没人手动 pull，那台机器的树会一直漂。
# 实测过：2026-09-10 setup 时 Mac mini 落后 14 个提交。
#
# 在过时的树上写文章的后果不是冲突那么简单 —— blog-publisher 的查重要读
# src/content/blog/ 和 published-ledger.jsonl，两者都过时，就会把已经发过的
# 选题判成「没发过」然后重发一遍。这正是四本账制度要防的事。
#
# 所以：定时把树对齐。但要足够胆小 ——
#   · 工作区脏 → 跳过（可能有会话正在写）
#   · 有 claude 进程的 cwd 在这个仓库 → 跳过（bot 正在干活）
#   · 只做 ff-only 或 rebase，绝不 merge 出一个提交
#
# 用法：
#   scripts/sync-repo.sh          # 对齐（cron 用这个）
#   scripts/sync-repo.sh --dry    # 只报告会做什么
# ============================================================================
set -uo pipefail
cd "$(dirname "$0")/.."
REPO="$(pwd)"
DRY=false
[ "${1:-}" = "--dry" ] && DRY=true

log() { echo "[$(date '+%F %T')] $*"; }

# ---- 1. 有会话在干活就别动 ----------------------------------------------
# Heinu1 spawn 的是 `claude`，cwd 就是这个仓库。逐个 pid 查 cwd ——
# `lsof -c claude` 在 macOS 上匹配不到（实测），只能 pgrep 出 pid 再逐个问。
if command -v lsof >/dev/null 2>&1 && command -v pgrep >/dev/null 2>&1; then
  for _p in $(pgrep -x claude 2>/dev/null); do
    _cwd=$(lsof -a -p "$_p" -d cwd -Fn 2>/dev/null | grep '^n' | cut -c2-)
    if [ "$_cwd" = "$REPO" ]; then
      log "有 claude 会话正在这个仓库里工作（pid $_p），跳过对齐（下次 cron 再说）"
      exit 0
    fi
  done
fi

# 判「能不能安全 rebase」只看**已跟踪文件**的改动。
# 未跟踪文件不挡 rebase，而且这个仓库常年有一批未跟踪产物
# （pipeline/m2/output 的新记录、submodules/ 里子模块自己的未跟踪内容）——
# 拿 `git status --porcelain` 全量口径判断的话，工作区永远是「脏」的，
# 这个脚本就永远跳过，等于没写。实测：submodules/xiaoheishu 就是这么一直脏着。
if [ -n "$(git status --porcelain --untracked-files=no)" ]; then
  log "有已跟踪文件被改动，跳过对齐 —— 不在别人写了一半的树上做 rebase"
  git status --short --untracked-files=no | head -5 | sed 's/^/    /'
  exit 0
fi

# ---- 2. 对齐 --------------------------------------------------------------
git fetch -q origin 2>/dev/null || { log "fetch 失败（网络？），退出"; exit 0; }
BEHIND=$(git rev-list --count HEAD..origin/main 2>/dev/null || echo 0)
AHEAD=$(git rev-list --count origin/main..HEAD 2>/dev/null || echo 0)

if [ "$BEHIND" = "0" ] && [ "$AHEAD" = "0" ]; then
  log "已同步（$(git log --oneline -1)）"
  exit 0
fi

log "落后 ${BEHIND} / 领先 ${AHEAD}"
if $DRY; then
  log "--dry，不动手"
  [ "$BEHIND" != "0" ] && git log --oneline HEAD..origin/main | head -10 | sed 's/^/    ← /'
  [ "$AHEAD" != "0" ] && git log --oneline origin/main..HEAD | head -10 | sed 's/^/    → /'
  exit 0
fi

if [ "$BEHIND" != "0" ]; then
  if git pull --rebase -q 2>&1 | tail -3; then
    log "已拉取到 $(git log --oneline -1)"
  else
    log "⚠️ rebase 失败 —— 需要人工处理，不自动解决冲突"
    git rebase --abort 2>/dev/null
    exit 1
  fi
fi

if [ "$(git rev-list --count origin/main..HEAD 2>/dev/null || echo 0)" != "0" ]; then
  if git push -q 2>&1 | grep -v "^remote:" | tail -2; then
    log "已推送本地领先的提交"
  else
    log "⚠️ push 失败"
  fi
fi

log "完成"
