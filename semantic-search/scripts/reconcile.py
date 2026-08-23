#!/usr/bin/env python3
"""
T1.4.2：每日对账——补 T1.4.1 发布 hook 覆盖不到的两类缺口：

  ① 漏索引：manifest 记的 content_hash 跟本地文章现在的内容对不上（比如某次发布 hook
     失败、或有人绕过 publish-blog.sh 直接改了文章内容）。发布 hook 只查当次发的那一篇，
     这里全库扫一遍才能发现。
  ② 孤儿：manifest KV 里有记录，本地已经没有对应 `.md` 了（文章被删除/改名）——它的向量
     还留在 Vectorize 里，会在检索结果里冒出一篇已经不存在的文章（或者改名前的旧 URL）。

复用 incremental-index.py 的 diff 路径（同一套 build_records/diff_against_manifest/
do_upsert），不是另起一套逻辑——①就是它的全库模式；这里新增的只是②，以及"列出全部
manifest key、找出本地没有对应文件的那些"这一步（manifest.py 新增的 list_manifest_keys/
delete_kv_entry）。

用法：
  python3 reconcile.py
      # dry-run：打印①②两类差异，不碰 Workers AI / Vectorize / KV
  python3 reconcile.py --upsert
      # 真正修复①（embed+upsert 漏索引的文章，逻辑等同 incremental-index.py --upsert）
  python3 reconcile.py --delete-orphans
      # 真正修复②（删 Vectorize 里的孤儿向量 + 对应 manifest KV 记录）
  两个 flag 可以一起传，各自独立生效，互不依赖。

跟其它脚本同一套纪律：默认 dry-run，真正的写/删操作需要显式 flag +
CLOUDFLARE_REGISTRAR_TOKEN/CLOUDFLARE_ACCOUNT_ID。**`--delete-orphans` 是破坏性操作
（删数据），比 `--upsert` 风险更高**，见 `docs/agent/tasks.md` T1.4.2 的风险说明。

明确不做（见 tasks.md T1.4.2"待决问题"）：不部署、不调度——这个脚本只是"跑一次对账"的
逻辑本身。"每天自动跑一次"用什么机制触发（本机 cron 还是 Cloudflare Worker Cron
Trigger）是一个还没拍板的架构决策，不由这个脚本决定。

⚠️ 只给人工操作者用，还不能接无人值守的自动触发：`--delete-orphans` 目前只有"文章列表
整个是空"这一道地板检查，没有比例上限。人工跑的时候你会先看 dry-run 打印的孤儿清单再
决定要不要加 `--delete-orphans`；如果换成 cron 定时驱动、又恰好跑在一个落后于 main 的
旧 checkout 上（本仓库确实同时开着多个 worktree，是真实场景），旧 checkout 缺的新文章
会被这个脚本当成孤儿全部删掉，没有人在中间看一眼。**谁要接自动触发，必须先加比例/数量
上限**，见 `docs/agent/tasks.md` T1.4.2"接自动触发前的硬性前提"。
"""

import importlib.util
import json
import sys
import time
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent
REPO_ROOT = Path(__file__).resolve().parents[2]
OUT_JSON = REPO_ROOT / "semantic-search" / "eval" / "reconcile-plan.json"


def _load_sibling_module(mod_name, filename):
    spec = importlib.util.spec_from_file_location(mod_name, SCRIPTS_DIR / filename)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# incremental-index.py 本身也用同一个 importlib 手法动态加载 build-vectorize-index.py/
# manifest.py——这里不重新加载一份，而是直接拿 incr 已经装好的 incr.bvi/incr.mf，避免
# 同一个模块在进程里存在两份不同的实例（两份实例的 module-level 变量如 ACCOUNT_ID/TOKEN
# 互相不可见，之前如果各自 import 一次，monkeypatch 测试时容易漏改到另一份）。
incr = _load_sibling_module("_incr_for_reconcile", "incremental-index.py")
bvi = incr.bvi
mf = incr.mf

ACCOUNT_ID = incr.ACCOUNT_ID
TOKEN = incr.TOKEN
INDEX_NAME = incr.INDEX_NAME


