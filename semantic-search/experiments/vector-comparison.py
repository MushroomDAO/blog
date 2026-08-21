#!/usr/bin/env python3
"""
T1.2.1 一次性实验脚本：离线对比"纯关键词(Pagefind) vs 纯向量(bge-m3) vs 简单融合(RRF)"。

不接入 Vectorize，不上线，不做生产级代码——只是为了 T1.2.2 的 Go/No-Go 裁定攒数据。

用法：
  CLOUDFLARE_REGISTRAR_TOKEN=... CLOUDFLARE_ACCOUNT_ID=... python3 vector-comparison.py

产出：semantic-search/eval/vector-comparison-raw.json（原始向量检索结果，供人工写最终报告用）

不做缓存/幂等——每次跑都会重新对全部 464 篇文章 + 24 条查询调用 Workers AI。这是刻意的：
这是给 T1.2.2 一次性拍板用的实验，不是要反复跑的工具；embedding 成本本身也可忽略（见
CODEX_REVIEW.md 的测算）。如果以后真的要反复跑做长期回归测试，再加内容寻址缓存，现在加是
过度工程。
"""

import json
import math
import os
import re
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
BLOG_DIR = REPO_ROOT / "src" / "content" / "blog"
QUERIES_MD = REPO_ROOT / "semantic-search" / "eval" / "queries.md"
OUT_JSON = REPO_ROOT / "semantic-search" / "eval" / "vector-comparison-raw.json"

ACCOUNT_ID = os.environ.get("CLOUDFLARE_ACCOUNT_ID")
TOKEN = os.environ.get("CLOUDFLARE_REGISTRAR_TOKEN")
MODEL = "@cf/baai/bge-m3"
BATCH_SIZE = 20  # Workers AI bge-m3 一次调用的输入条数，保守取值避免超时/payload 过大


