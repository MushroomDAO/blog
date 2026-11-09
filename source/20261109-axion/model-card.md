---
license: apache-2.0
library_name: transformers
pipeline_tag: text-generation
datasets:
  - Axion1-0/axion-training-data
tags:
  - reproduction
  - agent
  - tool-use
  - scientific-reasoning
  - moe
  - arxiv:2611.03233
---

# Axion 1.0-35B — Reproduction

[Paper](https://arxiv.org/abs/2611.03233) · [Project](https://axion1-0.github.io/) · [Code](https://github.com/bytedance/axion1_0) · [Training Data](https://huggingface.co/datasets/Axion1-0/axion-training-data)

This repository provides a **reproduction checkpoint of Axion 1.0-35B**, following the recipe described in *Axion 1.0: Open Agent Foundation Models, Simplified*. The model is designed for scientific reasoning, information seeking, and tool-augmented problem solving.

## Model Overview

| Property | Details |
| --- | --- |
| Model | Axion 1.0-35B |
| Release | Reproduction checkpoint |
| Architecture | Mixture of Experts (MoE) |
| Parameters | Approximately 35B total, 3B active |
| Weight precision | BF16 |

The training recipe combines approximately **18K SFT examples** with three stages:

1. **Learn to reason:** supervised fine-tuning on challenging, self-contained scientific problems constructed with model-aware feedback.
2. **Learn to investigate:** supervised fine-tuning on verifiable tasks requiring external information and tool use.
3. **Learn through interaction:** reinforcement learning over agent trajectories to refine reasoning and interaction with tools.

## Performance

The table compares paper-reported results with the results of the reproduction checkpoint released in this repository. All scores are percentages; higher is better.

| Model | HLE | BMB | SEAL&#8209;0 | HiPhO | FS&nbsp;Olympiad | FS&nbsp;Research |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Agents-A1 | 47.6 | — | 56.4 | 46.4 | 79.0 | 40.0 |
| Kimi-K2.6 | 54.0 | — | 50.5 | 41.1 | 73.0 | 17.9 |
| DeepSeek-V4-Pro (Preview) | 48.2 | — | 55.0 | 38.7 | 76.0 | 13.3 |
| Apodex 1.1 (ReAct) | 53.2 | 23.5 | — | — | — | 55.0 |
| Apodex 1.1 (Agent Team) | 56.1 | 35.3 | — | — | — | 63.3 |
| GPT-5.5 | 52.2 | — | 42.3 | 43.3 | 78.0 | 26.7 |
| GPT-5.6 Sol | — | 47.1 | 53.2 | 42.9 | 79.0 | 63.3 |
| GPT-6 Astra | 57.2 | — | — | — | — | — |
| Muse-Spark-1.0 | 58.0 | — | — | — | — | 38.0 |
| Gemini 3.1 Pro | 51.4 | 35.3 | 53.2 | 38.5 | 85.0 | 26.7 |
| Claude Opus 5 | 63.6 | 49.4 | — | — | — | — |
| Claude Fable 5 | 63.8 | 46.1 | — | — | — | — |
| Axion 1.0-35B (Paper) | 52.2 | 35.3 | 62.2 | 45.7 | 86.0 | 56.7 |
| **Axion 1.0-35B (Reproduction)** | **52.8** | **35.3** | **60.4** | **45.9** | **85.0** | **55.0** |

HLE denotes the full Humanity's Last Exam benchmark; BMB uses the human-difficult BioMysteryBench subset. FS denotes FrontierScience. A dash indicates an unreported result. Bold highlights the reproduction checkpoint released in this repository.

## Usage

Following the repository's [inference guide](https://github.com/bytedance/axion1_0/blob/main/axion/evaluation/README.md#serve-a-checkpoint), serve the released checkpoint with vLLM:

```bash
vllm serve Axion1-0/Axion-1.0-35B \
  --served-model-name axion-35b \
  --host 127.0.0.1 --port 8000 \
  --tensor-parallel-size 8 --dtype bfloat16 \
  --max-model-len 131072 \
  --reasoning-parser qwen3 \
  --enable-auto-tool-choice --tool-call-parser qwen3_coder
```

This example uses eight GPUs. Adjust tensor parallelism and context capacity to fit your GPU memory.

Call the OpenAI-compatible endpoint:

```bash
curl --fail-with-body http://127.0.0.1:8000/v1/chat/completions \
  -H 'Content-Type: application/json' \
  -d '{
    "model": "axion-35b",
    "messages": [
      {"role": "user", "content": "What is 2 + 3?"}
    ],
    "max_tokens": 1024
  }'
```

Tool-using agent evaluation additionally requires a harness that executes tool calls. See the [inference guide](https://github.com/bytedance/axion1_0/blob/main/axion/evaluation/README.md#serve-a-checkpoint) for details.

## License

This model is released under the **Apache License 2.0**. See [LICENSE](https://huggingface.co/Axion1-0/Axion-1.0-35B/blob/main/LICENSE) for details.

## Citation

```bibtex
@misc{jia2026axion,
  title         = {Axion 1.0: Open Agent Foundation Models, Simplified},
  author        = {Yuqi Jia and Yunjie Tian and Jiayu Zheng and Yijun Liang and Jingchen Sun and Mengyu Zhao and Di Fu},
  year          = {2026},
  eprint        = {2611.03233},
  archivePrefix = {arXiv},
  primaryClass  = {cs.AI},
  url           = {https://arxiv.org/abs/2611.03233}
}
```
