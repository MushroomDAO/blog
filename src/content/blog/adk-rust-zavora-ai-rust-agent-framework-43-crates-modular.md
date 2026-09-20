---
title: "ADK-Rust：43 个 crate 拆开来用，社区复刻的 Rust Agent 运行时"
titleEn: "ADK-Rust: 43 Composable Crates, a Community-Built Rust Agent Runtime"
description: "zavora-ai 社区维护的 ADK-Rust v2.2.0——不是 Google 官方项目，但把 Agent 运行时拆成 43 个可独立发布的 crate，按需引用。Type-safe、全异步、568 μs agent loop 开销，支持 Gemini/OpenAI/Anthropic/Ollama，含 graph 工作流、durable resume、realtime 语音、adk-skill 解析。本文做一次工程拆解。"
descriptionEn: "ADK-Rust v2.2.0 by zavora-ai — not a Google official project, but splits the agent runtime into 43 independently publishable crates. Type-safe, fully async, 568 μs agent loop overhead. Supports Gemini/OpenAI/Anthropic/Ollama, graph workflows with durable resume, realtime voice, and SKILL.md parsing."
pubDate: 2026-09-20
category: "Tech-Experiment"
tags: ["rust", "agent-runtime", "open-source", "multi-agent", "graph-workflow", "mcp"]
lang: zh-CN
heroImage: "../../assets/images/adk-rust-zavora-ai-rust-agent-framework-43-crates-modular-banner.jpg"
---

在挑 Agent 运行时的时候翻到了这个。

**ADK-Rust** 是 zavora-ai 社区维护的 Rust Agent 开发框架，不是 Google 官方项目，但名字和 API 风格跟 Google ADK 对齐（GitHub topic 里标了 `google-adk-rust`）。当前版本 v2.2.0，要求 Rust 1.95+，Apache-2.0 协议，43 个可独立发布的 crate 按职责拆开，用哪块引哪块。截至发稿 667 stars，crates.io 全工作空间合计超过 50 万次下载。

仓库：github.com/zavora-ai/adk-rust

---

## 为什么值得看

ADK 生态里不缺 Python 实现，缺的是敢拿 Rust 真正把 Agent 运行时生产化的项目。ADK-Rust 在几处正好压在关键点上：

- **模块化到 crate 级**：43 个 crate，每个都能独立发布、独立版本。写 CLI 脚本只引 `adk-core` + `adk-agent`，上 HTTP 服务再加 `adk-server`，不用把整个框架带进来。
- **Agent loop 开销 568 μs**：跟 Python SDK（253 μs）在一个数量级，比 LangGraph（1,228 ms）快了两千倍。但 Python SDK 的循环开销反而更低——Rust 的收益主要体现在冷启动（109 ms vs 501 ms）和内存（~15 MB vs 92.7 MB）。
- **adk-skill crate**：能解析 SKILL.md 格式的 Agent Skills，做词法匹配和提示注入——对用 Claude Code / Codex 等工具链的人直接有用。
- **graph 工作流的 durable resume**：SQLite checkpointer，进程崩了再启动可以从断点恢复，不是假的持久化。

---

## 架构：43 个 crate 分四层

README 把功能按 tier 分成四档，加进 `Cargo.toml` 的时候直接选：

```toml
[dependencies]
adk-rust = "2.2.0"
# adk-rust = { version = "2.2.0", features = ["standard"] }   # +server/auth/graph/eval
# adk-rust = { version = "2.2.0", features = ["enterprise"] }  # +realtime/browser/RAG
# adk-rust = { version = "2.2.0", features = ["full"] }        # 全部
```

| Tier | 包含 |
|------|------|
| `minimal`（默认）| Gemini、agent、runner、sessions |
| `standard` | minimal + OpenAI/Anthropic、tools、memory、telemetry、server、auth、graph、eval |
| `enterprise` | standard + realtime、browser、RAG、payments、AWP |
| `full` | enterprise + audio、代码执行、sandbox |

Tier 是起点不是上限——`features = ["minimal", "audio"]` 可以在 minimal 上单独加音频能力，不必整体升级到 enterprise。

---

## 最小可运行示例

