---
title: "一个 bug 修完，本地语音润色延迟从十秒降到一秒"
titleEn: "One Bug Fix: Local Voice Polishing Latency Drops from 10s to 1s"
description: "一位推理引擎工程师排查 Voxt + Ollama 语音润色链路延迟问题，发现 user input 被重复嵌入 system prompt 导致 prefix cache 完全失效，修复后延迟从十几秒降至一秒出头，最终方案速度超越 Wispr Flow 等云端服务。"
descriptionEn: "An inference engineer debugged Voxt + Ollama voice polishing latency, discovering user input was duplicated in system prompt causing prefix cache failure. After fix, latency dropped from 10s to 1s, outperforming cloud-based tools like Wispr Flow."
pubDate: "2026-05-11"
updatedDate: "2026-05-11"
category: "Tech-News"
tags: ["Voxt", "Ollama", "语音输入", "本地推理", "ASR", "开源", "Qwen3"]
heroImage: "../../assets/banners/xiaobaobao/banner-equity-opportunity.jpg"
---

一位有推理引擎背景的工程师近日在社交平台分享了一段实战排查记录：他在使用开源 macOS 语音输入工具 **Voxt** 的过程中，发现了一个隐藏的 prompt 构造 bug，导致 AI 润色延迟被无端放大十倍。修复后，整条本地链路的端到端速度已经超越 Wispr Flow 等付费云端服务。

---

## Voxt 是什么

**Voxt**（GitHub：`hehehai/voxt`）是 macOS 上的开源本地语音输入应用，定位与 Wispr Flow、Superwhisper 同一赛道——语音转文字后经 LLM 润色输出。核心差异在于：ASR 和 LLM **全部可在本地运行**，数据不出机器。

---

## 问题的起点：MLX 后端太慢

这位工程师原本用 Voxt 自带的 MLX 推理后端运行 Qwen3.5-9B 做润色，但效果不理想——每次说完一段话需要等待 3-5 秒，"等三秒已经过了我的忍耐线"。

他的第一反应是换后端：已知 Ollama 在本地跑比 MLX 快很多，于是尝试切换。

---

## 换了 Ollama，反而更慢

切到 Ollama 后端后，情况不但没有改善，延迟反而超过了 **10 秒**，远超模型本身的推理时间。

他开始 debug 单次请求的 latency，把 Ollama 端接收到的请求 payload 打开一看，发现了问题所在：

> **user input 被嵌进了很长的 system prompt 的前段，同时又作为正式的 user message 发了一次。**

也就是说，每次请求里 user input 出现了**两次**。

---

## 根本原因：prefix cache 完全失效

这个 bug 的破坏力不止于重复发送。更要命的是：user input 出现在 system prompt 的前段，意味着**prefix cache 完全失效**——每条新输入都让前缀整个失配，缓存形同虚设，Ollama 每次都要从头计算完整上下文。

定位问题后，他把 user input 从 system prompt 里挪出来，只作为 user message 单独发送，重新测试：

> **延迟从十几秒直接掉到一秒出头。**

---

## 开源社区的响应速度

在换 Ollama 后端的过程中，他还遇到了几个问题：鉴权流程复杂、无法显式传 sampling 参数、Ollama 对 Qwen3 系默认开启 thinking 模式而润色任务根本不需要思考链。他向 Voxt 作者提了 issue，**作者当天就把改动 ship 了**：鉴权简化、参数透传、thinking 关闭全部进入主线。

---

## 最终链路

修复后，他的本地语音输入方案定型为：

| 组件 | 工具 | 说明 |
|------|------|------|
| ASR 语音识别 | Voxt | 本地运行，数据不出机 |
| LLM 润色 | Ollama + Qwen3.6 35B | 常驻内存，无冷启动 |
| 端到端速度 | 优于 Wispr Flow | 纯本地，无网络往返 |

"开源生态这两年的积累，让一个个体工程师能在自己笔记本上搭出这种延迟和质量的 voice-to-text，已经是几年前不敢想的事。"

---

**来源**：作者社交平台原文；工具仓库：[github.com/hehehai/voxt](https://github.com/hehehai/voxt)

---

> © 2026 小宝宝. 转载请注明来源。
