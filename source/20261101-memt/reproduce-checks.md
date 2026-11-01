# Reproduce the configuration checks

Clone https://github.com/MemTensor/MemT-1.0 and check out commit `563aba62cab0031421807039d9330f0dc58db86c`. Read the repository's PolyForm Noncommercial license before use. The local check imports the official launcher using PYTHONPATH; it installs no server dependencies and loads no model weights.

Create CONFIGS/Nano/config.json and CONFIGS/Flash/config.json from these pinned metadata files:

- https://huggingface.co/MemTensor/MemT-1.0-Nano/raw/30fe0b22422c4cc4c87475f98db5c8baa5c1a902/config.json
- https://huggingface.co/MemTensor/MemT-1.0-Flash/raw/a707cf84ebbaf2151a005001f9dfed9ee97f60c8/config.json

Run `python3 source/20261101-memt/check-launch.py PATH_TO_CLONE CONFIGS` with Python >=3.11. Seven cases check the real CLI and supplied launch scripts. `launch-checks.json` contains the executed configuration identities and arguments. Dry-run does not verify SGLang ServerArgs, weights, CUDA, kernel execution or recall accuracy.

HF model cards explicitly distinguish permissive weight licenses from original repository software; do not infer one component's terms from another. No third-party model source code or checkpoint weights were executed in this audit.
