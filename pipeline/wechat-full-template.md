# WeChat 完整文章模板（m2 路径）

## 结构说明

m2 渲染器自动生成 header watermark + 免责声明 + 底部品牌卡。文章 markdown 只需提供正文内容，底部加简洁的 Mycelium Protocol 介绍即可。

每篇公众号文章的 blog MD 应包含以下区块：

---

## blog MD 标准结构（供 m2/index.js 渲染）

```markdown
---
title: "文章标题"
titleEn: "slug"
description: "描述"
descriptionEn: "EN description"
pubDate: "2026-xx-xx"
updatedDate: "2026-xx-xx"
category: "Tech-News"
tags: ["tag1", "tag2", ...]
heroImage: "../../assets/banner-ai-new-intelligence.jpg"
---

*by Mycelium Protocol*

---

[正文内容]

---

*Mycelium Protocol — 追踪 AI 系统的底层演化*

---

> **关于 Mycelium**
>
> 菌丝协议。持续追踪 AI 工具、系统和实验的内容节点。

---

<!--EN-->

## English Title

*by Mycelium Protocol*

[EN content]

---

*Mycelium Protocol — tracking the deep evolution of AI systems*

© 2026 Mycelium Protocol. All rights reserved.
```

---

## 渲染器自动追加的内容（无需手动写）

m2/renderer/wechat-renderer.js 自动在文章前后追加：

**前置（headerWatermark）**：
```html
🍄 原文发布于 blog.mushroom.cv
```

**后置（disclaimer）**：
```
关于本号 · 免责声明
🍄 Mushroom Research Blog 是非营利、免费公开的个人科技观察博客与公众号 XStack18...
```

**底部品牌卡（footerBanner）**：
```html
🍄 Mycelium Protocol
数字公共物品 · 开源免费无许可
🎵 表达者 | 🎨 创造者 | 🔨 建设者
🪵 Infras | 🦠 Protocols | 🕸️ Networks
📍 blog.mushroom.cv · Apache 2.0
```

---

## 发布流程

1. 写 blog article MD（含上述 frontmatter + 中英双语正文）
2. 运行：`bash scripts/publish-blog.sh src/content/blog/<slug>.md` 部署到 blog
3. 运行：`cd pipeline/m2 && node index.js "../../src/content/blog/<slug>.md"` 推微信草稿

---

## 底部品牌卡 HTML（当前 m2 渲染器版本）

```html
<div style="margin-top:40px;padding:24px;background:linear-gradient(135deg,#10b981 0%,#34d399 100%);border-radius:12px;text-align:center;color:#fff;">
  <div style="font-size:24px;margin-bottom:8px;">🍄</div>
  <div style="font-size:16px;font-weight:bold;margin-bottom:4px;">Mycelium Protocol</div>
  <div style="font-size:12px;opacity:0.85;margin-bottom:10px;">数字公共物品 · 开源免费无许可</div>
  <div style="font-size:13px;opacity:0.95;line-height:1.6;">
    <span style="margin:0 4px;">🎵 表达者</span> | <span style="margin:0 4px;">🎨 创造者</span> | <span style="margin:0 4px;">🔨 建设者</span>
  </div>
  <div style="margin-top:8px;font-size:12px;opacity:0.85;">
    <span style="margin:0 4px;">🪵 Infras</span> | <span style="margin:0 4px;">🦠 Protocols</span> | <span style="margin:0 4px;">🕸️ Networks</span>
  </div>
  <div style="margin-top:12px;padding-top:12px;border-top:1px solid rgba(255,255,255,0.3);font-size:12px;opacity:0.9;">
    📍 blog.mushroom.cv · Apache 2.0
  </div>
</div>
```

> **已移除**: GToken、USDC、Gnosis Safe、链上全透明、多签治理等 token/governance 相关描述。
> 品牌表达聚焦于"数字公共物品 · 开源免费无许可"和三类角色定位。
