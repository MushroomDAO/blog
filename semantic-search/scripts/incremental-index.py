#!/usr/bin/env python3
"""
T1.4.1：发布流程增量索引 hook。

发布流程（publish-blog.sh）每次只发一篇文章，不该为一篇文章重新 embed 全库 478 篇——
这里只对比"这篇文章现在的 content_hash"跟 manifest KV（T1.3.5）里记的上次索引值，
只有真的变了（新文章，或内容变了）才调用 Workers AI 重新 embed、upsert 进 Vectorize，
没变就跳过，不花一分钱。

用法：
  python3 incremental-index.py --slug foo-bar [--slug baz]
      # 只检查/索引指定的一篇或几篇文章（发布 hook 用这个，一次发布只传当次发的 slug）
  python3 incremental-index.py
      # 不传 --slug 就检查全库所有文章（人工手动跑一次全量对账时用；T1.4.2 的 Cron
      # 对账届时复用同一条 diff 路径，不是另起一套逻辑）

默认只对比不写入（不传 --upsert 时）：会读 manifest KV（只读，免费）算出"哪些
(article_id, language) 组合的内容变了"，打印差异、写本地 preview，不调用 Workers AI、
不碰 Vectorize、不写 KV——跟 build-vectorize-index.py/manifest.py 是同一套纪律。

真正 embed + upsert + 更新 manifest 需要显式传 --upsert，且需要
CLOUDFLARE_REGISTRAR_TOKEN/CLOUDFLARE_ACCOUNT_ID（同上两个脚本）。

明确不做（见 docs/agent/tasks.md T1.4.1"明确不做"、architecture.md Phase 2）：
不处理"文章被删除"的情况（manifest 里有但本地文件没了的条目，这里完全不碰，留给
T1.4.2 的 Cron 对账处理）。

**FU-32 修复（2026-08-25）**：do_upsert 现在会在文章内容被编辑时一并清理旧 chunk_id
对应的旧向量——之前这里的注释说"编辑过的文章旧向量不会被这里删掉"是过时的；孤儿向量
清理原本只覆盖"文章被删除"这一类（T1.4.2 负责），但"内容被编辑、article_id 还在"这一类
reconcile.py 的孤儿判定天然看不到，只有这里（新旧 chunk_id 都算得出来的地方）能修。
"""

import importlib.util
import json
import os
import re
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPTS_DIR = Path(__file__).resolve().parent
BLOG_DIR = REPO_ROOT / "src" / "content" / "blog"
OUT_JSON = REPO_ROOT / "semantic-search" / "eval" / "incremental-index-plan.json"

# 允许的 slug 字符集（覆盖全库 487 篇文章的真实文件名，含大小写字母，如 dualAR/macOS/agentOS）。
# 首字符强制字母数字——同时挡住 "/etc/passwd"（先被拒绝，不会靠后面 BLOG_DIR / slug 的路径
# 拼接语义"绝对路径覆盖"到仓库外）和 ".."（第一个字符是 "." 不是字母数字，同样被拒）。
# security review 指出：这是 load_articles 从 --slug 参数直接拼路径前唯一的校验点，不能指望
# manifest.py 的 KV key 校验顺带兜底（那是另一个模块的另一个目的，不该是这里的安全边界）。
SLUG_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,120}$")


def validate_slug(slug):
    if not SLUG_RE.match(slug):
        print(f"ERROR: invalid --slug {slug!r} (must match {SLUG_RE.pattern})", file=sys.stderr)
        sys.exit(1)


def _load_sibling_module(mod_name, filename):
    """build-vectorize-index.py 文件名带连字符，`import` 语法不认，用 importlib
    按路径动态加载，复用它已经过 review 的 parse/embed/upsert 逻辑，不重复写一份。"""
    spec = importlib.util.spec_from_file_location(mod_name, SCRIPTS_DIR / filename)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


bvi = _load_sibling_module("_bvi_incremental", "build-vectorize-index.py")
sys.path.insert(0, str(SCRIPTS_DIR))
import manifest as mf  # noqa: E402  （普通文件名，可以直接 import；须在 sys.path 插入后再导）

ACCOUNT_ID = os.environ.get("CLOUDFLARE_ACCOUNT_ID")
TOKEN = os.environ.get("CLOUDFLARE_REGISTRAR_TOKEN")
INDEX_NAME = bvi.DEFAULT_INDEX_NAME


