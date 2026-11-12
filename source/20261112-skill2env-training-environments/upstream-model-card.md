---
base_model:
- Qwen/Qwen3.6-35B-A3B
library_name: transformers
license: apache-2.0
license_link: https://huggingface.co/Qwen/Qwen3.6-35B-A3B/blob/main/LICENSE
pipeline_tag: image-text-to-text
tags:
- agent
- tool-use
- sft
- environment-synthesis
- skill2env
---

# Skill2Env: Capability-Oriented Environment Synthesis from Skills for General Agents

<p align="center">
  📄 <a href="https://huggingface.co/papers/2609.33772">Paper</a> &nbsp;|&nbsp;
  📚 <a href="https://arxiv.org/abs/2609.33772">arXiv</a> &nbsp;|&nbsp;
  💻 <a href="https://github.com/AllSpark-Research/AgentEnv">GitHub</a>
</p>

This repository contains a **Qwen3.6-35B-A3B agent model trained with Skill2Env**, a capability-oriented framework for synthesizing executable environments from skills.

## TL;DR

Skills provide reusable domain knowledge, procedures, and tool-use instructions. Skill2Env turns these ingredients into complete executable environments for agent post-training.

- **Capability-oriented synthesis:** reusable difficulty patterns target environment understanding, planning, skill usage, long-horizon consistency, and error recovery.
- **Blueprint-guided construction:** task blueprints specify objectives, challenges, environment facts, information boundaries, and acceptance criteria, guiding the construction of execution substrates, workspaces, and rubric-based evaluators.
- **Iterative Task Hardening:** agent rollouts reveal weaknesses in task design and guide coordinated updates to task blueprints and environments.
- **Supervised fine-tuning:** high-scoring trajectories generated in Skill2Env environments provide supervision for agent training.

We construct **2,963 tasks** and use **1.5K SFT trajectories** to train Qwen3.6-35B-A3B.

## Results

Skill2Env improves on its backbone by **+8.4 points on average** across seven agent benchmarks.

**Main results on seven agent benchmarks:**

| Model | Terminal-Bench 2.1 | SWE-bench Multilingual | SkillsBench | Claw-Eval | τ³-Banking | AutomationBench | VitaBench | Avg. |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| **Frontier Closed-Source Models** | | | | | | | | |
| GPT-5.4 | 78.3 | 71.7 | 51.7 | 60.3 | 28.5 | 27.7 | 47.1 | **52.2** |
| Claude Opus 4.6 | 71.2 | 77.8 | 50.2 | 70.4 | 20.3 | 25.5 | 38.3 | **50.5** |
| Gemini-3.1 Pro | 73.8 | 44.0 | 60.8 | 57.8 | 23.7 | 28.2 | 52.7 | **48.7** |
| **Open-Weight Models** | | | | | | | | |
| DeepSeek-V4-Flash-0731 | 78.7 | 76.0 | 53.8 | 49.3 | 30.3 | 36.3 | 56.3 | **54.4** |
| GLM-5.2 | 77.9 | 81.7 | 62.1 | 65.8 | 28.9 | 26.3 | 50.3 | **56.1** |
| Kimi-K2.6 | 65.9 | 76.7 | 54.0 | 62.3 | 19.9 | 26.3 | 43.9 | **49.9** |
| Qwen3.5-397B-A17B | 51.3 | 66.0 | 36.5 | 56.8 | 16.2 | 5.5 | 42.1 | **39.2** |
| Qwen3.6-35B-A3B | 44.9 | 63.3 | 32.5 | 55.8 | 10.7 | 10.3 | 38.9 | **36.6** |
| Qwen3.8-27B | 79.8 | 73.8 | 35.6 | 69.2 | 33.7 | 38.5 | 41.8 | **53.2** |
| **Skill-Based Environment Synthesis** | | | | | | | | |
| FACET-Terminal-Qwen3.5-27B | 47.6 | - | - | - | - | - | - | - |
| **Skill2Env (ours / 35B-A3B)** | 58.4 | 71.0 | 46.9 | 61.3 | 15.1 | 17.7 | 44.8 | **45.0** |
| *Gain over baseline* | **(+13.5)** | **(+7.7)** | **(+14.3)** | **(+5.5)** | **(+4.5)** | **(+7.3)** | **(+5.9)** | **(+8.4)** |

Avg. is the unweighted mean across the seven benchmarks. Scores are rounded to one decimal place for display. Reported gains are computed from the unrounded scores before rounding.

**Evaluation protocol.** We use Terminus-2 for Terminal-Bench 2.1, mini-SWE-agent for SWE-bench Multilingual, OpenHands with skills enabled for SkillsBench, and the native agent loop for Claw-Eval. We report success rate for Terminal-Bench 2.1, resolved rate for SWE-bench Multilingual, Avg@3 for SkillsBench, Pass³ for Claw-Eval, Pass¹ for τ³-Banking, pass rate for AutomationBench (v1.0.6), and mean score for VitaBench. FACET results are source-reported.

## Model Description

- **Base model:** [Qwen/Qwen3.6-35B-A3B](https://huggingface.co/Qwen/Qwen3.6-35B-A3B) (35B total parameters, 3B activated, MoE with vision encoder, 262,144-token context)
- **Training data:** 1.5K SFT trajectories
- **Format:** Hugging Face Transformers (compatible with Transformers, vLLM, SGLang, KTransformers, etc.)

## Quickstart

### vLLM

```shell
uv pip install vllm --torch-backend=auto

vllm serve AllSpark-Research/Skill2Env \
  --port 8000 \
  --tensor-parallel-size 8 \
  --max-model-len 262144 \
  --enable-auto-tool-choice \
  --tool-call-parser qwen3_coder \
  --reasoning-parser qwen3
```

### SGLang

```shell
uv pip install sglang[all]

python -m sglang.launch_server --model-path AllSpark-Research/Skill2Env \
  --port 8000 --tp-size 8 --mem-fraction-static 0.8 \
  --context-length 262144 --reasoning-parser qwen3 --tool-call-parser qwen3_coder
```

### Transformers

```python
from transformers import AutoModelForImageTextToText, AutoProcessor

model = AutoModelForImageTextToText.from_pretrained(
    "AllSpark-Research/Skill2Env", torch_dtype="auto", device_map="auto"
)
processor = AutoProcessor.from_pretrained("AllSpark-Research/Skill2Env")
```

> [!Note]
> The model has a default context length of 262,144 tokens. We advise maintaining a context length of at least 128K tokens to preserve thinking capabilities.


## License

This model is released under the [Apache 2.0 license](https://huggingface.co/Qwen/Qwen3.6-35B-A3B/blob/main/LICENSE), inherited from the base model.

## Citation

If you find this work useful, please cite:

```bibtex
@article{xu2026skill2env,
  title={Skill2Env: Capability-Oriented Environment Synthesis from Skills for General Agents},
  author={Xu, Weiyi and Yang, Xiaowen and Da, Wen and Xu, Hang and Li, Canwei and You, Hongjie and Dong, Pusen and Zeng, Yucheng and Luo, Zhaokai and Chuan, Mu},
  journal={arXiv preprint arXiv:2609.33772},
  year={2026}
}
```
