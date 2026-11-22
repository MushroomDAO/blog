# GLM-ASR-Nano-2512 source and local inference evidence

- GitHub: https://github.com/zai-org/GLM-ASR , pinned a324aa59a30952c54e8097c85efea592b7fafd81.
- HF: https://huggingface.co/zai-org/GLM-ASR-Nano-2512 , pinned 61ba4e0b3309b6656edea3e93e419f7bd5c61957.
- Exact source hashes: research/source-pins.json; model files and metadata: research/model-api.json.
- Code Apache-2.0; model card metadata MIT; standalone model LICENSE returned404 at this snapshot.
- Raw source card and original download/runtime logs kept privately in task85ae7a54-bb41-4790-96c3-9d504c3e1f45/research.
- Dedup: only incoming KB record; no previous Blog, M2 or remote draft. Published API48001; no old creation receipt.

## Reproduce bounded verification

Use the pinned official source checkout and downloaded model. `local-smoke.py` accepts GLM_ASR_REPO, GLM_ASR_MODEL and GLM_ASR_OUT; defaults are the original local paths. Dependencies actually used: Python3.12, PyTorch2.14.0, Transformers5.16.1, numpy and ffmpeg; Apple M4/16GB/macOS26.6.2. No environment packages were installed or upgraded for this check.

```sh
HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 /Users/jason/venvs/ml/bin/python local-smoke.py
python3 research/weight-audit.py /tmp/glm-asr-model-20261122/model.safetensors
python3 research/audit-checks.py
```

Four real model inputs: official Chinese6s, English10.6s, same Chinese multiplied by10^(-30/20), and3s digital silence. Deterministic generation, FP16 on MPS, max128 tokens. English punctuation/capitalization differs; quiet variant changes 准确 to 正确; silence returns no text. Stored2,257,843,200 tensor elements include a duplicated embedding/output matrix; current loaded unique parameter count2,136,470,528. Parent tie_word_embeddings true, inner text config false; equal stored matrices confirmed using torch.equal. No source patch.

Not tested: newly recorded actual whisper, Cantonese, full benchmark corpora, paired Whisper inference, quantized weights, production long recordings/streaming, peak RAM or throughput. Metadata/arithmetic checks are not model accuracy tests. Download SHA matches official LFS. Body illustrations are explanatory and generated; banner is local FLUX, not experiment evidence.
