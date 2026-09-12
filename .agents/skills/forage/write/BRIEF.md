# 写稿子任务规范（每个写稿子 agent 都必须遵守）

> 由 WRITE-JOB.md 的主流程分发。2026-09-11 那批 9 篇就是按这份规范写的。

仓库：/Users/jason/Dev/mycelium/blog （Astro 双语博客 blog.mushroom.cv，作者署名 Mycelium Protocol）

## 你只做这些
1. 一手源调研（必须通读完整 README / 模型卡，不能只看开头；用 `gh api repos/OWNER/REPO/readme -H "Accept: application/vnd.github.raw"`、`gh repo view`、`gh api repos/OWNER/REPO` 看 star/license/提交时间/目录结构；HF 用 `curl -s https://huggingface.co/api/models/ID` 和 `curl -sL https://huggingface.co/ID/raw/main/README.md`）。能便宜地本机验证的就验证（这台是 Apple Silicon Mac mini；不要下载 >5GB 的东西，不要装全局依赖，临时文件放 radar/scratch/）。需要背景时用 WebSearch/WebFetch 补外部报道，但结论以一手源为准，二手说法要标明来源。
2. 写出最终 markdown：`radar/staging/SLUG.md`（**不要**写进 src/content/blog/——主流程在 build/deploy，半成品会被一起编译上线）
3. 在 `radar/staging/SLUG.json` 写交接信息（格式见下）

## 你绝对不做
不 build、不 deploy、不 git add/commit/push、不跑 pipeline/m2、不生成任何图片、不改其他文章、不改 memory 目录。这些由主会话串行做。

## 文章规范
- SLUG：英文小写连字符，带关键词，4-9 个词；先 `ls src/content/blog | grep` 确认不撞名
- 先读两篇近期文章当风格参考：`src/content/blog/mcp-rag-server-local-rag-claude-code-blueprint.md`、`src/content/blog/krea-2-turbo-open-weight-text-to-image-license-hardware.md`。语气、结构、长度对齐它们：有独立判断和实测/核实，不是 README 翻译；要指出局限、坑、许可证限制、跟同类的区别。
- frontmatter（全部必填）：
```yaml
---
title: "中文标题"
titleEn: "English Title"
description: "中文描述（一句话 BLUF，含关键数字）"
descriptionEn: "English description"
pubDate: "YYYY-MM-DD"   # 写稿当天
updatedDate: "YYYY-MM-DD"
category: "Tech-News"   # 或 Research / Tech-Experiment（有本机实测时）
tags: ["...", "...", "..."]   # ≥3
heroImage: "../../assets/images/SLUG-banner.jpg"
author: "Mycelium Protocol"
---
```
- 结构：中文正文 → 中文版权块 → `<!--EN-->` → 英文正文（完整对应，不是摘要）→ 英文版权块
- 中英开头都要 BLUF；至少一个问句式 H2/H3；超 1000 字要有 FAQ；要有具体数字和一手事实
- **外部链接一律写成纯文本 URL，禁止 `[text](url)`**（公众号会吞掉链接）。文末放「一手源」列表，纯文本 URL。
- 版权块原样用：
  中文（放在 `<!--EN-->` 之前）：
  ```
  ---

  > © 2026 Author: Mycelium Protocol. 本文采用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.zh) 授权——欢迎转载和引用，须注明作者姓名及原文链接，不得去除署名后以原创发布。
  ```
  英文（文末）：
  ```
  ---

  > © 2026 Author: Mycelium Protocol. Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) — free to share and adapt with attribution. You must credit the author and link to the original; removing attribution and republishing as original is not permitted.
  ```
- 正文插图占位：挑 4 个关键认知节点（核心流程/逻辑骨架/前后对比），在中文和英文对应位置各放一行占位 `<!--FIG:01-->` … `<!--FIG:04-->`（中英同编号），独占一行。不要插任何图片语法。
- 不写中文文件名；不编造数字；拿不准的写「README 声称」「据 XX 报道」。
- 如果调研发现一手源根本找不到、或项目是空壳/骗星/纯搬运，**不要硬写**，在交接 JSON 里 `"write": false` 并说明理由。

## 交接 JSON 格式
```json
{
  "write": true,
  "slug": "...",
  "md": "radar/staging/SLUG.md",
  "category": "Tech-News",
  "ip": "mushroom | baobao | avatar",      // 科技工具类=mushroom，大众科普=baobao，思想/社会=avatar
  "banner_prompt": "英文写实摄影场景提示词，无文字、无人脸特写、不出现 logo，40-70 词",
  "figs": {"01": "这张图要画的核心逻辑（中文，一两句）", "02": "...", "03": "...", "04": "..."},
  "memory": "3-6 行要点：一手源、核心发现、关键数字、局限",
  "notes": "你没法确认的点 / 需要主会话留意的问题"
}
```
最后回复主会话时只需一段简短总结 + JSON 路径。