```rust
use adk_rust::prelude::*;
use adk_rust::Launcher;

#[tokio::main]
async fn main() -> AnyhowResult<()> {
    dotenvy::dotenv().ok();
    let model = GeminiModel::new(&std::env::var("GOOGLE_API_KEY")?, "gemini-3.7-flash")?;

    let agent = LlmAgentBuilder::new("assistant")
        .instruction("You are a helpful assistant. Be concise and accurate.")
        .model(Arc::new(model))
        .build()?;

    Launcher::new(Arc::new(agent)).run().await?;
    Ok(())
}
```

换 provider 只换 client，agent 和 tools 不动：

| Provider | 客户端构造 | Feature Flag |
|----------|------------|--------------|
| Gemini | `GeminiModel::new(key, "gemini-3.7-flash")` | 默认 |
| OpenAI | `OpenAIClient::new(OpenAIConfig::new(key, model))` | `openai` |
| Anthropic | `AnthropicClient::new(AnthropicConfig::new(key, model))` | `anthropic` |
| DeepSeek | `DeepSeekClient::chat(key)` | `deepseek` |
| Ollama | `OllamaModel::new(OllamaConfig::new(model))` | `ollama` |
| Bedrock | `BedrockClient::new(...).await?` | `bedrock` |

还支持 xAI Grok、Mistral、Fireworks、Together AI 等 OpenAI 兼容预设，以及 mistral.rs 本地推理（Gemma 4、Qwen 3.5）。

---

## graph 工作流：durable resume 怎么用

这是我觉得最值钱的部分。`adk-graph` 实现了 LangGraph 风格的有向图调度，叠了几个关键能力：

**Checkpointing（持久化）**：
- 内存 checkpointer（测试用）
- SQLite checkpointer（生产可用）
- Delta checkpointer（只存变化量，节省空间）

**Durable resume**：进程重启后从数据库恢复，只需要共享同一个 SQLite 文件：

```rust
let checkpointer = SqliteCheckpointer::new("agent_state.db").await?;
let graph = MyGraph::builder()
    .checkpointer(checkpointer)
    .build()?;

// 崩了重启，同一个 thread_id 继续
let run = graph.resume_or_start(thread_id, input).await?;
```

**Human-in-the-loop**：图节点可以 pause 等待人工确认，审批内容绑到 digest，审批的和实际执行的是同一份内容：

```rust
graph.add_node("sensitive_action", sensitive_node)
    .require_approval(ApprovalPolicy::DigestBound)
```

**`with_goto` 动态路由**：节点在运行时决定自己的下一个节点，不需要预先声明边，适合 LLM 输出决定下一步的场景。

**Time travel**：可以回到历史 checkpoint 重新执行，用于调试或对比不同分支。

---

## adk-skill：解析 SKILL.md

`adk-skill` crate 专门做 AgentSkills 解析，这对现在用 Claude Code / Codex 工具链的人直接有用：

```rust
use adk_skill::SkillIndex;

let index = SkillIndex::discover("/path/to/.claude/skills").await?;
let matches = index.match_input("generate a banner for this article");
// → 返回 banner-creator skill 的 SKILL.md 内容和触发置信度
```

词法匹配（不需要嵌入模型），找到匹配后自动注入 prompt。支持 `.skills` 目录发现和索引，能扫整个 `~/.claude/skills/` 树。

---

## 关键 crate 索引

挑几个有工程价值的：

| Crate | 干什么 |
|-------|--------|
| `adk-graph` | LangGraph 风格图调度，SQLite checkpoint，durable resume，time travel |
| `adk-skill` | SKILL.md 解析 + 词法匹配 + prompt 注入，支持 `.skills` 目录发现 |
| `adk-realtime` | OpenAI Realtime + Gemini Live，双向音频/视频，VAD，情感对话 |
| `adk-computer-use` | 受管桌面自动化，digest 绑定审批中断，篡改无效 |
| `adk-sandbox` | 进程/WASM 沙箱，macOS Seatbelt，Linux bubblewrap |
| `adk-memory` | 语义检索 + bi-temporal 知识图谱 |
| `adk-rag` | 文档切片 + 嵌入 + 向量检索 + reranking，6 种后端 |
| `adk-audio` | STT/TTS，Deepgram 流式，ONNX 本地（Whisper/Moonshine/Kokoro） |
| `adk-payments` | ACP/AP2 适配器，可审计支付流，durable journal |
| `adk-devtools` | `read_file`/`write_file`/`bash` 等 DevToolset，沙箱隔离 workspace |

