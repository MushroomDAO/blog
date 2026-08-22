#!/usr/bin/env python3
"""
T1.3.1：文章内容 → bge-m3 embedding → 写入 Cloudflare Vectorize 的全量索引脚本。

范围（按 tasks.md T1.3.1）：只做「文章级」chunk（chunk_type=article，标题+摘要+标签+
标题层级），不做段落级分片——段落级 chunk 是 T1.3.2 的范围。中英文双语文章（正文含
`<!--EN-->` 分隔符）按 spec.md 的模型拆成两条独立记录，共享 article_id，语言标记为
zh/en（不再有 bilingual 值）。

**语言判定说明（对抗式 review 修复的核心 bug）**：`titleEn`/`descriptionEn` frontmatter
字段是给 og:/twitter: 社交分享用的 SEO 元数据（见项目 CLAUDE.md 的 SEO 双语 meta 约定），
几乎每篇文章都会填，跟正文是否真的有 `<!--EN-->` 双语分段没有关系——第一版脚本曾经把
"有没有 titleEn" 当成"是否要建英文记录"的信号，导致单语文章也被错误地建出一条内容全是
标签/字面拼接的伪"英文记录"，且没有 `<!--EN-->` 分隔符时统一假设是中文，导致单语英文
文章的记录被错误标成 language=zh。现在的规则：只有正文真的出现 `<!--EN-->` 才拆成两条
记录；没有分隔符的单语文章只出一条记录，语言由正文实际内容的 CJK 字符占比判定，不是
凭有没有 titleEn 猜。

默认是 dry-run：只生成向量、打印/写入本地文件，不碰 Cloudflare 账号。
真正创建索引 / 写入 Vectorize 需要显式传 --create-index / --upsert，且这两步涉及真实账号
操作和计费，执行前应先跟用户确认（见 docs/agent/architecture.md 的"不可动摇的边界"）。

用法：
  CLOUDFLARE_REGISTRAR_TOKEN=... CLOUDFLARE_ACCOUNT_ID=... python3 build-vectorize-index.py [--create-index] [--upsert] [--index-name blog-search-v1]

  失败重跑：--upsert 会优先复用上一次 dry-run/失败运行留下的向量缓存
  （semantic-search/eval/.vectorize-vectors-cache.json，已 gitignore），不重新调用
  Workers AI 重算 embedding；只有缓存不存在或文章集合变化时才会重新 embed 全部文章。

前置检查（实现/执行前必须做，见 architecture.md）：
  Vectorize 的 create-index / insert 端点路径、维度上限、定价，本脚本按 2026-08-20 前后的
  已知 V2 REST API 形态实现（POST /accounts/{id}/vectorize/v2/indexes 建索引，
  POST .../indexes/{name}/upsert 写入），执行 --create-index/--upsert 前请先到 Cloudflare
  官方文档核实这两个端点和字段名没有变化。

已知范围外的缺口（记入 followups.md，T1.4.1 负责）：本脚本不做"先记录旧 chunk_id 再删"的
增量更新流程——如果两次运行之间文章内容被编辑，旧 chunk_id 不会被清理，会在索引里留下孤儿
向量。首次全量建索引后如需修改文章，在 T1.4.1 的对账逻辑落地前，应重新跑一次全量 --upsert
（chunk_id 是内容寻址的，新内容会产生新 id，不会覆盖旧的，需要人工用 wrangler vectorize
delete-by-ids 清理旧 id，或等 T1.4.1）。
"""

import hashlib
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
BLOG_DIR = REPO_ROOT / "src" / "content" / "blog"
OUT_JSON = REPO_ROOT / "semantic-search" / "eval" / "vectorize-index-plan.json"
VECTOR_CACHE = REPO_ROOT / "semantic-search" / "eval" / ".vectorize-vectors-cache.json"

ACCOUNT_ID = os.environ.get("CLOUDFLARE_ACCOUNT_ID")
TOKEN = os.environ.get("CLOUDFLARE_REGISTRAR_TOKEN")
MODEL = "@cf/baai/bge-m3"
EMBEDDING_DIMENSIONS = 1024
BATCH_SIZE = 20
DEFAULT_INDEX_NAME = "blog-search-v1"
CHUNKING_VERSION = "t1.3.1-article-only-v2"  # v2: 语言判定 bug 修复，v1 产出的向量不可复用
INDEX_NAME_RE = re.compile(r"^[a-z0-9][a-z0-9-]{0,63}$")

# CJK 统一表意文字 + 扩展 A，用于单语文章的语言判定（没有 <!--EN--> 分隔符时不能瞎猜）
CJK_RE = re.compile(r"[一-鿿㐀-䶿]")


