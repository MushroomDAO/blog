---
license: apache-2.0
license_link: https://huggingface.co/qvac/BotPsy-0.8B/blob/main/LICENSE
language:
- en
library_name: transformers
pipeline_tag: text-generation
base_model:
- Qwen/Qwen3.5-0.8B
base_model_relation: finetune
tags:
- tool-calling
- function-calling
- agent
- agentic
- on-device
- edge
- qwen3_5
- tether-ai
- qvac
---

# BotPsy-0.8B

**BotPsy-0.8B** is a 0.8B-parameter model designed for function calling and agentic workflows, built on top of [Qwen3.5-0.8B](https://huggingface.co/Qwen/Qwen3.5-0.8B) and suitable for on-device deployment. BotPsy is a "personal assistant" that uses tools to perform a variety of simple tasks for the user, in domains such as web search & research, travel & lifestyle, commerce & finance, business & customer operations, device & vehicle control, files & documents, calendar, and email & messaging. Due to its small parameter count, it is best suited to tasks of low to medium difficulty. BotPsy achieves state-of-the-art (SOTA) tool-use and agentic performance for its size, outperforming every model of up to 1.2B parameters that we tested. As a small model, BotPsy still makes mistakes and is best suited to tasks of low to medium difficulty; please read the [Intended Use and Limitations](#intended-use-and-limitations) section for more information.

This repository holds the BF16 weights in Hugging Face safetensors format. GGUF files (BF16, Q8_0 and Q4_K_M) for llama.cpp and the QVAC SDK are in [qvac/BotPsy-0.8B-GGUFs](https://huggingface.co/qvac/BotPsy-0.8B-GGUFs). The full write-up, with every benchmark and the training method, is the [BotPsy blog post](https://huggingface.co/blog/qvac/botpsy).

| | |
|:---|:---|
| **Developed by** | [Tether AI Research](https://tether.io/)<sup>*</sup> |
| **Model type** | Causal language model for tool calling (Qwen3.5 architecture: hybrid Gated DeltaNet + gated attention), used text-only |
| **Parameters** | 0.8B |
| **Base model** | [Qwen3.5-0.8B](https://huggingface.co/Qwen/Qwen3.5-0.8B) |
| **Reasoning** | Thinks before it answers (thinking mode, `enable_thinking=True`) |
| **Language** | English (recommended) |
| **Precision** | BF16 (this repository); BF16, Q8_0 and Q4_K_M GGUF in [BotPsy-0.8B-GGUFs](https://huggingface.co/qvac/BotPsy-0.8B-GGUFs) |
| **License** | [Apache 2.0](https://huggingface.co/qvac/BotPsy-0.8B/blob/main/LICENSE) |
| **Blog post** | [BotPsy on Hugging Face](https://huggingface.co/blog/qvac/botpsy) |
| **Collection** | [BotPsy](https://huggingface.co/collections/qvac/botpsy) |

<sup>*</sup> References to Tether AI Research are references to Tether Data, S.A. de C.V.

## Key Highlights

### Benchmark results
- **Twice the performance of its base model:** BotPsy roughly doubles the agentic capability of Qwen3.5-0.8B-Think on key benchmarks: BFCL v4 rises from 23.4 to 44.0, ACEBench from 30.1 to 58.7, and τ-bench from 23.2 to 51.5 (mean of the retail, telecom and banking subsets).
- **Best agent in its category:** BotPsy outperforms leading models in the ≤1.2B-parameter weight class (Qwen3.5-0.8B-Think, LFM2.5-1.2B-Think, MiniCPM5-1B-Think) on all six tool-use and agentic benchmarks: BFCL v4, ACEBench, τ-bench, ToolSandbox, Claw-Eval and BrowseComp-Plus.
- **Outperforms its larger sibling:** BotPsy has the highest score of all models tested on five of the six benchmarks, beating Qwen3.5-2B-Think, a model 2.5× its size, on BFCL v4 (44.0 vs 37.7), ACEBench (58.7 vs 55.4), τ-bench (51.5 vs 46.5), ToolSandbox (64.6 vs 41.2) and BrowseComp-Plus (4.5 vs 2.8). Only on Claw-Eval does Qwen3.5-2B-Think lead (48.9 vs 46.5).

### Model capabilities
- **More reliable in multi-turn workflows:** On τ²-bench, where the agent must hold a long customer conversation, follow a strict policy, and act on the customer's behalf, it scores 82.5 in telecom, ahead of Qwen3.5-2B-Think (69.3). On BFCL v4's multi-turn tasks, it rises from 7.5 to 46.1 over its base, nearly double Qwen3.5-2B-Think (23.8). Grouped by application, its multi-step scores lead all models tested in commerce and services (58.3 vs 47.4 for the next best, Qwen3.5-2B-Think) and in device and system management (46.1 vs 31.9).
- **Knows when (not) to call tools:** An agent that acts must also know when not to act. On BFCL v4's hallucination tests, which check that the model declines when no appropriate tool exists, BotPsy scores 86.1, the highest of all models tested. On ACEBench's special cases, where the request is incomplete, contains wrong parameters, or cannot be served by the given tools, it scores 51.3, up from 13.7 for its base model.
- **Follows instructions while preserving knowledge:** BotPsy specializes in tool use while preserving general skills. Instruction following improves sharply, with IFEval rising from 59.7 to 90.8 and IFBench from 22.0 to 55.9, the highest IFBench score of all models tested. General knowledge also improves, with GPQA Diamond rising from 33.2 to 38.1 and MMLU-Pro from 41.6 to 48.9. On all four benchmarks, BotPsy outperforms every other model of 1.2B parameters or fewer that we tested.

## Benchmark Results

All five models were evaluated in thinking mode with one shared evaluation harness. BotPsy was served from these BF16 weights with vLLM. Best score per row in **bold**, second best <u>underlined</u>; multipliers give parameter count relative to BotPsy-0.8B.

| Benchmark | **BotPsy-0.8B**<br><sub>ours</sub> | Qwen3.5-0.8B-Think<br><sub>base · 1×</sub> | Qwen3.5-2B-Think<br><sub>2.5×</sub> | LFM2.5-1.2B-Think<br><sub>1.5×</sub> | MiniCPM5-1B-Think<br><sub>1.25×</sub> |
| :--- | :---: | :---: | :---: | :---: | :---: |
| ***Tool use & agents*** | | | | | |
| BFCL v4¹ | **44.0** | 23.4 | <u>37.7</u> | 28.1 | 22.8 |
| ACEBench² | **58.7** | 30.1 | <u>55.4</u> | 39.4 | 24.5 |
| τ-bench³ | **51.5** | 23.2 | <u>46.5</u> | 6.5 | 28.8 |
| Claw-Eval⁴ | <u>46.5</u> | 39.3 | **48.9** | 31.6 | 31.0 |
| BrowseComp-Plus⁵ | **4.5** | 1.9 | <u>2.8</u> | 0.2 | 0.8 |
| ToolSandbox⁶ | **64.6** | 30.5 | 41.2 | <u>45.7</u> | 28.1 |
| *Average* | ***45.0*** | *24.7* | *<u>38.8</u>* | *25.3* | *22.7* |
| ***Knowledge*** | | | | | |
| GPQA Diamond⁷ | <u>38.1</u> | 33.2 | **59.9** | 35.0 | 15.8 |
| MMLU-Pro⁸ | <u>48.9</u> | 41.6 | **65.5** | 39.4 | 40.0 |
| ***Instruction following*** | | | | | |
| IFEval⁹ | **90.8** | 59.7 | 80.0 | <u>85.6</u> | 78.4 |
| IFBench⁹ | **55.9** | 22.0 | <u>40.9</u> | 33.9 | 40.6 |
| Multi-IF¹⁰ | <u>67.2</u> | 43.2 | 66.9 | **68.2** | 53.4 |

<details>
<summary>Evaluation footnotes</summary>

- All scores are percentages (higher is better).
- All models were evaluated in thinking (reasoning) mode.
- All benchmarks that use an external API were run on **November 3, 2026**.
- ¹ BFCL v4: overall score calculated using the official weighted formula (40% Agentic, 30% Multi-Turn, 10% Live, 10% Non-Live, and 10% Hallucination), averaged over 3 runs.
- ² ACEBench: overall accuracy. All models were evaluated in function-calling (FC) mode; mean of 2 runs.
- ³ τ-bench: average of τ²-bench (retail, telecom) and τ³-bench (banking), excluding airline; mean of 3 runs.
- ⁴ Claw-Eval: official average task score, where each task scores safety × (0.8 × completion + 0.2 × robustness); mean of 3 runs.
- ⁵ BrowseComp-Plus: accuracy, with a maximum of 30 steps for all models.
- ⁶ ToolSandbox: mean similarity score over 8 settings.
- ⁷ GPQA Diamond: accuracy over all 198 questions, mean of 3 runs, thinking enabled.
- ⁸ MMLU-Pro: accuracy.
- ⁹ IFEval, IFBench: prompt-level strict accuracy.
- ¹⁰ Multi-IF: average of 3 runs.

</details>

BotPsy's weaker spots are open-ended search and a few areas where Qwen3.5-2B-Think still leads: BrowseComp-Plus deep research (4.5, the best of the five but low in absolute terms), BFCL web search (14.0) and memory (16.3), Claw-Eval, and ACEBench's special cases. On τ³-banking no model gets above 5. Knowledge still scales mainly with parameter count, so BotPsy is designed to call tools for facts it does not know, not to serve as a knowledge model. See the [blog post](https://huggingface.co/blog/qvac/botpsy) for the multi-turn, app-level and efficiency analyses.

## Training

BotPsy is based on Qwen3.5-0.8B and is post-trained in four stages: supervised fine-tuning, multi-teacher on-policy distillation, and two rounds of reinforcement learning. See the [blog post (Methodology)](https://huggingface.co/blog/qvac/botpsy#methodology) for the training recipe and data composition. Training code and training data are not part of this release; the datasets used are listed under [Licensing](#licensing).

## Usage

BotPsy keeps the Qwen3.5 architecture, so Hugging Face Transformers, vLLM and llama.cpp run it without custom code. Two settings matter.

- **Turn thinking on.** BotPsy was trained and evaluated in thinking mode. The chat template defaults to non-thinking, so pass `enable_thinking=True`.
- **Sampling.** Our evaluations used `temperature=0.3`, `top_p=0.95`, `top_k=20`, `presence_penalty=1.5` and up to 32,768 new tokens. `generation_config.json` sets the first three; presence penalty is available in vLLM and llama.cpp.

### Transformers

Requires a `transformers` release with Qwen3.5 support (tested with 5.19.0). Install `flash-linear-attention` and `causal-conv1d` for the fast Gated DeltaNet kernels; without them Transformers falls back to a slower reference implementation.

```python
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

model_id = "qvac/BotPsy-0.8B"
tokenizer = AutoTokenizer.from_pretrained(model_id)
device = "cuda" if torch.cuda.is_available() else "cpu"
model = AutoModelForCausalLM.from_pretrained(model_id, dtype=torch.bfloat16).to(device)

tools = [{
    "type": "function",
    "function": {
        "name": "create_event",
        "description": "Add an event to the user's calendar",
        "parameters": {
            "type": "object",
            "properties": {
                "title": {"type": "string"},
                "day": {"type": "string", "description": "Day of the week"},
                "time": {"type": "string", "description": "Start time, 24h HH:MM"},
            },
            "required": ["title", "day", "time"],
        },
    },
}]
messages = [{"role": "user", "content": "Add the dentist on Friday at 3 pm."}]

inputs = tokenizer.apply_chat_template(
    messages, tools=tools, add_generation_prompt=True, enable_thinking=True,
    return_dict=True, return_tensors="pt",
).to(model.device)
out = model.generate(**inputs, max_new_tokens=4096)  # sampling from generation_config.json
print(tokenizer.decode(out[0, inputs["input_ids"].shape[1]:], skip_special_tokens=True))
```

The answer ends with a tool call in the Qwen3.5 XML format:

```
<tool_call>
<function=create_event>
<parameter=title>
Dentist
</parameter>
...
</function>
</tool_call>
```

### vLLM (OpenAI-compatible server)

```bash
vllm serve qvac/BotPsy-0.8B --language-model-only \
    --enable-auto-tool-choice --tool-call-parser qwen3_xml --reasoning-parser qwen3
```

```python
from openai import OpenAI

client = OpenAI(base_url="http://localhost:8000/v1", api_key="EMPTY")
resp = client.chat.completions.create(
    model="qvac/BotPsy-0.8B",
    messages=[{"role": "user", "content": "Add the dentist on Friday at 3 pm."}],
    tools=tools,  # same list as in the Transformers example
    temperature=0.3, top_p=0.95, presence_penalty=1.5, max_tokens=8192,
    extra_body={"top_k": 20, "chat_template_kwargs": {"enable_thinking": True}},
)
print(resp.choices[0].message.tool_calls)
```

### llama.cpp and the QVAC SDK

Use the GGUF files in [qvac/BotPsy-0.8B-GGUFs](https://huggingface.co/qvac/BotPsy-0.8B-GGUFs); its model card has llama.cpp and QVAC SDK examples.

## Intended Use and Limitations

BotPsy has been developed to advance the state of the art and to support research and educational uses. Models developed based on our work could be suitable for tasks in domains such as device & system management (settings, files & documents, clocks & alarms), personal productivity & work (calendar & tasks, email, collaboration tools), communication (messaging), information retrieval & research (web search, weather, news), media & lifestyle (video, music, recipes & fitness, photos) and commerce & services (maps & travel, finance, shopping & delivery). Due to its small parameter count, it is best suited to tasks of low to medium difficulty.

BotPsy has been primarily trained and tested in English, which is the recommended language. It has also been evaluated on Multi-IF, which covers seven additional languages (Chinese, French, Hindi, Italian, Portuguese, Russian and Spanish): it performs well in most of them, but scores much lower in Hindi and Russian. BotPsy is a small language model, and it makes mistakes. It is not intended for safety-critical or high-stakes automated decisions, or for applications involving money, personal information, health and other sensitive topics.

## Related Resources

- [BotPsy blog post](https://huggingface.co/blog/qvac/botpsy): methodology, all benchmarks, app-level breakdown, inference efficiency
- [BotPsy-0.8B-GGUFs](https://huggingface.co/qvac/BotPsy-0.8B-GGUFs): BF16, Q8_0 and Q4_K_M GGUF files for llama.cpp and the QVAC SDK
- [BotPsy collection](https://huggingface.co/collections/qvac/botpsy)
- [QVAC SDK](https://qvac.tether.io/dev/sdk/): on-device AI deployment framework
- [Qwen3.5-0.8B](https://huggingface.co/Qwen/Qwen3.5-0.8B): base model

## Citation

```bibtex
@misc{botpsy2026,
  title        = {BotPsy: On-Device Personal Assistant with a Sub-Billion-Parameter Agentic Language Model},
  author       = {Tether Data, S.A. de C.V. d.b.a. Tether AI Research},
  year         = {2026},
  howpublished = {Hugging Face blog},
  url          = {https://huggingface.co/blog/qvac/botpsy}
}
```

## Copyright Complaints

We will take appropriate actions in response to notice of copyright infringement. If you believe your work has been used or copied in a manner that infringes upon your intellectual property rights, please email [data-apps@tether.io](mailto:data-apps@tether.io) identifying and describing both the copyrighted work and alleged infringing content to file a notice of infringement.

## Licensing

This model which was trained as described in the [blog post](https://huggingface.co/blog/qvac/botpsy) is licensed by Tether Data, S.A. de C.V. under the [Apache 2.0](https://huggingface.co/datasets/choosealicense/licenses/blob/main/markdown/apache-2.0.md) license. As described in the blog post, this model is a version of the Qwen3.5-0.8B (Thinking) model ([https\://huggingface.co/Qwen/Qwen3.5-0.8B](https://huggingface.co/Qwen/Qwen3.5-0.8B)) which is licensed under the Apache 2.0 license ([https\://choosealicense.com/licenses/apache-2.0/](https://choosealicense.com/licenses/apache-2.0/)).

As described in the blog post, the Qwen3.5-4B model ([https\://huggingface.co/Qwen/Qwen3.5-4B](https://huggingface.co/Qwen/Qwen3.5-4B)) which is licensed under the Apache 2.0 license ([https\://choosealicense.com/licenses/apache-2.0/](https://choosealicense.com/licenses/apache-2.0/)) was put through three different reinforcement learning processes to create three versions of the model and each of those three versions of the model were then used as a teacher model.

Only subsets of some of the datasets listed below were used.

One version of the teacher model used the following datasets:

1) Nemotron-RL-Agentic-Conversational-Tool-Use-Pivot-v1 dataset	([https\://huggingface.co/datasets/nvidia/Nemotron-RL-Agentic-Conversational-Tool-Use-Pivot-v1](https://huggingface.co/datasets/nvidia/Nemotron-RL-Agentic-Conversational-Tool-Use-Pivot-v1)) made available under the CC-BY 4.0 (Creative Commons Attribution 4.0 International) license ([https\://choosealicense.com/licenses/cc-by-4.0/](https://choosealicense.com/licenses/cc-by-4.0/));
2) Tool N1 dataset ([https\://github.com/NVlabs/Tool-N1](https://github.com/NVlabs/Tool-N1)) made available under the Apache 2.0 license ([https\://github.com/NVlabs/Tool-N1/blob/master/LICENSE](https://github.com/NVlabs/Tool-N1/blob/master/LICENSE));
3) SuperGPQA dataset ([https\://huggingface.co/datasets/m-a-p/SuperGPQA](https://huggingface.co/datasets/m-a-p/SuperGPQA)) made available under the ODC-BY (Open Data Commons Attribution License v1.0) license ([https\://opendatacommons.org/licenses/by/1-0/](https://opendatacommons.org/licenses/by/1-0/));
4) Nemotron-RL-instruction\_following dataset ([https\://huggingface.co/datasets/nvidia/Nemotron-RL-instruction\_following](https://huggingface.co/datasets/nvidia/Nemotron-RL-instruction_following)) made available under the ODC-BY (Open Data Commons Attribution License v1.0) license ([https\://opendatacommons.org/licenses/by/1-0/](https://opendatacommons.org/licenses/by/1-0/));
5) xlam-irrelevance-7.5k dataset ([https\://huggingface.co/datasets/MadeAgents/xlam-irrelevance-7.5k](https://huggingface.co/datasets/MadeAgents/xlam-irrelevance-7.5k)) made available under the CC-BY 4.0 (Creative Commons Attribution 4.0 International) license ([https\://choosealicense.com/licenses/cc-by-4.0/](https://choosealicense.com/licenses/cc-by-4.0/));
6) When2Call dataset ([https\://huggingface.co/datasets/nvidia/When2Call](https://huggingface.co/datasets/nvidia/When2Call)) made available under the CC-BY 4.0 (Creative Commons Attribution 4.0 International) license ([https\://choosealicense.com/licenses/cc-by-4.0/](https://choosealicense.com/licenses/cc-by-4.0/));
7) ToolRL dataset ([https\://github.com/qiancheng0/ToolRL](https://github.com/qiancheng0/ToolRL)) made available under the Apache 2.0 license ([https\://github.com/qiancheng0/ToolRL?tab=Apache-2.0-1-ov-file](https://github.com/qiancheng0/ToolRL?tab=Apache-2.0-1-ov-file)); and
8) Nemotron-RL-Agentic-Function-Calling-Pivot-v1 dataset ([https\://huggingface.co/datasets/nvidia/Nemotron-RL-Agentic-Function-Calling-Pivot-v1](https://huggingface.co/datasets/nvidia/Nemotron-RL-Agentic-Function-Calling-Pivot-v1)) made available under the CC-BY 4.0 (Creative Commons Attribution 4.0 International) license ([https\://choosealicense.com/licenses/cc-by-4.0/](https://choosealicense.com/licenses/cc-by-4.0/)).

One version of the teacher model used the following datasets:

1) Nemotron-RL-knowledge-mcqa dataset ([https\://huggingface.co/datasets/nvidia/Nemotron-RL-knowledge-mcqa](https://huggingface.co/datasets/nvidia/Nemotron-RL-knowledge-mcqa)) made available under the CC-BY 4.0 (Creative Commons Attribution 4.0 International) license ([https\://choosealicense.com/licenses/cc-by-4.0/](https://choosealicense.com/licenses/cc-by-4.0/)); and
2) SuperGPQA dataset ([https\://huggingface.co/datasets/m-a-p/SuperGPQA](https://huggingface.co/datasets/m-a-p/SuperGPQA)) made available under the ODC-BY (Open Data Commons Attribution License v1.0) license ([https\://opendatacommons.org/licenses/by/1-0/](https://opendatacommons.org/licenses/by/1-0/)).

One version of the teacher model used the following datasets:

1) Nemotron-RL-instruction\_following dataset ([https\://huggingface.co/datasets/nvidia/Nemotron-RL-instruction\_following](https://huggingface.co/datasets/nvidia/Nemotron-RL-instruction_following)) made available under the CC-BY 4.0 (Creative Commons Attribution 4.0 International) license ([https\://choosealicense.com/licenses/cc-by-4.0/](https://choosealicense.com/licenses/cc-by-4.0/));
2) Nemotron-RL-Instruction-Following-Calendar-v2 dataset ([https\://huggingface.co/datasets/nvidia/Nemotron-RL-Instruction-Following-Calendar-v2](https://huggingface.co/datasets/nvidia/Nemotron-RL-Instruction-Following-Calendar-v2)) made available under the CC-BY 4.0 (Creative Commons Attribution 4.0 International) license ([https\://choosealicense.com/licenses/cc-by-4.0/](https://choosealicense.com/licenses/cc-by-4.0/)); and
3) Nemotron-RL-instruction\_following-structured\_outputs dataset ([https\://huggingface.co/datasets/nvidia/Nemotron-RL-instruction\_following-structured\_outputs](https://huggingface.co/datasets/nvidia/Nemotron-RL-instruction_following-structured_outputs)) made available under the CC-BY 4.0 (Creative Commons Attribution 4.0 International) license ([https\://choosealicense.com/licenses/cc-by-4.0/](https://choosealicense.com/licenses/cc-by-4.0/)).

As described in the blog post, the model was fine tuned using the teacher models described above and the following datasets:

1) AReaL\_tau2 dataset ([https\://huggingface.co/datasets/inclusionAI/AReaL-tau2-data](https://huggingface.co/datasets/inclusionAI/AReaL-tau2-data)) made available under the Apache 2.0 license ([https\://huggingface.co/datasets/choosealicense/licenses/blob/main/markdown/apache-2.0.md](https://huggingface.co/datasets/choosealicense/licenses/blob/main/markdown/apache-2.0.md));
2) EnvFactory-SFT-FILTERED dataset ([https\://huggingface.co/datasets/LARK-Lab/EnvFactory-SFT-FILTERED](https://huggingface.co/datasets/LARK-Lab/EnvFactory-SFT-FILTERED)) made available under the Apache 2.0 license ([https\://huggingface.co/datasets/choosealicense/licenses/blob/main/markdown/apache-2.0.md](https://huggingface.co/datasets/choosealicense/licenses/blob/main/markdown/apache-2.0.md));
3) xlam-function-calling-60k dataset ([https\://huggingface.co/datasets/Salesforce/xlam-function-calling-60k](https://huggingface.co/datasets/Salesforce/xlam-function-calling-60k)) made available under the  CC-BY 4.0 (Creative Commons Attribution 4.0 International) license ([https\://choosealicense.com/licenses/cc-by-4.0/](https://choosealicense.com/licenses/cc-by-4.0/));
4) glaive-function-calling-v2 dataset ([https\://huggingface.co/datasets/glaiveai/glaive-function-calling-v2](https://huggingface.co/datasets/glaiveai/glaive-function-calling-v2)) made available under the Apache 2.0 license ([https\://huggingface.co/datasets/choosealicense/licenses/blob/main/markdown/apache-2.0.md](https://huggingface.co/datasets/choosealicense/licenses/blob/main/markdown/apache-2.0.md));
5) ToolACE dataset ([https\://huggingface.co/datasets/Team-ACE/ToolACE](https://huggingface.co/datasets/Team-ACE/ToolACE)) made available under the Apache 2.0 license ([https\://huggingface.co/datasets/choosealicense/licenses/blob/main/markdown/apache-2.0.md](https://huggingface.co/datasets/choosealicense/licenses/blob/main/markdown/apache-2.0.md));
6) When2call\_v2 dataset ([https\://huggingface.co/datasets/nvidia/When2Call](https://huggingface.co/datasets/nvidia/When2Call)) made available under the CC-BY 4.0 (Creative Commons Attribution 4.0 International) license ([https\://creativecommons.org/licenses/by/4.0/legalcode](https://creativecommons.org/licenses/by/4.0/legalcode));
7) Nemotron-SFT-Agentic-v2 dataset ([https\://huggingface.co/datasets/nvidia/Nemotron-SFT-Agentic-v2](https://huggingface.co/datasets/nvidia/Nemotron-SFT-Agentic-v2)) made available under the CC-BY 4.0 (Creative Commons Attribution 4.0 International) license ([https\://huggingface.co/datasets/choosealicense/licenses/blob/main/markdown/cc-by-4.0.md](https://huggingface.co/datasets/choosealicense/licenses/blob/main/markdown/cc-by-4.0.md));
8) Infinity-Instruct dataset ([https\://huggingface.co/datasets/BAAI/Infinity-Instruct](https://huggingface.co/datasets/BAAI/Infinity-Instruct)) made available under the CC-BY 4.0 (Creative Commons Attribution 4.0 International) license ([https\://huggingface.co/datasets/choosealicense/licenses/blob/main/markdown/cc-by-sa-4.0.md](https://huggingface.co/datasets/choosealicense/licenses/blob/main/markdown/cc-by-sa-4.0.md));
9) toolbench\_v1 dataset ([https\://huggingface.co/datasets/tuandunghcmut/toolbench-v1](https://huggingface.co/datasets/tuandunghcmut/toolbench-v1)) made available under the Apache 2.0 license ([https\://huggingface.co/datasets/choosealicense/licenses/blob/main/markdown/apache-2.0.md](https://huggingface.co/datasets/choosealicense/licenses/blob/main/markdown/apache-2.0.md));
10) ToolMind dataset ([https\://huggingface.co/datasets/Nanbeige/ToolMind](https://huggingface.co/datasets/Nanbeige/ToolMind)) made available under the Apache 2.0 license ([https\://huggingface.co/datasets/choosealicense/licenses/blob/main/markdown/apache-2.0.md](https://huggingface.co/datasets/choosealicense/licenses/blob/main/markdown/apache-2.0.md));
11) Toucan-1.5M dataset (https\://huggingface.co/datasets/Agent-Ark/Toucan-1.5M) made available under the Apache 2.0 license ([https\://huggingface.co/datasets/choosealicense/licenses/blob/main/markdown/apache-2.0.md](https://huggingface.co/datasets/choosealicense/licenses/blob/main/markdown/apache-2.0.md));
12) an unpublished synthetic dataset generated by Tether Data using Qwen3.5-9B ([https\://huggingface.co/Qwen/Qwen3.5-9B](https://huggingface.co/Qwen/Qwen3.5-9B)) and Qwen3.6-27B ([https\://huggingface.co/Qwen/Qwen3.6-27B](https://huggingface.co/Qwen/Qwen3.6-27B)), both of which are licensed under the Apache-2.0 license ([https\://choosealicense.com/licenses/apache-2.0/](https://choosealicense.com/licenses/apache-2.0/)) and τ²-Bench made available under the MIT license ([https\://github.com/eligotts/tau2-bench?tab=License-1-ov-file](https://github.com/eligotts/tau2-bench?tab=License-1-ov-file));
13) xlam-irrelevance-7.5k dataset ([https\://huggingface.co/datasets/MadeAgents/xlam-irrelevance-7.5k](https://huggingface.co/datasets/MadeAgents/xlam-irrelevance-7.5k)) made available under the CC-BY 4.0 (Creative Commons Attribution 4.0 International) license ([https\://huggingface.co/datasets/choosealicense/licenses/blob/main/markdown/cc-by-4.0.md](https://huggingface.co/datasets/choosealicense/licenses/blob/main/markdown/cc-by-4.0.md));
14) ultrachat\_200k dataset ([https\://huggingface.co/datasets/HuggingFaceH4/ultrachat\_200k](https://huggingface.co/datasets/HuggingFaceH4/ultrachat_200k)) made available under the MIT license ([https\://huggingface.co/datasets/choosealicense/licenses/blob/main/markdown/mit.md](https://huggingface.co/datasets/choosealicense/licenses/blob/main/markdown/mit.md));
15) smoltalk2 dataset ([https\://huggingface.co/datasets/HuggingFaceTB/smoltalk2](https://huggingface.co/datasets/HuggingFaceTB/smoltalk2)) made available under the Apache 2.0 license  ([https\://huggingface.co/datasets/choosealicense/licenses/blob/main/markdown/apache-2.0.md](https://huggingface.co/datasets/choosealicense/licenses/blob/main/markdown/apache-2.0.md));
16) UltraData-SFT-2605 dataset ([https\://huggingface.co/datasets/openbmb/UltraData-SFT-2605](https://huggingface.co/datasets/openbmb/UltraData-SFT-2605)) made available under the Apache 2.0 license ([https\://choosealicense.com/licenses/apache-2.0/](https://choosealicense.com/licenses/apache-2.0/));
17) Nemotron-RL-Agentic-Conversational-Tool-Use-Pivot-v1 dataset ([https\://huggingface.co/datasets/nvidia/Nemotron-RL-Agentic-Conversational-Tool-Use-Pivot-v1](https://huggingface.co/datasets/nvidia/Nemotron-RL-Agentic-Conversational-Tool-Use-Pivot-v1)) made available under the CC-BY 4.0 (Creative Commons Attribution 4.0 International) license ([https\://choosealicense.com/licenses/cc-by-4.0/](https://choosealicense.com/licenses/cc-by-4.0/));
18) Tool N1 dataset ([https\://github.com/NVlabs/Tool-N1](https://github.com/NVlabs/Tool-N1)) made available under the Apache 2.0 license ([https\://github.com/NVlabs/Tool-N1/blob/master/LICENSE](https://github.com/NVlabs/Tool-N1/blob/master/LICENSE));
19) IF\_multi\_constraints\_upto5 dataset ([https\://huggingface.co/datasets/allenai/IF\_multi\_constraints\_upto5](https://huggingface.co/datasets/allenai/IF_multi_constraints_upto5)) made available under the ODC-BY (Open Data Commons Attribution License v1.0) license ([https\://opendatacommons.org/licenses/by/1-0/](https://opendatacommons.org/licenses/by/1-0/));
20) SuperGPQA dataset ([https\://huggingface.co/datasets/m-a-p/SuperGPQA](https://huggingface.co/datasets/m-a-p/SuperGPQA)) made available under the ODC-BY (Open Data Commons Attribution License v1.0) license ([https\://opendatacommons.org/licenses/by/1-0/](https://opendatacommons.org/licenses/by/1-0/));
21) Nemotron-RL-instruction\_following dataset ([https\://huggingface.co/datasets/nvidia/Nemotron-RL-instruction\_following](https://huggingface.co/datasets/nvidia/Nemotron-RL-instruction_following)) made available under the ODC-BY (Open Data Commons Attribution License v1.0) license ([https\://opendatacommons.org/licenses/by/1-0/](https://opendatacommons.org/licenses/by/1-0/));
22) xlam\_irrelevance-7.5K dataset ([https\://huggingface.co/datasets/MadeAgents/xlam-irrelevance-7.5k](https://huggingface.co/datasets/MadeAgents/xlam-irrelevance-7.5k)) made available under the CC-BY 4.0 (Creative Commons Attribution 4.0 International) license (https\://choosealicense.com/licenses/cc-by-4.0/);
23) Calendar-Scheduling-Dataset ([https\://huggingface.co/datasets/nvidia/Nemotron-RL-Instruction-Following-Calendar-v2](https://huggingface.co/datasets/nvidia/Nemotron-RL-Instruction-Following-Calendar-v2)) made available under the CC-BY 4.0 (Creative Commons Attribution 4.0 International) license ([https\://choosealicense.com/licenses/cc-by-4.0/](https://choosealicense.com/licenses/cc-by-4.0/));
24) When2Call dataset ([https\://huggingface.co/datasets/nvidia/When2Call](https://huggingface.co/datasets/nvidia/When2Call)) made available under the CC-BY 4.0 (Creative Commons Attribution 4.0 International) license (https\://choosealicense.com/licenses/cc-by-4.0/);
25) ToolRL dataset ([https\://github.com/qiancheng0/ToolRL](https://github.com/qiancheng0/ToolRL)) made available under the Apache 2.0 license ([https\://github.com/NVlabs/Tool-N1/blob/master/LICENSE](https://github.com/NVlabs/Tool-N1/blob/master/LICENSE));
26) Nemotron-RL-Agentic-Function-Calling-Pivot-v1 dataset ([https\://huggingface.co/datasets/nvidia/Nemotron-RL-Agentic-Function-Calling-Pivot-v1](https://huggingface.co/datasets/nvidia/Nemotron-RL-Agentic-Function-Calling-Pivot-v1)) made available under the CC-BY 4.0 (Creative Commons Attribution 4.0 International) license (https\://choosealicense.com/licenses/cc-by-4.0/);
27) DAPO-Math-17k dataset ([https\://huggingface.co/datasets/BytedTsinghua-SIA/DAPO-Math-17k](https://huggingface.co/datasets/BytedTsinghua-SIA/DAPO-Math-17k)) dataset made available under the Apache 2.0 license ([https\://github.com/NVlabs/Tool-N1/blob/master/LICENSE](https://github.com/NVlabs/Tool-N1/blob/master/LICENSE));
28) Skywork-OR1-RL-Data dataset ([https\://huggingface.co/datasets/Skywork/Skywork-OR1-RL-Data](https://huggingface.co/datasets/Skywork/Skywork-OR1-RL-Data)) made accessible on Huggingface at the foregoing link;
29) Nemotron-3-Nano-RL-Training-Blend dataset ([https\://huggingface.co/datasets/nvidia/Nemotron-3-Nano-RL-Training-Blend](https://huggingface.co/datasets/nvidia/Nemotron-3-Nano-RL-Training-Blend)) made available under the ODC-BY (Open Data Commons Attribution License v1.0) license (https\://opendatacommons.org/licenses/by/1-0/);
30) Nemotron-3-Nano-RL-Training-Blend dataset ([https\://huggingface.co/datasets/nvidia/Nemotron-3-Nano-RL-Training-Blend](https://huggingface.co/datasets/nvidia/Nemotron-3-Nano-RL-Training-Blend)) made available under the ODC-BY (Open Data Commons Attribution License v1.0) license ([https\://opendatacommons.org/licenses/by/1-0/](https://opendatacommons.org/licenses/by/1-0/)) which are a modified subset of the Nemotron-RL-knowledge-mcqa dataset ([https\://huggingface.co/datasets/nvidia/Nemotron-RL-knowledge-mcqa](https://huggingface.co/datasets/nvidia/Nemotron-RL-knowledge-mcqa)) made available under the CC-BY 4.0 (Creative Commons Attribution 4.0 International) license ([https\://choosealicense.com/licenses/cc-by-4.0/](https://choosealicense.com/licenses/cc-by-4.0/));
31) Nemotron-3-Nano-RL-Training-Blend dataset ([https\://huggingface.co/datasets/nvidia/Nemotron-3-Nano-RL-Training-Blend](https://huggingface.co/datasets/nvidia/Nemotron-3-Nano-RL-Training-Blend)) made available under the ODC-BY (Open Data Commons Attribution License v1.0) license ([https\://opendatacommons.org/licenses/by/1-0/](https://opendatacommons.org/licenses/by/1-0/)) which are a subset of the Nemotron-RL-coding-competitive\_coding dataset ([https\://huggingface.co/datasets/nvidia/Nemotron-RL-coding-competitive\_coding](https://huggingface.co/datasets/nvidia/Nemotron-RL-coding-competitive_coding)) made available under the CC-BY-SA 4.0 (Creative Commons Share Attribution Alike 4.0 International) ([https\://huggingface.co/datasets/choosealicense/licenses/blob/main/markdown/cc-by-sa-4.0.md](https://huggingface.co/datasets/choosealicense/licenses/blob/main/markdown/cc-by-sa-4.0.md));
32) Nemotron-3-Nano-RL-Training-Blend dataset ([https\://huggingface.co/datasets/nvidia/Nemotron-3-Nano-RL-Training-Blend](https://huggingface.co/datasets/nvidia/Nemotron-3-Nano-RL-Training-Blend)) made available under the ODC-BY (Open Data Commons Attribution License v1.0) license ([https\://opendatacommons.org/licenses/by/1-0/](https://opendatacommons.org/licenses/by/1-0/)) which are a subset of the Nemotron-RL-instruction\_following dataset ([https\://huggingface.co/datasets/nvidia/Nemotron-RL-instruction\_following](https://huggingface.co/datasets/nvidia/Nemotron-RL-instruction_following)) made available under the ODC-BY (Open Data Commons Attribution License v1.0) license ([https\://opendatacommons.org/licenses/by/1-0/](https://opendatacommons.org/licenses/by/1-0/));
33) Nemotron-3-Nano-RL-Training-Blend dataset ([https\://huggingface.co/datasets/nvidia/Nemotron-3-Nano-RL-Training-Blend](https://huggingface.co/datasets/nvidia/Nemotron-3-Nano-RL-Training-Blend)) made available under the ODC-BY (Open Data Commons Attribution License v1.0) license ([https\://opendatacommons.org/licenses/by/1-0/](https://opendatacommons.org/licenses/by/1-0/)) which are a subset of the Nemotron-RL-agent-workplace\_assistant dataset ([https\://huggingface.co/datasets/nvidia/Nemotron-RL-agent-workplace\_assistant](https://huggingface.co/datasets/nvidia/Nemotron-RL-agent-workplace_assistant)) made available under the CC-BY 4.0 (Creative Commons Attribution 4.0 International) license ([https\://choosealicense.com/licenses/cc-by-4.0/](https://choosealicense.com/licenses/cc-by-4.0/)); and
34) Nemotron-3-Nano-RL-Training-Blend dataset ([https\://huggingface.co/datasets/nvidia/Nemotron-3-Nano-RL-Training-Blend](https://huggingface.co/datasets/nvidia/Nemotron-3-Nano-RL-Training-Blend)) made available under the ODC-BY (Open Data Commons Attribution License v1.0) license ([https\://opendatacommons.org/licenses/by/1-0/](https://opendatacommons.org/licenses/by/1-0/)) which are a subset of the Nemotron-RL-instruction\_following-structured\_outputs dataset ([https\://huggingface.co/datasets/nvidia/Nemotron-RL-instruction\_following-structured\_outputs](https://huggingface.co/datasets/nvidia/Nemotron-RL-instruction_following-structured_outputs)) made available under the CC-BY 4.0 (Creative Commons Attribution 4.0 International) license ([https\://choosealicense.com/licenses/cc-by-4.0/](https://choosealicense.com/licenses/cc-by-4.0/)).

The full text of each license is reproduced in [ATTRIBUTIONS.md](https://huggingface.co/qvac/BotPsy-0.8B/blob/main/ATTRIBUTIONS.md).
