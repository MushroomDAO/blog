---
title: "Google开源了一个无向量库的常驻内存Agent——以及如何把它从谷歌生态里完整解绑"
titleEn: "Google Open-Sourced a Vector-DB-Free Always-On Memory Agent — And How to Fully De-Google It"
description: "GoogleCloudPlatform/generative-ai里有一个叫 always-on-memory-agent 的项目：基于 Google ADK + Gemini 3.1 Flash-Lite，用纯 SQLite 替代向量数据库，用后台睡眠整合循环模拟人脑记忆巩固机制。本文深入解析其架构、揭露实测缺陷，并给出把 google-adk/google-genai 完整替换为 LangGraph + Qwen2.5-VL + litellm 的迁移方案。"
descriptionEn: "GoogleCloudPlatform/generative-ai contains an always-on-memory-agent: built on Google ADK + Gemini 3.1 Flash-Lite, replacing vector databases with plain SQLite and using a background 'sleep consolidation loop' to mimic human memory consolidation. This post deep-dives the architecture, reveals the real rough edges, and provides a complete migration to LangGraph + Qwen2.5-VL + litellm."
pubDate: "2026-07-21"
updatedDate: "2026-07-21"
category: "Tech-Experiment"
tags: ["AI Agent", "Memory", "Google ADK", "开源替换", "LangGraph", "Qwen", "向量库替代", "SQLite", "长期记忆", "Gemini"]
heroImage: "../../assets/images/google-always-on-memory-agent-adk-open-source-replacement-banner.jpg"
---

