Title: Cheetah: A local LLM loader that went from 2GB to 62MB after a refactor (0.5B model, 13 tok/s on a 2013 i5) - code review - The Rust Programming Language Forum

URL Source: https://users.rust-lang.org/t/143689

Final URL: https://users.rust-lang.org/t/cheetah-a-local-llm-loader-that-went-from-2gb-to-62mb-after-a-refactor-0-5b-model-13-tok-s-on-a-2013-i5/143689

Published Time: 2026-11-15T13:45:48+00:00

Markdown Content:
## post by zuohanwen1009 3 days ago

I've been building Cheetah, a local LLM loader/backend focused on extreme memory efficiency.

After a full refactor, the numbers changed by an order of magnitude:

*   0.5B model: 2GB+ → 62MB (idle)
*   1.5B model: OOM → 67MB (idle)
*   Incremental memory for a 1.5B model over 0.5B: only +5MB
*   0.5B on an i5-4200M (2013): 13 tok/s (self-developed CPU backend with SIMD)
*   Tool-call overhead (e.g. weather query): +0.2MB

The goal isn't raw speed first — it's fitting usable local models into embedded/low-VRAM environments. The memory numbers come from a lazy-loading architecture and a self-developed CPU/Vulkan backend (CUDA/Metal currently via Candle as a transition).

Still early (V1 offload has ~0.5GB runtime overhead, being replaced in V2 by VRAM→RAM→DISK tiering for MoE). README has the full architecture, memory-loading internals, and contribution guide.

Repo: [GitHub - DA3M0/Cheetah: A single-binary local LLM inference server in Rust + C. Supports Safetensors (F32/F16/BF16) CPU/CUDA/Metal/Vulkan. OpenAI-compatible gateway · GitHub](https://github.com/DA3M0/cheetah)

Happy to answer questions about the memory model or the CPU backend.

[![Image 1](https://sea1.discourse-cdn.com/flex019/user_avatar/users.rust-lang.org/mockba/48/41423_2.png)](https://users.rust-lang.org/u/MOCKBA "MOCKBA")

## post by MOCKBA 3 days ago

Yeah, generally refactoring is a never stop game.

## post by zuohanwen1009 4 hours ago

Absolutely. Especially when chasing that 62MB idle memory footprint. The refactoring never ends, but the numbers are worth it. Thanks for checking it out!
