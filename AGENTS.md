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

## 已确认的选题到发布工作流（2026-10-11）

- 用户说 “forge” 获取选题时，指本仓库的 `forage` skill；先读取 `.agents/skills/forage/SKILL.md`，按指定方向筛选并去重，优先拉 Hugging Face 模型卡、官方仓库和论文等一手资料。
- 用户已确认的日常偏好是“写了就默认发”。请求选题并代写文章时，接着执行 `blog-publisher` 完成双语博客和微信公众号草稿；用户明确要求仅草稿时遵循该要求。
- 每篇文章给出独立分析，区分官方宣称与实际测得结果；小模型选题尽量做本地 smoke test，保存可复核的测试证据，不能把未验证能力写成实测。
- 按发布 skill 完成封面、科技类小M正文配图、SEO/GEO、M1 Blog、M2 微信草稿，并验证公开文章 URL、图片和新文章列表排序；批量发布后同步语义索引及相关发布记录。
- 每批结果记录到 forage 的反馈和发布账本，持久化项目记忆；外部记忆库写入失败时明确记录失败，不声称入库成功。Codex 和微信机器人在此工作区执行时均遵循这些规则。

## 收到素材后的默认三件套与补偿（2026-10-11 用户再次确认）

- 所有收到的内容消息默认执行三件套：原始素材进入 KB；写双语文章并创建公众号草稿；发布 Blog。公众号按既有流程创建草稿，不擅自群发。控制命令、日常状态问答及用户明确要求不发布时，遵循具体请求。
- 写作前必须按 `blog-publisher` Step 0 查重：一手源 URL + 精确实体名，对照 Blog、公众号草稿箱、本地 M2 记录、MemPalace 与仓库账本。KB 收到素材不等于文章已经发布。
- 每篇文章必须按内容生成或采用匹配的合格 banner，Blog 和公众号使用同一篇最终稿及对应封面。补发旧稿时复用已经匹配且合格的 banner，不套无关封面。
- 历史失败要主动补做：先确认哪些步骤已完成，只补缺失的 KB、Blog、公众号或索引环节，复用最终 slug 与既有 media ID，避免重写文章或重复创建草稿。失败原因和可重试素材必须持久化。
- Heinu1 默认自动选择模型：日常 Luna Medium；复杂研究和完整发布流程在启动前使用 Sol Medium，结束后日常仍用 Luna。Codex 与 Claude 的后端切换仍为显式操作。
- 公众号 API 的 `40164` 是出口 IP 白名单问题，不能通过重复发布或重新登录 Codex 修复。必须保留真实错误、先存 KB、暂停自动重试；在公众号后台修复白名单后才恢复待补任务。检查历史消息、补失败任务是管理指令，不能把该指令本身写成新文章。
- 2026-10-13 用户再次要求：公众号失败不能阻止 Blog。完成可用的本地 Blog、M2 持久记录和 KB 账本查重后，远程公众号账本若因 40164 无法读取，明确记录该缺口，先完成 KB 和 Blog，再实际尝试一次缺失的公众号草稿。已存在的文章和草稿复用；分别汇报状态，不能隐藏已上线链接、把部分完成说成全部失败，或把请求检查历史的指令写成文章。微信回执首句必须回答“是不是发布了博客？”，成功给完整链接，失败明确说明尚未核验成功。
- 复用前先核对是否已经发布：线上 Blog、公众号已发布记录、远程草稿箱和本地凭证分别核对。草稿创建记录不能证明当前草稿仍存在；已发布接口返回 48001 且旧草稿不在草稿箱时，保留旧凭证并标记“当前状态未核验”，不能重新创建可能已经发布的文章。汇总必须区分新发布与复用旧结果。
- 微信 draft/add 连接中断可能发生在服务器已创建草稿之后。必须先读服务器草稿箱，匹配完整正文、标题、作者、摘要、原文链接、封面和评论设置；唯一一致才恢复同一个 media_id。字段缺失、未能核验或有多个一致结果时保留不确定，不盲目再次创建。2026-10-13 Mellum 实测发生此情况，服务器仅有一份草稿，已找回原 ID。
