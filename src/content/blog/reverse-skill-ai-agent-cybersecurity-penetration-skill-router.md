---
title: "reverse-skill：给 AI Agent 装上逆向工程与渗透测试的神经系统"
titleEn: "reverse-skill: A Nervous System for Reverse Engineering and Penetration Testing Inside AI Agents"
description: "zhaoxuya520 开源的 AI Agent 安全技能路由包，20.9k stars，MIT License。解决 AI Agent 做安全分析时不知道用哪个工具的核心痛点——41条路由规则自动识别任务类型（APK/ELF/JS/PCAP/CTF），按需自举 jadx/Frida/Ghidra/BurpSuite 等工具链，自动沉淀经验到知识库。支持 Claude Code、Codex、Cursor、Kiro、Cline。"
descriptionEn: "zhaoxuya520's open-source AI agent cybersecurity skill router, 20.9k stars, MIT. Solves the core problem of agents not knowing which security tool to use — 41 routing rules auto-classify task type (APK/ELF/JS/PCAP/CTF), bootstrap jadx/Frida/Ghidra/BurpSuite on demand, and auto-distill experience into a knowledge base. Supports Claude Code, Codex, Cursor, Kiro, Cline."
pubDate: "2026-08-08"
updatedDate: "2026-08-08"
category: "Tech-News"
tags: ["安全技能", "AI渗透测试", "逆向工程", "Claude Code技能", "Agent路由", "网络安全", "Mycelium"]
heroImage: "../../assets/images/reverse-skill-ai-agent-cybersecurity-penetration-skill-router-banner.jpg"
---

*by Mycelium Protocol*

---

让 AI Agent 做安全分析，有一个绕不过的问题：Agent 不知道对着一个 APK 应该用 jadx 还是 apktool，不知道对着一个 ELF 应该用 radare2 还是 Ghidra，不知道遇到 JS 混淆应该上 de4js 还是 AST 分析。每次都要靠提示词碰运气，没有可复用的方法论。

reverse-skill 给这个问题提供了一套系统性的解法。

GitHub: https://github.com/zhaoxuya520/reverse-skill | ⭐ 20,925 | MIT License

---

## 核心机制

### 路由系统：41条规则，不猜工具

```
用户任务
  → RULES.md
  → MASTER-ROUTING / master-route.ps1
  → case-init / scope.md（授权确认 + 网络画像，未就绪前不执行）
  → 场景技能 → 工具 / MCP / 脚本
  → 时间线 + 证据→发现→路径 → 报告 + 现场日志
```

路由核心由一份结构化配置驱动，163个回归案例做 CI 验证，Windows + Ubuntu 双平台通过。

| 核心数字 | 数值 |
|---------|------|
| 路由规则 | 41 条（R0–R40）|
| 回归测试用例 | 163 个 |
| 核心技能模块 | 42 个 |
| 支持客户端 | Claude Code / Codex / Cursor / Kiro / Cline |

### 覆盖的安全场景

- **Android APK**：jadx / apktool 反编译 → Smali 分析 → Frida hook
- **ELF / 二进制**：radare2 / Ghidra / IDA Pro 静态分析 → 动态调试
- **前端 JS 加密**：混淆还原 → AST 分析 → 协议逆向
- **网络 PCAP**：流量解密 → 协议还原 → 异常提取
- **CTF**：题型识别 → 工具链匹配 → 解题路径规划
- **授权渗透**：scope 确认 → 网络画像 → 漏洞利用链

---

## 安装与使用

```bash
git clone https://github.com/zhaoxuya520/reverse-skill.git
```

刷新工具索引（让路由系统知道本机装了哪些工具）：

| 平台 | 命令 |
|------|------|
| Windows | `powershell -File skills/scripts/refresh-tool-index.ps1` |
| Linux / macOS | `bash skills/scripts/refresh-tool-index.sh` |
| Kali Linux | `bash kali/scripts/refresh-tool-index.sh` |

执行后查看 `skills/tool-index.md` 确认工具检测结果。

**对接 AI Agent**：

```bash
# Claude Code
claude --add-dir /path/to/reverse-skill

# 或让 Agent 读取并自动配置
# 按照 README_AI.md 的说明，Agent 会自己完成环境引导
```

---

## 自进化知识库

