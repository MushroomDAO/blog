# Sage-Interaction source and publication audit

Source: https://github.com/InternLM/Sage-Interaction at d3bc2703e0e7f4ec357fc3c73153dd9e9332f9d3. Official model card independently fetched over HTTPS. Apache-2.0 declaration for code/weights is from upstream README; this audit does not relicense third-party dependencies.

Only incoming raw KB hit at dedup; no dedicated Blog/M2/remote draft record. Published-list API returned 48001; raw incoming material is not a previous article. Source images were inspected: overview is a text-heavy illustrated scenario grid, benchmark figures are tables. Neither qualifies as a photographic hero. Fresh FLUX seed 10101 cover passed machine and manual review.

20 audit-authored protocol tests passed on CPU. Run `python3 source/20261126-sage-interaction/check-protocol.py /path/to/pinned/repo`. Uses original upstream protocol module; synthetic payloads, fake HTTP client and mocked sleeps. No downloaded model weights, CUDA/MPS execution, real endpoint, microphone/video integration, end-to-end performance, official benchmark reproduction or real timer latency measurement.

Publication preserves all prior live routes and the previously published GPUWorks branch. The prior OpenVINO restoration remains included. Base branch policy is respected; no force/admin push or merge bypass.

Public Blog exact title/list2/carousel1 and five image variants verified, 1047 prior routes preserved (1048 live). Remote WeChat full visible text, three ordered image identities, cover, author, digest, source URL and comments verified. Two semantic IDs and public search verified; KB note read back five rows including current draft ID and semantic timestamp. Repository review: https://github.com/MushroomDAO/blog/pull/298