def load_articles(slugs):
    """slugs 为 None → 全库；否则只读指定的几个 slug（对应的 .md 必须存在）。"""
    if slugs is None:
        # T1.4.2 review 抓到的真实 bug：只 glob "*.md" 漏掉 .mdx（`src/content.config.ts`
        # 的 blog collection pattern 是 `**/*.{md,mdx}`，本仓库真的有一篇发布中的 .mdx 文章
        # `using-mdx.mdx`），这个漏洞在 reconcile.py 的孤儿判定里会变成"误删一篇仍在发布的
        # 文章"——如果只有这里修、reconcile.py 的孤儿判定没跟着用同一个文件集合，两边就会
        # 对不上：reconcile.py 判定它"本地存在"（不删）,但这里的全库扫描又看不到它、
        # 永远不会真的把它 embed 进索引。
        all_md_paths = sorted(list(BLOG_DIR.glob("*.md")) + list(BLOG_DIR.glob("*.mdx")))
        paths = [p for p in all_md_paths if p.stem != mf.GLOBAL_KEY]
    else:
        paths = []
        for slug in slugs:
            validate_slug(slug)
            # manifest.py 的 build_manifest 已经因为同一类问题崩过一次（见该文件里
            # "review 抓到的真实 bug" 那段）：_global 是 manifest KV 的保留 key，存的是
            # embedding_model/chunking_version 等全局配置，不是某篇文章的记录。这里走的
            # 是直接 read_kv_entry/write_kv_entry，不经过 build_manifest 的保护，必须自己
            # 挡——否则一篇真的叫 _global.md 的文章会读到/写坏全局配置记录，而不是报错。
            if slug == mf.GLOBAL_KEY:
                print(f"ERROR: slug {slug!r} is the reserved manifest global key, refusing", file=sys.stderr)
                sys.exit(1)
            p = BLOG_DIR / f"{slug}.md"
            if not p.exists():
                print(f"ERROR: no such article: {p}", file=sys.stderr)
                sys.exit(1)
            paths.append(p)

    articles = []
    for md_path in paths:
        fm = bvi.parse_frontmatter(md_path)
        if fm and fm["title"]:
            articles.append(fm)
    return articles


def build_records(articles):
    """(article_id, language, text, content_hash, title, tags, url) 的扁平列表——
    跟 build-vectorize-index.py 的 all_records 是同一种形状，只是这里额外算好 content_hash，
    diff 阶段要用。"""
    records = []
    for a in articles:
        for rec in bvi.build_language_records(a):
            chash = bvi.content_hash(rec["text"])
            records.append({
                "article_id": a["slug"],
                "language": rec["language"],
                "text": rec["text"],
                "title": rec["title"],
                "tags": a["tags"],
                "url": f"/blog/{a['slug']}/",
                "content_hash": chash,
            })
    return records


def diff_against_manifest(records, namespace_id):
    """对每条 (article_id, language) 记录，跟 manifest KV 里存的 content_hash 比对。
    返回 (changed, unchanged, manifest_cache)：
      changed   — 需要重新 embed+upsert 的记录列表
      unchanged — 内容没变，跳过的记录列表（只用于汇报计数）
      manifest_cache — {article_id: 现有的完整 manifest 记录（可能是 None）}，
                        --upsert 阶段更新单个语言字段时要保留同一篇文章另一语言的
                        既有 content_hash，不能整条覆盖。
    """
    changed, unchanged = [], []
    manifest_cache = {}
    for r in records:
        aid = r["article_id"]
        if aid not in manifest_cache:
            manifest_cache[aid] = mf.read_kv_entry(namespace_id, aid)
        existing = manifest_cache[aid]
        prev_hash = (existing or {}).get("content_hash", {}).get(r["language"])
        if prev_hash == r["content_hash"]:
            unchanged.append(r)
        else:
            changed.append(r)
    return changed, unchanged, manifest_cache


