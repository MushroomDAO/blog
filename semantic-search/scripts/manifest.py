#!/usr/bin/env python3
"""
T1.3.5：索引 manifest 版本化——记录 embedding_model/embedding_dimensions/chunking_version/
indexed_at + 每篇文章的 content_hash，供 T1.4.1（增量索引）/T1.4.2（Cron 对账）判断
"文章内容变了没有、要不要重新索引"，以及模型/分片算法变更时判断"旧向量能不能继续用"。

存储后端选 Cloudflare KV（不是 D1）：这里只需要按 key（article_id）读写一条小 JSON 记录，
不需要跨记录 JOIN/聚合查询，KV 的 get/put/list 语义完全够用，比引入 D1 的 schema/迁移
更简单——跟 PLAN.md 一贯的"成熟简单轻量"选型原则一致。

默认 dry-run：只在本地生成 manifest 数据、写本地文件，不碰 Cloudflare 账号。
真正建 KV namespace / 写入 KV 需要显式传 --create-namespace / --write，这两步涉及真实
账号操作，执行前应先跟用户确认（跟 T1.3.1 的 --create-index/--upsert 是同一个纪律）。

用法：
  python3 manifest.py --from-plan semantic-search/eval/vectorize-index-plan.json
      # dry-run：从上一次索引的 plan 文件生成 manifest，写本地 JSON 预览
  CLOUDFLARE_REGISTRAR_TOKEN=... CLOUDFLARE_ACCOUNT_ID=... python3 manifest.py \
      --from-plan ... --create-namespace --write
      # 真正建 KV namespace（如果还没有）并写入全部记录
"""

import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
OUT_JSON = REPO_ROOT / "semantic-search" / "eval" / "manifest-plan.json"
NAMESPACE_ID_FILE = REPO_ROOT / "semantic-search" / "eval" / ".manifest-kv-namespace-id"

ACCOUNT_ID = os.environ.get("CLOUDFLARE_ACCOUNT_ID")
TOKEN = os.environ.get("CLOUDFLARE_REGISTRAR_TOKEN")
KV_NAMESPACE_TITLE = "blog-search-manifest"
EMBEDDING_MODEL = "@cf/baai/bge-m3"
EMBEDDING_DIMENSIONS = 1024

GLOBAL_KEY = "_global"


def build_manifest(plan_entries, chunking_version, indexed_at):
    """plan_entries: list of {id, metadata:{article_id, language, content_hash, ...}}
    （build-vectorize-index.py 的 plan/preview 格式，也是 chunking.py 输出接进索引流程后
    会用到的同一种形状）。

    产出：{
      "_global": {embedding_model, embedding_dimensions, chunking_version, indexed_at},
      "<article_id>": {
        "content_hash": {"zh": "...", "en": "..."},  # 按语言分开记录，双语文章两个都有
        "chunking_version": "...",
        "indexed_at": "...",
      },
      ...
    }

    每篇文章一条记录（不是每个 chunk 一条）——T1.4.2 的对账逻辑要判断的是"这篇文章内容变了
    没有"，不需要精确到每个段落级 chunk，粒度到文章+语言就够用，也避免 KV key 数量随分片
    数量线性膨胀（一篇文章十几个 paragraph chunk 没必要各自一条 manifest 记录）。
    """
    manifest = {
        GLOBAL_KEY: {
            "embedding_model": EMBEDDING_MODEL,
            "embedding_dimensions": EMBEDDING_DIMENSIONS,
            "chunking_version": chunking_version,
            "indexed_at": indexed_at,
        }
    }
    for entry in plan_entries:
        md = entry["metadata"]
        article_id = md["article_id"]
        # 修正（review 抓到的真实 bug）：GLOBAL_KEY 是保留 key，如果哪篇文章的 slug 恰好
        # 就叫 "_global"，setdefault 会拿到上面已经建好的全局配置字典（没有 content_hash
        # 字段），下面一行取 record["content_hash"] 直接 KeyError 崩溃。这里显式拒绝，
        # 报错信息比裸 KeyError 更清楚，指向真正的原因。
        if article_id == GLOBAL_KEY:
            raise ValueError(
                f"article_id 不能是保留字 {GLOBAL_KEY!r}——这个 key 被全局配置记录占用了"
            )
        language = md["language"]
        chash = md["content_hash"]
        record = manifest.setdefault(article_id, {
            "content_hash": {},
            "chunking_version": chunking_version,
            "indexed_at": indexed_at,
        })
        record["content_hash"][language] = chash
    return manifest


