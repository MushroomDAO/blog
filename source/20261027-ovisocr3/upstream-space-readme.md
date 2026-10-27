---
title: OvisOCR3
emoji: ⚡
colorFrom: yellow
colorTo: red
sdk: gradio
sdk_version: 6.26.0
python_version: "3.12"
app_file: app.py
pinned: false
license: apache-2.0
models:
  - ATH-MaaS/OvisOCR3
short_description: OCR and document understanding with OvisOCR3
---

# OvisOCR3

[Model](https://huggingface.co/ATH-MaaS/OvisOCR3) |
[Technical Report](https://arxiv.org/abs/2610.33066) |
[GitHub](https://github.com/AIDC-AI/Ovis)

A Hugging Face ZeroGPU demo for document parsing, general OCR, information
extraction, figure captioning, and cross-page table reconstruction.

## Runtime

Select ZeroGPU hardware for this Gradio Space. The app loads the public
`ATH-MaaS/OvisOCR3` model with Transformers; no model-access token is required.
Inference uses greedy decoding with thinking disabled. Each inference stage
requests up to 120 seconds of GPU time.

CPU input preparation runs before GPU allocation. The interface reports queue,
GPU preparation, prefill, and generation phases with elapsed time. Request
details include preprocessing, GPU wait, first-token time, and decode throughput.
The CUDA convolution wheel is pinned to Python 3.12, Torch 2.10, and CUDA 12;
keep these versions aligned when changing the inference environment.

Cross-page tables parse two pages before reconstructing the table. The bundled
example includes precomputed Stage 1 results for both Markdown and Structured
parsing. Exact matching image pairs and prompts use these results immediately,
with both pages marked Cached; Stage 2 is always generated live. Other inputs
run all three calls live. The token limit applies to live calls, not the frozen
example parses. Each page and the merged table have separate result tabs.
Downloads preserve the exact prompts, raw outputs, and cache provenance;
incomplete output is marked.

## Inputs And Privacy

Upload images or PDFs, up to 30 MB per file. Images are limited to 32 megapixels
and PDFs to 100 pages. A cross-page request processes two ordered images or one
adjacent pair of PDF pages. Password-protected PDFs are not supported.

The display uses lightweight WebP previews with a maximum edge of 1280 pixels.
Inference still reads the original inputs. The source inspector loads the
full-resolution image on demand; preview failures have an independent retry
control and do not block prompt updates. Browser image caches are private.
The Regions view shares the lightweight preview and loads full resolution only
when zooming, focusing a region, or expanding the inspector.

Uploads are processed by this Space. Temporary Gradio upload files expire after
24 hours; generated result archives remain on the server until the operator
removes them or the ephemeral storage is reset. Do not upload confidential
documents to a publicly shared instance.

## Repository

- `prompts/`: the 18 model task templates.
- `examples/cases.json`: example images, task parameters, and benchmark sources.
- `assets/`: interface styles, scripts, icons, and the formula renderer.

The application code is licensed under Apache 2.0. Third-party software and
brand assets retain their respective licenses; see `THIRD_PARTY_NOTICES.md`.
Benchmark examples retain their source terms.
