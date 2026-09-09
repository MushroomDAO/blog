---
title: "本地跑了七八个模型服务，端口和参数全靠记？LLM-Dock 用 Docker Compose 给你一块面板"
titleEn: "Juggling Half a Dozen Local Model Services by Memory? LLM-Dock Gives You One Dashboard on Docker Compose"
description: "LLM-Dock 是一个管理本地 LLM 推理服务的 Web 面板：自动扫描 HuggingFace 缓存发现模型，llama.cpp 跑 GGUF、vLLM 跑 safetensors，3300-3400 端口段自动分配，一键起停，自动注册进 Open WebUI，还能在面板里直接跑 llama-bench 并把结果存库对比。前提是 Linux + NVIDIA。"
descriptionEn: "LLM-Dock is a web dashboard for managing local LLM inference services: it scans your HuggingFace cache for models, runs GGUF on llama.cpp and safetensors on vLLM, auto-assigns ports in the 3300-3400 range, starts and stops services with a click, auto-registers them into Open WebUI, and runs llama-bench from the UI with results stored for comparison. Linux + NVIDIA only."
pubDate: "2026-09-09"
updatedDate: "2026-09-09"
category: "Tech-News"
tags: ["本地推理", "Docker", "llama.cpp", "vLLM", "运维", "开源", "Open WebUI", "local-first"]
heroImage: "../../assets/images/llm-dock-docker-compose-local-llm-dashboard-banner.jpg"
---

> 📌 项目地址：https://github.com/teo-mateo/llm-dock
> 语言：Kotlin + Python ｜ Star：11（2026-09-09）

## 一句话结论

**当你本地模型从"一个"变成"七八个"的那一刻，这类工具的价值才显现出来。**

单个模型的时候，一条 `llama-server` 命令就够了。但当你同时有 Qwen 的三个量化档、一个 vLLM 跑的 safetensors、一个多模态的 mmproj，还要记住谁在 3301 谁在 3307、谁开了 flash attention 谁没开——这时候你需要的不是更快的推理，是**一块面板**。

## 它解决的痛点：本地推理的运维碎片

本地推理跑起来之后的第二类问题，很少有人讲：

- 模型散落在 `~/.cache/huggingface/hub/` 和各种自定义目录，记不清有哪些
- 每个服务一串长长的 CLI 参数（`-c 8192 -ngl 99 -fa 1 -ctk q8_0 ...`），改一次要翻文档
- 端口靠脑子分配，起冲突了才发现
- 想对比两个量化档的实际速度，得手动跑 `llama-bench` 再自己记结果
- GGUF 用 llama.cpp、safetensors 用 vLLM，两套完全不同的参数体系

LLM-Dock 把这些收进一个 Flask 面板。

## 功能清单

| 功能 | 说明 |
|---|---|
| **模型发现** | 自动扫描 HuggingFace 缓存和本地目录 |
| **多引擎** | llama.cpp 跑 GGUF，vLLM 跑 safetensors |
| **GPU 监控** | 面板里实时显示 nvidia-smi 数据 |
| **服务管理** | Web UI 或 API 创建/启动/停止/重启 |
| **Open WebUI 集成** | 自动注册成 OpenAI 兼容端点 |
| **端口管理** | 3300-3400 段自动分配 |
| **基准测试** | 面板里直接跑 `llama-bench`，结果存本地数据库可跨次对比 |

最后一条我觉得是最有价值的：**基准测试继承服务自己的模型和参数**，输出实时流式显示，结果存进本地数据库做历史追踪。

这意味着"把 `-ngl` 从 60 调到 99 到底快了多少"这种问题，可以直接在面板里得到有记录的答案，而不是跑两次记在草稿纸上。

## 硬性前提：Linux + NVIDIA

这一点必须放在前面说，因为它会直接筛掉一大批人：

- Linux（在 Ubuntu 22.04 上测试）
- Docker，带 Compose v2（是 `docker compose`，**不是**老的 `docker-compose`）
- Python 3.10+
- **NVIDIA GPU + CUDA 驱动**
- nvidia-container-toolkit

