# Haru release audit

Exact source and entity dedup clear; generic Apache matches from bot were unrelated. Sources: official GitHub, HF model card, technical blog and Mac app documentation. Git revision 7fe6b7665f8bf035998f401f8cb779fbe53f2751; HF revision 8d6e83bcd3701a76fc27a764965665da1df7da78.

Official claims: 40M real-speech hours,160+languages,nine primary; no LLM/TTS dialogue in pretraining;13M separated dialogue hours, up to60min samples;256B200/8days. These are not reproduced.65.2ms p50 uses M1Max,int8,nativeSwift,wiredIO and excludes up to133ms framing. We did not treat this as user response latency or add it into a claimed measured worst case.

Code and weights Apache2; third party VibeVoice/Moshi/mlx-lm notices retained upstream. Public release covers inference/codecs/client; no claim fullcorpus released. Base-model facts/instruction following unreliable per card.

Actual checks: upstreamPyTorch non-gpu suite42pass2skip11deselected; substitute engine for server; no fullweights,no inference,no microphone,no training,no latencybenchmark. HF file10540113510bytes; only safetensorsheader fetched,5270000899storedtensor elements. No generated model speech.