def detect_language(text):
    non_space = re.sub(r"\s", "", text)
    if not non_space:
        return "en"
    cjk_count = len(CJK_RE.findall(text))
    return "zh" if (cjk_count / len(non_space)) > 0.15 else "en"


def embed_batch(texts):
    url = f"https://api.cloudflare.com/client/v4/accounts/{ACCOUNT_ID}/ai/run/{MODEL}"
    body = json.dumps({"text": texts}).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=body,
        headers={"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"},
        method="POST",
    )
    last_err = None
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                raw = resp.read()
            data = json.loads(raw)
            if not data.get("success"):
                raise RuntimeError(f"Workers AI error: {data.get('errors')}")
            return data["result"]["data"]
        except (urllib.error.URLError, urllib.error.HTTPError, json.JSONDecodeError, TimeoutError) as e:
            # URLError 覆盖超时/连接重置/DNS 失败；HTTPError 是它的子类（4xx/5xx）；
            # JSONDecodeError 覆盖响应体损坏/截断——这三类都值得重试，不只是 HTTP 状态码错误
            last_err = e
            if attempt == 3:
                raise
            code = getattr(e, "code", "n/a")
            print(f"  request error ({type(e).__name__}, code={code}), retrying ({attempt + 1}/4)...", file=sys.stderr)
            time.sleep(2 * (attempt + 1))
    raise last_err


def verify_batch_order(sample_texts):
    """抽样验证 Workers AI 批量 embedding 的返回顺序与输入顺序一一对应——批量接口的响应
    不带输入索引，只能靠"批量结果 vs 逐条重新请求"互相比对来自证。这批向量会被直接
    upsert 进生产 Vectorize 索引（不是像 vector-comparison.py 那样只是人工核对的实验数据），
    错配的后果是查询结果全部指向错误的文章，所以这一步不能省。"""
    print(f"  verifying batch order on {len(sample_texts)} samples...", file=sys.stderr)
    batch_vectors = embed_batch(sample_texts)
    for i, text in enumerate(sample_texts):
        single_vector = embed_batch([text])[0]
        dot = sum(x * y for x, y in zip(single_vector, batch_vectors[i]))
        na = sum(x * x for x in single_vector) ** 0.5
        nb = sum(x * x for x in batch_vectors[i]) ** 0.5
        sim = dot / (na * nb) if na and nb else 0.0
        if sim < 0.999:
            raise RuntimeError(
                f"batch order mismatch at position {i}: single-vs-batch cosine similarity {sim:.4f} "
                f"< 0.999 — Workers AI batch embedding order may not be input-order-preserving"
            )
    print("  batch order verified OK", file=sys.stderr)


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
            if len(v) != EMBEDDING_DIMENSIONS:
                raise RuntimeError(f"unexpected embedding dimension: {len(v)} (expected {EMBEDDING_DIMENSIONS})")
        vectors.extend(batch_vectors)
    return vectors


def parse_frontmatter(md_path):
    text = md_path.read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", text, re.DOTALL)
    if not m:
        return None
    fm, body = m.group(1), m.group(2)

    def field(name):
        fm_m = re.search(rf"^{name}:\s*\"((?:[^\"\\]|\\.)*)\"", fm, re.MULTILINE)
        if fm_m:
            return fm_m.group(1).replace('\\"', '"')
        fm_m = re.search(rf"^{name}:\s*'((?:[^'\\]|\\.)*)'", fm, re.MULTILINE)
        if fm_m:
            return fm_m.group(1).replace("\\'", "'")
        return ""

    tags_m = re.search(r"^tags:\s*\[(.*?)\]", fm, re.MULTILINE)
    tags = [t.strip().strip("'\"") for t in tags_m.group(1).split(",") if t.strip()] if tags_m else []
    category = field("category")

    # 只有正文真的出现 <!--EN--> 才是双语文章；titleEn/descriptionEn 是 SEO meta，
    # 跟正文有没有双语分段无关，不能用来判断要不要拆出第二条记录（见文件头注释）
    is_bilingual = "<!--EN-->" in body
    if is_bilingual:
        zh_body, en_body = body.split("<!--EN-->", 1)
    else:
        zh_body, en_body = body, ""

    def extract_headings(section):
        return [h.strip("# ").strip() for h in re.findall(r"^#{2,3}\s+.+$", section, re.MULTILINE)]

    return {
        "slug": md_path.stem,
        "title": field("title"),
        "titleEn": field("titleEn"),
        "description": field("description"),
        "descriptionEn": field("descriptionEn"),
        "tags": tags,
        "category": category,
        "is_bilingual": is_bilingual,
        "headings_zh": extract_headings(zh_body),
        "headings_en": extract_headings(en_body) if is_bilingual else [],
    }


