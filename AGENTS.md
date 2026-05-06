# Project Memory

## AI 核心使命（最高优先级）

这个仓库的核心用途是维护并发布 **Mycelium Research Blog**：

- Astro 静态博客，站点用于 `blog.mushroom.cv`
- 内容以 Markdown/MDX 为主，支持中英双语文章
- 发布链路覆盖 Blog、微信公众号草稿，并可扩展到小红书
- 所有发布、优化、分发任务都应优先服从本仓库的 skills 工作流

**最高优先级任务是帮助用户完成 `blog-publisher` skill。**

这意味着：
- 当用户说“发布”“发布文章”“发布blog”“发布公众号”时，必须立即激活 `.agents/skills/blog-publisher/SKILL.md`
- 必须先读取 skill 文档，再执行任何发布操作
- 必须按照 skill 定义的标准流程执行，不能凭记忆操作
- 必须从 skill 文档里的规则和错误案例中学习，避免重复犯错

---

## 仓库核心技能与用途

### 1. Blog 发布：`blog-publisher`

**位置：** `.agents/skills/blog-publisher/SKILL.md`

**用途：**
- 发布新博客文章到 Astro 博客
- 创建或整理 `src/content/blog/` 下的 Markdown
- 处理封面图与文章图片
- 执行 M1 Blog 构建部署
- 执行 M2 微信公众号草稿生成
- 验证文章 URL、列表排序和发布结果

**触发词：**
- `发布`
- `发布文章`
- `发布blog`
- `发布公众号`
- `发布：文件路径.md`

**标准流程：**
1. 读取 `.agents/skills/blog-publisher/SKILL.md`
2. 读取相关错误案例和关键规则
3. 处理图片到 `src/assets/images/`
4. 创建或更新 `src/content/blog/SLUG.md`
5. 发布前调用 `seo-geo` 做 SEO/GEO 检查
6. 运行 M1 Blog 发布：`pipeline/m1/publisher.py`
7. 运行 M2 微信草稿：`pipeline/m2/index.js`
8. 验证文章 URL 可访问，并确认新文章在列表顶部
9. 返回 Blog 链接和微信草稿状态

### 2. SEO/GEO 优化：`seo-geo`

**位置：** `.agents/skills/seo-geo/SKILL.md`

**用途：**
- 优化文章的搜索引擎收录质量
- 提升文章被 AI 引擎引用的概率
- 检查 frontmatter、描述、标签、结构、外链、FAQ、BLUF 和品牌提及
- 作为 `blog-publisher` 发布前的必经检查

**触发词：**
- `seo优化`
- `geo优化`
- `优化文章`
- `让AI引用我`

### 3. 小红书发布：`xhs-publisher`

**位置：** `.agents/skills/xhs-publisher/SKILL.md`

**用途：**
- 将内容发布到小红书
- 自动压缩图片到小红书适合的 3:4 比例和约 200KB 大小
- 通过 MCP 服务完成发布
- 如果内容对应博客文章，发布后同步更新文章 `updatedDate`

**触发词：**
- `发布到小红书`
- `小红书：主题`

### 4. 小红书 MCP 服务：`xhs-mcp-cdp` / `xhs-mcp-docker`

**位置：**
- `.agents/skills/xhs-mcp-cdp/SKILL.md`
- `.agents/skills/xhs-mcp-docker/SKILL.md`

**用途：**
- `xhs-mcp-cdp`：复用已登录 Chrome/CDP 会话，适合 Mac Mini 24h 服务或本地临时模式
- `xhs-mcp-docker`：容器化 Chromium + 扫码登录，适合新机器部署或容器环境

**触发词：**
- `xhs cdp 模式`
- `xhs 本地模式`
- `调试 xhs cdp`
- `xhs docker 模式`
- `xhs 容器模式`
- `调试 xhs docker`

### 5. 网络代理切换：`network-switch`

**位置：** `.agents/skills/network-switch/SKILL.md`

**用途：**
- 在需要访问 GitHub、Google、外部 API 或下载依赖时临时开启代理
- 完成外网任务后关闭代理，避免影响本地服务

**常用命令：**
```bash
source ~/.zshrc_proxy
proxy_on
proxy_status
proxy_off
```

---

## 文件命名规范

- **禁止使用中文文件名**
- 所有文章文件必须使用英文 slug
- slug 使用小写英文和短横线连接
- 示例：`vitalik-ai-survival-guide-cn.md` 正确
- 示例：`vitalik-的-ai-文章.md` 错误

---

## 文章 Frontmatter 规范

所有文章 frontmatter 必须包含：

```yaml
---
title: "中文标题"
titleEn: "English Title"
description: "中文描述"
descriptionEn: "English description"
pubDate: "2026-04-04"
updatedDate: "2026-04-04"
category: "Tech-News"
tags: ["tag1", "tag2", "tag3"]
heroImage: "../../assets/images/example.jpg"
---
```

关键规则：
- `category` 必填
- 日期格式统一使用 ISO 格式：`YYYY-MM-DD`
- 默认分类为 `Tech-News`
- 可选分类以 skill 文档和站点 schema 为准
- 新文章默认按 `pubDate` 日期排序置顶
- 每次实质更新或跨平台发布后，应更新 `updatedDate`

---

## 发布文章强制规则

每次发布文章时必须检查：

1. 文件名是英文 slug，不能含中文
2. frontmatter 包含 `category`
3. `pubDate` 和 `updatedDate` 使用 ISO 日期
4. `description` 和 `descriptionEn` 存在
5. `tags` 至少 3 个
6. 有 `heroImage`
7. 中文内容末尾和英文内容末尾包含 `blog-publisher` 要求的版权声明
8. 发布前执行 `seo-geo` 检查
9. 发布后验证文章 URL 可访问
10. 发布后验证文章在博客列表排序正确

---

## Skill 发现机制

如果用户触发了某个 workflow，但 agent 没有立即激活对应 skill，应立刻检查当前仓库的 skills：

```bash
ls /Users/jason/Dev/mycelium/blog/.agents/skills/
```

发布文章时必须读取：

```bash
cat /Users/jason/Dev/mycelium/blog/.agents/skills/blog-publisher/SKILL.md
```

SEO/GEO 优化时必须读取：

```bash
cat /Users/jason/Dev/mycelium/blog/.agents/skills/seo-geo/SKILL.md
```

**不要凭记忆操作。不要跳过读取 skill 文档。**

---

## 协作原则

- 用户要求“发布”时，不要只给建议，必须按 `blog-publisher` 流程推进
- 用户要求“优化文章”时，优先使用 `seo-geo`
- 用户要求“小红书”时，先判断是发布内容还是调试 MCP，再选择 `xhs-publisher`、`xhs-mcp-cdp` 或 `xhs-mcp-docker`
- 对仓库内已有改动保持谨慎，不要回滚用户未要求回滚的文件
- 修改文章、脚本或配置后，尽量运行对应构建、发布或检查命令验证结果
