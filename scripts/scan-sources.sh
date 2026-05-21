#!/usr/bin/env bash
# scan-sources.sh — 扫描 source/ 目录，用本地 AI 生成并发布博客文章
# 遵守 .agents/skills/source-scanner/SKILL.md 规范
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BLOG_DIR="$(dirname "$SCRIPT_DIR")"
SOURCE_DIR="$BLOG_DIR/source"
CONTENT_DIR="$BLOG_DIR/src/content/blog"
ASSETS_DIR="$BLOG_DIR/src/assets"
IMAGES_DIR="$BLOG_DIR/src/assets/images"
LOG_FILE="$SOURCE_DIR/.scan.log"
SKILL_DIR="$BLOG_DIR/.agents/skills/source-scanner"
KNOWN_ERRORS="$SKILL_DIR/KNOWN_ERRORS.md"

# 加载 .env
if [ -f "$BLOG_DIR/.env" ]; then set -a; source "$BLOG_DIR/.env"; set +a; fi

log() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG_FILE"; }

# ── 状态管理 ─────────────────────────────────────────────────────
state_get() {
  local f="$1/.state.json"; [ -f "$f" ] && jq -r --arg k "$2" '.[$k] // empty' "$f" || echo ""
}
state_set() {
  local f="$1/.state.json"; local cur="{}"; [ -f "$f" ] && cur="$(cat "$f")"
  echo "$cur" | jq --arg k "$2" --arg v "$3" '.[$k]=$v' > "$f"
}