作者列了实测过的组合：

| 系统 | GPU | CUDA 架构 |
|---|---|---|
| Ubuntu 22.04.5 LTS | RTX PRO 6000 Blackwell | 120 |
| Ubuntu 22.04.5 LTS | RTX 3090 | 86 |

**Mac 用户和 AMD 显卡用户可以直接关掉这一页了。** 这不是"暂不支持"，是整个架构建立在 nvidia-container-toolkit 的 GPU 直通上。

## 装起来

作者在 Quick Start 前面专门列了几个容易踩的前置条件，说明这些坑是真被踩过的：

- **Docker Compose v2** —— setup 脚本用 `docker compose`，老的带横线版本不行
- **docker 组成员** —— 你的用户得在 `docker` 组里（`sudo usermod -aG docker $USER`，然后重新登录），否则 `./build-llamacpp.sh` 会因权限错误失败
- **Python venv** —— Ubuntu 上需要 `python3.10-venv` 包，否则 `./setup.sh` 建不了虚拟环境
- **NVIDIA Container Toolkit** —— 装完还要配置 Docker 运行时并重启：
  ```bash
  sudo nvidia-ctk runtime configure --runtime=docker
  sudo systemctl restart docker
  ```

然后：

```bash
git clone https://github.com/teo-mateo/llm-dock.git
cd llm-dock

./setup.sh              # 建 venv、装依赖、生成密码、起 Open WebUI
./build-llamacpp.sh     # 构建 llama.cpp 镜像（用 GGUF 的话）

cd dashboard
source venv/bin/activate
python app.py
```

访问点：

- 面板：http://localhost:3399
- Open WebUI：http://localhost:3300

## 第一个模型怎么跑起来

如果你手上还没有模型，作者给了完整路径。装 huggingface-cli：

```bash
pip install huggingface-hub
```

（注意 `huggingface-cli` / `hf` 可能装到 `~/.local/bin/`，不在 PATH 里要么用全路径要么加进 shell profile。）

下一个入门模型——作者推荐 Qwen2.5-3B-Instruct 的 GGUF：

```bash
hf download Qwen/Qwen2.5-3B-Instruct-GGUF qwen2.5-3b-instruct-q4_k_m.gguf   # ~2GB
```

更小或更大的选项：

```bash
hf download Qwen/Qwen2.5-1.5B-Instruct-GGUF qwen2.5-1.5b-instruct-q4_k_m.gguf  # ~1.5GB
hf download Qwen/Qwen2.5-7B-Instruct-GGUF qwen2.5-7b-instruct-q4_k_m.gguf      # ~4.5GB
```

然后在面板里：模型出现在"Discovered Models"区域 → 点它，选 llama.cpp 引擎 → 用内联参考面板配参数（3B 模型默认值就行，`-c 8192` 上下文、`-ngl 99` 全部层扔 GPU）→ Create Service → Start。

聊天有两条路。**Open WebUI**：去 http://localhost:3300 先注册（第一个账号是管理员），注册完模型会自动出现。或者直接 **API**：

```bash
curl http://localhost:3301/v1/chat/completions \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "qwen2.5-3b-instruct",
    "messages": [{"role": "user", "content": "Hello!"}]
  }'
```

## 参数配置：CLI 标志直接给，但有提示面板

这是个务实的设计选择。它**没有**把 llama.cpp 的参数包装成一堆表单控件，而是让你直接写 CLI 标志（`-ngl 99`、`-fa 1`），但编辑器里配了一个**内联参考面板，带所有支持标志的说明**。

好处是：llama.cpp 更新加了新参数，你立刻就能用，不用等面板作者跟进封装。

常用标志：

| 标志 | 含义 |
|---|---|
| `-c` | 上下文长度 |
| `-ngl` | 扔到 GPU 的层数（99 = 全部）|
| `-b` / `-ub` | 批 / 微批大小 |
| `-fa` | Flash attention |
| `-ctk` / `-ctv` | KV cache 量化 |
| `-t` | 线程数 |
| `-sm` | 多 GPU 切分模式 |
| `-ts` | 张量切分比例 |
| `-ot` | 覆盖张量缓冲类型（MoE 模型用）|

