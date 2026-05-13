# Newsletter 系统调研报告

调研日期：2026-05-13  
决策：使用 **Listmonk**

---

## 调研范围

个人/中小组织场景，目标用户量：数千至数万级订阅者。要求：开源、可自建、有 Web 管理界面、支持定时发送。

---

## 候选方案对比

| 工具 | 语言 | 内存需求 | 数据库 | GitHub ⭐ | 活跃度 | 结论 |
|------|------|---------|--------|---------|-------|------|
| **Listmonk** | Go（单二进制） | 50–150 MB（运行时） | PostgreSQL | 18,936 | ⭐⭐⭐⭐⭐ v6.1.0 @ 2026-03 | ✅ **选用** |
| Keila | Elixir | ~512 MB–1 GB | PostgreSQL | ~2,000 | ⭐⭐⭐ 中等 | 视觉编辑器好，但内存高、社区小 |
| Plunk | TypeScript/Node | ~512 MB | PostgreSQL | 4,827 | ⭐⭐⭐ 中等 | 营销+事务一体，但社区不如 Listmonk |
| phpList | PHP | ~256 MB | MySQL | 低 | ⭐⭐ 老牌过时 | ❌ 不推荐 |
| SendPortal | PHP/Laravel | ~512 MB | MySQL | 低 | ⭐⭐ 低活跃 | ❌ 不推荐 |
| Ghost | Node.js | ~1 GB+ | MySQL | 高 | ⭐⭐⭐⭐ 活跃 | ❌ 太重，完整 CMS，不适合单一 newsletter |

---

## 选 Listmonk 的理由

1. **内存极低**：Go 单二进制，运行时约 50–150 MB，加 PostgreSQL 合计 300–450 MB，512 MB 机器完全可跑
2. **功能完整**：Web 管理界面、模板编辑器、分组/标签、定时发送、点击追踪、退订管理、统计
3. **社区最大**：18,936 GitHub ⭐，文档完善，问题好搜
4. **SMTP 灵活**：可接 Resend、Mailgun、SES 等任意 SMTP，不锁定服务商
5. **维护最积极**：v6.1.0 发布于 2026-03，持续迭代
6. **万级用户零压力**：实测 $5/月 512 MB VPS 可处理数万订阅者

---

## 部署资源需求

| 组件 | 内存占用 |
|------|---------|
| Listmonk 容器 | 50–150 MB |
| PostgreSQL 容器 | 150–300 MB |
| **合计** | **~300–450 MB** |

最低建议：512 MB 可用内存  
Docker 镜像大小：Listmonk ~20 MB

---

## 职责边界

| 角色 | 仓库 | 职责 |
|------|------|------|
| **运营方** | Agent24-Desktop | 部署运行 Listmonk、管理订阅者、发送 newsletter |
| **内容提供方** | mycelium/blog（本仓库） | 产出博客内容，通过 RSS 供 Listmonk 拉取；嵌入订阅入口 |

本仓库**不负责** Listmonk 的部署和运维。详细方案见 `Agent24-Desktop/docs/newsletter-plan.md`。

## 本仓库待办

- [ ] 在博客页面嵌入订阅表单（待 Agent24-Desktop 提供 Listmonk 订阅 API 地址后执行）
- [ ] 保持 `/rss.xml` 准确更新（Listmonk 内容来源）

---

## 参考链接

- [Listmonk 官网](https://listmonk.app)
- [GitHub - knadh/listmonk](https://github.com/knadh/listmonk)
- [安装文档](https://listmonk.app/docs/installation/)
- [内存需求讨论 Issue #584](https://github.com/knadh/listmonk/issues/584)
- [Docker Hub](https://hub.docker.com/r/listmonk/listmonk)
