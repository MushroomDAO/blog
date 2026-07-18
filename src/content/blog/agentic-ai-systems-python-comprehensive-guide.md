---
title: "Agentic AI 系统全景：用 Python 构建智能 Agent 的核心框架"
titleEn: "The Agentic AI Systems Landscape: Core Frameworks for Building Intelligent Agents with Python"
description: "Agentic AI 系统的核心概念全景：从 ReAct 循环到多 Agent 编排，从工具调用到记忆管理，从 LangChain/LangGraph 到 AutoGen/CrewAI，覆盖构建生产级 AI Agent 所需的架构模式、Python 实现和工程实践。面向希望系统性理解 Agentic AI 的开发者和建设者。"
descriptionEn: "Comprehensive overview of agentic AI systems: ReAct loop, multi-agent orchestration, tool calling, memory management, and production engineering patterns. Covers LangChain/LangGraph, AutoGen, CrewAI, and the Model Context Protocol (MCP). Python-focused, engineering-oriented guide for developers building AI agents."
pubDate: "2026-07-04"
updatedDate: "2026-07-04"
category: "Research"
tags: ["AI Agent", "Agentic AI", "LangChain", "Python", "多智能体", "工具调用", "记忆管理", "MCP"]
heroImage: "../../assets/images/agentic-ai-systems-python-comprehensive-guide-banner.jpg"
---

> **主题**: Agentic AI 系统工程全景  
> **适合**: 想系统理解和构建 AI Agent 的开发者

---

## 为什么 Agentic AI 是现在最重要的工程方向

2023 年以前，AI 应用主要是这个模式：
```
用户输入 → LLM → 输出
```

2024-2026 年，正在变成这个模式：
```
用户目标 → Agent 规划 → 工具调用 → 环境交互 → 反思 → 继续执行 → 完成目标
```

差别在于：**Agent 不只是回答问题，而是自主完成任务**。

这个转变带来了一套全新的工程问题：如何让 Agent 可靠？如何管理工具调用？如何处理长任务的中间状态？这些问题没有简单答案，但有一套正在成熟的模式。

---

## 基础架构：ReAct 循环

所有 Agentic AI 系统的核心都是 **ReAct（Reasoning + Acting）循环**：

```
观察（Observe）→ 思考（Think）→ 行动（Act）→ 观察（Observe）→ ...
```

```python
# ReAct 循环的核心实现
while not task_complete:
    # 1. 观察：收集当前状态
    observation = get_environment_state()
    
    # 2. 思考：LLM 决定下一步
    thought, action = llm.plan(observation, goal, history)
    
    # 3. 行动：执行工具/操作
    result = execute_tool(action)
    
    # 4. 更新历史
    history.append((thought, action, result))
    
    # 5. 检查是否完成
    task_complete = llm.check_completion(result, goal)
```

这个循环看起来简单，但工程实现中有大量细节：超时处理、错误恢复、无限循环检测、成本控制。

---

## 工具调用（Tool Calling）：Agent 的手脚

工具是 Agent 与外部世界交互的接口。现代 LLM 支持函数调用（Function Calling）/ 工具调用（Tool Use）：

```python
# OpenAI / Anthropic 工具定义格式
tools = [
    {
        "name": "search_web",
        "description": "搜索网页获取实时信息",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "搜索词"},
                "num_results": {"type": "integer", "default": 5}
            },
            "required": ["query"]
        }
    },
    {
        "name": "write_file",
        "description": "写入内容到文件",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {"type": "string"},
                "content": {"type": "string"}
            },
            "required": ["path", "content"]
        }
    }
]

# 调用 LLM，让它决定用哪个工具
response = claude.messages.create(
    model="claude-sonnet-4-6",
    tools=tools,
    messages=[{"role": "user", "content": "查一下今天 Bitcoin 价格并写入 price.txt"}]
)

# 执行 LLM 选择的工具
if response.stop_reason == "tool_use":
    tool_call = response.content[-1]
    result = execute_tool(tool_call.name, tool_call.input)
```

**工具设计的关键原则**：
1. **名称和描述要清晰**：LLM 根据描述决定用哪个工具
2. **参数要简单**：避免嵌套复杂对象
3. **错误要有意义**：返回 LLM 能理解并恢复的错误信息
4. **幂等性**：可以重复调用不产生副作用

---

## 记忆管理：Agent 的大脑

Agent 的记忆分四种类型：