def do_upsert(changed, manifest_cache, namespace_id, chunking_version):
    if not changed:
        return
    texts = [r["text"] for r in changed]
    print(f"embedding {len(texts)} changed record(s) (calls Workers AI)...", file=sys.stderr)
    # 无条件校验（不像早期草稿那样只在 >=5 条时才验）：发布 hook 的常见情况恰恰是
    # 1-2 条（单篇文章的 zh/en），批次错位在这个尺寸下一样会把 embedding 错配到
    # 错误语言——跟 build-vectorize-index.py 的纪律一致，这一步不能省。
    bvi.verify_batch_order(texts[:5])
    vectors = bvi.embed_all(texts, "incremental")

    plan = []
    stale_chunk_ids = []
    for rec, vec in zip(changed, vectors):
        chunk_id = bvi.make_vector_id(rec["article_id"], rec["language"], rec["content_hash"])
        metadata = {
            "article_id": rec["article_id"],
            "url": rec["url"],
            "title": rec["title"],
            "language": rec["language"],
            "excerpt": rec["text"][:280],
            "tags": rec["tags"],
            "content_hash": rec["content_hash"],
        }
        plan.append({"id": chunk_id, "values": vec, "metadata": metadata})

        # FU-32：文章内容被编辑后，旧 chunk_id 对应的旧向量此前从未被清理——manifest 记录
        # 被新 content_hash 覆盖后，旧向量在 Vectorize 里既没有 manifest 指针指向它，也不
        # 满足 reconcile.py 的孤儿判定（那只看 article_id 还在不在本地，编辑后 article_id
        # 显然还在）。search.js 按 article_id 取最高分，陈旧向量可能压过新向量、把编辑前的
        # 旧标题/摘录送回查询结果。用 manifest_cache（本轮开始前的快照，不是 touched_articles——
        # 后者会在本轮被逐步更新，取不到"编辑前"的原始值）里该语言的旧 content_hash 算出旧
        # chunk_id，一并清掉。manifest_cache[aid] 为 None（全新文章，从未索引过）或缺该语言
        # （该语言此前从未索引过，比如新增一种语言的翻译）时没有旧向量，跳过。
        prev_hash = (manifest_cache.get(rec["article_id"]) or {}).get("content_hash", {}).get(rec["language"])
        if prev_hash and prev_hash != rec["content_hash"]:
            stale_chunk_ids.append(bvi.make_vector_id(rec["article_id"], rec["language"], prev_hash))

    print(f"TARGET: account={ACCOUNT_ID} index={INDEX_NAME} vectors={len(plan)}", file=sys.stderr)
    for i in range(0, len(plan), bvi.BATCH_SIZE):
        batch = plan[i : i + bvi.BATCH_SIZE]
        result = bvi.upsert_vectors(INDEX_NAME, batch)
        print(f"  upserted {i + 1}-{i + len(batch)}/{len(plan)}: {result.get('success')}", file=sys.stderr)
        # review 抓到的真实 bug：upsert_vectors 只在 4xx/5xx 抛异常，HTTP 200 + `{"success":
        # false, "errors": [...]}` 不抛，循环若无其事走完，然后下面无条件把 content_hash
        # 写进 manifest——下一轮 diff 就会判"没变"，这篇文章/语言永远不会再被索引，且全程
        # 不报错，manifest 说"已索引"但向量其实没写进去。必须在写 manifest 之前挡住。
        if not result.get("success"):
            raise RuntimeError(f"Vectorize upsert failed (HTTP 200, success=false): {result.get('errors')}")

    if stale_chunk_ids:
        # 去重防御性处理（正常情况下每个 (article_id, language) 只贡献一个旧 id，不会重复，
        # 但同一批 changed 理论上可能因上游数据异常出现重复记录，delete_by_ids 对重复 id
        # 是安全的，这里去重只是减少一次没必要的请求体大小）。
        stale_chunk_ids = sorted(set(stale_chunk_ids))
        print(f"deleting {len(stale_chunk_ids)} stale chunk(s) from edited article(s)...", file=sys.stderr)
        # 跟上面 upsert 用同一个 BATCH_SIZE 分批：这里的 stale_chunk_ids 是"整轮 changed 里
        # 所有编辑过的文章"累积出来的，reconcile.py 的全库对账模式一次可能覆盖上百篇文章，
        # 不分批会把上百个 id 塞进一次 delete_by_ids 请求——delete_by_ids 本身不做内部分批
        # （不像 upsert_vectors 由调用方负责分批），Cloudflare Vectorize v2 对单次请求的 id
        # 数量有多大没有查到明确文档保证，跟 upsert 走同一条已验证能用的批量大小最稳妥。
        for i in range(0, len(stale_chunk_ids), bvi.BATCH_SIZE):
            batch = stale_chunk_ids[i : i + bvi.BATCH_SIZE]
            del_result = bvi.delete_by_ids(INDEX_NAME, batch)
            print(f"  deleted stale {i + 1}-{i + len(batch)}/{len(stale_chunk_ids)}: {del_result.get('success')}", file=sys.stderr)
            # 跟 upsert_vectors 同一套返回形状纪律：HTTP 200 + success=false 不抛异常，必须
            # 显式检查。删除失败时不写 manifest——保持 manifest 停在旧 content_hash，下一轮
            # diff 会把这条重新判成 changed，自然重试；如果这里假装成功继续写 manifest，旧
            # 向量就会永久留在索引里，且没有任何机制会再去清理它（reconcile.py 的孤儿判定
            # 看不到这类"内容被编辑"的陈旧向量，见本函数开头的说明）。
            if not del_result.get("success"):
                raise RuntimeError(f"Vectorize delete_by_ids failed for stale chunk(s): {del_result.get('errors')}")

    indexed_at = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    # 按文章合并写 manifest：同一篇文章的两个语言可能不是同一轮都变了，必须在已有记录
    # 基础上只更新变化的语言 key，不能用这一轮的 changed 列表整条覆盖（见 diff_against_manifest
    # 的说明）。
    touched_articles = {}
    for rec in changed:
        aid = rec["article_id"]
        # 必须先看 touched_articles（本轮已经写过的累积结果），manifest_cache 是循环开始前
        # 的快照——同一篇文章在 changed 里出现两条记录时（最常见：新发一篇双语文章，zh/en
        # 都是新的，两条都进 changed），如果每次都从 manifest_cache 重新起手，后处理的语言
        # 会把先处理的语言刚写的更新整个丢掉（真实回归：新双语文章的 zh 记录被 en 记录覆盖，
        # manifest 里永远缺 zh 的 content_hash，下次增量运行会把 zh 误判成"从未索引"反复重
        # 复 embed）。
        base = touched_articles.get(aid) or manifest_cache.get(aid) or {"content_hash": {}}
        base = dict(base)
        base["content_hash"] = dict(base.get("content_hash", {}))
        base["content_hash"][rec["language"]] = rec["content_hash"]
        base["chunking_version"] = chunking_version
        base["indexed_at"] = indexed_at
        touched_articles[aid] = base

    for aid, record in touched_articles.items():
        mf.write_kv_entry(namespace_id, aid, record)
    print(f"updated manifest for {len(touched_articles)} article(s)", file=sys.stderr)


