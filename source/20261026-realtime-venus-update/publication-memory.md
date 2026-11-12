---
name: project_realtime_venus
description: Realtime-Venus 双9B模型与异步Harness；2026-10-26复核旧稿，修正A100、权重容量和部署路径；公众号仅旧凭证，当前状态未核验。
type: project
---

# Realtime-Venus

来源：https://huggingface.co/inclusionAI/Realtime-Venus 、https://github.com/inclusionAI/Realtime-Venus 、https://arxiv.org/abs/2609.13814v3 。本次用户再次提供来源，要求官方自报口径，原始素材机器人已入KB。

复用旧文章：realtime-venus-fulldup-interactive-dual-loop-local-deploy，首次发布日期2026-09-20。更新核查日期2026-10-26，仓库e53ae8d5bde92b30364b26f2e4c13c9db7a8ffea；HF007097ab5d304ff1fff154bedf415b088717ec8d。

Omni与Audio是分别训练的9B前端，按模式选择，并非双Loop各用一个9B。Omni看听说，Audio音频/文本；Harness异步执行并返回原会话。当前官方推理路径CUDA，Demo要求Linux NVIDIA，未验证Mac MPS。每个safetensors合计18,743,802,932B，Omni完整目录20,084,171,408B，Audio19,993,734,943B（HF元数据，不是显存实测）；原稿两个9B合计18GB、必须A100和Mac MPS建议不成立。模型/代码Apache-2.0；论文另有自己的许可。分数全部官方自报，未运行GPU性能复现。

Blog复用原URL已原地更新修正文档，2026-10-26部署b51a9a19，HTTP200，5张图片/格式资源HTTP200，原发布日期保留，列表第232，首页轮播第1。公众号旧凭证prCUE631thH1cmNLi42prGYW-FBLlX7rgQa-_wSvFS3B1G9Lc8kxjipggicQNJts，2026-10-26 draft/get40007，远程5条无匹配；freepublish/batchget48001无权限。因此recorded，当前状态未核验，不新建可能已发布草稿。

本次更新部署/索引状态：Blog已部署核验；语义索引zh/en两向量upsert成功并删除2条旧chunk，在线搜索命中新英文标题，score0.7069386。公众号未新建，旧本地M2凭证保持原样。