def embed_batch(texts):
    url = f"https://api.cloudflare.com/client/v4/accounts/{ACCOUNT_ID}/ai/run/{MODEL}"
    body = json.dumps({"text": texts}).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=body,
        headers={
            "Authorization": f"Bearer {TOKEN}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                data = json.loads(resp.read())
            if not data.get("success"):
                raise RuntimeError(f"Workers AI error: {data.get('errors')}")
            return data["result"]["data"]
        except urllib.error.HTTPError as e:
            if attempt == 2:
                raise
            print(f"  HTTP error {e.code}, retrying ({attempt + 1}/3)...", file=sys.stderr)
            time.sleep(2 * (attempt + 1))
    raise RuntimeError("unreachable")


def embed_all(texts, label):
    vectors = []
    for i in range(0, len(texts), BATCH_SIZE):
        batch = texts[i : i + BATCH_SIZE]
        print(f"  embedding {label} {i + 1}-{i + len(batch)}/{len(texts)}...", file=sys.stderr)
        batch_vectors = embed_batch(batch)
        if len(batch_vectors) != len(batch):
            raise RuntimeError(
                f"embedding count mismatch: sent {len(batch)} texts, got {len(batch_vectors)} vectors"
            )
        for v in batch_vectors:
            if len(v) != 1024:
                raise RuntimeError(f"unexpected embedding dimension: {len(v)} (expected 1024)")
        vectors.extend(batch_vectors)
    return vectors


def parse_frontmatter(md_path):
    text = md_path.read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
    if not m:
        return None
    fm = m.group(1)

    def field(name):
        # frontmatter 里有的文章用双引号，有的用单引号，两种都要匹配
        fm_m = re.search(rf"^{name}:\s*\"((?:[^\"\\]|\\.)*)\"", fm, re.MULTILINE)
        if fm_m:
            return fm_m.group(1).replace('\\"', '"')
        fm_m = re.search(rf"^{name}:\s*'((?:[^'\\]|\\.)*)'", fm, re.MULTILINE)
        if fm_m:
            return fm_m.group(1).replace("\\'", "'")
        return ""

    tags_m = re.search(r"^tags:\s*\[(.*?)\]", fm, re.MULTILINE)
    tags = []
    if tags_m:
        tags = [t.strip().strip("'\"") for t in tags_m.group(1).split(",") if t.strip()]

    return {
        "title": field("title"),
        "titleEn": field("titleEn"),
        "description": field("description"),
        "descriptionEn": field("descriptionEn"),
        "tags": tags,
        "slug": md_path.stem,
    }


# 硬编码 24 条查询，与 semantic-search/eval/queries.md 逐一对应（那份 md 里第 15/16 条
# 写在同一行用 ↔ 分隔做中英对照展示，不适合用正则从 markdown 里稳定解析回 24 条独立查询，
# 一次性实验脚本直接维护一份字面量列表更可靠）。
QUERIES = [
    "Pagefind",
    "Cloudflare Vectorize",
    "MCP Model Context Protocol",
    "LoRA 训练",
    "Claude Code Skill",
    "WebGPU",
    "我想本地部署一个 AI 视频编辑工具",
    "怎么给 Claude Code 装技能包",
    "local-first sync AI agent",
    "有没有讲 Agent 循环设计的文章",
    "脑仿真 大脑连接组",
    "AI Agent 记忆系统",
    "浏览器自动化 Agent",
    "MLX Apple Silicon guide",
    "递归自我改进 RSI",
    "recursive self improvement",
    "3D 可视化工具",
    "terminal AI coding tool",
    "微信机器人远程控制 Claude Code",
    "open source video editing agent",
    "菜谱 家常菜做法",
    "报税指南 个人所得税",
    "育儿经验分享",
    "Kubernetes 集群运维",
]


def cosine(a, b):
    if len(a) != len(b):
        raise ValueError(f"dimension mismatch: {len(a)} != {len(b)}")
    na2 = sum(x * x for x in a)
    nb2 = sum(x * x for x in b)
    if na2 == 0 or nb2 == 0:
        raise ValueError("zero embedding vector")
    score = sum(x * y for x, y in zip(a, b)) / math.sqrt(na2 * nb2)
    if not math.isfinite(score):
        raise ValueError("non-finite cosine similarity")
    return score


def verify_batch_order(sample_texts):
    """抽样验证 Workers AI 批量 embedding 的返回顺序与输入顺序一一对应——
    官方批量接口的响应里不带输入索引，只能靠"批量结果 vs 逐条重新请求"互相比对来自证。
    一旦对不上就直接中止，不能让后续的 top5 排序建立在错配的向量上。"""
    print(f"  verifying batch order on {len(sample_texts)} samples...", file=sys.stderr)
    batch_vectors = embed_batch(sample_texts)
    for i, text in enumerate(sample_texts):
        single_vector = embed_batch([text])[0]
        sims = [cosine(single_vector, bv) for bv in batch_vectors]
        matched = max(range(len(sims)), key=sims.__getitem__)
        if matched != i or sims[matched] < 0.999:
            raise RuntimeError(
                f"batch order mismatch: sample {i} best-matches batch position {matched} "
                f"(sim={sims[matched]:.4f}) — Workers AI batch embedding order is not "
                f"input-order-preserving, or a text produced a near-duplicate vector"
            )
    print("  batch order verified OK", file=sys.stderr)


def main():
    if not TOKEN or not ACCOUNT_ID:
        print("ERROR: set CLOUDFLARE_REGISTRAR_TOKEN and CLOUDFLARE_ACCOUNT_ID", file=sys.stderr)
        sys.exit(1)

    articles = []
    for md_path in sorted(BLOG_DIR.glob("*.md")):
        fm = parse_frontmatter(md_path)
        if fm and fm["title"]:
            articles.append(fm)
    print(f"parsed {len(articles)} articles", file=sys.stderr)

    doc_texts = [
        " ".join(
            filter(
                None,
                [a["title"], a["titleEn"], a["description"], a["descriptionEn"], " ".join(a["tags"])],
            )
        )
        for a in articles
    ]

    queries = QUERIES
    print(f"{len(queries)} queries", file=sys.stderr)

    verify_batch_order(QUERIES[:5])

    print("embedding articles (this calls Workers AI, costs a small amount of quota)...", file=sys.stderr)
    article_vectors = embed_all(doc_texts, "articles")

    print("embedding queries...", file=sys.stderr)
    query_vectors = embed_all(queries, "queries")

    results = []
    for q, qv in zip(queries, query_vectors):
        scored = [
            (cosine(qv, av), articles[i]) for i, av in enumerate(article_vectors)
        ]
        scored.sort(key=lambda x: x[0], reverse=True)
        top5 = [
            {
                "score": round(score, 4),
                "title": a["title"],
                "url": f"/blog/{a['slug']}/",
            }
            for score, a in scored[:5]
        ]
        results.append({"query": q, "top5": top5})

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"wrote {OUT_JSON}", file=sys.stderr)


if __name__ == "__main__":
    main()