def main():
    # review 抓到的真实问题：旧版本对不认识的 flag 一律忽略——`--slugs`/`--sulg` 这类拼写错误
    # 会悄悄退化成"没传 --slug"，也就是全库对账，而不是报错。手工调用（T1.4.2 复用这条 diff
    # 路径时也会是手工/Cron 调用，不是 publish-blog.sh 那种 $SLUG 保证非空的自动路径）打错一个
    # 字符不该导致跑一遍全库。
    slugs = None
    do_write = False
    slug_args = []
    argv = sys.argv[1:]
    i = 0
    while i < len(argv):
        if argv[i] == "--slug" and i + 1 < len(argv):
            slug_args.append(argv[i + 1])
            i += 2
            continue
        if argv[i] == "--upsert":
            do_write = True
            i += 1
            continue
        print(f"ERROR: unrecognized argument {argv[i]!r} (expected --slug <slug> and/or --upsert)", file=sys.stderr)
        sys.exit(2)
    if slug_args:
        slugs = slug_args

    articles = load_articles(slugs)
    if not articles:
        print("ERROR: no matching articles found", file=sys.stderr)
        sys.exit(1)
    print(f"checking {len(articles)} article(s){' (' + ', '.join(slugs) + ')' if slugs else ' (full corpus)'}", file=sys.stderr)

    records = build_records(articles)

    # diff 阶段只做只读 KV GET，免费，不需要区分 dry-run/真跑——跟 build-vectorize-index.py
    # 的 dry-run 惯例一致（那边 dry-run 也会真的调一次 Workers AI，只有创建索引/upsert 才挡）。
    if not TOKEN or not ACCOUNT_ID:
        print("ERROR: set CLOUDFLARE_REGISTRAR_TOKEN and CLOUDFLARE_ACCOUNT_ID (needed to read the manifest KV, even for a dry-run diff)", file=sys.stderr)
        sys.exit(1)

    namespace_id = mf.find_or_create_namespace(create_if_missing=False)
    changed, unchanged, manifest_cache = diff_against_manifest(records, namespace_id)

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    preview = {
        "changed": [{"article_id": r["article_id"], "language": r["language"], "content_hash": r["content_hash"]} for r in changed],
        "unchanged_count": len(unchanged),
    }
    OUT_JSON.write_text(json.dumps(preview, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"diff: {len(changed)} changed/new, {len(unchanged)} unchanged (wrote {OUT_JSON})", file=sys.stderr)
    for r in changed:
        print(f"  + {r['article_id']} [{r['language']}]", file=sys.stderr)

    if not do_write:
        print("dry-run only (no --upsert passed) — no embedding, no Vectorize/KV writes", file=sys.stderr)
        return

    if not changed:
        print("nothing changed, nothing to upsert", file=sys.stderr)
        return

    do_upsert(changed, manifest_cache, namespace_id, bvi.CHUNKING_VERSION)


if __name__ == "__main__":
    main()