每次安全任务完成后，reverse-skill 会把有价值的发现（工具组合、绕过手法、常见坑）沉淀回知识库，下次遇到类似任务时路由命中更准、工具准备更快。这是「AI Agent 自进化」在垂直安全场景的具体落地：经验不靠人工维护，靠 Agent 自动提炼。

---

## 先决条件

- **Java / JDK**：jadx 和 apktool 依赖
- **Node.js 22.12+**：JS 工具链和 MCP 服务器
- **Python 3.x**：Frida 和辅助脚本
- **兼容的 AI 客户端**：Claude Code / Codex / Cursor / Kiro / Cline 之一

---

## 适用范围说明

reverse-skill 设计用于**已获授权的安全研究**场景：合规渗透测试、CTF 竞赛、漏洞赏金计划、安全工具研究。所有路由规则均包含授权确认步骤（`scope.md`），未确认目标授权前不会执行攻击性操作。

---

*Mycelium Protocol — 追踪 AI 系统的底层演化*

---

> **关于 Mycelium**
>
> 菌丝协议。持续追踪 AI 工具、系统和实验的内容节点。

---

<!--EN-->

## reverse-skill: A Routing System That Gives AI Agents a Nervous System for Cybersecurity

*by Mycelium Protocol*

---

When you point an AI agent at a security analysis task, there's one fundamental problem: the agent doesn't know whether to use jadx or apktool on an APK, radare2 or Ghidra on an ELF, or de4js vs AST analysis on obfuscated JS. Every run is guesswork, with no reusable methodology.

reverse-skill provides a systematic solution.

GitHub: https://github.com/zhaoxuya520/reverse-skill | ⭐ 20,925 | MIT License

---

### Core Mechanism: 41-Rule Router

```
User task
  → RULES.md
  → MASTER-ROUTING / master-route.ps1 (PRIMARY)
  → case-init / scope.md (auth + network_profile; no ACT until ready)
  → Scenario skill → tools / MCP / scripts
  → timeline + Evidence→Finding→Path → report + field-journal
```

The routing core is a single structured configuration, validated by 163 regression cases across Windows + Ubuntu CI.

| Metric | Value |
|--------|-------|
| Routing rules | 41 (R0–R40) |
| Regression test cases | 163 |
| Core skill modules | 42 |
| Supported clients | Claude Code / Codex / Cursor / Kiro / Cline |

### Covered Scenarios

- **Android APK**: jadx/apktool decompilation → Smali analysis → Frida hooks
- **ELF/binaries**: radare2/Ghidra/IDA Pro static analysis → dynamic debugging
- **Frontend JS encryption**: deobfuscation → AST analysis → protocol reversal
- **Network PCAP**: traffic decryption → protocol reconstruction → anomaly extraction
- **CTF**: challenge type classification → toolchain matching → solution path planning
- **Authorized pentest**: scope confirmation → network profiling → exploit chain

---

### Installation

```bash
git clone https://github.com/zhaoxuya520/reverse-skill.git
```

Refresh the tool index (lets the router know what's installed):

| Platform | Command |
|---------|---------|
| Windows | `powershell -File skills/scripts/refresh-tool-index.ps1` |
| Linux / macOS | `bash skills/scripts/refresh-tool-index.sh` |
| Kali Linux | `bash kali/scripts/refresh-tool-index.sh` |

Check `skills/tool-index.md` for detected tools. Then point your agent at the directory or have it read `README_AI.md` — the agent bootstraps itself from there.

---

### Self-Evolving Knowledge Base

After each security task, reverse-skill distills useful findings (tool combinations, bypass techniques, known pitfalls) back into the knowledge base. Next time a similar task appears, routing is more accurate and tools are ready faster. This is what "self-evolving AI agent" looks like in a specialized domain: experience compounds automatically rather than requiring human maintenance.

---

### Prerequisites

- **Java / JDK**: required by jadx and apktool
- **Node.js 22.12+**: JS toolchain and MCP servers
- **Python 3.x**: Frida and helper scripts
- **A compatible AI client**: Claude Code, Codex, Cursor, Kiro, or Cline

---

### Authorized Use

reverse-skill is designed for **authorized security research**: compliance pentesting, CTF competitions, bug bounty programs, security tooling research. All routing rules include a scope confirmation step — no offensive actions run until the target authorization is confirmed.

---

*Mycelium Protocol — tracking the deep evolution of AI systems*

© 2026 Mycelium Protocol. All rights reserved.
