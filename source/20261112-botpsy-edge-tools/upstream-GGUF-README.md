---
license: apache-2.0
license_link: https://huggingface.co/qvac/BotPsy-0.8B-GGUFs/blob/main/LICENSE
language:
- en
library_name: gguf
pipeline_tag: text-generation
base_model:
- qvac/BotPsy-0.8B
base_model_relation: quantized
tags:
- tool-calling
- function-calling
- agent
- agentic
- on-device
- edge
- smartphone
- qwen3_5
- tether-ai
- qvac
- gguf
- quantized
- llama.cpp
---

# BotPsy-0.8B-GGUFs

**BotPsy-0.8B-GGUFs** provides GGUF weights of [BotPsy-0.8B](https://huggingface.co/qvac/BotPsy-0.8B) for fully on-device inference with [llama.cpp](https://github.com/ggml-org/llama.cpp) and the [QVAC SDK](https://qvac.tether.io/dev/sdk/). BotPsy is a 0.8B-parameter model designed for function calling and agentic workflows, built on top of Qwen3.5-0.8B. In BF16, it outperforms every model of up to 1.2B parameters that we tested on six tool-use and agentic benchmarks (see the [BotPsy-0.8B model card](https://huggingface.co/qvac/BotPsy-0.8B)). The repository holds three files: an unquantized **BF16** export (about 1.52 GB), near-lossless **Q8_0** (about 0.81 GB) and compact **Q4_K_M** with importance-matrix calibration (about 0.53 GB). As a small model, BotPsy still makes mistakes and is best suited to tasks of low to medium difficulty; please read the [Intended Use and Limitations](#intended-use-and-limitations) section for more information.

| | |
|:---|:---|
| **Developed by** | [Tether AI Research](https://tether.io/)<sup>*</sup> |
| **Model type** | Causal language model for tool calling (Qwen3.5 architecture), GGUF |
| **Source (BF16) model** | [BotPsy-0.8B](https://huggingface.co/qvac/BotPsy-0.8B) |
| **Base model** | [Qwen3.5-0.8B](https://huggingface.co/Qwen/Qwen3.5-0.8B) |
| **Language** | English (recommended) |
| **License** | [Apache 2.0](https://huggingface.co/qvac/BotPsy-0.8B-GGUFs/blob/main/LICENSE) |
| **Conversion and quantization** | [llama.cpp](https://github.com/ggml-org/llama.cpp) |
| **Blog post** | [BotPsy on Hugging Face](https://huggingface.co/blog/qvac/botpsy) |
| **Collection** | [BotPsy](https://huggingface.co/collections/qvac/botpsy) |

<sup>*</sup> References to Tether AI Research are references to Tether Data, S.A. de C.V.

## Available Files

| File | Format | Imatrix | Size | Recommended for |
|:---|:---:|:---:|:---:|:---|
| `botpsy-0.8b-bf16.gguf` | BF16 | n/a | 1.52 GB | Unquantized GGUF, same tensors as the source checkpoint |
| `botpsy-0.8b-q8_0.gguf` | Q8_0 | no | 0.81 GB | **Recommended**: scores like BF16 at about half the size |
| `botpsy-0.8b-q4_k_m-imat.gguf` | Q4_K_M | yes | 0.53 GB | Smallest file, for tight memory budgets; about 1.5 points lower on average |

The BF16 file is unquantized. Q8_0 does not use imatrix calibration. Q4_K_M uses importance-matrix (imatrix) calibration, which lowered its KL divergence from the BF16 model on held-out text from 0.048 (plain Q4_K_M) to 0.036; for reference, Q8_0 is at 0.001. The multi-token-prediction (MTP) layers of the base model are not included.

## Benchmark Results

We ran the same evaluation suite on each GGUF file with llama.cpp (`llama-server`, CUDA build b12169) and compared it with the BF16 source model served with vLLM, which gives the scores reported in the [blog post](https://huggingface.co/blog/qvac/botpsy). All runs used thinking mode and the same sampling settings (`temperature=0.3`, `top_p=0.95`, `top_k=20`, `presence_penalty=1.5`).

| Benchmark | BotPsy-0.8B<br><sub>BF16 · vLLM</sub> | BF16 GGUF<br><sub>llama.cpp</sub> | Q8_0<br><sub>llama.cpp</sub> | Q4_K_M (imatrix)<br><sub>llama.cpp</sub> |
| :--- | :---: | :---: | :---: | :---: |
| ***Tool use & agents*** | | | | |
| BFCL v4¹ | 44.0 | 44.6 | 44.2 | 43.5 |
| ACEBench | 58.7 | 58.8 | 58.0 | 57.3 |
| τ-bench² | 51.5 | 47.5 | 48.6 | 46.7 |
| Claw-Eval | 46.5 | 43.4 | 44.0 | 42.1 |
| BrowseComp-Plus | 4.5 | 4.2 | 4.7 | 4.5 |
| ***Knowledge*** | | | | |
| GPQA Diamond³ | 38.0 | 39.2 | 38.2 | 35.3 |
| MMLU-Pro | 48.9 | 46.0 | 46.1 | 42.5 |
| ***Instruction following*** | | | | |
| IFEval | 90.8 | 92.6 | 93.2 | 93.3 |
| IFBench | 55.9 | 58.7 | 60.6 | 56.3 |
| Multi-IF | 67.2 | 69.4 | 69.7 | 67.6 |
| *Average (10 benchmarks)* | *50.6* | *50.4* | *50.7* | *48.9* |

<details>
<summary>Evaluation footnotes</summary>

- All scores are percentages (higher is better). Metrics, run counts and benchmark settings follow the [blog post](https://huggingface.co/blog/qvac/botpsy#evaluation-footnotes), except where noted below.
- The llama.cpp runs were made on November 6–7, 2026, with `llama-server` on NVIDIA H100 GPUs. Benchmarks that use an external API (simulated users, judges, search) therefore ran on a different day than the vLLM reference (November 3, 2026).
- ToolSandbox was not run on the GGUF files.
- ¹ BFCL v4: one run for each GGUF file; the vLLM reference is the mean of 3 runs.
- ² τ-bench: average of τ²-bench (retail, telecom) and τ³-bench (banking), excluding airline; mean of 3 runs.
- ³ GPQA Diamond: the vLLM value is from the same evaluation round as the GGUF runs (38.0); the blog post reports 38.1.

</details>

**Key findings**

- **Q8_0 matches BF16.** Q8_0 averages 50.7 against 50.4 for the BF16 GGUF, at about half the size. It is within about one point on nine of the ten benchmarks; on IFBench it is 1.9 points higher.
- **Q4_K_M costs about 1.5 points on average.** Q4_K_M stays close on tool use (BFCL v4 43.5, ACEBench 57.3, τ-bench 46.7) but loses most on knowledge (MMLU-Pro −3.5 and GPQA Diamond −3.9 against the BF16 GGUF).
- **The engine matters more than the format.** The BF16 GGUF and the vLLM reference use the same weights, yet differ by a few points on some benchmarks (τ-bench −4.0, Claw-Eval −3.1, MMLU-Pro −2.9, IFBench +2.8). Because the BF16 GGUF is not quantized, these differences reflect the inference engine and run-to-run variance rather than quantization.

## Usage

BotPsy was trained and evaluated in **thinking mode**. The embedded chat template defaults to non-thinking, so turn thinking on as shown below. Recommended sampling: `temperature=0.3`, `top_p=0.95`, `top_k=20`, `presence_penalty=1.5`.

### llama.cpp

```bash
# Download the recommended file
hf download qvac/BotPsy-0.8B-GGUFs botpsy-0.8b-q8_0.gguf --local-dir .

# Start an OpenAI-compatible server with tool calling and thinking on
llama-server -m botpsy-0.8b-q8_0.gguf --jinja -c 32768 \
    --temp 0.3 --top-p 0.95 --top-k 20 --presence-penalty 1.5 \
    --chat-template-kwargs '{"enable_thinking": true}' --port 8080
```

```bash
curl -s http://localhost:8080/v1/chat/completions -H "Content-Type: application/json" -d '{
  "messages": [{"role": "user", "content": "Add the dentist on Friday at 3 pm."}],
  "tools": [{"type": "function", "function": {
    "name": "create_event",
    "description": "Add an event to the user'"'"'s calendar",
    "parameters": {"type": "object",
      "properties": {"title": {"type": "string"},
                     "day": {"type": "string", "description": "Day of the week"},
                     "time": {"type": "string", "description": "Start time, 24h HH:MM"}},
      "required": ["title", "day", "time"]}}}],
  "max_tokens": 8192
}'
```

The response carries the reasoning in `reasoning_content` and the call in `tool_calls`.

### QVAC SDK

These GGUF files run on the [QVAC SDK](https://qvac.tether.io/dev/sdk/) (tested with `@qvac/sdk` 0.23.0) for fully private on-device inference on phones, laptops and desktops. See the [QVAC documentation](https://docs.qvac.tether.io/sdk/getting-started/quickstart/) for integration guides.

```bash
# 1. Project setup
mkdir botpsy && cd botpsy
npm init -y && npm pkg set type=module

# 2. Install the SDK and the matching Bare runtime binary
#    (swap linux-x64 for: linux-arm64 | darwin-arm64 | darwin-x64 | win32-x64 | win32-arm64)
npm i @qvac/sdk bare-runtime-linux-x64

# 3. Authenticate with Hugging Face (one-time) and download the recommended file
hf auth login
hf download qvac/BotPsy-0.8B-GGUFs botpsy-0.8b-q8_0.gguf --local-dir ./models
```

```js
// 4. Save as botpsy.mjs and run: node botpsy.mjs
import { loadModel, completion, unloadModel, VERBOSITY } from "@qvac/sdk";
import { resolve } from "node:path";

const modelId = await loadModel({
  modelSrc: resolve("./models/botpsy-0.8b-q8_0.gguf"),
  modelType: "llamacpp-completion",
  modelConfig: {
    device: "gpu",        // "cpu" on machines without a supported GPU
    ctx_size: 8192,
    tools: true,          // render tools into the prompt and parse tool calls
    system_prompt: "",
    verbosity: VERBOSITY.ERROR,
  },
});

const tools = [{
  type: "function",
  name: "create_event",
  description: "Add an event to the user's calendar",
  parameters: {
    type: "object",
    properties: {
      title: { type: "string" },
      day: { type: "string", description: "Day of the week" },
      time: { type: "string", description: "Start time, 24h HH:MM" },
    },
    required: ["title", "day", "time"],
  },
}];

const run = completion({
  modelId,
  history: [{ role: "user", content: "Add the dentist on Friday at 3 pm." }],
  tools,
  stream: true,
  generationParams: {
    temp: 0.3, top_p: 0.95, top_k: 20, presence_penalty: 1.5,
    predict: 4096,
    reasoning_budget: -1,  // thinking on
  },
});
for await (const token of run.tokenStream) process.stdout.write(token);
for (const call of await run.toolCalls) {
  console.log(`\ntool call: ${call.name}(${JSON.stringify(call.arguments)})`);
}
await unloadModel({ modelId });
```

Notes:

- BotPsy writes a `<think>...</think>` block before it answers, so keep `predict` at 2,048 tokens or more.
- If `hf` is not installed: `pip install --user "huggingface_hub[cli,hf_xet]"`.

## Intended Use and Limitations

BotPsy has been developed to advance the state of the art and to support research and educational uses. Models developed based on our work could be suitable for tasks in domains such as device & system management (settings, files & documents, clocks & alarms), personal productivity & work (calendar & tasks, email, collaboration tools), communication (messaging), information retrieval & research (web search, weather, news), media & lifestyle (video, music, recipes & fitness, photos) and commerce & services (maps & travel, finance, shopping & delivery). Due to its small parameter count, it is best suited to tasks of low to medium difficulty.

BotPsy has been primarily trained and tested in English, which is the recommended language. It has also been evaluated on Multi-IF, which covers seven additional languages (Chinese, French, Hindi, Italian, Portuguese, Russian and Spanish): it performs well in most of them, but scores much lower in Hindi and Russian. BotPsy is a small language model, and it makes mistakes. It is not intended for safety-critical or high-stakes automated decisions, or for applications involving money, personal information, health and other sensitive topics.

Quantization can add small errors that aggregate benchmarks do not show, and these grow at lower bit counts. Prefer Q8_0 unless memory is tight.

## Related Resources

- [BotPsy-0.8B](https://huggingface.co/qvac/BotPsy-0.8B): BF16 source model in safetensors, with the full benchmark table
- [BotPsy blog post](https://huggingface.co/blog/qvac/botpsy): methodology, all benchmarks, app-level breakdown, inference efficiency
- [BotPsy collection](https://huggingface.co/collections/qvac/botpsy)
- [QVAC SDK](https://qvac.tether.io/dev/sdk/): on-device AI deployment framework
- [llama.cpp](https://github.com/ggml-org/llama.cpp): inference engine and quantization toolchain

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

The full text of each license is reproduced in [ATTRIBUTIONS.md](https://huggingface.co/qvac/BotPsy-0.8B-GGUFs/blob/main/ATTRIBUTIONS.md).