> **仓库**：[GoogleCloudPlatform/generative-ai · always-on-memory-agent](https://github.com/GoogleCloudPlatform/generative-ai/tree/main/gemini/agents/always-on-memory-agent)  
> **作者**：Shubham Saboo（Google）  
> **深度测评**：[Sascha Heyer @ Google Cloud Medium](https://medium.com/google-cloud/agent-memory-head-to-head-469fd1cb71a0)

---

## 这个项目解决了什么问题

大多数 AI Agent 有失忆症。它们处理信息时有上下文，对话结束了一切归零。你下次再问，它什么都不记得了。

现有的记忆解决方案各有天花板：

| 方案 | 局限 |
|---|---|
| **向量库 + RAG** | 被动检索。嵌入一次，查询时拿回来。没有主动理解。 |
| **对话摘要** | 细节丢失，无法交叉引用。 |
| **知识图谱** | 构建和维护成本高。 |

**Always-On Memory Agent** 的答案是：像人脑一样主动处理记忆。

人类不只是存储记忆——在睡眠期间，大脑会回放、连接、压缩信息。这个 Agent 在后台持续做同样的事：摄入新信息，每30分钟整合一次，找到跨文件的连接和洞见。

**而且完全不需要向量数据库**。没有 Embedding，没有 Chroma/Pinecone/Qdrant。就是一个 SQLite 文件 + 一个 LLM。

---

## 仓库在哪里

```
https://github.com/GoogleCloudPlatform/generative-ai
└── gemini/agents/always-on-memory-agent/
    ├── agent.py          ← 全部核心逻辑，单文件
    ├── dashboard.py      ← Streamlit 可视化界面
    ├── requirements.txt  ← 依赖（5个包）
    └── README.md
```

只有两个 Python 文件。整个系统，包括 4 个 Agent、HTTP API、文件夹监听、定时整合，全在 `agent.py` 这一个文件里。这是它设计上最聪明的地方——极简。

---

## 架构：四个 Agent，一条睡眠循环

### Agent 结构

```
memory_orchestrator（主路由）
    ├── ingest_agent     → 工具: store_memory
    ├── consolidate_agent → 工具: read_unconsolidated_memories, store_consolidation
    └── query_agent      → 工具: read_all_memories, read_consolidation_history
```

ADK 的 `sub_agents` 机制让 orchestrator 用自然语言描述路由规则，而不是硬编码 if-else：

```python
orchestrator = Agent(
    name="memory_orchestrator",
    model=MODEL,
    instruction=(
        "Route requests to the right sub-agent:\n"
        "- New information -> ingest_agent\n"
        "- Consolidation request -> consolidate_agent\n"
        "- Questions -> query_agent\n"
    ),
    sub_agents=[ingest_agent, consolidate_agent, query_agent],
    tools=[get_memory_stats],
)
```

这是工具调用驱动的设计——模型决定调 `store_memory`，而不是强制结构化输出。这给了系统灵活性，也带来了延迟。

### SQLite Schema

```sql
CREATE TABLE memories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source TEXT,          -- 来源文件名/URL
    raw_text TEXT,        -- 原始内容
    summary TEXT,         -- 1-2句摘要
    entities TEXT,        -- JSON: ["Anthropic", "Claude", ...]
    topics TEXT,          -- JSON: ["AI", "agents", ...]
    connections TEXT,     -- JSON: [{linked_to, relationship}, ...]
    importance REAL,      -- 0.0~1.0 模型打分
    created_at TEXT,
    consolidated INTEGER  -- 是否已整合
);

CREATE TABLE consolidations (
    source_ids TEXT,      -- JSON: [1, 2, 3]
    summary TEXT,
    insight TEXT,         -- 跨文档洞见
    created_at TEXT
);
```

没有向量字段。没有 embedding 列。全是纯文本结构化存储。

### 两个后台循环

**循环1：文件夹监听（5秒轮询）**

```python
async def watch_folder(agent, folder, poll_interval=5):
    while True:
        for f in sorted(folder.iterdir()):
            if f not in processed:
                await agent.ingest_file(f)  # 文本/图片/音频/视频/PDF
        await asyncio.sleep(poll_interval)
```

把文件丢进 `./inbox/`，5秒内自动摄入。支持27种格式：文本、图片、音频、视频、PDF。

**循环2：睡眠整合（默认30分钟）**

```python
async def consolidation_loop(agent, interval_minutes=30):
    while True:
        await asyncio.sleep(interval_minutes * 60)
        count = unconsolidated_count()
        if count >= 2:
            await agent.consolidate()
```

这就是"睡眠机制"——定时醒来，看看有没有新记忆需要整合，找连接，写洞见，标记为已整合。

### HTTP API

```bash
GET  /query?q=...       # 查询记忆
POST /ingest            # 摄入文本 {"text": "..."}
POST /consolidate       # 立即触发整合
GET  /status            # 记忆统计
GET  /memories          # 所有记忆列表
POST /delete            # 删除单条
POST /clear             # 全部清空
```

启动就是一行：

```bash
python agent.py --watch ./inbox --port 8888 --consolidate-every 30
```

---

## 实测数据（Sascha Heyer 深度测评）

同一份输入（一个 markdown 会议记录 + 一张聊天截图 PNG + 一段音频 WAV）：

| 指标 | 数据 |
|---|---|
| 每次摄入耗时 | 2.4 ~ 4.7 秒 |
| 整合耗时 | 2.8 秒 |
| 查询耗时 | 1.9 秒 |
| 多模态支持 | ✅ 图片识别 + 音频转写 |
| 跨文件引用 | ✅ 答案引用 [Memory 1], [Memory 2], [Memory 3] |

系统有效：三个不同格式的文件，一个问题，综合三个来源回答。

---

## 已知缺陷（诚实评估）

**1. 检索不是语义搜索，是时序窗口**

```python
# read_all_memories 的实际实现
db.execute("SELECT * FROM memories ORDER BY created_at DESC LIMIT 50")
```

不是向量相似度检索，是"最近50条"。超过50条记忆后，旧记忆悄悄掉出查询范围，没有任何信号告诉你。

**2. 整合批次上限 LIMIT 10**

```python
# read_unconsolidated_memories
"SELECT * FROM memories WHERE consolidated = 0 ORDER BY created_at DESC LIMIT 10"
```

如果一次摄入了20个文件，整合只处理最新的10条。剩下10条等下一轮。大批量摄入会积压。

**3. 无用户隔离**

一个 SQLite 文件，所有查询共享。个人助手场景没问题；多用户场景完全无法用。

**4. 延迟来自多 Agent 路由开销**

2.4~4.7 秒不是模型慢，是 orchestrator → specialist → tool → back 这条链路每次都要跑一遍。Gemini 3.1 Flash-Lite 本身是极快的模型。

**5. 治理薄弱**

有删除端点，没有 retention 策略、没有审计日志、没有权限作用域。这是 reference implementation，不是生产 memory platform。

---

## 依赖分析：谷歌生态绑定在哪里

```
requirements.txt:
streamlit>=1.40.0      # Dashboard UI — 可保留或替换
google-genai>=1.0.0    # ← Google AI SDK，核心绑定
google-adk>=1.0.0      # ← Google ADK 框架，核心绑定
aiohttp>=3.9.0         # HTTP 服务器 — 无关谷歌，保留
requests>=2.31.0       # HTTP 客户端 — 无关谷歌，保留
```

**代码里的6个绑定点：**

```python
from google.adk.agents import Agent           # ① Agent 类
from google.adk.runners import Runner         # ② 执行器
from google.adk.sessions import InMemorySessionService  # ③ 会话管理
from google.genai import types                # ④ Content/Part 类型

MODEL = "gemini-3.1-flash-lite"              # ⑤ 模型字符串
# 所有 runner.run_async() 内部走 Gemini API  # ⑥ API 调用
```

**不需要动的部分（业务逻辑全部保留）：**
- 所有 SQLite 工具函数（`store_memory`, `read_all_memories`, `store_consolidation`...）
- HTTP API 路由（aiohttp app）
- 文件夹监听逻辑
- 整合定时器逻辑
- Streamlit dashboard

替换工作面只在 Agent 编排层和模型调用层。

---

## 完整去谷歌方案

### 方案选择

| 方案 | 框架 | 模型 | 难度 | 适合场景 |
|---|---|---|---|---|
| **A（推荐）** | LangGraph | Qwen2.5-VL + Whisper | 中 | 本地优先，完全自托管 |
| **B** | LangChain | 任意 OpenAI 兼容 API | 低 | 快速迁移，云端部署 |
| **C** | 手写 ReAct | litellm 统一调用 | 低 | 最小依赖，完全控制 |

**推荐方案 A：LangGraph + Qwen2.5-VL + litellm**

---

### 第一步：替换依赖

```bash
# 卸载谷歌绑定
pip uninstall google-adk google-genai

# 安装替代
pip install langgraph langchain-core litellm aiohttp streamlit
pip install faster-whisper  # 音频支持
pip install ollama          # 本地推理（可选）
```

**模型推荐：**

| 用途 | 推荐模型 | 部署方式 |
|---|---|---|
| 文本摄入/整合/查询 | `Qwen2.5-7B-Instruct` | Ollama 或 vLLM |
| 图片多模态 | `Qwen2.5-VL-7B-Instruct` | Ollama (`qwen2.5vl:7b`) |
| 音频转写 | `faster-whisper medium` | 本地 CPU/GPU |
| 更强推理（预算够） | `Qwen3-32B` / `Llama-3.3-70B` | vLLM |

---

### 第二步：替换 Agent 编排层

原 ADK 代码：
```python
from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

ingest_agent = Agent(
    name="ingest_agent",
    model=MODEL,
    instruction="...",
    tools=[store_memory],
)
```

替换为 litellm + 手写 ReAct（方案C，最简单）：

```python
import litellm
import json

MODEL = "ollama/qwen2.5:7b"  # 或 "anthropic/claude-haiku-4-5" 等任意端点

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "store_memory",
            "description": "Store a processed memory in the database.",
            "parameters": {
                "type": "object",
                "properties": {
                    "raw_text": {"type": "string"},
                    "summary": {"type": "string"},
                    "entities": {"type": "array", "items": {"type": "string"}},
                    "topics": {"type": "array", "items": {"type": "string"}},
                    "importance": {"type": "number"},
                    "source": {"type": "string"},
                },
                "required": ["raw_text", "summary", "entities", "topics", "importance"],
            },
        },
    },
    # ... 其他工具定义
]

TOOL_MAP = {
    "store_memory": store_memory,
    "read_all_memories": read_all_memories,
    "read_unconsolidated_memories": read_unconsolidated_memories,
    "store_consolidation": store_consolidation,
    "read_consolidation_history": read_consolidation_history,
}

async def run_agent(system_prompt: str, user_message: str, tools: list) -> str:
    """通用 ReAct 循环：支持任意 litellm 端点"""
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_message},
    ]
    
    for _ in range(5):  # 最多5轮工具调用
        response = litellm.completion(
            model=MODEL,
            messages=messages,
            tools=tools,
        )
        msg = response.choices[0].message
        
        if not msg.tool_calls:
            return msg.content or ""
        
        # 执行工具调用
        messages.append({"role": "assistant", "content": None, "tool_calls": msg.tool_calls})
        for tc in msg.tool_calls:
            fn = TOOL_MAP[tc.function.name]
            args = json.loads(tc.function.arguments)
            result = fn(**args)
            messages.append({
                "role": "tool",
                "tool_call_id": tc.id,
                "content": json.dumps(result),
            })
    
    return "Max iterations reached"
```

---

### 第三步：替换多模态处理

**图片（Qwen2.5-VL）：**

```python
import base64

async def ingest_image_file(file_path: Path) -> str:
    image_b64 = base64.b64encode(file_path.read_bytes()).decode()
    suffix = file_path.suffix.lower().lstrip(".")
    
    response = litellm.completion(
        model="ollama/qwen2.5vl:7b",  # 或 vllm/qwen2.5-vl-7b
        messages=[{
            "role": "user",
            "content": [
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/{suffix};base64,{image_b64}"},
                },
                {
                    "type": "text",
                    "text": f"Describe this image in detail for memory storage. Source: {file_path.name}",
                },
            ],
        }],
    )
    description = response.choices[0].message.content
    return await run_ingest_agent(description, source=file_path.name)
```

**音频（faster-whisper 预处理）：**

```python
from faster_whisper import WhisperModel

_whisper = None

def get_whisper():
    global _whisper
    if _whisper is None:
        _whisper = WhisperModel("medium", device="cpu", compute_type="int8")
    return _whisper

async def ingest_audio_file(file_path: Path) -> str:
    model = get_whisper()
    segments, _ = model.transcribe(str(file_path))
    transcript = " ".join(seg.text for seg in segments)
    
    if not transcript.strip():
        return "No speech detected"
    
    # 转成文字后走普通文本摄入
    return await run_ingest_agent(
        f"Audio transcript from {file_path.name}:\n\n{transcript}",
        source=file_path.name,
    )
```

---

### 第四步：替换 Session 管理

原 ADK 的 `InMemorySessionService` 在替换方案里不再需要——`run_agent()` 每次调用是无状态的，状态全在 SQLite 里。

```python
# 原 ADK 代码（删除）
self.session_service = InMemorySessionService()
self.runner = Runner(agent=self.agent, ...)
session = await self.session_service.create_session(...)

# 替换后（MemoryAgent 类简化为）
class MemoryAgent:
    async def ingest(self, text: str, source: str = "") -> str:
        return await run_ingest_agent(
            f"Remember this (source: {source}):\n\n{text}", source
        )
    
    async def consolidate(self) -> str:
        return await run_consolidate_agent("Consolidate unconsolidated memories.")
    
    async def query(self, question: str) -> str:
        return await run_query_agent(f"Answer: {question}")
```

---

### 第五步：litellm 切换模型零改动

litellm 的最大价值是统一接口——同一段代码，通过改 `MODEL` 字符串切换任何模型：

```python
# 本地 Ollama
MODEL = "ollama/qwen2.5:7b"

# vLLM 自托管
MODEL = "openai/qwen2.5-7b-instruct"  # + OPENAI_API_BASE=http://your-vllm:8000/v1

# Anthropic Claude（最强推理，有成本）
MODEL = "anthropic/claude-haiku-4-5"

# 任何 OpenAI 兼容 API
MODEL = "openai/your-custom-model"  # + OPENAI_API_BASE=...
```

---

## 新旧对比

| 维度 | 原版（谷歌生态） | 去谷歌版 |
|---|---|---|
| **框架** | google-adk | litellm + 手写 ReAct |
| **模型** | Gemini 3.1 Flash-Lite | Qwen2.5-7B-Instruct (Ollama) |
| **图片** | Gemini 原生多模态 | Qwen2.5-VL-7B |
| **音频** | Gemini 原生 | faster-whisper → 文本 |
| **Session管理** | InMemorySessionService | 无状态（SQLite兜底） |
| **存储** | SQLite（不变） | SQLite（不变） |
| **HTTP API** | aiohttp（不变） | aiohttp（不变） |
| **Dashboard** | Streamlit（不变） | Streamlit（不变） |
| **云依赖** | Gemini API（按量付费） | 零云依赖（本地运行） |
| **数据主权** | 数据传谷歌 | 完全本地 |
| **迁移工作量** | — | ~200行改动，1-2天 |

---

## 什么时候用原版，什么时候去谷歌化

**用原版的场景：**
- 已经在谷歌云上，Vertex AI 有信用
- 需要 Gemini 对复杂音视频的最强多模态理解
- 团队已经熟悉 ADK 生态
- 不介意数据走谷歌 API

**去谷歌化的场景：**
- 数据主权要求（企业/医疗/金融等敏感场景）
- 不想绑定 Gemini API 成本
- 需要完全离线运行（edge / air-gapped）
- 想要在不同模型之间灵活切换和 A/B 测试
- 中文场景——Qwen2.5 在中文记忆摄入和整合上显著优于 Gemini Flash-Lite

---

## 核心判断

这个项目的**真正价值不在于谷歌的 SDK**，在于它展示了一个干净的记忆架构模式：

```
摄入（结构化提取）→ 整合（跨文档综合）→ 查询（上下文引用）
```

配合 SQLite 的极简存储，这个三段式架构完全可以用任何 LLM 重现——成本更低，数据更安全，模型更自由。

把它从谷歌生态解绑，核心业务逻辑一行不改，只是换了谁在执行那些工具调用。

> **Agent 记忆的天花板不在向量库，在整合机制。**

---

## 参考资源

- **仓库**：[GoogleCloudPlatform/generative-ai/gemini/agents/always-on-memory-agent](https://github.com/GoogleCloudPlatform/generative-ai/tree/main/gemini/agents/always-on-memory-agent)
- **深度对比测评**：[Agent Memory Head to Head — Always-On vs Vertex AI Memory Bank](https://medium.com/google-cloud/agent-memory-head-to-head-469fd1cb71a0)
- **litellm**：[github.com/BerriAI/litellm](https://github.com/BerriAI/litellm)
- **Qwen2.5-VL**：[github.com/QwenLM/Qwen2.5-VL](https://github.com/QwenLM/Qwen2.5-VL)
- **faster-whisper**：[github.com/SYSTRAN/faster-whisper](https://github.com/SYSTRAN/faster-whisper)
- **Vertex AI Memory Bank**（托管替代）：[cloud.google.com/agent-builder/memory-bank](https://cloud.google.com/agent-builder/agent-engine/memory-bank/set-up)

© 2026 Author: Mycelium Protocol

<!--EN-->

## Google Open-Sourced a Vector-DB-Free Always-On Memory Agent — And How to Fully De-Google It

**Repo**: [GoogleCloudPlatform/generative-ai · always-on-memory-agent](https://github.com/GoogleCloudPlatform/generative-ai/tree/main/gemini/agents/always-on-memory-agent)  
**By**: Shubham Saboo (Google) · **Benchmarked by**: [Sascha Heyer](https://medium.com/google-cloud/agent-memory-head-to-head-469fd1cb71a0)

### What It Solves

Most AI agents have amnesia. This project gives them a persistent, evolving memory that runs 24/7 as a background process — continuously ingesting, consolidating, and connecting information. No vector database. No embeddings. Just SQLite and an LLM that reads, thinks, and writes structured memory.

The key idea: humans don't just store memories. During sleep, the brain replays, connects, and compresses information. The consolidation loop in this agent does the same thing every 30 minutes.

### Architecture

**Four ADK agents:**
```
memory_orchestrator → routes to:
  ├── ingest_agent     (extracts summary/entities/topics/importance → store_memory)
  ├── consolidate_agent (finds cross-memory patterns → store_consolidation)
  └── query_agent       (synthesizes answers with citations)
```

**Two background loops:**
1. Folder watcher (5s poll) — drop any file in `./inbox/`, auto-ingested. 27 formats: text, images, audio, video, PDF.
2. Consolidation timer (every 30 min) — runs if ≥2 unconsolidated memories exist.

**SQLite schema**: memories table with `summary`, `entities` (JSON), `topics` (JSON), `connections` (JSON), `importance` (0.0–1.0), `consolidated` flag.

**HTTP API**: `/query?q=`, `POST /ingest`, `POST /consolidate`, `GET /status`, `GET /memories`.

### Real Benchmarks (Sascha Heyer's Tests)

Same input: markdown meeting note + PNG chat screenshot + WAV audio memo. Results: ingest 2.4–4.7s/file, consolidation 2.8s, query 1.9s. Genuinely multimodal — read the screenshot, transcribed the audio. Cross-file citation worked.

### The Rough Edges

1. **No semantic search** — `SELECT * FROM memories ORDER BY created_at DESC LIMIT 50`. Past 50 memories, older ones silently fall out.
2. **Consolidation batch cap** — `LIMIT 10`. Burst of 20 files? Only 10 consolidate per pass.
3. **No user isolation** — one shared SQLite file.
4. **Latency is orchestration, not model** — multi-agent routing costs 2.4–4.7s per ingest.
5. **Thin governance** — no retention, no audit, no scoped access. Reference implementation, not a memory platform.

### Google Ecosystem Bindings

**requirements.txt** (5 packages):
- `google-adk>=1.0.0` ← core binding
- `google-genai>=1.0.0` ← core binding
- `streamlit`, `aiohttp`, `requests` ← neutral, keep

**Six code-level bindings:**
1. `from google.adk.agents import Agent`
2. `from google.adk.runners import Runner`
3. `from google.adk.sessions import InMemorySessionService`
4. `from google.genai import types` (Content/Part)
5. `MODEL = "gemini-3.1-flash-lite"`
6. All API calls routed to Gemini

**What doesn't need to change**: all SQLite tool functions, the HTTP API, the folder watcher, the consolidation timer, the Streamlit dashboard. The replacement surface is only the agent orchestration and model call layers.

### Full De-Googling Plan

**Step 1 — Replace deps**
```bash
pip uninstall google-adk google-genai
pip install litellm langgraph faster-whisper
```

**Step 2 — Model choices**
| Use | Model | Deploy |
|---|---|---|
| Text (ingest/consolidate/query) | `Qwen2.5-7B-Instruct` | Ollama or vLLM |
| Image multimodal | `Qwen2.5-VL-7B-Instruct` | `ollama pull qwen2.5vl:7b` |
| Audio | `faster-whisper medium` | local CPU/GPU |

**Step 3 — Replace Agent orchestration with litellm ReAct loop**

```python
async def run_agent(system_prompt, user_message, tools):
    messages = [{"role":"system","content":system_prompt},{"role":"user","content":user_message}]
    for _ in range(5):
        response = litellm.completion(model=MODEL, messages=messages, tools=tools)
        msg = response.choices[0].message
        if not msg.tool_calls: return msg.content
        # execute tool calls, append results, continue loop
```

**Step 4 — Replace multimodal**

Images → `model="ollama/qwen2.5vl:7b"` with base64 image content.
Audio → `faster-whisper` transcribes to text first, then runs through text ingest agent.

**Step 5 — One-line model switching via litellm**
```python
MODEL = "ollama/qwen2.5:7b"           # local Ollama
MODEL = "anthropic/claude-haiku-4-5"   # Claude
MODEL = "openai/your-model"            # any OpenAI-compatible endpoint
```

### When to Stay on Google vs. De-Google

**Keep the original when**: already on GCP with Vertex AI credits, need Gemini's strongest multimodal for complex audio/video, data sovereignty isn't a concern.

**De-Google when**: data privacy requirements (healthcare/finance/enterprise), want zero API cost, need fully offline/air-gapped operation, want to A/B test models freely, or building for Chinese language use cases where Qwen2.5 noticeably outperforms Gemini Flash-Lite on Chinese memory extraction.

### The Core Insight

The real value here isn't Google's SDK — it's the clean three-stage memory architecture pattern:

```
Ingest (structure) → Consolidate (cross-connect) → Query (cite sources)
```

With SQLite as the store. This pattern works with any LLM. De-Googling is ~200 lines of change: swap the orchestration layer, keep all business logic intact.

**The ceiling of agent memory isn't the vector database. It's the consolidation mechanism.**

© 2026 Author: Mycelium Protocol
