---
title: "40万首中国古诗词，做成REST+GraphQL API开源了"
titleEn: "400,000 Chinese Classical Poems, Packaged as a REST+GraphQL API"
description: "palemoky 开源了「诗泉」（chinese-poetry-api）：约 40 万首古诗词（唐诗宋词元曲诗经楚辞元曲乐府等），Go 编写，REST + GraphQL 双接口，简繁体切换，IP限速，多架构 Docker 一键部署，端口 1279，有在线演示。GPL-3.0，3.2K stars，数据来自 chinese-poetry/chinese-poetry 子模块，支持按朝代/作者/类型过滤，随机取诗，GraphQL 支持全文/标题/作者三种搜索模式。"
descriptionEn: "palemoky open-sourced chinese-poetry-api (诗泉): ~400,000 classical Chinese poems (Tang, Song, Yuan, Shijing, Chuci, Yuefu and more), written in Go, with REST + GraphQL dual interfaces, simplified/traditional conversion, IP rate limiting, multi-arch Docker, port 1279, and a live demo. GPL-3.0, 3.2K stars. Data comes from the chinese-poetry/chinese-poetry submodule. Supports filtering by dynasty/author/type, random poem retrieval, and GraphQL full-text/title/author search modes."
pubDate: 2026-10-09
heroImage: "../../assets/images/chinese-poetry-api-palemoky-40wan-poems-go-rest-graphql-banner.jpg"
category: "Tech-Experiment"
tags: ["开源工具", "API", "中文", "古诗词", "Go"]
lang: "zh-CN"
wechatTitle: "40万首古诗词：Go写的API开源了"
wechatDigest: "3.2K stars GPL；唐诗宋词元曲；REST+GraphQL；简繁体切换；Docker一键部署"
---

40 万首古诗词，从诗经到清诗，一个 Go 写的 REST + GraphQL API 全打包了。

项目叫「诗泉」，作者 palemoky，GPL-3.0，目前 3.2K stars。数据来自 chinese-poetry/chinese-poetry 这个已有 50K stars 的社区诗词数据集（git 子模块引入）。

GitHub: https://github.com/palemoky/chinese-poetry-api | 在线演示: https://poetry.palemoky.com

---

## 收录规模

| 类型 | 首数 |
|------|------|
| 七言绝句 | 82,744 |
| 七言律诗 | 68,696 |
| 五言律诗 | 59,681 |
| 五言绝句 | 16,860 |
| 宋词 | 21,347 |
| 元曲 | 10,904 |
| 乐府诗 | 6,714 |
| 五代词 | 543 |
| 诗经 | 305 |
| 楚辞 | 65 |
| 论语 | 20 |
| 其余/未分类 | 76,077+ |

总计约 **40 万首**，含作者、朝代、类型标注。

---

## API：REST + GraphQL 双接口

**REST base URL**：`http://<host>:1279/api/v1/`

常用端点：

```
GET /poems                          # 分页列出诗词
GET /poems/search?q=静夜思          # 关键词搜索
GET /poems/random?author=李白&dynasty=唐&type=七言绝句  # 随机取诗（支持过滤）
GET /authors                        # 作者列表
GET /dynasties                      # 朝代列表
GET /types                          # 类型列表
```

**GraphQL** 路径：`/graphql`

支持三种搜索模式（`searchType` 参数）：

```graphql
query {
  searchPoems(query: "春眠", searchType: all) {
    title
    author
    content
  }
  statistics {
    total
    byDynasty { name count }
  }
}
```

`searchType` 可选：`TITLE`（标题）、`content`（全文）、`author`（作者）、`all`（全字段）。

---

## 简繁体切换

请求时带 `lang` 参数：

- `zh-Hans`：简体中文（默认）
- `zh-Hant`：繁体中文