def list_local_slugs():
    """孤儿判定的"本地真的有没有这个文件"判据——必须是原始文件列表，不能是
    `incr.load_articles(None)` 解析成功的那个子集。`load_articles` 会静默丢掉 frontmatter
    解析失败/缺 title 的 `.md`（对增量索引这没事，反正没法生成 embedding 文本），但如果
    孤儿判定也用那个子集，一篇文件还在、只是暂时解析失败的文章会被误判成"文件已经不在
    了"，`--delete-orphans` 就会删掉一篇真实存在的文章的向量+manifest 记录。"""
    # 跟 incremental-index.py 的全库扫描用同一个文件集合（含 .mdx，见那边"review 抓到的真实
    # bug"的注释）——两边如果对不上，孤儿判定和"要不要重新索引"判定会互相矛盾。
    return {p.stem for p in list(bvi.BLOG_DIR.glob("*.md")) + list(bvi.BLOG_DIR.glob("*.mdx"))
            if p.stem != mf.GLOBAL_KEY}


def find_orphans(local_article_ids, namespace_id):
    """manifest KV 里有、本地文章集合里没有的 key（排除 GLOBAL_KEY）就是孤儿。

    review 抓到的真实 bug：`BLOG_SEARCH_KV` 这个 namespace 是四个用途共享的（见
    `wrangler.toml`），除了这里管的 manifest（裸 article_id 做 key），还有登录限速
    （`ratelimit:` 前缀，值是纯数字字符串）、`/api/search` 限速（`searchlimit:` 前缀，同上）、
    搜索结果缓存（`searchcache:v2:` 前缀，值是 JSON 数组）。这些 key 不满足"在本地文章集合
    里"，原来的逻辑会把它们全部当成孤儿——不是"静默删错东西"（`read_kv_entry` 读回来的是
    `int`/`list`，`delete_orphans` 里 `record.get("content_hash")` 会直接 `AttributeError`
    崩溃），而是**排序上更靠前的非 manifest key 先崩，真正的孤儿一个都清不掉**，`--delete-
    orphans` 在有真实流量的生产 namespace 上完全跑不通。

    改成白名单而不是黑名单：只有"读出来是 dict 且有 content_hash 字段"的 key 才算 manifest
    记录、才可能是孤儿；不认识的 key 形状一律跳过并打印一行说明，不是当成异常终止整个对账。
    这样以后这个 namespace 里再加新用途/新前缀，默认是"不管"而不是"当成孤儿删掉"。
    """
    all_keys = mf.list_manifest_keys(namespace_id)
    orphans = []
    for k in all_keys:
        if k == mf.GLOBAL_KEY or k in local_article_ids:
            continue
        record = mf.read_kv_entry(namespace_id, k)
        if isinstance(record, dict) and isinstance(record.get("content_hash"), dict):
            orphans.append(k)
        else:
            print(f"  skip non-manifest key in shared BLOG_SEARCH_KV namespace: {k!r}", file=sys.stderr)
    return sorted(orphans)


