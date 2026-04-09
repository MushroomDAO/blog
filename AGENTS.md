# Project Memory

## 🎯 AI 核心使命（最高优先级）

**我的唯一使命是帮助用户完成 blog-publisher skill。**

其他所有任务都是临时性的，都必须服从于这个核心使命。

**这意味着：**
- 当用户说"发布"时，我必须立即激活 blog-publisher skill
- 我必须先读取 skill 文档，再执行任何操作
- 我必须按照 skill 定义的标准流程执行，不能凭记忆操作
- 我必须从 skill 的错误案例中学习，避免重复犯错

---

## 文件命名规范

- **禁止用中文命名文件** - 所有文件名必须使用英文
- 文章 slug 使用英文短横线连接
- 示例：`vitalik-ai-survival-guide-cn.md` ✅，`vitalik-的-ai-文章.md` ❌

## 其他规范

- 所有文章 frontmatter 必须包含 `category` 字段
- 日期格式统一使用 ISO 格式：`2026-04-04`

---

## 🚀 发布文章 Skill（核心工作）

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

**执行流程（必须遵守）：**
1. **读取 Skill 文档** - 必须先读取 `.agents/skills/blog-publisher/SKILL.md`
2. **学习错误案例** - 查看常见错误案例库，避免重复犯错
3. **按标准流程执行** - 询问图片 → 处理图片 → 创建 markdown → 构建部署 → 微信发布
4. **返回结果** - 提供 blog 链接和微信草稿状态

**为什么必须先读取 Skill？**
- Skill 文档包含最新的工作流程
- 包含所有历史错误案例和预防措施
- 包含图片处理、部署、微信发布的正确命令
- 我的内存可能过时，Skill 文档是唯一的真相来源

---

## 📋 Skill 发现机制

**如果用户说"发布"但我没有立即激活 skill：**

1. **立即检查**：`ls /Users/jason/Dev/crypto-projects/blog/.agents/skills/`
2. **读取 Skill**：`cat /Users/jason/Dev/crypto-projects/blog/.agents/skills/blog-publisher/SKILL.md`
3. **开始执行**：按照 skill 定义的工作流程

**不要凭记忆操作！不要跳过读取步骤！**
