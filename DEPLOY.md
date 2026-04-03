# 独立部署指南

让朋友也能使用这套 Blog + 微信发布系统

---

## 快速开始（5分钟部署）

### 1. Fork 仓库

```bash
# 朋友操作
1. 访问 https://github.com/MushroomDAO/blog
2. 点击右上角 "Fork" 按钮
3. 等待 Fork 完成，进入自己的仓库（如 friend/blog）
```

### 2. 克隆到本地

```bash
git clone https://github.com/friend/blog.git
cd blog
```

### 3. 修改配置

#### 3.1 域名配置 `astro.config.mjs`

```javascript
// 修改第 9 行
site: 'https://blog.friendname.com',  // 换成自己的域名
```

#### 3.2 网站信息 `src/consts.ts`

```typescript
// 修改网站标题和描述
export const SITE_TITLE = 'Friend Blog';  // 你的网站名
export const SITE_DESCRIPTION = '技术分享与探索';  // 你的描述
```

#### 3.3 微信配置 `.env`

```bash
# 创建 .env 文件
cp .env.example .env

# 编辑 .env，填入自己的微信公众号信息
WECHAT_APP_ID=wx_your_app_id_here
WECHAT_APP_SECRET=your_app_secret_here
```

**如何获取微信配置：**
1. 登录 https://mp.weixin.qq.com
2. 设置与开发 → 基本配置
3. 复制 AppID 和 AppSecret
4. 设置 IP 白名单（你的服务器 IP）

### 4. 安装依赖

```bash
# 安装博客依赖
pnpm install

# 安装 M2 微信发布依赖
cd pipeline/m2 && pnpm install && cd ../..
```

### 5. 本地测试

```bash
# 预览
pnpm dev

# 访问 http://localhost:4321 查看效果
```

### 6. 首次发布测试

```bash
# 创建测试文章
echo "测试文章" > /tmp/test.txt

# 发布（P1 Blog + P2 微信）
./publish-fast.sh /tmp/test.txt
```

---

## 绑定自定义域名（Cloudflare）

### 方式 A: Cloudflare Pages（推荐）

```bash
# 1. 安装 Wrangler
npm install -g wrangler

# 2. 登录 Cloudflare
npx wrangler login

# 3. 创建 Pages 项目
npx wrangler pages project create my-blog

# 4. 部署
pnpm build
npx wrangler pages deploy dist

# 5. 绑定域名
# 在 Cloudflare Dashboard → Pages → 自定义域名
# 添加 blog.friendname.com
```

### 方式 B: 手动上传

```bash
# 构建
pnpm build

# dist/ 目录就是静态网站，可以上传到任何托管服务
# - Cloudflare Pages
# - Vercel
# - GitHub Pages
# - 自己的服务器
```

---

## 日常使用

### 发布文章

```bash
# 方式 1: 全自动（文字已润色）
./publish-fast.sh article.txt

# 方式 2: 交互式（需要 AI 润色）
./publish.sh article.txt
```

### 仅发布 Blog（不发布微信）

```bash
./publish-fast.sh article.txt --blog-only
```

### 仅发布微信（已有 Markdown）

```bash
cd pipeline/m2
node index.js ../../src/content/blog/article.md --theme claude
```

---

## 常见问题

### Q1: 微信发布失败，提示 IP 不在白名单

```bash
# 1. 获取你的服务器 IP
curl https://api.ipify.org

# 2. 登录微信公众号后台
# 3. 设置与开发 → 基本配置 → IP白名单
# 4. 添加你的 IP
```

### Q2: 封面图没有显示

```bash
# 确保文章 frontmatter 有 heroImage
# 或运行 publish-fast.sh 自动生成
```

### Q3: 如何修改主题颜色？

```bash
# 微信主题（4种可选）
--theme claude      # 橙色（默认）
--theme chengyun    # 渐变杂志风
--theme blue        # 蓝色商务
--theme sticker     # 贴纸风格
```

### Q4: 能否同时使用多个公众号？

```bash
# 当前不支持，需要修改 .env 切换
# 或复制多份仓库，配置不同的 .env
```

---

## 文件结构

```
blog/
├── .env                    # 微信配置（重要！）
├── astro.config.mjs        # 域名配置
├── src/consts.ts           # 网站标题/描述
├── publish-fast.sh         # 一键发布脚本 ⭐
├── publish.sh              # 交互式发布
├── pipeline/
│   ├── m1/                 # Blog 发布模块
│   └── m2/                 # 微信发布模块
└── src/content/blog/       # 文章目录
```

---

## 升级更新

如果原仓库有更新，同步到自己的 Fork：

```bash
# 添加上游仓库
git remote add upstream https://github.com/MushroomDAO/blog.git

# 拉取更新
git fetch upstream
git merge upstream/main

# 解决冲突后提交
git push origin main
```

---

## 需要帮助？

- 微信配置问题：查看 [微信官方文档](https://developers.weixin.qq.com/doc/offiaccount/Getting_Started/Getting_Started_Guide.html)
- Cloudflare 问题：查看 [Cloudflare Pages 文档](https://developers.cloudflare.com/pages/)
- 本项目问题：在原仓库提 Issue
