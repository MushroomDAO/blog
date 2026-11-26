<div align="center">

# Sage-Interaction

**An Omni Interaction Model with Agentic Task Delegation**

[🌐 Project Page](https://internlm.github.io/Sage-Interaction/) •
[🤗 Hugging Face](https://huggingface.co/internlm/Sage-Interaction) •
[<img src="assets/modelscope-logo.png" height="14" alt="" /> ModelScope](https://modelscope.cn/models/Shanghai_AI_Laboratory/Sage-Interaction) •
[🚀 Quick Start](#quick-start) •
[🎬 Demo](#demo)

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)

[English](README.md) | [简体中文](README_zh-CN.md)

<a href="assets/sage-overview.png">
  <img src="assets/sage-overview.png" alt="Sage-Interaction in six scenarios: information retrieval, timed reminders, travel planning, scientific calculation, safety alerts, and laboratory assistance." width="100%" />
</a>

</div>

<p align="center">
  <a href="#news">News</a> ·
  <a href="#introduction">Introduction</a> ·
  <a href="#model-downloads">Model Downloads</a> ·
  <a href="#performance">Performance</a> ·
  <a href="#quick-start">Quick Start</a> ·
  <a href="#demo">Demo</a> ·
  <a href="#license">License</a> ·
  <a href="#citation">Citation</a>
</p>

## News

- **[2026-11-23]** 🎉 We release **Sage-Interaction**, a 9B omni interaction model with agentic task delegation. Weights are available on [Hugging Face](https://huggingface.co/internlm/Sage-Interaction) and [ModelScope](https://modelscope.cn/models/Shanghai_AI_Laboratory/Sage-Interaction), together with a [real-time voice demo](demo/README.md).

## Introduction

We introduce **Sage-Interaction**, a **9B-parameter omni interaction model** built on **MiniCPM-o 4.5**. It combines **full-duplex interaction** with **agentic task delegation**: the model can submit tasks for asynchronous execution while continuing to converse with the user and process incoming audio and video. When delegated work is complete, its results are incorporated into the ongoing conversation.

Sage-Interaction operates within a coordinated frontend–backend system. The frontend handles real-time interaction, remaining attentive to the user and evolving visual context, while the backend carries out longer-running tasks that require sustained reasoning or tool use. This connects continuous audio-visual interaction with background task execution, supporting task-oriented collaboration in everyday assistance and scientific workflows.

### Features

- **Full-duplex omni interaction.** Continuously perceive incoming audio and video while producing responses, maintaining conversational continuity through user interruptions, backchannels, and background speech.
- **Agentic task delegation.** Identify tasks suitable for delegation, submit them for asynchronous background execution, and incorporate returned results into subsequent conversation while remaining responsive to the user.
- **Streaming video understanding.** Understand evolving visual context, respond proactively to relevant events, and support delegation of tasks grounded in a live video stream.
- **Scenario-grounded interaction training.** Generate interaction trajectories with a role-playing multi-agent system grounded in real-world scenarios. An asymmetric audio-video supervision objective accounts for denser audio signals and sparser video signals.

## Model Downloads

| Model | Parameters | Base model | Hugging Face | ModelScope |
| --- | --- | --- | --- | --- |
| Sage-Interaction | 9B | MiniCPM-o 4.5 | [🤗 internlm/Sage-Interaction](https://huggingface.co/internlm/Sage-Interaction) | [Shanghai_AI_Laboratory/Sage-Interaction](https://modelscope.cn/models/Shanghai_AI_Laboratory/Sage-Interaction) |

## Performance

We evaluate Sage-Interaction across full-duplex voice interaction, task delegation, and streaming video understanding.

### Full-Duplex Voice Interaction

Sage-Interaction achieves an **80.73 average score on FD-Bench v1.5**, the highest among the compared open- and closed-source models, with **1.29 s turn-taking latency on FD-Bench v1**.

<p align="center">
  <img src="assets/interaction-quality-latency.png" alt="Interaction quality versus turn-taking latency for nine models. Sage-Interaction scores 80.73 at 1.29 seconds." width="100%" />
</p>

The horizontal axis measures interaction quality on FD-Bench v1.5; the vertical axis measures turn-taking latency on FD-Bench v1. Higher quality and lower latency are better.

On FD-Bench v1.5, Sage-Interaction scores **83.00** for responding to user interruptions and **96.94** for resuming after a user backchannel, such as a brief acknowledgment. It also scores **82.00** for resuming after background speech and **61.00** when the user is talking to others.

<p align="center">
  <img src="assets/audio-benchmarks.png" alt="Full comparison on FD-Bench v1, FD-Bench v1.5, Llama Questions, and AlpacaEval." width="100%" />
</p>

### Task Delegation and Timed Reminders

Sage-Interaction achieves **80.47 F1 on Daily Delegation**, the highest among the compared models, with **4.13/5 response quality**. On **Time Speak**, it reaches **85.96 F1** with **1.019 s reminder latency**. These tasks evaluate delegation during everyday interactions and the ability to deliver a timed response.

<p align="center">
  <img src="assets/task-delegation.png" alt="Daily Delegation and Time Speak results. Sage-Interaction achieves 80.47 and 85.96 F1, respectively, with 1.019 seconds Time Speak latency." width="100%" />
</p>

### Streaming Video Understanding and Proactive Response

Sage-Interaction achieves **21.6 mIoU on Charades** and **42.3 PAUC on ProactiveQA**, leading the compared models on both proactive-response benchmarks. It also leads this comparison on **OmniVideoBench (41.1)** and **LVOmniBench (40.5)**, with **69.1** on StreamingBench and **80.1** on DailyOmni.

<p align="center">
  <img src="assets/video-benchmarks.png" alt="Streaming video results on Charades, ProactiveQA, StreamingBench, DailyOmni, OmniVideoBench, and LVOmniBench." width="100%" />
</p>

## Quick Start

The real-time voice demo runs Sage-Interaction as the frontend model and connects to an OpenAI-compatible API as the backend for delegated tasks. It requires Linux, a BF16-capable NVIDIA GPU, Python 3.12, and a CUDA 12.8 toolkit.

**1. Install**

```bash
git clone https://github.com/InternLM/Sage-Interaction.git
cd Sage-Interaction/demo
python3.12 -m venv .venv && source .venv/bin/activate
mkdir -p .cache/tmp && export TMPDIR="$PWD/.cache/tmp" PIP_NO_CACHE_DIR=1
python -m pip install --upgrade pip setuptools wheel packaging ninja
python -m pip install -r requirements.txt
python -m pip install flash-attn==2.8.3 --no-build-isolation
python scripts/prepare_environment.py
```

**2. Download the model**

```bash
huggingface-cli download internlm/Sage-Interaction --local-dir models/sage-interaction
# or from ModelScope:
# pip install modelscope && modelscope download --model Shanghai_AI_Laboratory/Sage-Interaction --local_dir models/sage-interaction
```

**3. Configure and start**

```bash
cp config.example.json config.local.json   # set backend_base_url and backend_model_name
bash start_demo.sh --config config.local.json --gpu 0 --instances 1
```

Enter the backend API key when prompted (or set `SAGE_BACKEND_API_KEY`). When `Demo ready` appears, open <http://127.0.0.1:18080/> and allow microphone access.

See the [Demo guide](demo/README.md) for all configuration fields, multi-GPU workers, and remote access.

## Demo

### Task Delegation

https://github.com/user-attachments/assets/5c4da4f5-a9a6-40ce-aa26-0f734e18f8bc

## Acknowledgments

This work was supported by the Shanghai Artificial Intelligence Laboratory.

We are especially grateful to the developers and maintainers of [MiniCPM-o 4.5](https://github.com/OpenBMB/MiniCPM-V), [Qwen3-TTS](https://github.com/QwenLM/Qwen3-TTS), [Qwen3-ASR](https://github.com/QwenLM/Qwen3-ASR), [Whisper](https://github.com/openai/whisper), [DeepSeek-V4.1-Flash](https://huggingface.co/deepseek-ai/DeepSeek-V4.1-Flash), and [JoyAI-VL-Interaction](https://github.com/jd-opensource/JoyAI-VL-Interaction), among others, for sharing models, tools, and other resources that supported this work. We also thank our colleagues and collaborators who supported the development of Sage-Interaction and its associated datasets.

## License

The code in this repository and the Sage-Interaction model weights are released under the [Apache License 2.0](LICENSE).

## Citation

If you find Sage-Interaction useful in your research, please consider citing:

```bibtex
@misc{sage_interaction,
  title = {Sage-Interaction: An Omni Interaction Model with Agentic Task Delegation},
  author= {Sage-Interaction Team},
  year = {2026},
  url = {https://github.com/InternLM/Sage-Interaction}
}
```