---

## 脚手架工具

```bash
cargo install cargo-adk

cargo adk new my-agent                       # 基础 Gemini agent
cargo adk new my-agent --template graph      # graph 工作流 + checkpoint
cargo adk new my-agent --template realtime   # 实时语音 agent
cargo adk new my-agent --template api        # HTTP 服务
cargo adk new my-agent --template agent-engine  # Gemini Enterprise BYOC
cargo adk new my-agent --addon mcp --addon guardrails  # 叠 addon
```

生成的项目带嵌入式 UI，打开 http://127.0.0.1:8080/ui/ 可以看到对话流、工具结果、workflow 拓扑图、事件 timeline 和 OpenTelemetry tracing。

---

## 性能数据

用 `cargo adk bench` 在 Apple M 系列 + macOS + gemini-2.5-flash 上测，同一负载：

| 框架 | 冷启动 | Agent Loop 均值 | P95 | 峰值 RSS |
|------|--------|----------------|-----|---------|
| **ADK-Rust** | **109 ms** | **568 μs** | **615 μs** | ~15 MB |
| Gemini Python SDK | 501 ms | **253 μs** | 334 μs | 69.7 MB |
| LangGraph | 502 ms | 1,228 ms | 1,228 ms | 92.7 MB |

值得注意的是：Agent loop 均值 Python SDK（253 μs）比 ADK-Rust（568 μs）低——Rust 的主要优势在冷启动（快 4.6x）和内存（低 4.6x），在 loop 开销上跟 Python SDK 是同数量级但并非更快。LangGraph 的 1,228 ms 是另一个量级，跟这两个不在同一个对比维度上。

自报数据，请打折看。用 `cargo adk bench --dry-run` 可以先估成本再跑。

---

## v2.2.0 新增的 Gemini Enterprise 路径

v2.2.0 完成了 Gemini Enterprise Agent Platform 的消费路径，全部可选、可组合：

- Gen AI Evaluation Service bridge
- Vertex AI RAG Engine 检索与接地
- Agent Retrieval 向量存储
- Agent Registry 发现与注册
- Skill Registry 远程 skill 加载
- 远程 ReasoningEngine agent 可作为 sub-agent 调用

Graph 工作流新增原生工具确认暂停。Tracing 修复了一次调用导出多条断裂 trace 的问题。

---

## 几点局限

- **社区维护，非 Google 官方**：API 和 Google ADK 对齐，但不是官方实现，稳定性保障不同。
- **NOASSERTION license**：GitHub API 返回的是 NOASSERTION，README 标注 Apache-2.0，商用前需自行核查 LICENSE 文件。
- **macOS sandbox 更完善**：Windows AppContainer 沙箱**未实现**，在文档里明确写了。
- **Python SDK loop 开销更低**：如果你的 agent 是 loop-heavy 而非 process-heavy，Python SDK 反而更快。
- **`adk-managed` 和 `adk-codeact-monty` 标为 Experimental**：生产慎用。

---

## 配套仓库

- **adk-ui**：动态 UI 生成（github.com/zavora-ai/adk-ui）
- **adk-studio**：可视化 agent builder（github.com/zavora-ai/adk-studio）
- **adk-playground**：120+ 可运行示例（github.com/zavora-ai/adk-playground）

Podcast 系列（Episode 1–3）是用 ADK-Rust 自己的音频能力生成的——`adk-audio` crate 驱动 Chirp3-HD 多说话人 TTS，脚本 + 幻灯片 + 音频片段拼成视频，零人工录音。

> 开源代码仅供学习研究，用于生产前请自行评估稳定性和 license。

---

**仓库**：github.com/zavora-ai/adk-rust  
**版本**：v2.2.0 | **Stars**：667 | **License**：Apache-2.0 | **Rust**：1.95+

<!--EN-->

When shopping for an agent runtime, I came across this one.

**ADK-Rust** is a Rust agent development framework maintained by the zavora-ai community organization — not a Google official project, but the name and API style align with Google ADK (the GitHub topics include `google-adk-rust`). Current version is v2.2.0, requires Rust 1.95+, Apache-2.0 license. 43 independently publishable crates split by responsibility — pull in only what you need. 667 stars at time of writing, 500K+ cumulative crates.io downloads across the workspace.