def build_language_records(article):
    """按 spec.md：中英文各自独立记录，language 只取 zh|en，不再有 bilingual。

    真正双语（含 <!--EN-->）→ 最多两条记录，zh 半段用 title/description，en 半段用
    titleEn/descriptionEn（双语文章里这两个字段就是真正的英文版）。
    单语（无分隔符）→ 只出一条记录，文本和标题统一用 title/description（唯一确实存在的
    正文语言字段），语言由正文实际内容判定，不假设"没分隔符=中文"。
    """
    tags_text = " ".join(article["tags"])

    if article["is_bilingual"]:
        records = []
        zh_text = " ".join(p for p in [article["title"], article["description"], tags_text, " ".join(article["headings_zh"])] if p)
        if zh_text.strip():
            records.append({"language": "zh", "text": zh_text, "title": article["title"]})
        en_text = " ".join(p for p in [article["titleEn"], article["descriptionEn"], tags_text, " ".join(article["headings_en"])] if p)
        if en_text.strip():
            records.append({"language": "en", "text": en_text, "title": article["titleEn"] or article["title"]})
        return records

    text = " ".join(p for p in [article["title"], article["description"], tags_text, " ".join(article["headings_zh"])] if p)
    if not text.strip():
        return []
    return [{"language": detect_language(text), "text": text, "title": article["title"]}]


