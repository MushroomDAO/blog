# M2: WeChat Publisher

Markdown → WeChat HTML → 微信公众号草稿

## 使用方式

```bash
cd pipeline/m2

# 基本用法
node index.js ../../src/content/blog/article.md

# 指定主题
node index.js article.md --theme blue

# 指定作者
node index.js article.md --author "Your Name"
```

## 主题列表

| 主题 | 名称 | 特点 |
|------|------|------|
| claude | Claude | 橙色边框，简约 |
| chengyun | 橙韵 | 渐变橙，杂志风 |
| blue | 蓝色专业 | 深蓝，商务风 |
| sticker | 贴纸 | 活泼，卡通 |

## 流程

1. 读取 Markdown
2. 解析 frontmatter
3. 渲染为微信兼容 HTML
4. 上传封面图到微信 CDN
5. 调用 draft/add 发布草稿

## 依赖

```bash
pnpm install
```

## 配置

确保 `.env` 包含：

```
WECHAT_APP_ID=your_app_id
WECHAT_APP_SECRET=your_app_secret
```
