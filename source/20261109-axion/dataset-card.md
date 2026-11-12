---
language:
- en
license: apache-2.0
size_categories:
- 10K<n<100K
task_categories:
- text-generation
- question-answering
pretty_name: Axion 1.0 Training Data
tags:
- agents
- scientific-reasoning
- tool-use
- supervised-fine-tuning
- reinforcement-learning
- datasets
configs:
- config_name: default
  default: true
  data_files:
  - split: stage1
    path: data/stage1-*.parquet
  - split: stage2
    path: data/stage2-*.parquet
- config_name: rl
  data_files:
  - split: train
    path: rl.parquet
---

<p align="center">
  <img src="assets/axion-card.svg" width="180" alt="Axion 1.0 logo">
</p>

<h1 align="center">Axion 1.0 Training Data</h1>

<p align="center">
  <b>Scientific reasoning and tool use for open agent foundation models.</b>
</p>

<p align="center">
  <a href="https://axion1-0.github.io/">Project Page</a> ·
  <a href="https://huggingface.co/papers/2611.03233">Paper (Hugging Face)</a> ·
  <a href="https://axion1-0.github.io/paper/axion.pdf">Paper (PDF)</a> ·
  <a href="https://github.com/bytedance/axion1_0">Code</a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/SFT_trajectories-18%2C363-2358d4" alt="18,363 SFT trajectories">
  <img src="https://img.shields.io/badge/RL_tasks-484-299bad" alt="484 RL tasks">
  <img src="https://img.shields.io/badge/Format-Parquet-69746d" alt="Parquet">
</p>

Axion 1.0 follows a three-stage training recipe: learn self-contained reasoning,
learn to acquire missing information through tools, then refine these abilities
through reinforcement learning. This repository contains the two SFT trajectory
splits and the RL training tasks used by the 122B R3 run.

## Dataset at a glance

| Configuration | Split | Records | Contents |
|---|---|---:|---|
| `default` | `stage1` | 10,819 | Self-contained scientific reasoning; Python execution, without retrieval |
| `default` | `stage2` | 7,544 | Verified tool-use trajectories for tasks constructed from public databases |
| `rl` | `train` | 484 | RL prompts, reference answers, and task metadata |

The two SFT splits contain **18,363 trajectories**. Each row is a complete
conversation, including its system prompt, reasoning, tool calls, tool responses,
and assistant messages. Tool responses are represented within `user` messages in
the released conversation format.

## Data construction

![Axion's two-stage data construction pipeline](assets/web_overview.svg)

**Stage I — learn to reason.** Model-aware construction strengthens self-contained
scientific problems. Solvers can use Python to carry out computations.

**Stage II — learn to investigate.** Tasks require external information, with
reference answers established through structured data and deterministic
computation. The released records contain the collected solution trajectories.

See the [paper](https://axion1-0.github.io/paper/axion.pdf) for the construction,
verification, training, and evaluation procedures.

## Browse the trajectories

Select the `default` configuration and the `stage1` or `stage2` split in the
Dataset Viewer. The table presents the question and the last assistant response
alongside the complete conversation.

| Column | Description |
|---|---|
| `id` | Stable identifier based on the stage and original row position |
| `question` | First `user` message, copied from the conversation |
| `response` | Last `assistant` message, retaining its original reasoning and answer tags |
| `num_messages` | Number of messages, including the system prompt and tool-response messages |
| `messages` | Complete ordered list of `{role, content}` objects |

`question` and `response` are browsing columns derived from `messages`. Use
`messages` to train on the complete multi-turn trajectory.

## Load the data

```python
from datasets import load_dataset

repo = "Axion1-0/axion-training-data"

stage1 = load_dataset(repo, name="default", split="stage1")
stage2 = load_dataset(repo, name="default", split="stage2")
rl_tasks = load_dataset(repo, name="rl", split="train")

conversation = stage2[0]["messages"]
```

The RL configuration has a separate schema: `prompt`, `reward_model`,
`rl_task_category`, `data_source`, and `extra_info`. It contains tasks and reference
answers, rather than completed SFT solution trajectories.

## Files

```text
assets/                    Logo and data-construction figure
data/stage1-*.parquet       Stage I SFT trajectories
data/stage2-*.parquet       Stage II SFT trajectories
rl.parquet                 RL training tasks
```

The repository distributes the complete SFT conversations and RL tasks in Parquet
format. The Dataset Viewer and loading examples read these files directly.

Environment-specific runtime path prefixes in a small number of tool outputs
have been normalized.

## Reference

[**Axion 1.0: Open Agent Foundation Models, Simplified**](https://huggingface.co/papers/2611.03233)

Yuqi Jia, Yunjie Tian, Jiayu Zheng, Yijun Liang, Jingchen Sun, Mengyu Zhao, and Di Fu.

[Project page](https://axion1-0.github.io/)

## License

This dataset is licensed under the [Apache License 2.0](LICENSE).