转换由 [gocc](https://github.com/liuzl/gocc) 完成，benchmark 约 300 ns/op，对 API 响应延迟影响可以忽略。

---

## 本地部署

Docker 一行起：

```bash
docker run -d -p 1279:1279 palemoky/chinese-poetry-api:latest
```

镜像支持 `linux/amd64` 和 `linux/arm64`（Apple Silicon 可直接跑）。默认端口 1279（取"诗"的部分谐音？），也可以通过 compose 改映射。

也可以直接 clone 源码编译：

```bash
git clone --recurse-submodules https://github.com/palemoky/chinese-poetry-api
cd chinese-poetry-api
go build .
./chinese-poetry-api
```

`--recurse-submodules` 必须带，数据在子模块里，不带拉不到诗词数据。

---

## 限速和边界

- **IP 限速**：内置，具体阈值文档未标注，生产用建议在前面挂反代加额外限速
- **只读**：纯查询 API，没有写入接口
- **无认证**：本地或内网部署不需要 API key；公网暴露需自己加认证层
- **LICENSE**：GPL-3.0——商用嵌入需注意，内容展示类用途（网站、App）要评估是否触发 copyleft

---

## 数据来源的溯源

诗词数据引用自 [chinese-poetry/chinese-poetry](https://github.com/chinese-poetry/chinese-poetry)（50.2K stars，CC 协议，已整理超 80 万首），这个数据集本身也是社区多年维护的成果，诗泉在它上面建了查询层。

---

## 一句话说清楚

chinese-poetry-api 是一个 Go 写的古诗词查询服务：40 万首，REST + GraphQL 双接口，简繁体切换，Docker 多架构支持，GPL-3.0。在线试用：https://poetry.palemoky.com

---

> GPL-3.0。palemoky，2025-12-08 创建，数据源：chinese-poetry/chinese-poetry。开源仅供学习参考。

---

<!--EN-->

## 400,000 Chinese Classical Poems, Packaged as a REST+GraphQL API

400,000 classical Chinese poems — from Shijing to Qing dynasty verse — wrapped in a Go-written REST + GraphQL API.

The project is called Shiquan (诗泉, "Poetry Spring"), by palemoky. GPL-3.0, 3.2K stars. Poem data comes from the chinese-poetry/chinese-poetry community dataset (50K+ stars), brought in as a git submodule.

GitHub: https://github.com/palemoky/chinese-poetry-api | Live demo: https://poetry.palemoky.com

---

### Collection Size

| Type | Count |
|------|-------|
| 7-character jueju | 82,744 |
| 7-character lüshi | 68,696 |
| 5-character lüshi | 59,681 |
| 5-character jueju | 16,860 |
| Song ci | 21,347 |
| Yuan qu | 10,904 |
| Yuefu | 6,714 |
| Five Dynasties ci | 543 |
| Shijing | 305 |
| Chuci | 65 |
| Analects (Lunyu) | 20 |
| Other/unclassified | 76,077+ |

Total: approximately **400,000 poems**, with author, dynasty, and type annotations.

---

### API: REST + GraphQL Dual Interface

**REST base URL**: `http://<host>:1279/api/v1/`

Common endpoints:

```
GET /poems                          # paginated listing
GET /poems/search?q=静夜思          # keyword search
GET /poems/random?author=李白&dynasty=唐&type=七言绝句  # random poem (with filters)
GET /authors                        # author list
GET /dynasties                      # dynasty list
GET /types                          # type list
```

**GraphQL** path: `/graphql`

Three search modes via `searchType`:

```graphql
query {
  searchPoems(query: "spring", searchType: all) {
    title
    author
    content
  }
  statistics {
    total
    byDynasty { name count }
  }
}
```

`searchType` options: `TITLE`, `content`, `author`, `all`.

---

### Simplified/Traditional Conversion

Pass a `lang` parameter:

- `zh-Hans`: Simplified Chinese (default)
- `zh-Hant`: Traditional Chinese

Conversion uses [gocc](https://github.com/liuzl/gocc), benchmarked at ~300 ns/op — negligible API latency impact.

---

### Local Deployment

One-line Docker start:

```bash
docker run -d -p 1279:1279 palemoky/chinese-poetry-api:latest
```

Multi-arch image: `linux/amd64` and `linux/arm64` (Apple Silicon works natively).

Or build from source:

```bash
git clone --recurse-submodules https://github.com/palemoky/chinese-poetry-api
cd chinese-poetry-api
go build .
./chinese-poetry-api
```

`--recurse-submodules` is required — poem data lives in the submodule.

---

### Limits and Boundaries

- **IP rate limiting**: built-in; specific thresholds undocumented — add a reverse proxy for production
- **Read-only**: query-only API, no write endpoints
- **No authentication**: no API key needed for local/internal use; add an auth layer before public exposure
- **GPL-3.0**: commercial embedding requires evaluation; display-only use cases (websites, apps) should assess copyleft implications

---

### TL;DR

chinese-poetry-api is a Go-based classical Chinese poetry query service: 400,000 poems, REST + GraphQL, simplified/traditional conversion, multi-arch Docker, GPL-3.0. Try it: https://poetry.palemoky.com

---

> GPL-3.0. palemoky, created 2025-12-08. Data source: chinese-poetry/chinese-poetry. For reference only.
