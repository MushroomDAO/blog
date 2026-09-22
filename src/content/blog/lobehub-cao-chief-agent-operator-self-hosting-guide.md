---
title: "LobeHub 自架 CAO 指南：82K⭐从 Lobe Chat 变成首席 Agent 运营官，像雇员工一样管理 AI 团队"
titleEn: "Self-Hosting LobeHub CAO: 82K⭐ From Lobe Chat to Chief Agent Operator — Manage Your AI Team Like Employees"
description: "lobehub/lobe-chat，82,706 stars，LobeHub 社区许可证。从聊天 UI 转型为 CAO（首席 Agent 运营官），334,081 个 Skill 和 100,897 个 MCP 服务器可按需调用。核心架构：Next.js + PostgreSQL 14+ PGVector + RustFS S3 + Agent Gateway（8787端口）。Docker Compose 一键部署，IM Gateway 让 Agent 通过 Slack/Discord/Telegram/微信汇报工作结果。本文为完整工程部署指南：最小配置、环境变量、数据库和存储选型、多 Agent 编排原语。"
descriptionEn: "lobehub/lobe-chat — 82,706 stars, LobeHub Community License. Evolved from chat UI to CAO (Chief Agent Operator): 334,081+ skills and 100,897+ MCP servers available on demand. Core architecture: Next.js + PostgreSQL 14+ PGVector + RustFS S3 + Agent Gateway (port 8787). Docker Compose one-command deploy; IM Gateway lets agents report results via Slack/Discord/Telegram/WeChat. This article is a complete engineering deployment guide: minimum config, environment variables, database and storage choices, multi-agent orchestration primitives."
pubDate: 2026-09-22
heroImage: "../../assets/images/lobehub-cao-chief-agent-operator-self-hosting-guide-banner.jpg"
category: "Tech-Experiment"
tags: ["ai-agent", "self-hosting", "docker", "multi-agent", "open-source", "lobehub", "mcp"]
lang: zh-CN
---

`lobehub/lobe-chat` 是目前 stars 最多的开源 AI 界面项目之一（82,706 stars），但它已经不只是"Lobe Chat"了。

2026 年中以后，LobeHub 做了一次产品定位的重写：从"一个漂亮的 ChatGPT 替代 UI"变成了 **CAO——Chief Agent Operator（首席 Agent 运营官）**。核心叙事从"你和 AI 聊天"变成了"你指挥一支 24/7 运转的 AI 员工团队"。

**GitHub**：github.com/lobehub/lobe-chat | **Stars**：82,706 | **⚠️ License**：LobeHub 社区许可证（非 MIT/Apache）| **文档**：lobehub.com/docs

---

## 定位变了什么

**Lobe Chat 时代**：一个支持多模型的聊天前端，有插件市场、Agent 模板、多模型切换。对标 ChatGPT 的 UI 层。

**CAO 时代**：重新定义了主角关系——你是 CAO，AI 是你的直属团队。你的工作不是"和 AI 聊天"，而是：

- 招募 Agent（从 334,081 个 Skill 里挑）
- 给 Agent 分配任务（工作区 + 项目 + 日程）
- Agent 在后台并行执行
- 结果通过 Slack / Discord / Telegram / 微信汇报给你

他们记录的真实案例：同时部署 50 个 Agent 处理一个有 500 个 Issue 的仓库扫描任务，一次性完成，结果发到 Telegram。

---

## 核心新基础设施

CAO 时代新增的架构组件：

```
用户
 ↓ 微信/Slack/Discord/Telegram
IM Gateway  ←→  Agent Gateway（8787）
                     ↓
         多 Agent 并行执行层
         ├── Agent A（工具调用）
         ├── Agent B（内容生成）
         └── Agent C（审核验证）
                     ↓
         Device Gateway（8788）
         PostgreSQL PGVector
         RustFS（S3兼容存储）
```