def validate_key_name(key):
    # KV key 名字实际限制很宽松（最大 512 字节），这里只做一个保守的健全性检查，
    # 避免明显异常的 article_id（比如包含路径穿越字符）被当成 key 用。
    # 修正（review 抓到的真实 bug）：原来没拒绝 "?"/"#"——这两个字符对 URL 有结构意义，
    # 如果 key 直接拼进 URL 路径（没有 quote），"foo?evil=1" 会被 HTTP 层解析成
    # "对 key=foo 的请求 + 一个查询参数"，实际写入的是被截断的 key，可能悄悄覆盖另一篇
    # 文章的 manifest 记录。除了这里拒绝，下面 write_kv_entry/read_kv_entry 也改成对 key
    # 做 URL 编码，双重防护（key 校验防"看得出来的异常"，quote 防"编码层面的变体"）。
    if not key or len(key) > 480 or "/" in key or ".." in key or "?" in key or "#" in key:
        raise ValueError(f"unsafe manifest key: {key!r}")


def _list_all_namespaces():
    """翻完全部分页——review 指出只读第一页会在账号里 namespace 数量较多时漏掉已经
    存在的 blog-search-manifest，进而在 --create-namespace 下建出一个同名重复 namespace
    （Cloudflare 不强制 title 唯一），两个 namespace 各自攒一份数据、互不同步。"""
    results = []
    page = 1
    while True:
        url = (f"https://api.cloudflare.com/client/v4/accounts/{ACCOUNT_ID}"
               f"/storage/kv/namespaces?page={page}&per_page=50")
        req = urllib.request.Request(url, headers={"Authorization": f"Bearer {TOKEN}"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read())
        page_result = data.get("result", [])
        results.extend(page_result)
        info = data.get("result_info") or {}
        total_pages = info.get("total_pages", 1)
        if page >= total_pages or not page_result:
            break
        page += 1
    return results


def find_or_create_namespace(create_if_missing):
    # 修正（review 抓到的真实 bug）：本地缓存文件没有记录是哪个账号建的，如果换了
    # CLOUDFLARE_ACCOUNT_ID 跑（比如换了个人测试）、缓存文件还在，会拿着旧账号的
    # namespace id 去撞新账号的 API——Cloudflare 会因为 id 不属于这个账号返回
    # 401/403/404（namespace id 是账号维度隔离的，不会跨账号生效，不会静默写错账号），
    # 但报错信息很难看出问题在"缓存文件跟当前账号对不上"。这里把账号 id 也存进缓存、
    # 读的时候校验一致，不一致就当缓存不存在重新查。
    if NAMESPACE_ID_FILE.exists():
        try:
            cached = json.loads(NAMESPACE_ID_FILE.read_text(encoding="utf-8"))
            if cached.get("account_id") == ACCOUNT_ID and cached.get("namespace_id"):
                return cached["namespace_id"]
            print(
                f"  本地缓存的 namespace id 是账号 {cached.get('account_id')} 建的，"
                f"跟当前 CLOUDFLARE_ACCOUNT_ID（{ACCOUNT_ID}）对不上，忽略缓存重新查询",
                file=sys.stderr,
            )
        except (json.JSONDecodeError, AttributeError):
            pass  # 兼容改版前的旧缓存格式（纯文本 id，不是 JSON），当作没有缓存处理

    for ns in _list_all_namespaces():
        if ns.get("title") == KV_NAMESPACE_TITLE:
            ns_id = ns["id"]
            NAMESPACE_ID_FILE.write_text(
                json.dumps({"account_id": ACCOUNT_ID, "namespace_id": ns_id}),
                encoding="utf-8",
            )
            return ns_id

    if not create_if_missing:
        raise RuntimeError(
            f"KV namespace '{KV_NAMESPACE_TITLE}' 不存在，且未传 --create-namespace"
        )

    print(f"creating KV namespace '{KV_NAMESPACE_TITLE}' (account={ACCOUNT_ID})...", file=sys.stderr)
    url = f"https://api.cloudflare.com/client/v4/accounts/{ACCOUNT_ID}/storage/kv/namespaces"
    body = json.dumps({"title": KV_NAMESPACE_TITLE}).encode("utf-8")
    req = urllib.request.Request(
        url, data=body,
        headers={"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read())
    ns_id = data["result"]["id"]
    NAMESPACE_ID_FILE.write_text(
        json.dumps({"account_id": ACCOUNT_ID, "namespace_id": ns_id}),
        encoding="utf-8",
    )
    return ns_id


def write_kv_entry(namespace_id, key, value_dict):
    validate_key_name(key)
    url = f"https://api.cloudflare.com/client/v4/accounts/{ACCOUNT_ID}/storage/kv/namespaces/{namespace_id}/values/{urllib.parse.quote(key, safe='')}"
    body = json.dumps(value_dict).encode("utf-8")
    req = urllib.request.Request(
        url, data=body,
        headers={"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"},
        method="PUT",
    )
    last_err = None
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                return json.loads(resp.read())
        except urllib.error.HTTPError as e:
            detail = e.read().decode("utf-8", errors="replace")
            if 400 <= e.code < 500:
                print(f"  KV write error (HTTP {e.code}, not retrying — client error): {detail}", file=sys.stderr)
                raise
            last_err = e
            if attempt == 3:
                # 修正（review 抓到的真实 bug）：原来这里直接 raise，不打印 detail——
                # 4 次都失败时操作者只看到裸的 HTTPError，看不到 Cloudflare 返回的
                # 错误码/ray-id/message，排查不了到底是什么原因。跟 build-vectorize-index.py
                # 的 upsert_vectors 保持一致，最终失败也要把 detail 打出来。
                print(f"  KV write error (HTTP {e.code}), giving up after 4 attempts: {detail}", file=sys.stderr)
                raise
            print(f"  KV write error (HTTP {e.code}), retrying ({attempt + 1}/4): {detail}", file=sys.stderr)
            time.sleep(2 * (attempt + 1))
        except urllib.error.URLError as e:
            last_err = e
            if attempt == 3:
                print(f"  KV write error ({type(e).__name__}), giving up after 4 attempts: {e}", file=sys.stderr)
                raise
            print(f"  KV write error ({type(e).__name__}), retrying ({attempt + 1}/4)...", file=sys.stderr)
            time.sleep(2 * (attempt + 1))
    raise last_err


def read_kv_entry(namespace_id, key):
    validate_key_name(key)
    url = f"https://api.cloudflare.com/client/v4/accounts/{ACCOUNT_ID}/storage/kv/namespaces/{namespace_id}/values/{urllib.parse.quote(key, safe='')}"
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {TOKEN}"})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return None
        raise


def main():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--from-plan", required=True, help="build-vectorize-index.py 产出的 plan/preview JSON 路径")
    parser.add_argument("--chunking-version", default=None, help="不传则从 plan 文件里的 chunking_version 字段读取")
    parser.add_argument("--create-namespace", action="store_true")
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()

    plan_path = Path(args.from_plan)
    if not plan_path.exists():
        print(f"ERROR: plan 文件不存在: {plan_path}", file=sys.stderr)
        sys.exit(1)
    raw = json.loads(plan_path.read_text(encoding="utf-8"))

    # build-vectorize-index.py 的 preview 文件是一个 list；也兼容 cache 文件的 {"plan": [...]} 包装。
    # 修正（review 指出的边界情况）：如果传进来一个既不是 list、也不含 "plan" key 的畸形
    # dict，明确报错而不是让它当成 plan_entries 往下走、在 build_manifest 里因为遍历字符串
    # key 而炸出一个不知所云的 TypeError
    if isinstance(raw, dict):
        if "plan" not in raw:
            print(f"ERROR: {plan_path} 是 dict 但没有 'plan' key，不是预期的两种格式之一", file=sys.stderr)
            sys.exit(1)
        plan_entries = raw["plan"]
    else:
        plan_entries = raw
    chunking_version = args.chunking_version or raw.get("chunking_version") if isinstance(raw, dict) else args.chunking_version
    if not chunking_version:
        # preview 格式没有顶层 chunking_version 字段，从文件名或调用方传参兜底
        chunking_version = "unknown"

    indexed_at = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    manifest = build_manifest(plan_entries, chunking_version, indexed_at)

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"wrote manifest preview to {OUT_JSON} ({len(manifest) - 1} articles + 1 global entry)", file=sys.stderr)

    if not args.create_namespace and not args.write:
        print("dry-run only (no --create-namespace/--write passed) — no Cloudflare account resources touched", file=sys.stderr)
        return

    if not TOKEN or not ACCOUNT_ID:
        print("ERROR: set CLOUDFLARE_REGISTRAR_TOKEN and CLOUDFLARE_ACCOUNT_ID", file=sys.stderr)
        sys.exit(1)

    namespace_id = find_or_create_namespace(create_if_missing=args.create_namespace)
    print(f"TARGET: account={ACCOUNT_ID} kv_namespace={namespace_id} entries={len(manifest)}", file=sys.stderr)

    if args.write:
        # 每 20 条报一次进度（跟 build-vectorize-index.py 的 BATCH_SIZE 对齐），
        # 中途失败时能定位到大致是第几条，不用等 50 条那么宽的误差范围
        for i, (key, value) in enumerate(manifest.items()):
            write_kv_entry(namespace_id, key, value)
            if (i + 1) % 20 == 0 or i + 1 == len(manifest):
                print(f"  wrote {i + 1}/{len(manifest)}", file=sys.stderr)


if __name__ == "__main__":
    main()
