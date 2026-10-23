# NVIDIA Flare primary-source research
Repository https://github.com/NVIDIA/flare-local-inference
Snapshot aca7888f835000b5365468533733bf9d99dbce4d
Fetched 2026-10-23. agent-reach skill/CLI unavailable in catalog and searched installations; Jina Reader fallback plus direct official git clone.
Dedup: raw KB material only; no article or draft/creation receipt. freepublish returns48001; remote six drafts read.
Official README: research prototype, SM120/121; Python Ignition prepares, Rust Helios serves; not a vLLM replacement.
Sources: README.md, AGENTS.md, docs/model-preparation.md, docs/multi-host.md, docs/api.md, docs/cli-design.md.

Validation: upstream ignition export --help succeeded on Apple Silicon; real parser accepted single-host four-GPU command and multi-host --ranks4 command. No CUDA build, model execution or performance benchmark.
Official source images downloaded to /Users/jason/.heinu1-bot/media/nvidia-flare-logo-20261023.png and nvidia-flare-architecture-20261023.png. README logo is predominantly text so generated a distinct photorealistic workstation banner rather than cropping it.
Memory: initial broad ingestion failed in Chroma compaction; narrowed to current project file, re-ingestion succeeded and SQLite readback confirmed current slug and TP4 content.

Source-fetch fallback: agent-reach not installed; Jina Reader fetched official README successfully, official git clone pinned the docs.
Temporary-clone cleanup freed disk for illustration generation; only completed task clones removed.
