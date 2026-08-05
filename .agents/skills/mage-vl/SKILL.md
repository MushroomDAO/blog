---
name: mage-vl
description: "用本机跑的 Mage-VL 视觉语言模型看图片和视频（microsoft/Mage-VL，Apple Silicon / MPS，全程离线不出网）。触发场景：给博客配图写 alt / 描述 / caption；检查某张 banner 或截图和文章内容是否对得上；问「这张图里有什么」「这个视频讲了什么」；给视频做分段解说时间线；批量给一批配图生成描述。仅在用户指向具体的本地图片或视频文件时使用；纯文字任务、需要联网搜图、或用户要的是生成图片（那是 banner-creator）时不要用。"
---

# Mage-VL 本地视觉理解

本机跑着微软 Mage-VL，能读图片和视频。媒体文件不出本机，适合还没发布的草稿配图。

服务实现在 `~/Dev/tools/model-download-tool/vendor/mage-vl-local-mac`（社区包装的
`karlazx/mage-vl-local-mac`），权重在 `~/.omlx/models/Mage-VL`。本 skill 只是它的客户端。

## 怎么用

一律通过本 skill 自带的脚本，它会在服务没起来时自动拉起来并等模型加载（首次约 60–90 秒）。

> 本 skill 有两份：`.agents/skills/mage-vl/` 是提交进仓库的源，`.claude/skills/mage-vl/`
> 是 Claude Code 实际加载的镜像（未跟踪）。改动请改 `.agents/` 那份再 `cp -r` 过去。

```bash
SKILL=$(ls .claude/skills/mage-vl/scripts/mage.py .agents/skills/mage-vl/scripts/mage.py 2>/dev/null | head -1)

python3 $SKILL status                       # 看服务状态，未运行返回退出码 1
python3 $SKILL up                           # 只启动，不跑任务
python3 $SKILL down                         # 停掉服务（释放约 20GB 内存）

# 图片
python3 $SKILL image src/assets/images/foo-banner.jpg -q "用两句话描述这张图。"

# 视频
python3 $SKILL video demo.mp4 -q "这段视频里发生了什么？"

# 主动流式解说：按片段边看边说，产出时间线
python3 $SKILL stream demo.mp4 -q "像体育解说一样，逐段解说画面里正在发生的事。"

# 批量：对一批图跑同一个问题
python3 $SKILL batch src/assets/images -q "用一句英文描述这张图。" --out /tmp/alt.jsonl

# 批量判定：按规则分成 YES / NO 两组
python3 $SKILL batch src/assets/images --judge --quality quick \
  -q "这张图里是否出现了人物（人脸、人体或人形轮廓）？" --out /tmp/person.jsonl

# 把视频的 canvas/帧抠出来
python3 $SKILL video demo.mp4 -q "描述内容" --save-frames /tmp/frames
```

进度和流式 token 走 stderr，最终结果走 stdout —— 需要拿干净结果时加 `2>/dev/null`。

## 批量与判定

`batch` 接目录、文件列表或加引号的通配符（`"src/assets/images/*banner*.jpg"`），
按顺序一张张跑 —— 后端一次只处理一个任务，并发提交只会排队，没有意义。

- `--out x.jsonl` 边跑边追加写，配 `--resume` 可以中断后接着跑，跑一半崩了不用重来。
- `--judge` 强制模型首行只输出 YES/NO、次行给一句理由，跑完按结论分成三组打印
  （YES / NO / 无法判定）。**无法判定那组一定要人工看**，不要当成 NO。
- 吞吐参考：`--quality quick` 约 2.6 秒/张，300 张十几分钟；`balanced` 约 4–7 秒/张。
  判定类问题用 `quick` 就够，写 alt 文本用 `balanced`。

**`batch` 永远不删除、不移动、不修改任何输入文件**，只输出判定结果。筛图这类需求
一律走「先判定 → 给用户看 YES 列表 → 用户确认后再由用户决定怎么处理」。不要因为
模型说了 YES 就直接 `rm` 或 `mv` —— 它会看错，实测里"人形轮廓"这种边界情况尤其容易翻车。

## 参数怎么选

| 参数 | 取值 | 什么时候调 |
|---|---|---|
| `--quality`（图片） | `quick` / `balanced` / `high` | 默认 `balanced`。要认图里的小字、UI 截图细节用 `high`（视觉 token 翻倍、耗时翻倍）；只要个大意用 `quick` |
| `--max-tokens` | 16–1024 | 图片默认 256，视频默认 512。**视频给少了必然中途重复退化**，要完整叙述就给 512 以上 |
| `--backend`（视频） | `dcvc` / `frames` | 默认 `dcvc`，用神经编解码器拼 canvas，信息密度高；`frames` 是均匀抽帧，快但粗 |
| `--frames` | 8–64 | 默认 32。视频长或事件密就加到 48–64 |
| `--segment-sec`（stream） | 4–12 | 默认 8。要更细的时间线就调小 |
| `--max-segments`（stream） | 2–8 | 默认 4。视频超过 30 秒才有必要加大 |

耗时参考（M1 Max 64GB）：图片 `balanced` 约 7 秒、`high` 约 13 秒；30 秒视频走 dcvc
约 45 秒预处理 + 100 秒生成。视频任务先告诉用户要等一两分钟，别让它看起来像卡住了。

## 它做不了什么

- **听不见声音。** Mage-VL 的 config 里只有 `vision_config` + qwen3 文本塔，没有音频塔；
  后端喂给它的也只是帧和 canvas。**视频里的语音转文字它做不了**，问它「这段视频说了什么」
  它只会根据画面猜。要字幕/转录请另找 ASR（whisper.cpp / mlx-whisper / ququ 里的 FunASR），
  再把转录文本和本 skill 的画面描述拼起来用。
- **不生成图片。** 生成配图是 `banner-creator`。
- 不做像素级定位（没有 bbox 输出），不做 OCR 级别的逐字抄写 —— 大字标题能认，
  密集小字会漏字，别拿它当 OCR 用。

## 已知毛病

- **中文提问会拿到中文回答，但要英文 alt 文本必须在问题里写死「只输出英文」** —— 只说「给出英文描述」它经常仍然回中文。
- **视频叙述后半段容易重复**（"手持黄色麦克风，另一名评论员手持黄色麦克风…"）。给足 `--max-tokens`，并把问题问得具体（"列出关键事件"好过"描述视频"）。
- 视频最长只处理前 150 秒，上传上限 500MB。
- 一次只跑一个任务，第二个会排队。

## 端口 3000 的坑

Web UI 是 **http://127.0.0.1:3000/**，不要用 `localhost:3000`。本机另有一个 NestJS 服务
（`~/Dev/aastar/YetAnotherAA`）绑在 `*:3000` 的 IPv6 通配地址上，浏览器的 `localhost`
会先解析到 `::1` 打给它，返回 `{"message":"Cannot GET /"}`。后端 API 在 8000，没有冲突。

命令行走本 skill 时不受影响 —— 脚本只连 `127.0.0.1:8000`。

## 排查

服务起不来或任务报错，先看 `~/Dev/tools/model-download-tool/vendor/mage-vl-local-mac/logs/backend.log`。
模型文件损坏时用同目录的 `.venv/bin/python scripts/verify_model.py` 校验。
