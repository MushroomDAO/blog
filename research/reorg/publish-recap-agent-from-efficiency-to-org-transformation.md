## 发布复盘: Agent：从效率替代到组织变革

**发布时间**: 2026-04-09
**文章**: Agent：从效率替代到组织变革 / agent-from-efficiency-to-org-transformation

### 本次发布遇到的问题

| 序号 | 问题描述 | 错误信息 | 根本原因 |
|------|----------|----------|----------|
| 1 | 没有使用 Skill | AI 直接手动操作，未读取 skill 文档 | 不知道 skill 位置，没有主动查找 |
| 2 | 图片路径错误 | `[ImageNotFound] Could not find requested image '/images/jack-dorsey.png'` | 图片放在 `public/images/`，但 heroImage 路径格式错误 |
| 3 | heroImage 路径格式 | 使用了绝对路径 `/images/xxx.png` | 应该用相对路径 `../../assets/images/xxx.jpg` |

### 解决方案

1. **Skill 发现问题**: 在 `.agents/skills/blog-publisher/SKILL.md` 添加清晰的触发词和位置指引
2. **图片路径问题**: 将图片移到 `src/assets/images/`，并使用相对路径
3. **路径格式**: 使用 `../../assets/images/cover-[slug].jpg` 而非 `/images/xxx.png`

### 改进措施（已更新到 Skill）

- [x] 更新 Skill：添加 "错误 9: 没有使用 Skill 而手动操作"
- [x] 更新 Skill：完善触发词说明（发布文章/发布blog/发布公众号）
- [x] 更新 Skill：添加 skill 位置指引供 AI 参考
- [x] 更新 AGENTS.md：添加 blog-publisher skill 的引用
- [ ] 下次发布前，首先检查 `.agents/skills/` 目录
- [ ] 任何发布操作前，先读取 skill 文档

### 本次新增/更新的 Skill 条目

- [错误 9]: 没有使用 Skill 而手动操作（严重）
- [更新]: 触发词和发现机制完善
- [更新]: AGENTS.md 添加 skill 引用

### 耗时统计

- 发现问题: 5 分钟（用户提醒后才意识到）
- 图片处理: 2 分钟（重新生成到正确位置）
- 文章创建: 3 分钟
- 构建部署: 2 分钟
- WeChat 发布: 1 分钟
- **总计**: 13 分钟

### 关键教训

1. **必须先找 Skill**: 任何发布任务开始前，先检查 `.agents/skills/` 目录
2. **图片路径**: 封面必须放在 `src/assets/images/`，使用相对路径 `../../assets/images/xxx.jpg`
3. **触发词**: 用户说"发布"时，立即激活 blog-publisher skill

### 备注

- 封面图：65KB，压缩质量 85%
- 用户提供了 Jack Dorsey 照片作为封面
- 文章底部补充了福布斯报道和召回新闻链接
