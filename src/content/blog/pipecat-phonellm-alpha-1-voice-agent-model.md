---
title: "PhoneLLM Alpha 1：Pipecat 罕见自研模型，专攻电话语音 Agent 的工具调用"
titleEn: "PhoneLLM Alpha 1: Pipecat's Rare In-House Model, Built Just for Phone Voice Agent Tool-Calling"
description: "开源语音 AI 框架 Pipecat（15k⭐，本来接 50+ 家 LLM 服务不做自有模型）罕见发布首个自研模型 PhoneLLM Alpha 1：基于 NVIDIA Nemotron 3 Nano 30B-A3B 全参数微调，PhoneBench v1 上性能对齐 GPT-4 Turbo，成本低 94%，P95 首字延迟快 1300ms。"
descriptionEn: "Pipecat (15k⭐ open-source voice AI framework, normally LLM-agnostic across 50+ providers) has released its first in-house model, PhoneLLM Alpha 1 — a full-parameter fine-tune of NVIDIA's Nemotron 3 Nano 30B-A3B that matches GPT-4 Turbo on PhoneBench v1 while being 94% cheaper and 1,300ms faster at P95 time-to-first-token."
pubDate: "2026-08-30"
updatedDate: "2026-08-30"
category: "Tech-News"
tags: ["Pipecat", "PhoneLLM", "语音Agent", "Nemotron", "工具调用", "开源"]
heroImage: "../../assets/images/pipecat-phonellm-alpha-1-voice-agent-model-banner.jpg"
---

> 📌 模型主页：huggingface.co/pipecat-ai/phonellm-alpha-1
> Pipecat 框架：github.com/pipecat-ai/pipecat（15k⭐）

**Pipecat 是一个"什么 LLM 都能接"的开源实时语音 AI 编排框架，对接 50+ 家 LLM 服务、25+ 家语音识别、20+ 家语音合成——正因为它一贯中立，这次自己发模型才显得反常。** PhoneLLM Alpha 1 是 Pipecat 团队（背后是做 WebRTC 的 Daily）发布的第一个自研模型：基于 NVIDIA Nemotron 3 Nano 30B-A3B（Mamba-Transformer 混合架构 MoE，30B 总参数、3.5B 激活参数）做全参数微调，专门解决一个具体问题——电话场景下的语音 Agent，工具调用要准、还要快。

## 一个中立框架为什么要自己做模型？

Pipecat 的定位一直是编排层：语音识别、大模型、语音合成、传输协议随便换，框架本身不绑定任何一家。这次破例，说明的是一个真实存在的缺口，不是又要卷一个通用对话模型。

缺口在延迟。人类对话的正常轮次间隔在 200 毫秒左右，电话里如果 AI 那头明显"卡壳"，体验就是断线感。通用大模型为了准确率会开思考链（thinking tokens），这在打字场景里是加分项，在电话场景里就是死寂——用户会真的以为电话断了。PhoneLLM 训练时直接把 thinking 模式关掉、温度设成 0，只做一件事：不磨叽地把工具调对。

## 架构与训练：从 Nemotron 3 Nano 全参数微调出来

- **基座**：NVIDIA Nemotron 3 Nano 30B-A3B，Mamba + Transformer 混合架构的 MoE，30B 总参数、3.5B 激活参数，262K 上下文
- **训练方式**：用 NVIDIA NeMo 做全参数监督微调（不是 LoRA），训练数据覆盖金融客服、医疗、零售/酒店客服、外呼等多个真实业务场景的对话
- **训练目标很窄**：不开思考模式的前提下，把工具/函数调用的准确率做上去——官方数据显示相比原版 Nemotron 3 Nano 有明显提升

## 实测数字（PhoneBench v1）

Pipecat 自己的电话场景评测集 PhoneBench v1 上：

- 综合表现对齐 GPT-4 Turbo
- 成本低 94%
- P95 首字延迟（time-to-first-token）比 GPT-4 Turbo 快 1,300 毫秒，目标是把 P95 的"首个可用回答 token"压到 600 毫秒以内
- 在 Modal 的 B200 上，每个并发 Agent 每分钟成本约 $0.00025

## 怎么用

- 推荐部署方式：vLLM 或 SGLang，需要 `trust_remote_code=True`，推理时温度设 0、关闭思考模式
- HuggingFace 上已经有面向 llama.cpp / Ollama / LM Studio / Jan 的量化版本，个人电脑本地也能跑
- 云端可以用 Modal AutoEndpoints 一行命令拉起（针对语音负载做了专门优化）
- License 是 BSD 2-Clause，但作为 Nemotron 系的衍生模型，继承了 Nemotron Open Model License 的条款——衍生作品要保留 NVIDIA 的版权声明

