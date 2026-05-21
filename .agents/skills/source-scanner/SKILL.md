---
name: source-scanner
description: |
  Scan source/ directory for new unprocessed subdirectories, extract content (text, images, URLs),
  generate a complete bilingual blog post, and call blog-publisher to deploy.

  Trigger when:
  - scripts/scan-sources.sh detects a new source directory
  - User says "扫描source", "处理source目录", "process source", "scan sources"
  - User passes a specific directory: "处理 source/DIRNAME"

  This skill handles content extraction. Blog-publisher handles deployment.
---

# Source Scanner Skill

## Mission

Process one or more unprocessed directories under `source/`, generate complete bilingual blog posts,
and publish them via the blog-publisher skill.

An "unprocessed" directory is any `source/*/` subdirectory that has **no `.published` file**.

---

## Step 1: Discover Unprocessed Directories

```bash
for dir in source/*/; do
  [ -d "$dir" ] && [ ! -f "$dir/.published" ] && [ ! -f "$dir/.processing" ] && echo "$dir"
done
```

If a specific directory was named by the user or scan script, use only that one.
If none found, report "No new sources found" and stop.

---

## Step 2: For Each Unprocessed Directory — Inventory

```bash
ls -la source/DIRNAME/
```

Classify files found:
- **Text**: `.txt`, `.md` → read with Read tool
- **Metadata hints**: `meta.yaml` → read first, apply its hints
- **Images**: `.png`, `.jpg`, `.jpeg`, `.webp` → view with Read tool (Claude can see images)
- **Video**: `.mp4`, `.mov` → note exists; extract first frame with ffmpeg if available
- **URLs**: `url.txt` or `urls.txt` → fetch each with WebFetch tool

Mark as processing to prevent duplicate runs:
```bash
touch source/DIRNAME/.processing
```

---

## Step 3: Extract All Content

### Text files
Read every `.txt` and `.md` file. This is the primary content source.

### meta.yaml hints (read first if present)
```yaml
title: "Optional title"         # skip AI title generation if provided
category: "Tech-News"           # use directly
tags: ["tag1", "tag2"]          # merge with AI-generated tags
theme: "blue"                   # WeChat theme for M2
```

### Images
Use the Read tool on each image file. Note:
- What is shown in the image
- Any visible text, UI elements, diagrams
- The first image found will be the banner candidate

### URLs (url.txt / urls.txt)
Fetch each URL with WebFetch. Extract:
- Page title
- Main content / README
- Any banner or og:image URL
- For GitHub repos: fetch the README via `gh api repos/OWNER/REPO/readme`

---

## Step 4: Generate Blog Content

Based on all collected content, write a complete bilingual blog post following blog-publisher conventions:

### Frontmatter
```yaml
---
title: "中文标题"
titleEn: "English Title"
description: "中文描述 100字以内"
descriptionEn: "English description under 160 chars"
pubDate: "YYYY-MM-DD"
updatedDate: "YYYY-MM-DD"
category: "Tech-News"
tags: ["tag1", "tag2", "tag3"]
heroImage: "../../assets/images/SLUG-banner.jpg"
---
```

### Content rules
- Open with BLUF (Bottom Line Up Front)
- Chinese body: 1000-2000 words
- At least one question-format heading
- FAQ section if over 1000 words
- Source link at the end
- Copyright block before `<!--EN-->`
- English section after `<!--EN-->`
- Copyright block at end of English section
- Concrete numbers and source facts where available

### Slug
Choose a short English slug (3-5 words, hyphen-separated) that is keyword-bearing and unique.
Do not use today's date in the slug.

---

## Step 5: Banner Selection

Priority order:
1. **Image in source directory**: resize first `.png`/`.jpg` to 1200x630 using sips:
   ```bash
   sips -z 630 1200 source/DIRNAME/image.png --out /tmp/banner-raw.png
   sips -s format jpeg -s formatOptions 75 /tmp/banner-raw.png \
     --out src/assets/images/SLUG-banner.jpg
   ```
2. **GitHub repo og:image / README banner**: if URL points to GitHub, try fetching the banner image
3. **Random banner from pool**: pick from available banners in `src/assets/`:
   - `banner-ai-new-intelligence.jpg`
   - `banner-digital-public-goods.jpg`
   - `banner-future-is-now.jpg`
   - `banner-ai-smart-city-collab.jpg`
   - `blog-placeholder-1.jpg` … `blog-placeholder-5.jpg`

   For random banner, use path format: `../../assets/banner-NAME.jpg`

---

## Step 6: Write Markdown File

```bash
src/content/blog/SLUG.md
```

Write the complete markdown file directly. Do not use M1 pipeline (it may alter the slug).

---

## Step 7: Hand Off to Blog Publisher

Run all blog-publisher steps from **Step 5 (Build)** onward:

```bash
# SEO/GEO check (quick pass)
# - description and descriptionEn exist
# - tags >= 3
# - BLUF present
# - copyright blocks present

# Build
pnpm build

# Verify built
ls dist/blog | grep SLUG

# Deploy
npx wrangler pages deploy dist --project-name=blog-mushroom --branch=main --commit-dirty=true

# Validate
curl -sI https://blog.mushroom.cv/blog/SLUG/ | head -3

# Commit
git add src/content/blog/SLUG.md
git add src/assets/images/SLUG-banner.jpg 2>/dev/null || true
git commit -m "feat(blog): publish SLUG"

# WeChat draft (use theme from meta.yaml, default: blue)
cd pipeline/m2
node index.js "../../src/content/blog/SLUG.md" --theme blue
cd ../..
```

---

## Step 8: Mark as Published

```bash
touch source/DIRNAME/.published
rm -f source/DIRNAME/.processing
git add source/DIRNAME/.published
git commit -m "chore(source): mark DIRNAME as published"
```

---

## Step 9: Report

Return:
- Blog URL: `https://blog.mushroom.cv/blog/SLUG/`
- WeChat draft media ID
- Banner path and size
- Any issues encountered

---

## Error Handling

If any step fails:
1. Remove `.processing` marker: `rm -f source/DIRNAME/.processing`
2. Do NOT create `.published` marker
3. Report the failure so the directory can be retried on next scan

If WeChat fails but blog succeeded:
- Still create `.published` marker (blog is live)
- Report the WeChat failure separately

---

## Content Type Handling Reference

| File type | Tool | What to extract |
|---|---|---|
| `.txt` | Read | All text content |
| `.md` | Read | All content, strip frontmatter if present |
| `meta.yaml` | Read | Title hint, category, tags, theme |
| `.png/.jpg/.webp` | Read (image) | Visual content, visible text, UI description |
| `url.txt` / `urls.txt` | WebFetch per line | Page title, main content, images |
| GitHub URL | `gh api repos/OWNER/REPO/readme` | Full README |
| `.mp4/.mov` | Bash `ffmpeg` | Extract first frame (if ffmpeg available) |
