---
license: apache-2.0
base_model: Qwen/Qwen3.8-27B
library_name: transformers
pipeline_tag: image-text-to-text
tags:
  - qsa
  - multimodal
  - custom_code
  - bf16
---
![Qwen3.8-27B + QSA teaser](https://huggingface.co/higa2515/Qwen3.8-27B-QSA-BF16/resolve/main/assets/qsa-teaser.jpg)

[QSA Paper](https://arxiv.org/abs/2608.30320) | [GitHub](https://github.com/kuraneko1/Qwen3.8-27B-QSA-llama.cpp) | [Engine + Build](https://github.com/kuraneko1/Qwen3.8-27B-QSA-llama.cpp#build-from-source) | [Runtime Guide](https://github.com/kuraneko1/Qwen3.8-27B-QSA-llama.cpp/blob/main/qsa27b/RUNTIME.md) | [GGUF Model Series](https://huggingface.co/higa2515/Qwen3.8-27B-QSA-GGUF) | [Unsloth GGUF](https://huggingface.co/unsloth/Qwen3.8-27B-GGUF) | [X](https://x.com/_ryu15_) | [License](https://huggingface.co/higa2515/Qwen3.8-27B-QSA-BF16/blob/main/LICENSE)

# Qwen3.8-27B QSA - BF16 source weights

The original 18 backbone, vision, and MTP shards are byte-for-byte unchanged from [Qwen/Qwen3.8-27B](https://huggingface.co/Qwen/Qwen3.8-27B/tree/1d4bf0f2ff6012fd82039f2fa52739d0dd7c60c0). This release adds 52,434,944 FP32 indexer parameters to the 16 full-attention layers. The other 48 decoder layers retain their original Gated DeltaNet architecture. Training left the backbone, vision encoder, projector, and MTP weights unchanged.

The original checkpoint is included as `indexers/qsa_indexers.pt`. It originates from [higa2515/qwen38-27b-qsa-indexers](https://huggingface.co/higa2515/qwen38-27b-qsa-indexers/tree/b51b8d15e4342f2bc11ad8419abc18e3be6a8c8a) and was trained for 300 steps at length 16,384 with a 50% multimodal mix and synthetic OCR, table, and shape tasks. The training source snapshot is included under `research/`.

## QSA in brief

Qwen Sparse Attention (QSA) uses a learned, compressed indexer to select context in four-token blocks. The 16 full-attention layers in this 27B adaptation use fixed K=2,048 plus the current block. All original KV entries are retained, so this is not KV-cache compression. The 12.5% figure describes K at 16k, not a constant ratio at every context length. The architecture reference is [*On the Design of Qwen3.8-Next Architecture: Evaluation, Efficiency, and Training Stability*](https://arxiv.org/abs/2608.30320).

![Architecture of the original Qwen3.8-27B and the QSA adaptation](https://huggingface.co/higa2515/Qwen3.8-27B-QSA-BF16/resolve/main/assets/qsa-architecture-en.png)

Original Qwen3.8-27B (left) and the QSA adaptation with 16 learned indexers (right).

## Quantized model series

The [GGUF model series](https://huggingface.co/higa2515/Qwen3.8-27B-QSA-GGUF) contains the Q8_0 conversion and three Unsloth mixed-precision variants. These are separate artifacts from this BF16 repository.

| Variant | Source | Size |
| --- | --- | ---: |
| Q8_0 | Conversion from this QSA BF16 release | 29.26 GB |
| Unsloth UD-Q4_K_M | Unsloth mixed-precision tensors plus the same FP32 indexers | 16.67 GB |
| Unsloth UD-Q5_K_M | Unsloth mixed-precision tensors plus the same FP32 indexers | 19.98 GB |
| Unsloth UD-Q6_K | Unsloth mixed-precision tensors plus the same FP32 indexers | 22.19 GB |

The Unsloth variants reuse 866 original tensors from [unsloth/Qwen3.8-27B-GGUF](https://huggingface.co/unsloth/Qwen3.8-27B-GGUF/tree/4ca720788d1e01f1bff70c033e0d0028fd02e502) byte-for-byte and add the same 80 FP32 QSA indexer tensors. No retraining or requantization was performed after adding the indexers. UD denotes mixed precision, not a uniform bit depth for every tensor.

## Two execution paths

The Transformers wrapper in this repository is a correctness reference. Text uses an SDPA mask, image and video conversations use dense attention, and MTP execution is not implemented. This wrapper does not provide native sparse-kernel speed.

For deployment, select a GGUF variant and use [Qwen3.8-27B QSA for llama.cpp](https://github.com/kuraneko1/Qwen3.8-27B-QSA-llama.cpp). The engine supports native text, image, and video QSA with M-RoPE, MTP with up to two draft tokens, and prefix-cache reuse. Stock llama.cpp does not support these QSA files. See the [runtime guide](https://github.com/kuraneko1/Qwen3.8-27B-QSA-llama.cpp/blob/main/qsa27b/RUNTIME.md) for model selection, build, and launch instructions.

When launching, set `QSA_MODEL` to the selected GGUF filename, for example:

```sh
QSA_MODEL=Qwen3.8-27B-QSA-Unsloth-UD-Q5_K_M.gguf QSA_MODEL_DIR=/path/to/gguf ./qsa27b-runtime/launch.sh
```

## Reference loading

Install `requirements.txt`. The captured Python environment used torch `2.14.1+cu126` and torchvision `0.29.1+cu126`; the native runtime separately uses CUDA 12.9. Inspect the packaged custom code before enabling it.

```python
from transformers import AutoModelForImageTextToText, AutoProcessor

path = "higa2515/Qwen3.8-27B-QSA-BF16"
processor = AutoProcessor.from_pretrained(path, trust_remote_code=True)
model = AutoModelForImageTextToText.from_pretrained(
    path, trust_remote_code=True, dtype="auto", device_map="auto",
    attn_implementation="sdpa",
)
```

## Restore the original model

`original/` contains the pinned official metadata, including the original config, weight index, processor, tokenizer, license, and model card. The additional QSA shard is excluded by the original index. After downloading this complete repository:

```sh
python restore_original.py --source . --output ../Qwen3.8-27B-original
```

The tool verifies all original LFS hashes and then creates a separate, dense, standard HF snapshot, hard-linking large unchanged weights where possible. It refuses to overwrite an existing output directory.

## Limited quality checks

### BF16 reference

These BF16 research-reference checks compare QSA with the original dense path. They are not Q8_0 native quality results.

| Check | Original dense | QSA | Observed comparison |
| --- | ---: | ---: | --- |
| Text PPL on 32,766 tokens, lower is better | 7.072960 | 7.071384 | QSA/dense ratio 0.99978 |
| Constructed 50-item four-choice DocVQA | 50/50 | 50/50 | 100% of the dense score on this probe |

The DocVQA probe is not standard open-ended DocVQA scoring. DocVQA was used for evaluation, not as the synthetic indexer training set. These small checks do not establish a general performance-retention percentage or broad quality equivalence.

Native image/video and cache probes passed, with limited multimodal checks through 64k. General multimodal quality at 128k/262k remains unverified.

### Unsloth Q4/Q5/Q6 text checks

A teacher-forced evaluation used six fixed windows, up to 65,024 input tokens, FP16 KV, and MTP disabled. PPL differences are QSA relative to dense within each quantized model.

| Variant | Overall PPL difference | 64k capture | Same-budget oracle | 64k prose PPL difference |
| --- | ---: | ---: | ---: | ---: |
| UD-Q4_K_M | -1.41% | 73.82% | 82.93% | +2.44% |
| UD-Q5_K_M | -0.47% | 73.76% | 82.91% | +1.97% |
| UD-Q6_K | -0.35% | 73.89% | 83.04% | +1.76% |

Capture measures attention mass, not task accuracy. These text-only checks do not establish general quality equivalence, free-generation quality, or a comparison with this BF16 model. See the [complete evaluation](https://huggingface.co/higa2515/Qwen3.8-27B-QSA-GGUF/tree/main/unsloth-qsa).

## Q8_0 throughput: QSA vs dense

The following results apply only to Q8_0, not to the Unsloth variants. The [GGUF engine](https://huggingface.co/higa2515/Qwen3.8-27B-QSA-GGUF) was measured against its dense Q8_0 control with the same weights, FP16 KV, MTP draft2, engine, and two sm70 32GB GPUs.

| Input tokens | QSA cold prefill | Dense cold prefill | QSA decode | Dense decode |
| ---: | ---: | ---: | ---: | ---: |
| 0 | 660.75 | 658.87 | 49.28 | 49.87 |
| 261,120 | 1071.53 | 366.84 | 41.07 | 22.91 |

All values are token/s. At 261,120 input tokens, QSA was 1.793x faster in decode and 2.921x faster in cold prefill. From each path's re-measured 0k point, mixed decode declined 16.66% for QSA and 54.06% for dense.

![Measured QSA and Dense prefill and decode throughput](https://huggingface.co/higa2515/Qwen3.8-27B-QSA-BF16/resolve/main/assets/qsa-vs-dense.png)

These are text-speed results, not long-context reasoning accuracy. QSA's nonzero-depth samples were retained from the earlier matched run, and the two paths were measured in separate sessions. See the [full comparison data and methodology](https://huggingface.co/higa2515/Qwen3.8-27B-QSA-GGUF/tree/main/benchmark).

## Credits and licenses

- [Qwen](https://huggingface.co/Qwen/Qwen3.8-27B): original model and the [QSA architecture paper](https://arxiv.org/abs/2608.30320).
- [Unsloth](https://github.com/unslothai/unsloth) and the [Unsloth Qwen3.8-27B GGUF repository](https://huggingface.co/unsloth/Qwen3.8-27B-GGUF): UD mixed-precision recipes and the source tensors reused in the Q4/Q5/Q6 variants.
- [pentaCoxian](https://github.com/pentaCoxian/Qwen-V100-llama.cpp): V100-oriented engine base.
- [Warabii1248](https://github.com/Warabii1248) and [ggml-org contributors](https://github.com/ggml-org/llama.cpp): V100 patches and upstream llama.cpp.
- [kuraneko1](https://github.com/kuraneko1): QSA 27B integration, multimodal runtime, and release engineering.

Original model weights and notices retain the upstream Apache-2.0 license. QSA additions in this release are provided under Apache-2.0. Native llama.cpp code retains MIT and its included third-party notices.