vLLM 那边是另一套：

| 标志 | 含义 |
|---|---|
| `--max-model-len` | 上下文长度 |
| `--gpu-memory-utilization` | 显存占用比例 |
| `--max-num-batched-tokens` | 批大小 |
| `--max-num-seqs` | 最大并发序列 |
| `--enable-prefix-caching` | 前缀缓存 |
| `--tensor-parallel-size` | 多 GPU |

vLLM 用的是官方镜像 `vllm/vllm-openai:v0.11.0`，llama.cpp 那边是自定义构建（`llm-dock-llamacpp`），因为要选 GPU 架构编译。

## 配置项

`.env` 放在 dashboard 目录：

| 变量 | 说明 | 默认 |
|---|---|---|
| `DASHBOARD_TOKEN` | 面板密码 | （必填）|
| `DASHBOARD_PORT` | 面板端口 | 3399 |
| `DASHBOARD_HOST` | 绑定地址 | 0.0.0.0 |
| `COMPOSE_PROJECT_NAME` | Docker 项目名 | llm-dock |
| `COMPOSE_FILE` | compose 文件路径 | ../docker-compose.yml |
| `LOG_LEVEL` | 日志级别 | INFO |

注意 `DASHBOARD_HOST` 默认是 `0.0.0.0`——**面板默认监听所有网卡**。它有密码保护（`DASHBOARD_TOKEN` 必填，setup 会生成一个），但如果你的机器在不可信网络里，建议改成 `127.0.0.1` 再用 SSH 转发访问。

模型扫描路径默认是 `~/.cache/huggingface/hub/` 和 `~/.cache/models/`，要加自定义路径得改 `model_discovery.py` 的代码——这一点还没做成配置项。

## 值不值得用

**推荐给：** 有 Linux + NVIDIA 机器、同时跑多个本地模型服务、需要横向对比不同量化/参数组合性能的人。特别是**家庭实验室**场景——一台带显卡的机器，跑好几个模型给不同用途。

**不推荐给：** Mac 用户、AMD 用户、只跑一个模型的人（那直接 `llama-server` 就够了，加一层 Docker 编排是负收益）。

**要有心理准备的：** 11 个 Star，2025 年 11 月建库，作者用 Kotlin + Python 混着写。前置条件多，装的过程大概率不会一次成功——不过作者把常见坑都写进 README 了，这是个好信号。

真正吸引我的是**内置 benchmark 且结果存库**这一条。本地推理调参最大的问题是"改了之后到底有没有变快"缺少可靠反馈，多数人凭感觉。把 `llama-bench` 做成面板里的一等公民，参数继承自服务本身，结果自动留档——这个设计比"又一个模型管理 UI"要有想法得多。

---

> © 2026 Author: Mycelium Protocol. 本文采用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.zh) 授权——欢迎转载和引用，须注明作者姓名及原文链接，不得去除署名后以原创发布。

<!--EN-->

> 📌 Repository: https://github.com/teo-mateo/llm-dock
> Language: Kotlin + Python ｜ Stars: 11 (2026-09-09)

## The Short Version

**Tools like this only start paying off the moment your local model count goes from one to seven.**

With one model, a single `llama-server` command is enough. But once you're running three quantizations of Qwen, a safetensors model on vLLM, and something multimodal with an mmproj — while remembering who's on 3301 and who's on 3307, and which one has flash attention on — what you need isn't faster inference. It's **a dashboard**.

## The Pain It Addresses: Operational Sprawl

The second class of local-inference problems, the one nobody writes about:

- Models scattered across `~/.cache/huggingface/hub/` and assorted custom directories, with no inventory
- A long CLI string per service (`-c 8192 -ngl 99 -fa 1 -ctk q8_0 ...`) that means re-reading docs to change
- Ports allocated from memory, conflicts discovered on collision
- Comparing two quantizations means running `llama-bench` by hand and recording results yourself
- GGUF goes to llama.cpp, safetensors goes to vLLM — two entirely different flag vocabularies

