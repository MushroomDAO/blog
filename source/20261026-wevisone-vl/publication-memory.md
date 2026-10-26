---
name: WeVisOne-VL unified visual perception
description: Tencent WeChat Vision 2B/4B seven-task VLM source review; circulated 4090 latency/VRAM claims not substantiated in primary sources.
type: project
---

Sources: https://github.com/Tencent/WeVisOne-VL , https://huggingface.co/tencent/WeVisOne-VL-2B , https://huggingface.co/tencent/WeVisOne-VL-4B , https://arxiv.org/abs/2610.31329 . Raw user material already in bot KB. Exact source/entity dedup found raw KB only, not an existing article/M2/remote draft; broad apache/arxiv bot duplicate was a false positive. Published-list API48001 gap recorded; current remote draft list checked before writing.

Pinned repo9a6bcd85404505df0d05cfb5d97512ccacf35dee; paper v1 October22. Apache2 model cards. Qwen3-VL plus9.6Mpixeldecoder; structured next-token prediction for boxes/points/OCR, OBJ states for masks/alpha. All seven task families; not all outputs concurrently from one call and not a proven universal replacement for task-specific pipelines. Official reported detection/OCR/segmentation/matting metrics need separate definitions. No 4090/48ms/152ms/6GB/10.8GB latency-comparison evidence found in reviewed primary README/paper; do not repeat as established.

Published2026-10-26: https://blog.mushroom.cv/blog/wevisone-vl-unified-vision/ . Finaldeployac8738f2 (initialcb96bbe6); HTTP200 andfiveimagevariants200,list3,carousel1. Officialrabbitmattingteasercrop covercredited,3XiaoMfigures. Source archive source/20261026-wevisone-vl/.

M4lightverification: two actualupstream parsertests passed, plusNone->empty; coordinaterescale/degeneratefilter/truncated/multipoint handling. No modelweightsloaded, no recognition/rejectionquality/pixeldecoder/4090latency/VRAM test. Header-onlyaudit2B24.41744384e8elementsF16,4B48.30581248e8F32;4.88GB/19.32GBfilesnotruntimeRAM.4B BF16payloadarith9.66GB,sidecarmask_decoder.ptrequired. Auto device CUDA/NPU/CPU noMPS;CPUFP32. No promise16GBMac smoothmodelrun.

Semantic2vectorsupserted; liveENquerymatched score0.72497326. FinalcanonicalURLaddition reindexed as needed.

CurrentremoteWeChat draft verified: prCUE631thH1cmNLi42prD5IKoEvZR_2YVOWOzqgUy4KG_qOPfTKsHAn35VnEO6j . Fullvisiblebodytext,ordered3bodyimages,title,author,digest,cover,canonicalbodyandcontent_source_url,commentsettings1/0match. Initialcheckfoundmissingowncanonical; fixedfinalmarkdown and draft/update on SAMEID, reusedimageURLs/cover, no duplicate draft/add. Source input botKB reused; projectmemorysaved beforewriting.

