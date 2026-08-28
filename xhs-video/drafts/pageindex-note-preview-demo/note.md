# 图文帖预览 demo（非选题队列条目）

用来验证 `pipeline/m3/note-template.md` 的结构 + 博客真实文风，取材于已发布文章
`src/content/blog/pageindex-vectorless-reasoning-rag.md`。不进 `topics.yml`
选题队列——这条不是"痛点倒推"逻辑的视频选题，纯粹是模板效果演示。

**封面标题**：RAG 不切 chunk 也不建向量库？

**正文**：
向量数据库不是 RAG 唯一解法，PageIndex 想验证这句话。

🌳 不切 chunk、不建向量库，给文档生成一棵"目录树"索引
🔍 检索靠 LLM 沿树推理找答案，不是拿 embedding 查最近邻
📊 自报 FinanceBench 准确率 98.7%，对比传统向量 RAG 约 50%
⚠️ 但质疑也不少：树结构规模、检索延迟从毫秒变分钟级、成本只是从建库搬到调用 LLM、缺第三方基准
🔗 完整拆解看主页博客同名文章

#RAG #开源工具 #向量数据库 #LLM #AIAgent