def delete_orphans(orphan_ids, namespace_id):
    """对每个孤儿 article_id：读它的 manifest 记录，拿到已记录的每种语言的 content_hash，
    算出对应的 chunk_id（跟当初 upsert 时用的是同一个确定性哈希——make_vector_id 是纯函数，
    不需要额外存一份 vector_id 映射），批量 delete_by_ids，再删 manifest 记录本身。

    这个"每种语言正好一个 chunk_id"的假设成立，是因为当前索引粒度是文章级
    （CHUNKING_VERSION="t1.3.1-article-only-v3"，T1.3.2 的段落级分片还没接入这条索引流程）。
    如果以后段落级分片真的接进来、一篇文章一种语言对应多个 chunk，这里要跟着改成枚举
    manifest 记录里存的全部 chunk_id（而不是现算一个），否则会漏删多余的 chunk。

    manifest 记录缺失/content_hash 缺失的极端情况（理论上不该发生，key 都来自
    list_manifest_keys）容错跳过该语言，不因为一条脏数据中止整个对账。
    """
    total_vectors_deleted = 0
    for aid in orphan_ids:
        record = mf.read_kv_entry(namespace_id, aid)
        if not record:
            print(f"  ⚠ {aid}: manifest record disappeared between list and read, skipping", file=sys.stderr)
            continue
        chunk_ids = []
        for language, chash in (record.get("content_hash") or {}).items():
            chunk_ids.append(bvi.make_vector_id(aid, language, chash))
        # review 抓到的真实 bug：这原来是 `if chunk_ids:` 包住 delete_by_ids，但下面的
        # `delete_kv_entry` 跟这个 if 同缩进、在 if 块外面——chunk_ids 为空（content_hash
        # 缺失或是空 dict）时 delete_by_ids 确实没调用，但 delete_kv_entry 照样执行，
        # docstring 说的"容错跳过该语言"根本没发生，是"零向量被删、manifest 指针照删"。
        # 改成早退：真的没有可推导的 vector id 就整条跳过，不删 manifest 记录。
        if not chunk_ids:
            print(f"  ⚠ {aid}: manifest 记录没有可用的 content_hash，推不出 vector id —— "
                  f"跳过，不删 manifest 记录", file=sys.stderr)
            continue
        result = bvi.delete_by_ids(INDEX_NAME, chunk_ids)
        # review 抓到的真实 bug：delete_by_ids 跟 upsert_vectors 是同一套返回形状——只在
        # 4xx/5xx 抛异常，HTTP 200 + success=false 不抛。不检查就删 manifest 记录，
        # 会把"向量其实还在"报告成"已删除"，而且下一轮 find_orphans 再也看不到这个 key
        # （manifest 记录没了），这个孤儿永久漏网、向量永久留在生产索引里，比 T1.4.1 那个
        # 同类 bug 更严重——那边最多是"文章暂时搜不到"，这里是"删除操作报告成功但没删掉"。
        if not result.get("success"):
            print(f"  ⚠ {aid}: delete_by_ids failed (HTTP 200, success=false): {result.get('errors')}, "
                  f"NOT deleting manifest entry so it can be retried next run", file=sys.stderr)
            continue
        total_vectors_deleted += len(chunk_ids)
        mf.delete_kv_entry(namespace_id, aid)
        # Vectorize 的 delete_by_ids 是异步的（真正的处理结果要靠 mutationId 另外查）；
        # success=true 只代表"请求已被受理排队"，不是"向量这一刻已经从索引里消失"。
        print(f"  - {aid}: accepted delete of {len(chunk_ids)} vector(s) (mutationId="
              f"{result.get('mutationId')}) + deleted manifest entry", file=sys.stderr)
    return total_vectors_deleted


def main():
    do_upsert = "--upsert" in sys.argv
    do_delete = "--delete-orphans" in sys.argv
    for arg in sys.argv[1:]:
        if arg not in ("--upsert", "--delete-orphans"):
            print(f"ERROR: unrecognized argument {arg!r} (expected --upsert and/or --delete-orphans)", file=sys.stderr)
            sys.exit(2)

    if not TOKEN or not ACCOUNT_ID:
        print("ERROR: set CLOUDFLARE_REGISTRAR_TOKEN and CLOUDFLARE_ACCOUNT_ID", file=sys.stderr)
        sys.exit(1)

    articles = incr.load_articles(None)  # None = 全库，同 incremental-index.py 不传 --slug 时的行为
    if not articles:
        print("ERROR: no articles found in corpus", file=sys.stderr)
        sys.exit(1)
    local_ids = list_local_slugs()
    print(f"corpus: {len(articles)} parseable article(s), {len(local_ids)} .md file(s) on disk", file=sys.stderr)

    records = incr.build_records(articles)
    namespace_id = mf.find_or_create_namespace(create_if_missing=False)
    changed, unchanged, manifest_cache = incr.diff_against_manifest(records, namespace_id)
    orphans = find_orphans(local_ids, namespace_id)

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    preview = {
        "stale_or_missing": [{"article_id": r["article_id"], "language": r["language"]} for r in changed],
        "unchanged_count": len(unchanged),
        "orphans": orphans,
    }
    OUT_JSON.write_text(json.dumps(preview, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"diff: {len(changed)} stale/missing, {len(unchanged)} unchanged, {len(orphans)} orphan article(s) "
          f"(wrote {OUT_JSON})", file=sys.stderr)
    for r in changed:
        print(f"  + stale/missing: {r['article_id']} [{r['language']}]", file=sys.stderr)
    for aid in orphans:
        print(f"  - orphan: {aid}", file=sys.stderr)

    if not do_upsert and not do_delete:
        print("dry-run only (no --upsert/--delete-orphans passed) — nothing written or deleted", file=sys.stderr)
        return

    if do_upsert:
        if changed:
            incr.do_upsert(changed, manifest_cache, namespace_id, bvi.CHUNKING_VERSION)
        else:
            print("nothing stale/missing, nothing to upsert", file=sys.stderr)

    if do_delete:
        if orphans:
            n = delete_orphans(orphans, namespace_id)
            print(f"deleted {n} orphan vector(s) across {len(orphans)} article(s)", file=sys.stderr)
        else:
            print("no orphans, nothing to delete", file=sys.stderr)


if __name__ == "__main__":
    main()
