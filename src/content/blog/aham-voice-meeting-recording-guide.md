---
title: "Aham Voice：Mac 本地会议录音，转写+说话人分离全离线，纪要接自己的大模型"
titleEn: "Aham Voice: Local Offline Meeting Transcription for Mac — Speaker Diarization + AI Minutes with Your Own LLM"
description: "Aham Voice 是一款 macOS 本地优先的会议录音转写工具（MIT 开源）：FunASR 离线转写 + CAM++ 说话人分离 + emotion2vec 情绪标注全部本地跑，音频不上传；会议纪要接你自己的 OpenAI 兼容大模型 API，Key 只存本机。适合任何不想把录音上传到陌生服务器的 Mac 用户。"
descriptionEn: "Aham Voice is a macOS-native, local-first meeting transcription app (MIT). FunASR transcription + CAM++ speaker diarization + emotion2vec sentiment — all offline. Your audio never leaves your machine. Meeting summaries use your own OpenAI-compatible LLM API key. Perfect for anyone who doesn't want to upload recordings to third-party servers."
pubDate: "2026-06-28"
updatedDate: "2026-06-28"
category: "Tech-News"
tags: ["macOS", "会议录音", "本地AI", "转写", "说话人分离", "隐私", "开源工具", "FunASR"]
heroImage: "../../assets/images/aham-voice-meeting-recording-guide-banner.jpg"
---

> **一句话定位**：Aham Voice 把「录音 → 逐句分说话人稿 → 结构化纪要」这条链路在你自己的 Mac 上跑完——转写、说话人分离、情绪标注全本地，纪要才出门走你自己的大模型 API，音频数据不离开本机。

---

## 项目信息

GitHub：https://github.com/li599198347-svg/aham-voice （23 ⭐，MIT 开源）

当前版本：v2.0.0（2026-06-21）

系统要求：**仅 Apple Silicon**（M1/M2/M3/M4 Mac）

---

## 为什么值得一用

现在录音转写工具很多，但几乎都有一个共同问题：**你的录音要上传到别人的服务器**。

Aham Voice 的立场很清晰：

| 能力 | 在哪里跑 |
|---|---|
| 语音转文字（FunASR）| **本地离线** |
| 说话人分离——谁在说（CAM++）| **本地离线** |
| 声学情绪分析（emotion2vec）| **本地离线** |
| 会议纪要生成 | 你自己的大模型 API |

音频文件、转写结果、声纹数据全留在你的 Mac 上，只有最后生成纪要时才调用你配置的 LLM API（Key 也只存本机）。

**适合谁用：**
- 开会多、不想录音上传到陌生服务器的职场人
- 访谈、播客录制需要逐字稿的创作者
- 对话类内容想要自动区分说话人的研究者
- 有自己的 API Key（如 DeepSeek、Qwen、OpenAI）想充分利用的用户

---

## 功能全景

### 1. 本地离线转写

基于 **FunASR paraformer**（阿里达摩院开源的 ASR 模型）+ VAD（语音活动检测）+ 标点恢复，离线生成逐句文稿。不需要联网，不需要账号，关飞行模式也能跑。

### 2. 说话人分离（谁在说）

基于 **CAM++** 声纹模型，自动区分每句话由谁说出：

- 每个说话人用不同形状/颜色标注
- 声纹可管理（命名、修改、跨录音复用）
- 同一个人的声音在不同录音里会自动关联

会议里有 3 个人，你能直接看到「张三说了什么、李四说了什么、王五说了什么」，不再是混在一起的纯文本。

### 3. 声学情绪标注

基于 **emotion2vec** 在本地对每句话做情绪分类（正向 / 中性 / 负向等），全程离线。

### 4. AI 会议纪要

转写完成后，把逐句稿发给你配置的大模型生成结构化纪要：

- 支持任意 **OpenAI 兼容接口**（DeepSeek、Qwen、硅基流动、OpenRouter 等都行）
- 支持自然语言重写：「帮我把纪要改成汇报口吻」「提取所有 Action Item」
- 包含情绪语义分析（结合声学情绪 + LLM 分析）

### 5. 热词功能

在「热词」页手动添加专有名词（公司名、产品名、人名），提升转写准确率。支持从 txt 文件批量导入。

---

## 安装步骤（普通用户版）

### 第一步：下载