```python
class AgentMemory:
    def __init__(self):
        # 1. 工作记忆（当前上下文）
        self.working_memory = []  # 当前对话历史
        
        # 2. 情节记忆（事件序列）
        self.episodic_memory = EpisodicStore()  # 过去的任务记录
        
        # 3. 语义记忆（知识库）
        self.semantic_memory = VectorDB()  # 文档、事实
        
        # 4. 程序记忆（技能）
        self.procedural_memory = SkillLibrary()  # 可复用的子程序
```

**实践建议**：
- 工作记忆用滑动窗口（保留最近 N 轮）
- 语义记忆用向量数据库（Chroma、Pinecone、Weaviate）
- 情节记忆用结构化存储（SQLite 或 PostgreSQL）
- **Wiki Memory 模式**（参考 Harrison Chase）：用 Agent 维护的 Markdown 文件作为记忆基底

---

## 多 Agent 编排：让 Agent 协作

单个 Agent 处理复杂任务会遇到上下文长度限制和专注度问题。多 Agent 架构把大任务分解给专门的 Agent：

```python
# 常见的多 Agent 模式

# 1. 流水线（Pipeline）：A → B → C
class Pipeline:
    def run(self, task):
        plan = planner_agent.plan(task)
        code = coder_agent.write(plan)
        result = reviewer_agent.review(code)
        return result

# 2. 网络（Network）：任意 Agent 可以调用任意 Agent
class AgentNetwork:
    agents = {"coder": CoderAgent(), "researcher": ResearcherAgent(), ...}
    
    def route(self, task):
        # LLM 决定路由到哪个 Agent
        target = router.decide(task, self.agents.keys())
        return self.agents[target].run(task)

# 3. 主管-工人（Supervisor-Worker）：一个主 Agent 分配任务给多个 Worker
class SupervisorAgent:
    def run(self, big_task):
        subtasks = self.decompose(big_task)
        results = [worker.run(t) for t in subtasks]  # 并行执行
        return self.synthesize(results)
```

**主流框架比较**：

| 框架 | 模式 | 特点 |
|---|---|---|
| **LangGraph** | 图状态机 | 最灵活，适合复杂工作流 |
| **AutoGen** | 对话 Agent | 多 Agent 对话，容易上手 |
| **CrewAI** | 角色扮演 | 高层抽象，快速原型 |
| **Swarm** (OpenAI) | 轻量交接 | 最简单，Agent 之间直接交接控制权 |

---

## Model Context Protocol (MCP)：工具标准化的未来

MCP 是 Anthropic 提出的工具调用标准协议，正在成为行业规范：

```python
# MCP Server 实现示例
from mcp import Server, Tool

server = Server("my-tool-server")

@server.tool()
async def search_database(query: str) -> str:
    """在数据库中搜索内容"""
    results = await db.query(query)
    return json.dumps(results)

# 任何支持 MCP 的 AI Agent 都可以自动发现并使用这个工具
```

**MCP 的价值**：工具一次实现，所有支持 MCP 的 Agent（Claude Code、Cursor、自定义 Agent）都能用。这正在成为 Agent 工具生态的基础设施。

---

## 生产工程：让 Agent 可靠

理论很美好，生产中会遇到很多问题：

### 1. 可观测性（Observability）

```python
# 每次 LLM 调用、工具调用都要记录
from opentelemetry import trace

tracer = trace.get_tracer(__name__)

with tracer.start_as_current_span("agent_run") as span:
    span.set_attribute("task", task)
    result = agent.run(task)
    span.set_attribute("result_length", len(result))
```

记录：调用链、token 消耗、耗时、错误率。工具推荐：LangSmith、Retrace、Arize。

### 2. 错误恢复（Error Recovery）

```python
def run_with_retry(agent, task, max_retries=3):
    for attempt in range(max_retries):
        try:
            return agent.run(task)
        except ToolExecutionError as e:
            # 工具失败：告诉 LLM 发生了什么，让它重新规划
            agent.add_to_history(f"工具 {e.tool} 失败: {e.message}")
            continue
        except MaxIterationsError:
            # 无限循环：强制停止，报告进度
            return agent.get_partial_result()
```

### 3. 成本控制

```python
class CostAwareAgent:
    MAX_TOKENS = 100_000  # 每个任务最多消耗
    
    def run(self, task):
        tokens_used = 0
        while not done:
            if tokens_used > self.MAX_TOKENS:
                return self.graceful_stop()
            response = llm.call(...)
            tokens_used += response.usage.total_tokens
```

