# Project Memory

## 文件命名规范

- **禁止用中文命名文件** - 所有文件名必须使用英文
- 文章 slug 使用英文短横线连接
- 示例：`vitalik-ai-survival-guide-cn.md` ✅，`vitalik-的-ai-文章.md` ❌

## 其他规范

- 所有文章 frontmatter 必须包含 `category` 字段
- 日期格式统一使用 ISO 格式：`2026-04-04`

---

## 🚀 发布文章 Skill

**位置：** `.agents/skills/blog-publisher/SKILL.md`

**触发词：**
- "发布文章"
- "发布blog"
- "发布公众号"
- "发布：文件路径.md"

**使用示例：**
```
发布：research/my-article.md，分类为 Research
```

**当用户要求发布文章时：**
1. 读取 `.agents/skills/blog-publisher/SKILL.md`
2. 按照 skill 定义的工作流程执行
3. 完成后返回 blog 链接和微信草稿状态
