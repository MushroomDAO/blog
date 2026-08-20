# Phase 0A 评测查询集

> 24 条查询，覆盖技术名词 / 自然语言问题 / 宽泛探索 / 跨语言 / 英文对照组 / 负样本。
> 用于跑通 T1.1.3 的 `/search` 页面（Pagefind 关键词检索），记录 Recall@5 基线，
> 作为 T1.2.1（离线向量对比实验）判断"语义检索是否真的比关键词好"的基准。
> 记录日期：2026-08-21

## 技术名词（6 条）

1. Pagefind
2. Cloudflare Vectorize
3. MCP Model Context Protocol
4. LoRA 训练
5. Claude Code Skill
6. WebGPU

## 自然语言问题（4 条）

7. 我想本地部署一个 AI 视频编辑工具
8. 怎么给 Claude Code 装技能包
9. local-first sync AI agent
10. 有没有讲 Agent 循环设计的文章

## 宽泛探索（3 条）

11. 脑仿真 大脑连接组（跨语言，见下）
12. AI Agent 记忆系统
13. 浏览器自动化 Agent

## 跨语言 / 中英对照组（7 条，成对设计）

- 14. MLX Apple Silicon guide（英文技术名词）
- 15. 递归自我改进 RSI（中文自然语言）↔ 16. recursive self improvement（英文对照）
- 17. 3D 可视化工具（中文宽泛）
- 18. terminal AI coding tool（英文技术名词）
- 19. 微信机器人远程控制 Claude Code（中文自然语言）
- 20. open source video editing agent（英文对照，对应第 7 条中文提问的同一主题）

## 负样本（4 条，博客里不该有对应内容）

21. 菜谱 家常菜做法
22. 报税指南 个人所得税
23. 育儿经验分享
24. Kubernetes 集群运维