| 新组件 | 端口 | 作用 |
|--------|------|------|
| Agent Gateway | 8787 | Agent 间路由、状态维护、任务编排 |
| Device Gateway | 8788 | 设备侧接入 |
| IM Gateway | — | 汇报结果到 Slack/Discord/Telegram/微信 |
| Agent Dashboard | — | 所有 Agent 的工作状态总览、token 成本统计 |

---

## 最小硬件配置

| 资源 | 最低 | 生产推荐 |
|------|------|---------|
| CPU | 2 核 | 4 核+ |
| 内存 | 4 GB | 8 GB+ |
| 磁盘 | 20 GB | 50 GB+ |
| OS | Linux（推荐）| 也支持 macOS；Windows 需 WSL 2 |

---

## 一键部署（Docker Compose）

```bash
mkdir lobehub && cd lobehub
bash <(curl -fsSL https://lobe.li/setup.sh) -l en
```

安装脚本会引导你选择部署模式：
- **Local**（localhost 访问，本地测试）
- **Port**（局域网 HTTP 访问）
- **Domain**（HTTPS + 反代，生产环境）

```bash
# 启动所有服务
docker compose up -d

# 查看日志
docker compose logs -f lobehub

# 更新到最新版
docker compose pull && docker compose up -d
```

需要开放的端口：

| 端口 | 服务 |
|------|------|
| 3210 | 主应用 |
| 9000 / 9001 | RustFS 文件存储 |
| 8787 | Agent Gateway |
| 8788 | Device Gateway |

---

## 核心环境变量

### 应用基本配置

```bash
# 对外访问地址（浏览器用）
APP_URL=https://your-domain.com

# Docker 内部服务互相调用地址（不能和 APP_URL 一样）
INTERNAL_APP_URL=http://lobehub:3210

# 凭据加密密钥（存储 API Key 等敏感信息时用）
KEY_VAULTS_SECRET=$(openssl rand -base64 32)
```

### 数据库（PostgreSQL 14+ + PGVector）

```bash
DATABASE_URL=postgresql://postgres:yourpassword@postgresql:5432/lobechat
POSTGRES_PASSWORD=yourpassword
LOBE_DB_NAME=lobechat
```

**PGVector 是必须的**，没有它向量搜索和 Agent 记忆功能不工作。托管选项：Neon、Supabase、Railway，本地 Docker Compose 已内置 PostgreSQL + PGVector。

### 文件存储（S3 兼容）

默认使用 **RustFS**（LobeHub 自己做的 MinIO 替代品，已内置在 compose 里）：

```bash
S3_ACCESS_KEY_ID=your-access-key
S3_SECRET_ACCESS_KEY=your-secret-key
S3_ENDPOINT=https://your-domain.com:9000    # 浏览器访问的地址
S3_INTERNAL_ENDPOINT=http://rustfs:9000     # 服务端内部访问地址
S3_BUCKET=lobechat
S3_ENABLE_PATH_STYLE=1                       # MinIO/自托管必须设 1
S3_SET_ACL=1                                 # 允许公开读（预览图片用）
```

换成 AWS S3 或 Cloudflare R2，把 `S3_ENDPOINT` 改成对应 endpoint，删掉 `S3_INTERNAL_ENDPOINT`。

### Auth（Better Auth）

```bash
# 主密钥
AUTH_SECRET=$(openssl rand -base64 32)

# RSA 密钥对（JWKS 格式，Agent Gateway 需要）
# 用官方命令生成：
# docker run --rm --entrypoint /bin/node lobehub/lobehub -e '...'
JWKS_KEY='{"keys":[...]}'           # 私钥（完整 JWKS）
JWKS_PUBLIC_KEY='{"keys":[...]}'    # 公钥（Agent Gateway 用）

# OAuth 提供商（可多选）
AUTH_SSO_PROVIDERS=google,github,microsoft,feishu,wechat

# 限制注册邮箱域名（可选）
AUTH_ALLOWED_EMAILS=@yourcompany.com
```

### Agent Gateway（多 Agent 编排核心）