## 局限

目前只支持英语；这是为语音/对话 Agent 这个场景专门调出来的模型，通用任务上的表现不一定比原版 Nemotron 3 Nano 好，别拿它当通用大模型用。

## 这释放了什么信号

语音 Agent 这条赛道正在从"接一个通用大模型 API 糊弄过去"走向"为具体的延迟/成本/可靠性要求做垂直微调"。跟端侧小模型（比如前几天写过的 Needle 2，14MB 跑在手机里的工具调用模型）是同一个方向的两端——一个往云端的专用推理服务器走，一个往手机本地走，共同点都是不再指望一个通用大模型覆盖所有场景。

---

> © 2026 Author: Mycelium Protocol. 本文采用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.zh) 授权——欢迎转载和引用，须注明作者姓名及原文链接，不得去除署名后以原创发布。

<!--EN-->

> 📌 Model card: huggingface.co/pipecat-ai/phonellm-alpha-1
> Pipecat framework: github.com/pipecat-ai/pipecat (15k⭐)

**Pipecat is an open-source real-time voice AI orchestration framework that stays LLM-agnostic across 50+ providers, 25+ speech-to-text services, and 20+ text-to-speech services — which is exactly why it releasing its own model is notable.** PhoneLLM Alpha 1 is the Pipecat team's (built by Daily, the WebRTC company) first in-house model: a full-parameter fine-tune of NVIDIA's Nemotron 3 Nano 30B-A3B (a hybrid Mamba-Transformer MoE with 30B total / 3.5B active parameters) built to solve one specific problem — accurate, fast tool-calling for phone-based voice agents.

## Why would a neutral framework build its own model?

Pipecat has always positioned itself as an orchestration layer — swap in any STT, LLM, or TTS provider, and the framework doesn't care. Making an exception here signals a real gap, not another generic chat model entering the race.

The gap is latency. Human conversational turn-taking normally happens at around 200ms intervals. On a phone call, if the AI visibly "thinks," it reads as dead air — the caller assumes the line dropped. General-purpose LLMs use thinking tokens to boost accuracy, which helps in text contexts but actively hurts in voice. PhoneLLM was trained with thinking disabled and temperature at 0, optimized for exactly one thing: calling the right tool, without hesitation.

## Architecture and training: a full-parameter fine-tune of Nemotron 3 Nano

- **Base model**: NVIDIA Nemotron 3 Nano 30B-A3B, a hybrid Mamba + Transformer MoE with 30B total parameters and 3.5B active, 262K context length
- **Training method**: full-parameter supervised fine-tuning via NVIDIA NeMo (not LoRA), on conversational data spanning financial services, healthcare, retail/hospitality customer support, and outbound calling
- **A narrow training objective**: improve tool/function-calling accuracy with thinking disabled — official numbers show a clear improvement over the base Nemotron 3 Nano

## The numbers (PhoneBench v1)

On Pipecat's own phone-scenario eval set, PhoneBench v1:

- Overall performance comparable to GPT-4 Turbo
- 94% cheaper
- 1,300ms faster P95 time-to-first-token than GPT-4 Turbo, targeting sub-600ms P95 time-to-first-answer-token
- On Modal's B200 infrastructure, roughly $0.00025 per minute per concurrent agent

## How to use it

- Recommended serving stack: vLLM or SGLang, with `trust_remote_code=True`, temperature 0, thinking disabled
- Quantized builds for llama.cpp / Ollama / LM Studio / Jan are already on HuggingFace, so it runs locally too
- Modal AutoEndpoints offers a one-command deploy tuned for voice workloads
- Licensed BSD 2-Clause, but as a Nemotron derivative it inherits Nemotron Open Model License terms — derivative works must retain NVIDIA's copyright notices

## Limitations

English only for now. This is a narrowly-tuned model for voice/conversational agent use — don't expect it to outperform the base Nemotron 3 Nano on general tasks.

## What this signals

Voice agents are shifting from "bolt on a general-purpose LLM API" toward vertical fine-tuning for specific latency/cost/reliability requirements. It's the cloud-side counterpart to a trend we've also covered on the device side — Needle 2, a 14MB tool-calling model that runs on phones. Same direction, opposite ends: one heads toward specialized cloud inference, the other toward on-device — neither is betting on one general model covering every case anymore.

---

> © 2026 Author: Mycelium Protocol. Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) — free to share and adapt with attribution. You must credit the author and link to the original; removing attribution and republishing as original is not permitted.