Repository: github.com/zavora-ai/adk-rust

---

## Why it's worth looking at

The ADK ecosystem has no shortage of Python implementations. What's missing is a project that seriously productionizes an agent runtime in Rust. ADK-Rust hits several points that matter:

- **Modular to the crate level**: 43 crates, each independently publishable and versioned. A CLI script pulls in only `adk-core` + `adk-agent`. An HTTP service adds `adk-server`. No need to drag the full framework in.
- **568 μs agent loop overhead**: Same order of magnitude as Python SDK (253 μs), two thousand times faster than LangGraph (1,228 ms). That said, Python SDK's loop overhead is actually lower — Rust's advantage is cold start (109 ms vs 501 ms) and memory (~15 MB vs 92.7 MB).
- **`adk-skill` crate**: Parses SKILL.md-format Agent Skills, does lexical matching and prompt injection — directly useful for anyone using Claude Code or Codex toolchains.
- **Graph workflow with durable resume**: SQLite checkpointer. Process crashes and restarts resume from the breakpoint. Not simulated persistence.

---

## Architecture: 43 crates in four tiers

Features are organized into tiers, selected directly in `Cargo.toml`:

```toml
[dependencies]
adk-rust = "2.2.0"
# adk-rust = { version = "2.2.0", features = ["standard"] }   # +server/auth/graph/eval
# adk-rust = { version = "2.2.0", features = ["enterprise"] }  # +realtime/browser/RAG
# adk-rust = { version = "2.2.0", features = ["full"] }        # everything
```

| Tier | Includes |
|------|----------|
| `minimal` (default) | Gemini, agent, runner, sessions |
| `standard` | minimal + OpenAI/Anthropic, tools, memory, telemetry, server, auth, graph, eval |
| `enterprise` | standard + realtime, browser, RAG, payments, AWP |
| `full` | enterprise + audio, code execution, sandbox |

A tier is a starting point, not a ceiling. `features = ["minimal", "audio"]` adds audio on top of minimal without upgrading to enterprise.

---

## Minimal runnable example

```rust
use adk_rust::prelude::*;
use adk_rust::Launcher;

#[tokio::main]
async fn main() -> AnyhowResult<()> {
    dotenvy::dotenv().ok();
    let model = GeminiModel::new(&std::env::var("GOOGLE_API_KEY")?, "gemini-3.7-flash")?;

    let agent = LlmAgentBuilder::new("assistant")
        .instruction("You are a helpful assistant. Be concise and accurate.")
        .model(Arc::new(model))
        .build()?;

    Launcher::new(Arc::new(agent)).run().await?;
    Ok(())
}
```

Swap the provider by swapping the client — the agent and tools are unchanged:

| Provider | Client | Feature |
|----------|--------|---------|
| Gemini | `GeminiModel::new(key, "gemini-3.7-flash")` | default |
| OpenAI | `OpenAIClient::new(OpenAIConfig::new(key, model))` | `openai` |
| Anthropic | `AnthropicClient::new(AnthropicConfig::new(key, model))` | `anthropic` |
| DeepSeek | `DeepSeekClient::chat(key)` | `deepseek` |
| Ollama | `OllamaModel::new(OllamaConfig::new(model))` | `ollama` |
| Bedrock | `BedrockClient::new(...).await?` | `bedrock` |

Also supports xAI Grok, Mistral, Fireworks, Together AI, and other OpenAI-compatible presets, plus mistral.rs for local inference (Gemma 4, Qwen 3.5).

---

## Graph workflows: how durable resume works

This is the most valuable part. `adk-graph` implements LangGraph-style directed graph scheduling with several critical capabilities:

**Checkpointing**:
- In-memory checkpointer (for tests)
- SQLite checkpointer (production-ready)
- Delta checkpointer (stores only deltas, saves space)

**Durable resume**: recover from a database after process restart, sharing only an SQLite file:

```rust
let checkpointer = SqliteCheckpointer::new("agent_state.db").await?;
let graph = MyGraph::builder()
    .checkpointer(checkpointer)
    .build()?;

// Crashed and restarted — same thread_id continues
let run = graph.resume_or_start(thread_id, input).await?;
```

**Human-in-the-loop**: graph nodes can pause waiting for human approval, bound to a digest — what you approved is what runs:

```rust
graph.add_node("sensitive_action", sensitive_node)
    .require_approval(ApprovalPolicy::DigestBound)
```

**`with_goto` dynamic routing**: a node decides its own successor at runtime without pre-declared edges — good for LLM-driven control flow.

**Time travel**: rewind to a historical checkpoint and re-execute, for debugging or branch comparison.

---

## adk-skill: parsing SKILL.md

The `adk-skill` crate specifically handles AgentSkills parsing — directly useful for Claude Code and Codex toolchain users:

```rust
use adk_skill::SkillIndex;

let index = SkillIndex::discover("/path/to/.claude/skills").await?;
let matches = index.match_input("generate a banner for this article");
// → returns banner-creator skill's SKILL.md content and trigger confidence
```

Lexical matching (no embedding model needed). Finds matches and auto-injects prompts. Supports `.skills` directory discovery and indexing, can scan an entire `~/.claude/skills/` tree.

---

## Key crates

A selection of the ones with engineering value:

| Crate | Purpose |
|-------|---------|
| `adk-graph` | LangGraph-style graph scheduling, SQLite checkpoint, durable resume, time travel |
| `adk-skill` | SKILL.md parsing + lexical matching + prompt injection, `.skills` directory discovery |
| `adk-realtime` | OpenAI Realtime + Gemini Live, bidirectional audio/video, VAD, affective dialogue |
| `adk-computer-use` | Governed desktop automation, digest-bound approval interrupts, tamper-evident |
| `adk-sandbox` | Process/WASM sandbox, macOS Seatbelt, Linux bubblewrap |
| `adk-memory` | Semantic retrieval + bi-temporal knowledge graph |
| `adk-rag` | Chunking + embeddings + vector search + reranking, 6 backends |
| `adk-audio` | STT/TTS, Deepgram streaming, ONNX local models (Whisper/Moonshine/Kokoro) |
| `adk-payments` | ACP/AP2 adapters, auditable payment flows, durable journals |
| `adk-devtools` | `read_file`/`write_file`/`bash` DevToolset, sandboxed workspace |

---

## Performance numbers

Measured with `cargo adk bench` on Apple M-series + macOS + gemini-2.5-flash (self-reported — apply a discount):

| Framework | Cold Start | Loop Overhead (mean) | P95 | Peak RSS |
|-----------|-----------|---------------------|-----|---------|
| **ADK-Rust** | **109 ms** | 568 μs | 615 μs | ~15 MB |
| Gemini Python SDK | 501 ms | **253 μs** | 334 μs | 69.7 MB |
| LangGraph | 502 ms | 1,228 ms | 1,228 ms | 92.7 MB |

Note: Python SDK's loop overhead (253 μs) is lower than ADK-Rust (568 μs). Rust's main advantage is cold start (4.6x faster) and memory (4.6x less). LangGraph's 1,228 ms is a different order of magnitude entirely.

Run `cargo adk bench --dry-run` to see cost estimates before running.

---

## Key limitations

- **Community-maintained, not Google official**: API aligns with Google ADK, but stability guarantees differ from an official implementation.
- **NOASSERTION license**: GitHub's API returns NOASSERTION; README badges say Apache-2.0. Verify the LICENSE file before commercial use.
- **Windows AppContainer sandbox not implemented**: Explicitly documented. macOS Seatbelt and Linux bubblewrap work; Windows doesn't.
- **Python SDK has lower loop overhead**: For loop-heavy (not process-heavy) agents, Python SDK is actually faster.
- **`adk-managed` and `adk-codeact-monty` are Experimental**: Avoid in production.

---

## Related repos

- **adk-ui**: Dynamic UI generation (github.com/zavora-ai/adk-ui)
- **adk-studio**: Visual agent builder (github.com/zavora-ai/adk-studio)
- **adk-playground**: 120+ runnable examples (github.com/zavora-ai/adk-playground)

The podcast series (Episodes 1–3) is generated by ADK-Rust itself — `adk-audio` drives Chirp3-HD multi-speaker TTS, and the script + slide deck + audio segments are concatenated with ffmpeg into a video. Zero manual voice recording.

> Open-source code is for learning and research. Evaluate stability and license before production use.

---

**Repository**: github.com/zavora-ai/adk-rust  
**Version**: v2.2.0 | **Stars**: 667 | **License**: Apache-2.0 | **Rust**: 1.95+