```bash
ENABLE_AGENT_GATEWAY=1
AGENT_GATEWAY_URL=http://agent-gateway:8787
GATEWAY_SERVICE_TOKEN=$(openssl rand -hex 32)
```

**注意**：Agent Gateway 把运行中的 Agent 状态存在内存里，重启会中断所有进行中的任务。生产环境需要规划维护窗口。

### LLM 提供商

```bash
# 按需填写，支持所有主流提供商
OPENAI_API_KEY=sk-xxx
ANTHROPIC_API_KEY=sk-ant-xxx
GOOGLE_API_KEY=xxx

# 本地 Ollama
OPENAI_PROXY_URL=http://host.docker.internal:11434/v1
OPENAI_MODEL_LIST=-all,+ollama/qwen3:latest

# 系统默认模型
SYSTEM_AGENT=default=claude-sonnet-4-5
```

---

## 数据库 + 存储备份

```bash
# PostgreSQL 备份
docker compose exec postgresql pg_dump -U postgres lobechat > backup_$(date +%Y%m%d).sql

# PostgreSQL 恢复
docker compose exec -T postgresql psql -U postgres lobechat < backup_20260922.sql

# 文件存储备份
docker compose exec rustfs tar czf /tmp/storage_backup.tar.gz /data
docker compose cp rustfs:/tmp/storage_backup.tar.gz ./storage_backup.tar.gz
```

---

## 多 Agent 编排：三个核心原语

### 1. Agent Groups（并行执行）

把多个 Agent 分配到同一个 Group，它们并行执行同一个任务的不同子任务，或迭代处理同一个任务。

典型用法：
- Group A：内容采集 Agent + 内容验证 Agent + 内容格式化 Agent
- 三个 Agent 并行跑，结果在 Group 里汇总

### 2. Context Forwarding（上下文转交）

一个 Agent 完成任务后，把它的输出上下文直接转交给另一个 Agent 作为输入。这是构建处理链的基本机制。

```
Agent 1（研究）→ [转交上下文] → Agent 2（写作）→ [转交] → Agent 3（审核）
```

### 3. IM Gateway（结果汇报）

Agent 执行完毕后，结果不需要你盯着界面——会直接发到你指定的 IM 频道：

| 渠道 | 状态 |
|------|------|
| Slack | ✅ 支持 |
| Discord | ✅ 支持 |
| Telegram | ✅ 支持 |
| 微信（企业微信） | ✅ 支持（付费版） |

这是 CAO 定位的核心交互模型：早上分配任务，晚上收结果，全程不需要留在界面上。

---

## ⚠️ 许可证：不是 MIT

使用前必须确认：LobeHub 使用的是**自己的社区许可证（LobeHub Community License）**，不是标准的 MIT 或 Apache 2.0。

- 个人使用和内部使用：免费
- 商业 SaaS 化（向第三方提供基于 LobeHub 的服务）：需要付费授权
- 详情：lobehub.com/pricing

---

## Agent 市场：334,081 个 Skill

从官方 Store（lobehub.com）可以"雇佣"现成的 Agent，涵盖：编程助手、营销文案、数据分析师、法律顾问等各类角色。

```bash
# 指向自定义/私有 Agent 商店
AGENTS_INDEX_URL=https://your-internal-agents-store.com/index.json

# 指向自定义插件商店
PLUGINS_INDEX_URL=https://your-internal-plugins-store.com/index.json
```

官方 Agent 仓库（可提交自制 Agent）：github.com/lobehub/lobe-chat-agents

---

## 与竞品的关键差异

| 维度 | LobeHub | Open WebUI | Jan.ai |
|------|---------|-----------|--------|
| 定位 | 多 Agent 云编排 | 本地 LLM 界面 | 本地桌面应用 |
| Agent 并发 | 支持 50+ 并行 | 无多 Agent | 无多 Agent |
| MCP 生态 | 100,897 个 MCP 服务器 | 逐步接入 | 有限 |
| IM 汇报 | Slack/Discord/Telegram/微信 | 无 | 无 |
| 存储层 | PGVector + 自研 RustFS | SQLite / PG | 本地文件 |
| 许可证 | 社区许可证 | MIT | MIT |

