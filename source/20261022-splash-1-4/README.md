# Splash1.4.0 source update — 2026-10-22

Task462f0d88-deb5-4fe3-abe6-1d3778ff76ad. Reuse existing article:
https://blog.mushroom.cv/blog/specialized-inference-engines-rise-hardware-specific-llm-optimization/

Pre-update public URL returned200. Original pubDateOctober5 retained; updatedDateOctober22. New bilingual Splash1.4 section precedes clearly dated historical six-engine material. Other five engines were not reverified. Original unsupported exclusivity and token-agreement wording qualified; stale global bold formatting reduced. No duplicate route.

Primary release https://github.com/incoai/splash/releases/tag/1.4.0 published2026-10-20T22:35:11Z. Pin1482f6bbc2abf12375332725302019594150b6cb; source-review.json contains file hashes, source-verification.json checks the relevant claims. Release API metadata retained, upstream full body excluded from Git.

Official Flash-Next benchmark: M5Pro20-coreGPU64GB, same Q2_0 GGUF againstStrata, selected SPEED-Bench coding prompts overHTTP,1024token outputlimit.95tok/s decode,1312tok/s32Kprefill,171ms cachedTTFT,171tok/s aggregate4requests. All16replays cached. Rounded1.3x is not an all-workload greater-than30percent claim;212x cachedTTFT is not decode. Unverified120not asserted impossible. Historical48GB16GPU launch results and27B35B token-agreement tests are separate. No measured Flash-Next taskaccuracy or BF16 equivalence.

SSD experts,PLE and activeKV roles distinguished from prefixcache. Flash-Next only activeKVspill;27B35B keepactiveKVresident.1M staticYaRN memorycapacity and alteredoutputs; auto verify nondeterminism and allmode controls explained. Format versus family support separated. Homebrew commands are instructions, not executed model installs, and do not pin future versions.

Local attempted service-test command:

```sh
cd /tmp/splash-1-4-research
python3 -m unittest dev.tests.server.test_memory_release
/Users/jason/venvs/ml/bin/python -m unittest dev.tests.server.test_memory_release
```

First interpreter was systemPython3.9 and failed importing match syntax; secondPython3.12 lackedllguidance. No suite assertions passed; no model downloaded, no inference, no Metal performance reproduction. These environmental import failures do not establish engine incompatibility. No package installation or machine configuration changed.

Dedup matched old Blog/receipt/KB and raw user material. Old WeChat creation receipt retained unchanged. Remote old draft/get40007, absent fromdraftbox2entries, publishedlist48001. Mark recorded with archivedMediaId; do not recreate uncertain previously published content. This update is confirmed on Blog only. Remote status script is read-only; publish command deliberately omits --wechat.

Old FLUX42 cover rejected for generated garbled lettering; source has only text/badges and no suitable publichero. ReplacementFLUX165 processor/fibers photo is themed to broad article, rootviewed and verifier0warnings. Three current redcapXiaoM figures rootreviewed, each1280x720<90KB. No asset borrowed from unrelated article.

SEO/GEO, live page and4assets, list position, current semantic search and MemPalace status proofs are saved separately. Raw logs with environment paths, private KB matching text and nested imagegeneration logs are not tracked. Original M2 receipt and drafts-map must not be overwritten with an invented current draft status.
