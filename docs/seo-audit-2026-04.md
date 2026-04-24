# SEO Audit Report — Mushroom Research Blog
*审计时间：2026-04-24 | 执行状态：部分已修复*

---

## 执行摘要

博客 SEO 基础扎实（有 sitemap、RSS、OG tags），但存在若干高优先级缺口，修复后预计可显著提升中英文双语搜索可见度。

---

## 已执行修复（2026-04-24）

| # | 修复内容 | 文件 | 优先级 |
|---|---------|------|-------|
| ✅ 1 | 创建 `robots.txt`，允许 AI 爬虫（OAI-SearchBot、PerplexityBot、Claude-SearchBot） | `public/robots.txt` | HIGH |
| ✅ 2 | BlogPosting JSON-LD 结构化数据（headline、datePublished、dateModified、author、publisher、keywords、articleSection、inLanguage） | `src/layouts/BlogPost.astro` | HIGH |
| ✅ 3 | hreflang 标签（zh / en / x-default） | `src/layouts/BlogPost.astro` | CRITICAL |
| ✅ 4 | 修复 OG title 拼接：`Title | ` → `Title`（titleEn 为空时不追加 `| `） | `src/layouts/BlogPost.astro` | MEDIUM |
| ✅ 5 | heroImage 传入 BaseHead（OG image 使用文章封面而非全站默认） | `src/layouts/BlogPost.astro` | MEDIUM |
| ✅ 6 | RSS feed 添加 `<language>zh-CN</language>`、`<lastBuildDate>`、按日期降序排列、每条目含 `<category>` 标签 | `src/pages/rss.xml.js` | MEDIUM |

---

## 已执行修复（第二批，2026-04-24）

| # | 修复内容 | 文件 | 优先级 |
|---|---------|------|-------|
| ✅ 7 | 补全 12 篇文章的 titleEn / descriptionEn | 各 .md/.mdx 文件 | HIGH |
| ✅ 8 | 自定义 sitemap.xml（精确 lastmod = pubDate/updatedDate，含 priority、changefreq） | `src/pages/sitemap.xml.js` | HIGH |
| ✅ 9 | 移除 @astrojs/sitemap，改用自定义 sitemap 路由 | `astro.config.mjs` | HIGH |
| ✅ 10 | 相关文章区块（按 tag + category 匹配，最多 3 篇，含封面缩略图） | `src/layouts/BlogPost.astro` | MEDIUM |
| ✅ 11 | robots.txt 和 BaseHead sitemap 链接更新为 /sitemap.xml | `public/robots.txt`, `BaseHead.astro` | MEDIUM |

## 待执行（待办清单）

### Medium Priority

- [ ] **homepage 图片添加 `loading="lazy"`**
  - 50 篇列表图片同时加载影响首屏 LCP
  - 修改 `src/pages/index.astro` 的文章列表图片组件

- [ ] **添加面包屑导航**（BlogPost 布局 + BreadcrumbList schema）

- [ ] **修复 slug 命名**：`second-post`, `third-post`, `using-mdx` → 有语义的英文名

- [ ] **为 RSS feed 添加 `<content:encoded>`**（全文 HTML）
  - 当前 RSS 只有 description 摘要，读者无法在 RSS 阅读器看全文

### Low Priority

- [ ] 创建 `/categories/` 和 `/tags/` 独立页面（topical authority clustering）
- [ ] 添加 Organization JSON-LD 到首页
- [ ] 考虑 `/en/` 子目录或语言参数策略（English-first URL）
- [ ] `<link rel="prefetch">` 为热门文章链接添加预取提示

---

## 关键发现详解

### 1. 结构化数据缺失（已修复）
之前 Google 无法识别内容类型，添加 BlogPosting schema 后可能出现富摘要（发布日期、作者、图片）。

### 2. hreflang 缺失（已修复）
Google 不知道页面有中英双语内容，中英文 SERP 均损失可见度。

### 3. 内容架构：无 category/tag 独立页面
目前过滤是 JS 客户端实现（`?category=XXX`），搜索引擎无法为具体分类建立独立权威页面。这是中期最大的 topical authority 提升机会。

### 4. 内链不足
52 篇文章互相之间几乎没有内链。Google 靠内链传递权重——添加"相关文章"模块可显著提升整体 crawl efficiency。

---

## 参考工具

- Schema 验证：https://validator.schema.org
- 搜索结果富摘要测试：https://search.google.com/test/rich-results
- hreflang 验证：https://hreflang.org/checker/
- Robots.txt 测试：Google Search Console → URL Inspection