LobeHub 独有的、竞品没有复刻的：**Agent Gateway + IM 汇报闭环**。这是让 Agent 真正变成"员工"而不是"聊天对象"的关键基础设施。

---

## 不足之处

**1. Agent Gateway 状态在内存中**：重启会中断所有进行中的 Agent 任务，生产环境需要规划维护窗口。

**2. LobeHub 社区许可证不等于 MIT**：商业化使用前必须确认付费计划，不适合直接拿去做 SaaS 二次销售。

**3. 基础设施重**：PostgreSQL + PGVector + RustFS + Agent Gateway + Device Gateway，全跑起来至少需要 8GB 内存。比 Open WebUI/Jan.ai 重很多。

**4. 中文文档覆盖不均匀**：高级功能（IM Gateway、Agent Gateway 配置）文档还不够全，社区讨论偏向 GitHub Issue。

**5. 项目演进速度快**：每周多个版本，env var 可能随版本变动，建议部署前对照最新文档。

---

## 完整启动 checklist

```bash
# 1. 生成密钥
AUTH_SECRET=$(openssl rand -base64 32)
KEY_VAULTS_SECRET=$(openssl rand -base64 32)
GATEWAY_SERVICE_TOKEN=$(openssl rand -hex 32)

# 2. 生成 JWKS 密钥对（见官方文档命令）

# 3. 克隆/下载 compose 文件
bash <(curl -fsSL https://lobe.li/setup.sh) -l en

# 4. 填写 .env 文件（必填项）
# APP_URL, DATABASE_URL, AUTH_SECRET, KEY_VAULTS_SECRET
# S3_* 变量（RustFS 默认已内置，只需配 ACCESS_KEY）
# 至少一个 LLM 提供商的 API Key

# 5. 启动
docker compose up -d

# 6. 检查健康
curl http://localhost:3210/api/health

# 7. 配置 IM Gateway（可选但推荐）
# 在设置界面填写 Telegram/Slack Bot Token
```

> 代码遵循 LobeHub 社区许可证，商业用途请阅读 lobehub.com/pricing，仅供学习研究参考。

---

<!--EN-->

## Self-Hosting LobeHub CAO: From Lobe Chat to Chief Agent Operator

`lobehub/lobe-chat` (82,706 stars) has repositioned itself from a polished ChatGPT-alternative UI to **CAO — Chief Agent Operator**: a platform for managing AI agents as employees, with 334,081+ skills and 100,897+ MCP servers available.

**GitHub**: github.com/lobehub/lobe-chat | **Stars**: 82,706 | **⚠️ License**: LobeHub Community License (not MIT) | **Docs**: lobehub.com/docs

---

### What Changed

**Before (Lobe Chat)**: A multi-model chat frontend with plugins, agent templates, and model switching.

**Now (CAO)**: The relationship is reframed — you're the CAO, AI agents are your direct reports. You assign tasks; agents execute in parallel; results arrive in your Slack/Telegram/WeChat. Documented real-world use case: 50 agents simultaneously processing a 500-issue repository sweep.

---

### New Infrastructure (CAO Era)

| Component | Port | Purpose |
|-----------|------|---------|
| Agent Gateway | 8787 | Agent-to-agent routing, state, orchestration |
| Device Gateway | 8788 | Device-side access |
| IM Gateway | — | Report results to Slack/Discord/Telegram/WeChat |
| Agent Dashboard | — | Work status and token cost per agent |

---

### Minimum Hardware

| Resource | Minimum | Production |
|----------|---------|------------|
| CPU | 2 cores | 4+ cores |
| RAM | 4 GB | 8+ GB |
| Disk | 20 GB | 50+ GB |
| OS | Linux recommended | macOS OK; Windows needs WSL 2 |

---

### Quick Deploy