# ── 错误归因 ──────────────────────────────────────────────────────
record_known_error() {
  local step="$1" error="$2" context="$3"
  mkdir -p "$SKILL_DIR"
  [ -f "$KNOWN_ERRORS" ] || printf '# Source Scanner — 已知错误\n\n---\n' > "$KNOWN_ERRORS"
  cat >> "$KNOWN_ERRORS" <<EOF

## [$(date '+%Y-%m-%d %H:%M')] 步骤: ${step}
**错误**: \`${error}\`
**上下文**: ${context}
**建议**: $(suggest_fix "$step" "$error")
---
EOF
  log "⚠️  错误已记录到 KNOWN_ERRORS.md"
}

suggest_fix() {
  case "$2" in
    *"40164"*|*"not in whitelist"*) echo "在 mp.weixin.qq.com 基本配置 → IP白名单 添加出口IP" ;;
    *"40007"*|*"invalid media_id"*) echo "media_id 已过期（72h），需重新上传封面图片" ;;
    *"AI returned empty"*)         echo "检查本地 AI 服务是否在线: curl $AI_API_URL/models" ;;
    *"build"*)                     echo "检查 MDX frontmatter 格式，运行 pnpm build 查看详情" ;;
    *)                             echo "查看 $LOG_FILE 获取完整错误" ;;
  esac
}

# ── AI 调用（纯文本）────────────────────────────────────────────
call_ai() {
  curl -s --max-time 300 -X POST "${AI_API_URL}/chat/completions" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer ${AI_API_KEY}" \
    -d "$(jq -n \
      --arg model "${AI_MODEL:-Qwen3-8B-4bit}" \
      --arg content "$1" \
      '{model:$model,messages:[{role:"system",content:"/no_think"},{role:"user",content:$content}],max_tokens:8192}')" \
  | jq -r '.choices[0].message.content // empty'
}

# ── 图片 OCR（macOS Vision framework，无需额外依赖）─────────────
OCR_SWIFT="$SCRIPT_DIR/ocr-image.swift"
ocr_image() {
  local img_path="$1"
  [ -f "$OCR_SWIFT" ] || { log "⚠️  ocr-image.swift not found"; return; }
  swift "$OCR_SWIFT" "$img_path" 2>/dev/null || true
}

# ── GitHub README 拉取 ──────────────────────────────────────────
fetch_github_readme() {
  local url="$1"
  # 从 URL 提取 owner/repo
  local repo_path
  repo_path=$(echo "$url" | grep -oE 'github\.com/[^/]+/[^/?#]+' | sed 's|github.com/||' | head -1)
  [ -z "$repo_path" ] && return

  log "Fetching GitHub README: $repo_path"
  local readme
  # 先用 gh cli，失败再用 curl GitHub API
  if command -v gh &>/dev/null; then
    readme=$(gh api "repos/${repo_path}/readme" --jq '.content' 2>/dev/null | base64 -d 2>/dev/null) || readme=""
  fi
  if [ -z "$readme" ]; then
    readme=$(curl -s "https://api.github.com/repos/${repo_path}/readme" \
      | jq -r '.content // empty' | base64 -d 2>/dev/null) || readme=""
  fi
  echo "$readme"
}

# ── Banner 选择（SKILL.md Step 5 优先级）──────────────────────────
# 返回两个值到全局变量: BANNER_ABSPATH / BANNER_HEROIMAGE
select_banner() {
  local dir="$1" slug="$2"
  mkdir -p "$IMAGES_DIR"

  # 优先级 1：source 目录里有图片 → sips 缩放到 1200x630
  local src_img
  src_img=$(find "$dir" -maxdepth 1 \( -iname "*.jpg" -o -iname "*.jpeg" -o -iname "*.png" -o -iname "*.webp" \) | head -1)
  if [ -n "$src_img" ]; then
    local banner_path="$IMAGES_DIR/${slug}-banner.jpg"
    log "Banner: resizing source image → ${slug}-banner.jpg"
    # sips: 先缩放保持比例，再裁切到 1200x630
    sips -z 630 1200 "$src_img" --out "$banner_path" >> "$LOG_FILE" 2>&1 || \
      cp "$src_img" "$banner_path"
    BANNER_ABSPATH="$banner_path"
    BANNER_HEROIMAGE="../../assets/images/${slug}-banner.jpg"
    return
  fi

  # 优先级 2：随机从 banner 池选取
  local banners=()
  while IFS= read -r f; do banners+=("$f"); done < <(ls "$ASSETS_DIR"/banner-*.jpg 2>/dev/null)
  if [ ${#banners[@]} -gt 0 ]; then
    local idx=$(( RANDOM % ${#banners[@]} ))
    local chosen="${banners[$idx]}"
    local chosen_name
    chosen_name="$(basename "$chosen")"
    log "Banner: random pool → $chosen_name"
    BANNER_ABSPATH="$chosen"
    BANNER_HEROIMAGE="../../assets/${chosen_name}"
    return
  fi

  # 优先级 3：fallback blog-placeholder
  log "Banner: fallback placeholder"
  BANNER_ABSPATH=""
  BANNER_HEROIMAGE="../../assets/blog-placeholder-1.jpg"
}

# ── 步骤 1: AI 生成文章 ────────────────────────────────────────────
step_ai_generate() {
  local dir="$1"
  local text_content="" url_content="" ocr_content="" readme_content=""
  [ -f "$dir/info.txt" ] && text_content="$(cat "$dir/info.txt")"
  [ -f "$dir/url.txt"  ] && url_content="$(cat "$dir/url.txt")"

  # 找所有图片（含 .bin 实为 JPEG 的情况）
  local images=()
  while IFS= read -r f; do
    local ftype; ftype=$(file -b "$f" 2>/dev/null)
    if echo "$ftype" | grep -qi "jpeg\|png\|webp\|gif"; then
      images+=("$f")
    fi
  done < <(find "$dir" -maxdepth 1 -type f \( -iname "*.jpg" -o -iname "*.jpeg" -o -iname "*.png" -o -iname "*.webp" -o -iname "*.bin" \))

  local image_count=${#images[@]}

  if [ -z "$text_content" ] && [ -z "$url_content" ] && [ "$image_count" -eq 0 ]; then
    log "⚠️  内容为空，跳过"; state_set "$dir" "ai" "skip"
    state_set "$dir" "blog" "skip"; state_set "$dir" "wechat" "skip"
    touch "$dir/.published"; return 0
  fi

  # ── OCR：提取图片中的文字 ──
  if [ "$image_count" -gt 0 ]; then
    log "OCR: extracting text from $image_count image(s)..."
    local i=1
    for img in "${images[@]}"; do
      log "  OCR image $i/$image_count: $(basename "$img")"
      local extracted
      extracted=$(ocr_image "$img" 2>/dev/null || echo "")
      if [ -n "$extracted" ]; then
        ocr_content="${ocr_content}
[图片 $i 文字]:
$extracted
"
      fi
      i=$((i+1))
    done
    [ -n "$ocr_content" ] && log "OCR done: $(echo "$ocr_content" | wc -w) words extracted"
  fi

  # ── 合并所有文字来源，提取 GitHub URL ──
  local all_text="${text_content}
${ocr_content}
${url_content}"

  local github_urls
  github_urls=$(echo "$all_text" | grep -oE 'https?://github\.com/[^/]+/[^[:space:]/]+' | sort -u || true)

  # ── 拉取 GitHub README ──
  if [ -n "$github_urls" ]; then
    log "Found GitHub URLs:"
    while IFS= read -r gh_url; do
      [ -z "$gh_url" ] && continue
      log "  → $gh_url"
      local readme
      readme=$(fetch_github_readme "$gh_url")
      if [ -n "$readme" ]; then
        readme_content="${readme_content}
[GitHub README: $gh_url]
$(echo "$readme" | head -200)
"
        log "  ✅ README fetched ($(echo "$readme" | wc -l) lines)"
      fi
    done <<< "$github_urls"
  fi

  # 先选 banner，把 heroImage 路径传给 AI
  local slug_tmp="tmp-$(date '+%Y%m%d%H%M%S')"
  BANNER_ABSPATH=""; BANNER_HEROIMAGE=""
  select_banner "$dir" "$slug_tmp"
  local hero_hint="$BANNER_HEROIMAGE"

  local today; today="$(date '+%Y-%m-%d')"
  local prompt
  prompt="你是 Mycelium Protocol 的技术博客写手，写简洁有深度的中英双语技术文章。

根据以下内容，生成一篇完整博客文章（Astro Markdown 格式）。

## 内容来源（按重要性排序）

### GitHub 仓库 README（主要信息来源）
${readme_content:-（无 GitHub 仓库）}

### 图片 OCR 提取文字
${ocr_content:-（无图片文字）}

### 用户文字备注
${text_content:-（无文字备注）}

### 链接列表
${url_content:-（无链接）}

（共 ${image_count} 张图片）

## 输出格式（严格遵守）

第一行：英文 slug（3-5个单词，小写+连字符，不含日期，例如 local-ai-model-guide）
第二行：空行
第三行起：完整 Markdown 文件，必须以 --- 开头（frontmatter）

frontmatter（所有字段必须填写）：
---
title: \"中文标题\"
titleEn: \"English Title\"
description: \"中文一句话描述（50字以内）\"
descriptionEn: \"English one-line description under 160 chars\"
pubDate: ${today}
updatedDate: ${today}
category: Tech-News
tags: [tag1, tag2, tag3]
heroImage: \"${hero_hint}\"
---

## 正文结构要求（SEO/GEO 规范）

中文正文（800-1200字）：
1. 第一行必须是 BLUF：> **BLUF**: 用一句话说核心价值或结论
2. 至少一个疑问句式的标题，如 ## 为什么值得关注？或 ## 它解决了什么问题？
3. 使用具体数字和事实（来自上面的内容）
4. 如果正文超过 1000 字，文末加 FAQ 部分：
   **FAQ**
   **Q: 问题？**
   A: 答案。
5. 文末版权（在 <!--EN--> 之前）：

---

> © 2026 Author: Mycelium Protocol. 本文采用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.zh) 授权——欢迎转载和引用，须注明作者姓名及原文链接。

<!--EN-->

英文正文（400-600字）：
1. 第一行必须是 BLUF：> **BLUF**: one sentence core value
2. 至少一个问句标题
3. 文末版权：

---

> © 2026 Author: Mycelium Protocol. Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) — free to share and adapt with attribution.

只输出 slug 和 Markdown，不要代码块标记或其他解释。"

  log "Calling AI (${AI_MODEL})..."
  local ai_output
  ai_output="$(call_ai "$prompt")"

  if [ -z "$ai_output" ]; then
    local err="AI returned empty response"
    log "❌ $err"; state_set "$dir" "ai" "failed"; state_set "$dir" "ai_error" "$err"
    record_known_error "ai_generate" "$err" "dir=$(basename "$dir") model=${AI_MODEL}"; return 1
  fi

  local slug
  slug="$(echo "$ai_output" | head -1 | tr -s ' ' '-' | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9-]//g; s/-*$//' | cut -c1-60)"
  [ -z "$slug" ] && slug="post-$(date '+%Y%m%d-%H%M%S')"
  local mdx_content
  # 去掉开头空行，确保文件以 --- 开头（否则 YAML frontmatter 解析失败）
  mdx_content="$(echo "$ai_output" | tail -n +3 | sed '/./,$!d')"

  # 真正的 banner（用真实 slug）
  BANNER_ABSPATH=""; BANNER_HEROIMAGE=""
  select_banner "$dir" "$slug"

  # 如果 banner 路径和 AI 生成的 heroImage 不一致，替换
  if [ -n "$BANNER_HEROIMAGE" ] && [ "$BANNER_HEROIMAGE" != "$hero_hint" ]; then
    mdx_content="${mdx_content//$hero_hint/$BANNER_HEROIMAGE}"
  fi

  local mdx_file="$CONTENT_DIR/${slug}.md"
  echo "$mdx_content" > "$mdx_file"
  log "✅ MDX written: src/content/blog/${slug}.md (banner: $BANNER_HEROIMAGE)"

  state_set "$dir" "ai" "done"
  state_set "$dir" "slug" "$slug"
  state_set "$dir" "banner" "$BANNER_HEROIMAGE"
}

# ── 步骤 2: Build + Deploy（强制 main 分支）─────────────────────
step_blog_deploy() {
  local dir="$1"
  local slug; slug="$(state_get "$dir" "slug")"

  log "Building..."
  if ! pnpm --prefix "$BLOG_DIR" build >> "$LOG_FILE" 2>&1; then
    local err="pnpm build failed"
    log "❌ $err"; state_set "$dir" "blog" "failed"
    record_known_error "blog_deploy" "$err" "slug=$slug"; return 1
  fi

  log "Deploying to Cloudflare Pages (branch=main)..."
  if ! (cd "$BLOG_DIR" && npx wrangler pages deploy dist \
      --project-name=blog-mushroom \
      --branch=main \
      --commit-dirty=true) >> "$LOG_FILE" 2>&1; then
    local err="wrangler deploy failed"
    log "❌ $err"; state_set "$dir" "blog" "failed"
    record_known_error "blog_deploy" "$err" "slug=$slug"; return 1
  fi

  # Git commit
  log "Committing..."
  (cd "$BLOG_DIR" && \
    git add "src/content/blog/${slug}.md" && \
    { git add "src/assets/images/${slug}-banner.jpg" 2>/dev/null || true; } && \
    git commit -m "feat(blog): publish ${slug}" >> "$LOG_FILE" 2>&1) || \
    log "⚠️  git commit skipped (nothing to commit or error)"

  state_set "$dir" "blog" "done"
  log "✅ Blog deployed → https://blog.mushroom.cv/blog/${slug}/"
}

# ── 步骤 3: 微信公众号草稿（带重试）──────────────────────────────
step_wechat_draft() {
  local dir="$1"
  local slug; slug="$(state_get "$dir" "slug")"
  local mdx_file="$CONTENT_DIR/${slug}.md"
  local max_retries=3

  [ -f "$BLOG_DIR/pipeline/m2/index.js" ] || { state_set "$dir" "wechat" "skip"; return 0; }
  [ -f "$mdx_file" ] || { log "⚠️  MDX not found"; return 1; }

  local retries; retries="$(state_get "$dir" "wechat_retries")"; retries="${retries:-0}"

  while [ "$retries" -lt "$max_retries" ]; do
    log "WeChat draft attempt $((retries+1))/$max_retries..."
    local out
    if out=$(node "$BLOG_DIR/pipeline/m2/index.js" "$mdx_file" 2>&1); then
      echo "$out" >> "$LOG_FILE"
      state_set "$dir" "wechat" "done"
      log "✅ WeChat draft created"; return 0
    fi
    echo "$out" >> "$LOG_FILE"
    retries=$((retries+1)); state_set "$dir" "wechat_retries" "$retries"
    local err; err="$(echo "$out" | grep -o '"errcode":[0-9]*.*"errmsg":"[^"]*"' | head -1)"
    log "❌ WeChat attempt $retries failed: $err"
    [ "$retries" -lt "$max_retries" ] && { log "Retrying in 10s..."; sleep 10; }
  done

  local final_err; final_err="$(state_get "$dir" "wechat_error")"
  state_set "$dir" "wechat" "failed"
  record_known_error "wechat_draft" "$final_err" "slug=$slug retries=$max_retries"
  log "❌ WeChat failed after $max_retries attempts"
  return 1
}

# ── 主处理函数 ────────────────────────────────────────────────────
process_dir() {
  local dir="$1"; local dirname; dirname="$(basename "$dir")"
  touch "$dir/.processing"

  local ai_st blog_st wechat_st
  ai_st="$(state_get "$dir" "ai")"; blog_st="$(state_get "$dir" "blog")"; wechat_st="$(state_get "$dir" "wechat")"
  log "--- $dirname [ai=$ai_st blog=$blog_st wechat=$wechat_st]"

  if [[ "$ai_st" != "done" && "$ai_st" != "skip" ]]; then
    step_ai_generate "$dir" || { rm -f "$dir/.processing"; return 1; }
  else log "⏭  AI: already done"; fi

  if [[ "$blog_st" != "done" && "$blog_st" != "skip" ]]; then
    step_blog_deploy "$dir" || { rm -f "$dir/.processing"; return 1; }
  else log "⏭  Blog: already done"; fi

  if [[ "$wechat_st" != "done" && "$wechat_st" != "skip" ]]; then
    local wr; wr="$(state_get "$dir" "wechat_retries")"; wr="${wr:-0}"
    if [ "$wr" -lt 3 ]; then
      step_wechat_draft "$dir" || true
    else log "⏭  WeChat: max retries reached, skipping"; fi
  else log "⏭  WeChat: already done"; fi

  blog_st="$(state_get "$dir" "blog")"; wechat_st="$(state_get "$dir" "wechat")"
  if [[ "$blog_st" == "done" || "$blog_st" == "skip" ]]; then
    touch "$dir/.published"
    if [[ "$wechat_st" == "done" || "$wechat_st" == "skip" ]]; then
      log "✅ Fully published: $dirname"
    else
      log "⚠️  Blog published, WeChat pending: $dirname"
    fi
  else
    log "⚠️  Incomplete: $dirname (will retry)"
  fi
  rm -f "$dir/.processing"
}

# ── 主循环 ────────────────────────────────────────────────────────
log "=== Source scan started ==="
[ -d "$SOURCE_DIR" ] || { log "ERROR: source/ not found"; exit 1; }
[ -n "${AI_API_KEY:-}" ] || { log "ERROR: AI_API_KEY not set"; exit 1; }

FOUND=0
for dir in "$SOURCE_DIR"/*/; do
  if [ ! -d "$dir" ]; then continue; fi

  # 已有 .published → 只在 blog完成+wechat未完成 时移除标记重试
  if [ -f "$dir/.published" ]; then
    blog_st="$(state_get "$dir" "blog")"
    wechat_st="$(state_get "$dir" "wechat")"
    if [[ "$blog_st" == "done" && ("$wechat_st" == "failed" || "$wechat_st" == "pending") ]]; then
      wr="$(state_get "$dir" "wechat_retries")"; wr="${wr:-0}"
      if [ "$wr" -lt 3 ]; then
        rm -f "$dir/.published"
      else
        continue
      fi
    else
      continue
    fi
  fi

  # 正在处理中，跳过
  if [ -f "$dir/.processing" ]; then continue; fi

  FOUND=1
  process_dir "$dir" || log "⚠️  Error in $(basename "$dir")"
done

[ $FOUND -eq 0 ] && log "No new sources found."
log "=== Source scan done ==="