打开 [Releases 页面](https://github.com/li599198347-svg/aham-voice/releases/latest)，下载**全部** `Aham Voice.dmg.part*` 分卷文件到同一个文件夹。

> **为什么有好几个分卷？** DMG 里内置了 AI 模型文件，体积较大，GitHub 有单文件 2GB 上限，所以拆分上传了。下载时全部选中，放在同一个文件夹里。

### 第二步：合并分卷

分卷下载完成后，打开「终端」（Terminal），运行：

```bash
# 先进入你下载分卷的文件夹，比如下载到桌面的 aham-voice 文件夹：
cd ~/Desktop/aham-voice

# 合并分卷（文件名按实际版本号调整）：
cat AhamVoice-v2.0.0.dmg.* > "Aham Voice.dmg"
```

稍等片刻，当前目录会出现一个 `Aham Voice.dmg` 文件。

> **终端在哪里？** 按 `Command + 空格` 打开 Spotlight，搜索「Terminal」或「终端」，回车打开。

### 第三步：安装

双击 `Aham Voice.dmg` → 把 **Aham Voice** 图标拖入「应用程序」文件夹。

### 第四步：解除 macOS 隔离

macOS 对从非 App Store 下载的应用有安全限制。首次运行前，在终端执行：

```bash
xattr -dr com.apple.quarantine "/Applications/Aham Voice.app"
```

执行完不会有任何提示，这是正常的。

> **更简单的方法**：在 Finder 中找到 Aham Voice，**右键 → 打开**，弹出警告后点「打开」即可跳过隔离。

### 第五步：配置 LLM API Key

打开 Aham Voice → 点「设置」→ 填入你的 OpenAI 兼容 API：

| 字段 | 填什么 |
|---|---|
| API Base URL | 你的服务商地址（如 `https://api.deepseek.com/v1`）|
| API Key | 你的 Key（形如 `sk-...`）|
| 模型名 | 比如 `deepseek-chat` 或 `gpt-4o-mini` |

填完后点「测试连接」，显示成功就可以用了。

**没有 API Key？** 推荐注册 [DeepSeek](https://platform.deepseek.com)（价格低、中文效果好）或 [硅基流动](https://cloud.siliconflow.cn)（国内访问稳定），新用户一般有免费额度。

---

## 使用工作流

### 录制新会议

1. 打开 Aham Voice → 点「新录音」
2. 开始说话，实时看到波形
3. 结束后点停止，等待本地转写（视录音长度，通常 1-2 分钟录音约需 30 秒）

### 导入已有录音

如果你之前用手机/录音笔/其他工具录好了音频，可以直接导入：

1. 点「导入录音」，选择音频文件（支持常见格式）
2. 等待转写和说话人分离完成

### 查看逐句稿

转写完成后进入「逐句转写」页面：
- 不同说话人用不同形状标注
- 点击任意句子可跳转到对应时间点播放
- 点击说话人标签可试听、命名声纹

### 生成会议纪要

进入「会议纪要」页面 → 点「生成纪要」，等待大模型返回结果。

纪要生成后可以用自然语言进一步加工，比如：
- 「提取今天会议里所有的待办事项」
- 「把这份纪要改写成发给客户的邮件格式」
- 「用中文总结关键结论，每条不超过两句」

### 添加热词

如果转写结果里公司名、产品名经常出错，进入「热词」页面手动添加。比如把「阿汉」加入热词后，系统会优先识别为你指定的写法。

---

## 技术选型说明（给好奇的读者）

| 组件 | 技术 | 说明 |
|---|---|---|
| 语音转文字 | FunASR paraformer | 阿里达摩院开源，中文效果尤其强 |
| 说话人分离 | CAM++ 声纹模型 | 精确区分不同声音，支持跨录音复用 |
| 情绪分析 | emotion2vec | 声学层面的情绪分类，本地运行 |
| 会议纪要 | OpenAI 兼容 API | 用你自己的 Key，支持所有兼容接口 |
| 运行环境 | macOS Apple Silicon | 本地模型需要 M 系列芯片性能 |

整个设计思路是：**能在本地跑的全在本地跑，只有生成质量最高的自然语言内容（纪要）才出门走大模型**。这样既保证了隐私，也能让你自由选择最适合自己的大模型。

---

## 与其他方案的对比

| 方案 | 隐私 | 说话人分离 | 纪要 | 价格 |
|---|---|---|---|---|
| Aham Voice | ✅ 全本地 | ✅ 本地 CAM++ | ✅ 自己的 LLM | 开源免费 |
| 飞书妙记 | ❌ 上传服务器 | ✅ 有 | ✅ 内置 | 会员付费 |
| Otter.ai | ❌ 上传服务器 | ✅ 有 | ✅ 有 | 订阅付费 |
| Whisper + 脚本 | ✅ 本地 | ❌ 需额外配置 | ❌ 需额外配置 | 折腾成本高 |
| 通义听悟 | ❌ 上传服务器 | ✅ 有 | ✅ 有 | 有免费额度 |

Aham Voice 的核心差异化：**本地推理链路最完整**——不只是转写本地，说话人分离和情绪标注也全在本机跑，而且作为开源项目可以审查每一行代码。

---

## 常见问题

**Q：转写速度怎么样？**
A：1 分钟录音大约需要 30-60 秒（视 Mac 型号和录音质量）。说话人分离会额外花一些时间，但基本可接受。M2 Pro 以上体验明显更流畅。

**Q：支持英文吗？**
A：FunASR 主要针对中文优化，英文也能转写但不是强项。中英混合对话效果尚可。

**Q：我用的是 Intel Mac，可以用吗？**
A：目前发布的 DMG 仅支持 Apple Silicon（M1/M2/M3/M4），Intel Mac 暂不支持。如果你是开发者，可以从源码自行构建。

**Q：API Key 安全吗？**
A：Key 只存在本机的配置文件里，Aham Voice 不会把它发送到任何第三方服务，只用来调用你指定的 LLM API。

**Q：哪个 LLM 效果最好？**
A：中文纪要推荐 DeepSeek V3 或 Qwen-Plus，性价比高、中文理解强。如果追求质量上限，Claude Sonnet 或 GPT-4o 效果会更好。

**Q：免费的吗？**
A：完全开源免费（MIT 协议）。唯一的花费是你调用大模型 API 的费用，通常一次会议纪要不超过几分钱。

---

## Aham 工具生态

Aham Voice 是 Aham 系列工具之一，作者的设计理念是「每个工具只把一件事做利落」：

| 工具 | 功能 |
|---|---|
| [Aham Voice](https://github.com/li599198347-svg/aham-voice) | 会议录音转写纪要（本文主角）|
| [Aham Survey](https://github.com/li599198347-svg/aham-survey) | 现场调研工具——把对话做成结构化调研成果 |
| [Aham PPT](https://github.com/li599198347-svg/aham-ppt) | AI PPT 制作技能 |
| [Aham UI](https://github.com/li599198347-svg/aham-ui) | 供 AI 消费的设计系统 |
| [Aham Word](https://github.com/li599198347-svg/aham-word) | 供 AI 消费的 Word 规范 |

---

## 总结

如果你是 Mac 用户，经常开会或录访谈，又不想把录音上传到陌生的服务器，Aham Voice 是目前开源社区里少数把「转写 + 说话人分离 + 纪要」都做进单机应用的项目。

安装稍有门槛（合并分卷 + 解除隔离），但配好后日常使用非常顺畅。配合价格便宜的 DeepSeek API，一个月会议纪要花不了几块钱。

---

> © 2026 Author: Mycelium Protocol. 本文采用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.zh) 授权——欢迎转载和引用，须注明作者姓名及原文链接。

<!--EN-->

> **In one line**: Aham Voice transcribes your meetings, separates speakers, and generates structured minutes — everything runs locally on your Mac except the final LLM call, so your audio never leaves your machine.

---

## Quick Facts

- **GitHub**: https://github.com/li599198347-svg/aham-voice (MIT, 23⭐)
- **Version**: v2.0.0 (June 21, 2026)
- **Requires**: Apple Silicon Mac (M1/M2/M3/M4)

---

## What Makes It Different

Most transcription tools upload your audio to a server. Aham Voice runs the full pipeline locally:

| Capability | Where it runs |
|---|---|
| Speech-to-text (FunASR paraformer) | **Local, offline** |
| Speaker diarization (CAM++) | **Local, offline** |
| Emotion analysis (emotion2vec) | **Local, offline** |
| Meeting minutes generation | Your own LLM API |

Only the final meeting summary uses an external LLM — and you supply your own API key, which stays on your machine.

---

## Install Steps

1. Download all `Aham Voice.dmg.part*` splits from [Releases](https://github.com/li599198347-svg/aham-voice/releases/latest) into one folder
2. Merge: `cat AhamVoice-v2.0.0.dmg.* > "Aham Voice.dmg"`
3. Open DMG, drag to Applications
4. Remove quarantine: `xattr -dr com.apple.quarantine "/Applications/Aham Voice.app"` (or right-click → Open)
5. Open app → go to Settings → enter your OpenAI-compatible API key (DeepSeek, Qwen, OpenRouter, etc.)

---

## Key Features

- **Offline transcription** — Chinese-optimized FunASR, no internet required
- **Speaker diarization** — CAM++ voice prints identify who said what, reusable across recordings
- **Acoustic emotion tagging** — emotion2vec labels each sentence, local only
- **AI meeting minutes** — any OpenAI-compatible endpoint; natural language rewrites supported
- **Custom vocabulary** — add proper nouns to improve accuracy

---

> © 2026 Author: Mycelium Protocol. Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Free to share and adapt with attribution.
