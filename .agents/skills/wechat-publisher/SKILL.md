---
name: wechat-publisher
description: |
  Publish content directly to WeChat Official Account only — no blog deploy.

  Trigger when user says: 发布公众号, 公众号发布, 发微信, 推送公众号, publish wechat, wechat draft.

  Use for:
  - turning raw notes / topic description / article content into a WeChat-ready draft
  - optimizing structure and title for WeChat readership
  - selecting a random banner
  - creating a WeChat Official Account draft via M2 pipeline

  Critical rules:
  - WeChat title must be ≤ 64 characters (Chinese counts as 2 bytes, strict limit)
  - no blog deploy needed — this is WeChat only
  - create a temp markdown file, run M2, then report media ID
---

# WeChat Publisher Skill

## Mission

Take user-provided content (raw notes, topic, article body) → optimize for WeChat → pick banner → push draft to WeChat Official Account.

No Astro build. No Cloudflare deploy. WeChat only.

M2 pipeline: `pipeline/m2/index.js`
Draft output: `pipeline/m2/output/`

---

## Trigger Words

Use this skill immediately when the user says any of:
- `发布公众号`
- `公众号发布`
- `发微信`
- `推送公众号`
- `publish wechat`
- `wechat draft`

---

## Step 1 — Generate Title

WeChat title rules:
- **Hard limit: ≤ 64 characters** (WeChat API returns `errcode 45003` if exceeded)
- Chinese characters each count as 2 bytes; ASCII as 1
- Good style: punchy, informative, no padding
- If the user provides a title, check its length. Trim if over limit.
- If no title provided, draft one from the content — short and specific.

Quick byte check:
```bash
echo -n "标题文字" | wc -c   # must be ≤ 64
```

---

## Step 2 — Optimize Content for WeChat

Structure the content as:

1. **开头钩子（Hook）** — 1-2 sentences, state the most interesting fact or conclusion
2. **正文** — 3-5 sections, each with a clear heading; concrete numbers and facts preferred
3. **结尾** — actionable takeaway or call to reflection

WeChat-specific rules:
- Ideal length: 500–900 characters (Chinese). Longer is fine if content warrants it.
- Avoid AI filler phrases; write directly
- Keep paragraphs short (2-4 lines max)
- Use H2 (`##`) as section dividers — WeChat renderer converts them to styled headers
- Tables are supported by the M2 renderer — use them for comparisons
- Code blocks are supported

---

## Step 3 — Pick Banner

### Priority order

1. **User provides an image** → compress and use it directly.
2. **xiaobaobao banner pool** (`src/assets/banners/xiaobaobao/`) → if any `.jpg` / `.png` files exist here, pick one at random.
3. **Default pool** (fallback, see below) → if the xiaobaobao directory is empty.

Check xiaobaobao pool:
```bash
ls src/assets/banners/xiaobaobao/*.jpg src/assets/banners/xiaobaobao/*.png 2>/dev/null
```

Pick random from xiaobaobao pool (bash):
```bash
files=(src/assets/banners/xiaobaobao/*.jpg src/assets/banners/xiaobaobao/*.png)
banner="${files[RANDOM % ${#files[@]}]}"
echo "Selected: $banner"
```

User provides an image → compress and save:
```bash
sips -s format jpeg INPUT.png --out src/assets/images/SLUG-hero.jpg
sips -Z 1200 src/assets/images/SLUG-hero.jpg --out src/assets/images/SLUG-hero.jpg
```

### Adding banners
Place new banner images (JPG/PNG, ideally 1200×630) into:
```
src/assets/banners/xiaobaobao/
```
They will be picked up automatically on the next publish.

### Default fallback pool (used only when xiaobaobao pool is empty)
```
../../assets/banner-future-is-now.jpg
../../assets/banner-ai-new-intelligence.jpg
../../assets/banner-human-ai-coexistence.jpg
../../assets/banner-digital-public-goods.jpg
../../assets/banner-ai-personal-assistant.jpg
../../assets/banner-personal-growth-ai-skills.jpg
```

---

## Step 4 — Create Minimal Markdown

Create `src/content/blog/SLUG.md` with this frontmatter:

```yaml
---
title: "中文标题（≤64字节）"
titleEn: "English Title"
description: "一句话描述"
descriptionEn: "One-line description"
pubDate: "YYYY-MM-DD"
updatedDate: "YYYY-MM-DD"
category: "Tech-News"
tags: ["tag1", "tag2", "tag3"]
heroImage: "../../assets/banner-XXX.jpg"
---
```

Followed by the optimized Chinese content body.

No English section required for WeChat-only publish. Optionally add `<!--EN-->` section if bilingual is desired.

---

## Step 5 — Run M2

```bash
node pipeline/m2/index.js "src/content/blog/SLUG.md"
```

Themes available (M2 picks randomly if not specified):
`claude` / `chengyun` / `blue` / `sticker` / `mint` / `purple` / `cyber` / `rose`

To specify a theme:
```bash
node pipeline/m2/index.js "src/content/blog/SLUG.md" --theme chengyun
```

---

## Step 6 — Report Result

Return:
- Draft title
- Theme used
- Media ID (for WeChat backend confirmation)
- Markdown file path

---

## Known Failure Cases

### Title too long (errcode 45003)
WeChat rejects titles over ~64 chars. Shorten and retry:
```bash
echo -n "你的标题" | wc -c
```

### WeChat IP whitelist error (40164)
```
invalid ip x.x.x.x, not in whitelist
```
Fix: log into mp.weixin.qq.com → Settings → API whitelist → add the reported IP. Retry after ~1 min.

### Wrong WeChat account
Check `.env` has the correct `WECHAT_APP_ID` / `WECHAT_APP_SECRET` / `WECHAT_MP_ID` for the intended account.

---

## Banner Pool Quick Reference

### xiaobaobao 专属 banner（优先使用）
存放路径：`src/assets/banners/xiaobaobao/`
推荐主题：财富、金融、股票、理财、赚钱相关
推荐尺寸：1200×630，文件大小 ≤ 150KB

### 默认 fallback banner
| Filename | Theme Feel |
|----------|-----------|
| `banner-future-is-now.jpg` | 科技感/未来 |
| `banner-ai-new-intelligence.jpg` | AI/智能 |
| `banner-human-ai-coexistence.jpg` | 人机协作 |
| `banner-digital-public-goods.jpg` | 开源/公共 |
| `banner-ai-personal-assistant.jpg` | 个人助理 |
| `banner-personal-growth-ai-skills.jpg` | 成长/技能 |