LLM-Dock pulls all of that into one Flask dashboard.

## Feature List

| Feature | What it does |
|---|---|
| **Model discovery** | Scans the HuggingFace cache and local directories automatically |
| **Multi-engine** | llama.cpp for GGUF, vLLM for safetensors |
| **GPU monitoring** | Live nvidia-smi stats in the dashboard |
| **Service management** | Create / start / stop / restart via web UI or API |
| **Open WebUI integration** | Auto-registers services as OpenAI-compatible endpoints |
| **Port management** | Automatic assignment in the 3300-3400 range |
| **Benchmarking** | Run `llama-bench` from the dashboard; results stored locally for cross-run comparison |

That last row is the most valuable one: **benchmarks inherit the service's own model and parameters**, output streams live, and results land in a local database for history tracking.

Which means "how much faster did bumping `-ngl` from 60 to 99 actually make it" becomes a question with a recorded answer, rather than two runs and a note on scrap paper.

## Hard Prerequisite: Linux + NVIDIA

This belongs up front, because it disqualifies a lot of readers immediately:

- Linux (tested on Ubuntu 22.04)
- Docker with Compose v2 (`docker compose`, **not** the legacy `docker-compose`)
- Python 3.10+
- **NVIDIA GPU with CUDA drivers**
- nvidia-container-toolkit

The tested combinations:

| OS | GPU | CUDA arch |
|---|---|---|
| Ubuntu 22.04.5 LTS | RTX PRO 6000 Blackwell | 120 |
| Ubuntu 22.04.5 LTS | RTX 3090 | 86 |

**Mac users and AMD owners can close this page.** This isn't "not yet supported" — the whole architecture rests on GPU passthrough via nvidia-container-toolkit.

## Installing

The author lists several prerequisites ahead of the Quick Start, which reads like scar tissue from real failures:

- **Docker Compose v2** — the setup script calls `docker compose`; the hyphenated legacy binary won't do
- **docker group membership** — your user must be in the `docker` group (`sudo usermod -aG docker $USER`, then log out and back in), or `./build-llamacpp.sh` fails on permissions
- **Python venv** — Ubuntu needs the `python3.10-venv` package, or `./setup.sh` can't create the virtualenv
- **NVIDIA Container Toolkit** — after installing, configure the Docker runtime and restart:
  ```bash
  sudo nvidia-ctk runtime configure --runtime=docker
  sudo systemctl restart docker
  ```

Then:

```bash
git clone https://github.com/teo-mateo/llm-dock.git
cd llm-dock

./setup.sh              # venv, deps, generated password, starts Open WebUI
./build-llamacpp.sh     # build the llama.cpp image (if using GGUF)

cd dashboard
source venv/bin/activate
python app.py
```

Access points:

- Dashboard: http://localhost:3399
- Open WebUI: http://localhost:3300

## Getting Your First Model Running

If you have no models yet, the author gives the full path. Install huggingface-cli:

```bash
pip install huggingface-hub
```

(`huggingface-cli` / `hf` may land in `~/.local/bin/`; use the full path or add it to your shell profile.)

Grab a starter model — the author recommends Qwen2.5-3B-Instruct in GGUF:

```bash
hf download Qwen/Qwen2.5-3B-Instruct-GGUF qwen2.5-3b-instruct-q4_k_m.gguf   # ~2GB
```

Smaller and larger options:

```bash
hf download Qwen/Qwen2.5-1.5B-Instruct-GGUF qwen2.5-1.5b-instruct-q4_k_m.gguf  # ~1.5GB
hf download Qwen/Qwen2.5-7B-Instruct-GGUF qwen2.5-7b-instruct-q4_k_m.gguf      # ~4.5GB
```