def content_hash(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def validate_index_name(name):
    if not INDEX_NAME_RE.match(name):
        print(f"ERROR: invalid --index-name '{name}' — must match {INDEX_NAME_RE.pattern}", file=sys.stderr)
        sys.exit(1)


def create_index(index_name):
    url = f"https://api.cloudflare.com/client/v4/accounts/{ACCOUNT_ID}/vectorize/v2/indexes"
    body = json.dumps({
        "name": index_name,
        "config": {"dimensions": EMBEDDING_DIMENSIONS, "metric": "cosine"},
    }).encode("utf-8")
    req = urllib.request.Request(
        url, data=body,
        headers={"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        detail = e.read().decode("utf-8", errors="replace")
        if e.code == 409 or "already exists" in detail.lower():
            print(f"  index '{index_name}' already exists, continuing (not an error on retry)", file=sys.stderr)
            return {"success": True, "already_existed": True}
        print(f"ERROR creating index (HTTP {e.code}): {detail}", file=sys.stderr)
        raise


def upsert_vectors(index_name, vectors):
    """vectors: list of {id, values, metadata} — NDJSON body per Vectorize v2 upsert.
    chunk_id 是内容寻址的确定性 ID，同一批重复 upsert 只会覆盖，是安全的重试点。"""
    url = f"https://api.cloudflare.com/client/v4/accounts/{ACCOUNT_ID}/vectorize/v2/indexes/{index_name}/upsert"
    ndjson = "\n".join(json.dumps(v) for v in vectors).encode("utf-8")
    req = urllib.request.Request(
        url, data=ndjson,
        headers={"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/x-ndjson"},
        method="POST",
    )
    last_err = None
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                return json.loads(resp.read())
        except (urllib.error.URLError, urllib.error.HTTPError, json.JSONDecodeError) as e:
            last_err = e
            if attempt == 3:
                raise
            code = getattr(e, "code", "n/a")
            print(f"  upsert error ({type(e).__name__}, code={code}), retrying batch ({attempt + 1}/4)...", file=sys.stderr)
            time.sleep(2 * (attempt + 1))
    raise last_err


def load_or_build_plan(articles):
    """优先复用向量缓存（同一批文章、同一个 chunking_version 时），避免失败重跑重新
    花 Workers AI 额度重算全部 embedding——embedding 成本虽然本就可忽略，但 --upsert 中途
    失败后不该强迫操作者重新等一遍全量 embedding 才能继续。"""
    all_records = []
    for a in articles:
        for rec in build_language_records(a):
            all_records.append({
                "article_id": a["slug"], "language": rec["language"], "text": rec["text"],
                "url": f"/blog/{a['slug']}/", "title": rec["title"], "tags": a["tags"],
            })
    print(f"{len(all_records)} language records ({len(articles)} articles, article-level chunk only)", file=sys.stderr)

    record_hashes = sorted(f"{r['article_id']}:{r['language']}:{content_hash(r['text'])}" for r in all_records)

    if VECTOR_CACHE.exists():
        cached = json.loads(VECTOR_CACHE.read_text(encoding="utf-8"))
        if cached.get("chunking_version") == CHUNKING_VERSION and cached.get("record_hashes") == record_hashes:
            print(f"  reusing cached vectors from {VECTOR_CACHE} (record set unchanged, no re-embedding)", file=sys.stderr)
            return cached["plan"]
        print("  cache exists but stale (record set or chunking_version changed) — re-embedding", file=sys.stderr)

    texts = [r["text"] for r in all_records]
    print("embedding article-level chunks (this calls Workers AI, costs a small amount of quota)...", file=sys.stderr)
    verify_batch_order(texts[:5])
    vectors = embed_all(texts, "article-chunks")

    plan = []
    for rec, vec in zip(all_records, vectors):
        chash = content_hash(rec["text"])
        chunk_id = f"{rec['article_id']}:{rec['language']}:{chash}"
        metadata = {
            "article_id": rec["article_id"],
            "url": rec["url"],
            "title": rec["title"],
            "language": rec["language"],
            "excerpt": rec["text"][:280],
            "tags": rec["tags"],
            "content_hash": chash,
        }
        plan.append({"id": chunk_id, "values": vec, "metadata": metadata})

    VECTOR_CACHE.parent.mkdir(parents=True, exist_ok=True)
    VECTOR_CACHE.write_text(json.dumps({
        "chunking_version": CHUNKING_VERSION, "record_hashes": record_hashes, "plan": plan,
    }, ensure_ascii=False), encoding="utf-8")

    return plan


def main():
    do_create_index = "--create-index" in sys.argv
    do_upsert = "--upsert" in sys.argv
    index_name = DEFAULT_INDEX_NAME
    for i, a in enumerate(sys.argv):
        if a == "--index-name" and i + 1 < len(sys.argv):
            index_name = sys.argv[i + 1]
    validate_index_name(index_name)

    if not TOKEN or not ACCOUNT_ID:
        print("ERROR: set CLOUDFLARE_REGISTRAR_TOKEN and CLOUDFLARE_ACCOUNT_ID", file=sys.stderr)
        sys.exit(1)

    articles = []
    for md_path in sorted(BLOG_DIR.glob("*.md")):
        fm = parse_frontmatter(md_path)
        if fm and fm["title"]:
            articles.append(fm)
    print(f"parsed {len(articles)} articles", file=sys.stderr)

    plan = load_or_build_plan(articles)

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    # 落盘的人可读预览不重复写完整 1024 维向量（体积大且无需人工核查，向量本身存在
    # VECTOR_CACHE 里供 --upsert 复用），只写结构供人核对
    preview = [{"id": p["id"], "metadata": p["metadata"], "vector_dims": len(p["values"])} for p in plan]
    OUT_JSON.write_text(json.dumps(preview, ensure_ascii=False, indent=2), encoding="utf-8")
    lang_counts = {}
    for p in plan:
        lang_counts[p["metadata"]["language"]] = lang_counts.get(p["metadata"]["language"], 0) + 1
    print(f"wrote plan preview to {OUT_JSON} ({len(plan)} vectors, dim={EMBEDDING_DIMENSIONS}, "
          f"chunking_version={CHUNKING_VERSION}, by language={lang_counts})", file=sys.stderr)

    if not do_create_index and not do_upsert:
        print("dry-run only (no --create-index/--upsert passed) — no Cloudflare account resources touched", file=sys.stderr)
        return

    # 操作者可见的账号/目标确认——不是密码，是"即将对哪个账号的哪个索引做真实写入"，
    # 供人在真正执行前肉眼核对没有指错账号/环境
    print(f"TARGET: account={ACCOUNT_ID} index={index_name} vectors={len(plan)}", file=sys.stderr)

    if do_create_index:
        print(f"creating Vectorize index '{index_name}' ({EMBEDDING_DIMENSIONS}d, cosine)...", file=sys.stderr)
        result = create_index(index_name)
        print(json.dumps(result, ensure_ascii=False, indent=2), file=sys.stderr)

    if do_upsert:
        print(f"upserting {len(plan)} vectors into '{index_name}'...", file=sys.stderr)
        for i in range(0, len(plan), BATCH_SIZE):
            batch = plan[i : i + BATCH_SIZE]
            result = upsert_vectors(index_name, batch)
            print(f"  upserted {i + 1}-{i + len(batch)}/{len(plan)}: {result.get('success')}", file=sys.stderr)


if __name__ == "__main__":
    main()
