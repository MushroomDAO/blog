  搜索流量接近零的根本原因诊断

  🔴 第一类：结构性障碍（最关键）

  1. 域名历史污染 — 影响所有早期收录

  代码历史里有一条提交：fix(seo): correct canonical domain
  mshroom→mushroom。这意味着博客上线初期所有页面的 canonical URL
  都指向了错误的域名（mshroom.cv）。Google 如果在 canonical 修复之前已经收录了这些页面，等于把权重
  给了一个不存在的域名，修复后这些权重也不会自动迁移，需要时间重建。

  2. 网站太新，域名权重近乎为零

  最早的文章提交记录在 4 月初，距今不到 2 个月。Google 对新域名有 6-12
  个月的"沙盒期"，不会轻易给新站排名。这是最大的结构性原因，无法绕过，只能用内容质量和外链加速。

  3. Google Search Console 是最近才接入的

  GSC 验证是近期才加的（feat(seo): add Google Search Console verification file and meta
  tag）。没有提前提交 sitemap，Google 是通过自然爬取慢慢发现页面的，速度很慢。

  ---
  🟠 第二类：技术缺陷（可立即修复）

  4. title 和 description meta 标签过长且双语混用

  当前实现：
  title={titleEn ? `${title} | ${titleEn}` : title}
  description={descriptionEn ? `${description} | ${descriptionEn}` : description}

  结果是 title 长达 60-100 个字符（最优是 50-60），description 长达 200-300 个字符。Google
  会直接截断，关键词也被稀释。中英文混在同一个标签里，Google 不清楚该用哪个语言定向排名。

  5. lang="zh" 在 BlogPost.astro 里是硬编码

  <html lang="zh">

  所有页面都被标记为中文，英文内容对 Google 的英文排名没有贡献，中英双语优势完全浪费。

  6. sitemap 里静态页面 lastmod 每次构建都变化

  <lastmod>${new Date().toISOString()}</lastmod>  // 首页/关于/博客列表

  每次部署首页的 lastmod 都变成当前时间，Google
  抓取器认为首页"一直在改变"，反而可能降低对内容页的爬取优先级，因为它认为 sitemap 数据不可靠。

  7. hreflang 指向同一个 URL

  <link rel="alternate" hreflang="zh" href="同一个URL" />
  <link rel="alternate" hreflang="en" href="同一个URL" />

  中英文指向同一个 URL 对 Google 来说没有意义——它不知道该把这个页面展示给中文用户还是英文用户。

  ---
  🟡 第三类：内容与外链（中长期问题）

  8. 几乎没有外部链接（外链）

  这是新站流量为零的另一个核心原因。没有其他网站链接过来，PageRank 为零，Google
  对这个域名没有任何"信任背书"。

  9. 文章主题多为极新的小众技术

  SkillFlow、FastMCP、SuperPaymaster 这些关键词几乎没有人在搜索——它们太新了，搜索量接近
  0。覆盖有搜索量的经典问题（"ERC-4337 是什么"、"TTS 开源方案对比"）才能带来流量。

  10. 文章间没有内链策略

  100 篇文章几乎不互相引用，PageRank 无法在站内流动。Google 抓到一篇文章，不容易发现其他相关文章。

  ---
  改进措施（按优先级）

  立即执行（本周）

  ① 去 Google Search Console 提交 sitemap

  登录 GSC → 左边"站点地图" → 填入 https://blog.mushroom.cv/sitemap.xml → 提交。然后对最重要的 5-10
   篇文章手动"网址检查 → 请求编入索引"。

  ② 修复 title 和 description meta 标签

  中英文用不同标签，不要混拼：

  <!-- 根据页面语言用对应语言的 title/desc -->
  <title>{title}</title>
  <meta name="description" content={description} />
  <!-- 英文变体用 og 标签携带，或通过 hreflang 分离 -->

  ③ 修复 sitemap 静态页面 lastmod

  // 改为固定日期，不要用 new Date()
  { path: '', lastmod: '2026-04-01', priority: '1.0', changefreq: 'daily' },

  ④ 修复 html lang 动态化

  <html lang={hasEnglish ? "zh" : "zh"}>  // 至少别全写死

  更好的方案：中文内容用 zh-CN，如果页面有英文版本考虑用子路径（/en/blog/slug/）分离。

  ---
  近期执行（1-2 周）

  ⑤ 在外部平台发布内容，建立外链

  每篇文章发布后同步：
  - V2EX（中文技术社区，链接可被 Google 索引）
  - GitHub README 或 Discussion（技术类权重高）
  - Hacker News / Reddit r/MachineLearning（英文受众）
  - 微信公众号文章里加博客链接（目前没有）

  ⑥ 为每篇文章加内链

  在文章末尾加"相关文章"的文字链接（你现在有 related posts 卡片，但 Google 更看重正文内的 <a>
  标签链接）。

  ⑦ 补充有搜索量的"常青"主题文章

  除了追新，补充一些有稳定搜索量的主题：
  - "ERC-4337 账户抽象完整指南"
  - "本地 TTS 方案对比 2026"
  - "MCP 服务器开发入门"

  这类文章的关键词有真实搜索量，能带来持续流量。

  ---
  中期（1-3 个月）

  ⑧ 考虑中英文内容分离

  当前双语同 URL 方案对 SEO 效率低。更好的方案：
  - 中文：blog.mushroom.cv/blog/slug/
  - 英文：blog.mushroom.cv/en/blog/slug/（或独立域名）

  这样 hreflang 才能真正发挥作用，中英文各自参与对应语言市场的排名。

  ⑨ 建立 Google News 或 Topic Authority

  在某几个垂直主题（比如 MCP 生态、Account Abstraction、开源 TTS）持续深耕，Google
  会逐步识别这个站点作为该主题的权威来源。

  ---
  最后的判断

  最主要原因只有两个：① 域名太新（时间无法绕过）；② GSC 没早接入 + sitemap
  没有提交。其余都是加分项。

  当前最值得花时间的事：去 GSC 提交 sitemap，对重要文章手动请求索引，然后每次发新文章都同步去
  V2EX/Reddit 发一条带链接的讨论帖。流量通常要 3-6
  个月后才能体现，但从现在开始操作能把时间线往前推。