Then in the dashboard: the model shows up under "Discovered Models" → click it, pick llama.cpp → configure with the inline reference panel (defaults are fine for a 3B: `-c 8192` context, `-ngl 99` to offload every layer) → Create Service → Start.

Two ways to chat. **Open WebUI**: go to http://localhost:3300 and register first (the first account becomes admin); your model auto-registers. Or the **API** directly:

```bash
curl http://localhost:3301/v1/chat/completions \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "qwen2.5-3b-instruct",
    "messages": [{"role": "user", "content": "Hello!"}]
  }'
```

## Configuration: Raw CLI Flags, With a Reference Panel

This is a pragmatic design choice. It does **not** wrap llama.cpp's flags into a wall of form controls. You write the CLI flags directly (`-ngl 99`, `-fa 1`), and the editor ships an **inline reference panel with tooltips for every supported flag**.

The upside: when llama.cpp adds a flag, you can use it immediately without waiting for the dashboard author to wrap it.

Common flags:

| Flag | Meaning |
|---|---|
| `-c` | Context length |
| `-ngl` | GPU layers (99 = all) |
| `-b` / `-ub` | Batch / micro-batch size |
| `-fa` | Flash attention |
| `-ctk` / `-ctv` | KV cache quantization |
| `-t` | Thread count |
| `-sm` | Multi-GPU split mode |
| `-ts` | Tensor split ratios |
| `-ot` | Override tensor buffer types (for MoE) |

vLLM has its own vocabulary:

| Flag | Meaning |
|---|---|
| `--max-model-len` | Context length |
| `--gpu-memory-utilization` | GPU memory fraction |
| `--max-num-batched-tokens` | Batch size |
| `--max-num-seqs` | Max concurrent sequences |
| `--enable-prefix-caching` | Prefix caching |
| `--tensor-parallel-size` | Multi-GPU |

vLLM runs the official `vllm/vllm-openai:v0.11.0` image; llama.cpp is a custom build (`llm-dock-llamacpp`) because the GPU architecture has to be selected at compile time.

## Configuration Variables

`.env` lives in the dashboard directory:

| Variable | Description | Default |
|---|---|---|
| `DASHBOARD_TOKEN` | Dashboard password | (required) |
| `DASHBOARD_PORT` | Dashboard port | 3399 |
| `DASHBOARD_HOST` | Bind address | 0.0.0.0 |
| `COMPOSE_PROJECT_NAME` | Docker project name | llm-dock |
| `COMPOSE_FILE` | Path to docker-compose.yml | ../docker-compose.yml |
| `LOG_LEVEL` | Logging level | INFO |

Note that `DASHBOARD_HOST` defaults to `0.0.0.0` — **the dashboard listens on every interface by default**. It is password-protected (`DASHBOARD_TOKEN` is required and setup generates one), but on a machine sitting in an untrusted network, change it to `127.0.0.1` and reach it over an SSH tunnel.

Model scan paths default to `~/.cache/huggingface/hub/` and `~/.cache/models/`; adding custom paths means editing `model_discovery.py` — it isn't a config option yet.

## Worth Using?

**Recommended for:** anyone with a Linux + NVIDIA box running several local model services at once, especially if you want to compare quantizations and parameter sets. The **home lab** case fits perfectly — one GPU machine serving several models for different purposes.

**Not for:** Mac users, AMD users, or anyone running exactly one model (plain `llama-server` is enough; a Docker orchestration layer is net negative there).

**Set expectations:** 11 stars, repo created November 2025, Kotlin and Python mixed. The prerequisite list is long and installation probably won't work first try — though the author has documented the common traps in the README, which is a good sign.

What genuinely appeals to me is **built-in benchmarking with stored results**. The biggest problem with tuning local inference is the lack of reliable feedback on whether a change actually helped; most people go on feel. Making `llama-bench` a first-class dashboard citizen, with parameters inherited from the service and results archived automatically, is a more thoughtful design than "yet another model management UI."

---

> © 2026 Author: Mycelium Protocol. Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) — free to share and adapt with attribution. You must credit the author and link to the original; removing attribution and republishing as original is not permitted.