### 4. 沙箱执行

Agent 执行代码或操作文件时必须有沙箱：
```python
# 用 Docker 沙箱执行 Agent 生成的代码
import docker

client = docker.from_env()
result = client.containers.run(
    "python:3.12-slim",
    command=f"python -c '{agent_generated_code}'",
    mem_limit="256m",
    network_disabled=True,  # 禁止网络访问
    read_only=True,          # 只读文件系统
    timeout=30
)
```

---

## 2026 年的 Agent 工程状态

**已经成熟的**：
- 工具调用（所有主流 LLM 都支持，标准化程度高）
- RAG 检索增强（工具链完善）
- 简单的单 Agent 任务流

**正在成熟的**：
- 多 Agent 协调（框架多，标准少）
- 长时间任务的可靠性（会话中断恢复）
- Agent 记忆的最佳实践（wiki memory 正在浮现）

**还很早期的**：
- Agent 安全（权限控制、提示注入防御）
- Agent 自我改进（让 Agent 学习自己的错误）
- 多模态 Agent（视觉+代码+工具的协同）

---

## 给开发者的快速开始建议

**新手路径**：
```
Week 1: 用 LangChain + Claude 实现一个 ReAct Agent
Week 2: 加上 3-5 个工具（web search、file ops、code exec）
Week 3: 加记忆（对话历史 + 向量 DB）
Week 4: 加可观测性（日志 + 成本追踪）
Month 2+: 引入 LangGraph 实现更复杂的工作流
```

**推荐资源**：
- [LangGraph 文档](https://langchain-ai.github.io/langgraph/)
- [Anthropic Claude 工具调用文档](https://docs.anthropic.com/en/docs/tool-use)
- [MCP 官方文档](https://modelcontextprotocol.io)
- [OpenAI Swarm](https://github.com/openai/swarm)

---

> © 2026 Author: Mycelium Protocol. 本文采用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.zh) 授权。

<!--EN-->

> **TL;DR**: Comprehensive engineering overview of agentic AI systems: the ReAct loop, tool calling patterns, memory management (working/episodic/semantic), multi-agent orchestration (pipeline/network/supervisor), Model Context Protocol (MCP), and production reliability (observability, error recovery, cost control, sandboxing). Python-focused with code examples.

---

## The Agentic Shift

Pre-2024: `User Input → LLM → Output`
2024-2026: `Goal → Agent Planning → Tool Calls → Environment Interaction → Reflection → Continue → Done`

The difference: agents don't answer questions — they complete tasks autonomously.

## Core Architecture: The ReAct Loop

```python
while not task_complete:
    observation = get_environment_state()
    thought, action = llm.plan(observation, goal, history)
    result = execute_tool(action)
    history.append((thought, action, result))
    task_complete = llm.check_completion(result, goal)
```

## Tool Calling: Agent's Hands

Define tools with clear names, descriptions, and input schemas. LLM selects the right tool based on description — quality of description directly determines tool selection accuracy. Key principles: clear naming, simple parameters, meaningful errors, idempotency.

## Memory Types

- **Working memory**: current conversation context (sliding window)
- **Episodic**: structured log of past task executions
- **Semantic**: vector DB for documents and facts
- **Procedural**: reusable skill library

## Multi-Agent Orchestration

| Pattern | When to use |
|---|---|
| Pipeline (A→B→C) | Linear workflows with clear stages |
| Network | Tasks that need dynamic routing |
| Supervisor-Worker | Large tasks with parallelizable subtasks |

**Framework comparison**: LangGraph (most flexible), AutoGen (multi-agent conversation), CrewAI (role-based high-level), Swarm (lightest, direct handoffs).

## MCP: The Tool Standard

Anthropic's Model Context Protocol: define a tool server once, all compatible agents discover and use it automatically. Becoming the industry standard for agent tool ecosystems.

## Production Engineering

- **Observability**: trace every LLM call and tool invocation (Retrace, LangSmith, Arize)
- **Error recovery**: feed tool failures back to LLM for replanning
- **Cost control**: hard token caps per task, graceful degradation
- **Sandboxing**: Docker containers for code execution (network-disabled, read-only FS, memory-limited)

**Links**: [LangGraph](https://langchain-ai.github.io/langgraph/) · [Claude Tool Use docs](https://docs.anthropic.com/en/docs/tool-use) · [MCP](https://modelcontextprotocol.io)

---

> © 2026 Author: Mycelium Protocol. Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