```bash
mkdir lobehub && cd lobehub
bash <(curl -fsSL https://lobe.li/setup.sh) -l en
docker compose up -d
```

Open ports: 3210 (app), 9000/9001 (RustFS storage), 8787 (Agent Gateway), 8788 (Device Gateway).

---

### Critical Environment Variables

```bash
# Core
APP_URL=https://your-domain.com
INTERNAL_APP_URL=http://lobehub:3210          # Server-side self-calls; must differ from APP_URL
KEY_VAULTS_SECRET=$(openssl rand -base64 32)  # Encrypts stored API keys

# Database (PostgreSQL 14+ with PGVector required)
DATABASE_URL=postgresql://postgres:pass@postgresql:5432/lobechat
POSTGRES_PASSWORD=yourpassword

# Storage (RustFS bundled by default)
S3_ACCESS_KEY_ID=your-key
S3_SECRET_ACCESS_KEY=your-secret
S3_ENDPOINT=https://your-domain.com:9000
S3_INTERNAL_ENDPOINT=http://rustfs:9000
S3_BUCKET=lobechat
S3_ENABLE_PATH_STYLE=1                        # Required for self-hosted S3

# Auth (Better Auth, not NextAuth)
AUTH_SECRET=$(openssl rand -base64 32)
AUTH_SSO_PROVIDERS=google,github,microsoft

# Agent Gateway
ENABLE_AGENT_GATEWAY=1
AGENT_GATEWAY_URL=http://agent-gateway:8787
GATEWAY_SERVICE_TOKEN=$(openssl rand -hex 32)

# LLM providers
ANTHROPIC_API_KEY=sk-ant-xxx
OPENAI_API_KEY=sk-xxx
SYSTEM_AGENT=default=claude-sonnet-4-5        # Default model for system agents
```

**JWKS key pair** (required for Agent Gateway): generate with the Docker command in the official docs.

---

### Three Multi-Agent Orchestration Primitives

**Agent Groups**: Multiple agents assigned to a group execute in parallel or iterate on the same task.

**Context Forwarding**: Explicit handoff — one agent's output context forwarded as another agent's input. Enables delegation chains: Research → Write → Review.

**IM Gateway**: Results delivered to your messaging app without staying in the UI. Slack, Discord, Telegram (free tier), WeChat (paid tier).

**Production caveat**: Agent Gateway holds in-flight agent state in memory — restarts interrupt running tasks. Plan maintenance windows.

---

### ⚠️ License: LobeHub Community License ≠ MIT

- Personal and internal use: free
- Commercial SaaS (serving third parties with a LobeHub-based product): requires paid license
- Details: lobehub.com/pricing

---

### Backup

```bash
# Database
docker compose exec postgresql pg_dump -U postgres lobechat > backup_$(date +%Y%m%d).sql

# File storage
docker compose exec rustfs tar czf /tmp/storage_backup.tar.gz /data
docker compose cp rustfs:/tmp/storage_backup.tar.gz ./storage_backup.tar.gz
```

---

### Limitations

1. **Agent Gateway state in memory**: Restarts kill in-progress tasks.
2. **Community license, not MIT**: Commercial SaaS use requires payment.
3. **Heavy infra**: PostgreSQL + PGVector + RustFS + two gateways — 8+ GB RAM needed.
4. **Rapid release cadence**: Env vars change across versions; verify against latest docs before deploying.
5. **Advanced docs incomplete**: IM Gateway and Agent Gateway configuration documentation is still thin.

---

### Bottom Line

LobeHub's differentiator is the Agent Gateway + IM reporting loop — agents operate autonomously and report results to your messaging app, not to a UI you must keep open. No other major open-source alternative has replicated this at the same scale (334K+ skills, 100K+ MCP servers, 50-agent parallel execution tested).

If you want a chat UI, Open WebUI is lighter. If you want an AI team that reports to Slack while you're away, LobeHub CAO is the current benchmark.

> LobeHub Community License. Commercial SaaS use requires authorization — see lobehub.com/pricing. For learning and research only.
