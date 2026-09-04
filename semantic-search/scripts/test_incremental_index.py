#!/usr/bin/env python3
"""T1.4.1 验收测试：diff 逻辑（changed vs unchanged）。不调用任何网络/Cloudflare API——
diff_against_manifest 依赖的 manifest.read_kv_entry 在这里被换成内存假实现。"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import manifest as mf
import importlib.util

spec = importlib.util.spec_from_file_location("_incr_under_test", Path(__file__).resolve().parent / "incremental-index.py")
incr = importlib.util.module_from_spec(spec)
spec.loader.exec_module(incr)

failures = []


def check(name, condition, detail=""):
    status = "PASS" if condition else "FAIL"
    print(f"[{status}] {name}" + (f" — {detail}" if detail and not condition else ""))
    if not condition:
        failures.append(name)


def fake_kv(store):
    def _read(namespace_id, key):
        return store.get(key)
    return _read


# ---- 场景 1：全新文章（manifest 里完全没有这个 article_id）----
store = {}
mf.read_kv_entry = fake_kv(store)
records = [
    {"article_id": "brand-new", "language": "zh", "text": "t", "title": "t", "tags": [], "url": "/blog/brand-new/", "content_hash": "hash-zh-1"},
]
changed, unchanged, cache = incr.diff_against_manifest(records, "ns")
check("全新文章 → changed", len(changed) == 1 and len(unchanged) == 0)
check("全新文章 manifest_cache 记录为 None", cache["brand-new"] is None)

# ---- 场景 2：内容没变（manifest 里已有相同 content_hash）----
store = {"unchanged-article": {"content_hash": {"zh": "hash-zh-1"}, "chunking_version": "v1", "indexed_at": "t"}}
mf.read_kv_entry = fake_kv(store)
records = [
    {"article_id": "unchanged-article", "language": "zh", "text": "t", "title": "t", "tags": [], "url": "/blog/unchanged-article/", "content_hash": "hash-zh-1"},
]
changed, unchanged, cache = incr.diff_against_manifest(records, "ns")
check("内容没变 → unchanged，不进 changed", len(changed) == 0 and len(unchanged) == 1)

# ---- 场景 3：内容变了（content_hash 跟 manifest 里记的不一样）----
store = {"edited-article": {"content_hash": {"zh": "hash-zh-OLD"}, "chunking_version": "v1", "indexed_at": "t"}}
mf.read_kv_entry = fake_kv(store)
records = [
    {"article_id": "edited-article", "language": "zh", "text": "t", "title": "t", "tags": [], "url": "/blog/edited-article/", "content_hash": "hash-zh-NEW"},
]
changed, unchanged, cache = incr.diff_against_manifest(records, "ns")
check("内容变了 → changed", len(changed) == 1)

# ---- 场景 4：双语文章，只有一种语言变了 → 只有变的那条进 changed，另一条保持 unchanged ----
store = {"bilingual-article": {"content_hash": {"zh": "hash-zh-1", "en": "hash-en-1"}, "chunking_version": "v1", "indexed_at": "t"}}
mf.read_kv_entry = fake_kv(store)
records = [
    {"article_id": "bilingual-article", "language": "zh", "text": "t", "title": "t", "tags": [], "url": "/x/", "content_hash": "hash-zh-1"},  # 没变
    {"article_id": "bilingual-article", "language": "en", "text": "t", "title": "t", "tags": [], "url": "/x/", "content_hash": "hash-en-2"},  # 变了
]
changed, unchanged, cache = incr.diff_against_manifest(records, "ns")
check("双语文章只有变化的语言进 changed", len(changed) == 1 and changed[0]["language"] == "en")
check("没变的那个语言在 unchanged 里", len(unchanged) == 1 and unchanged[0]["language"] == "zh")

# ---- 场景 5：do_upsert 合并 manifest 时，不能把另一语言的既有 content_hash 覆盖掉 ----
# （回归测试：如果 do_upsert 直接用 changed 列表整条覆盖 manifest 记录，双语文章里没变的
# 那个语言的 content_hash 会被误删——这里只测 merge 逻辑本身，不触发真实网络写入。）
written = {}


def fake_write(namespace_id, key, value):
    written[key] = value


mf.write_kv_entry = fake_write
manifest_cache = {"bilingual-article": {"content_hash": {"zh": "hash-zh-1", "en": "hash-en-OLD"}, "chunking_version": "v1", "indexed_at": "old"}}
changed_for_upsert = [
    {"article_id": "bilingual-article", "language": "en", "text": "t", "title": "t", "tags": [], "url": "/x/", "content_hash": "hash-en-NEW"},
]
# do_upsert 会调用 bvi.verify_batch_order/embed_all/upsert_vectors/delete_by_ids（FU-32
# 起，en 从 hash-en-OLD 变成 hash-en-NEW 会触发旧向量清理）——这里只想测 manifest 合并这
# 一段，所以把网络相关函数换成假的，只保留 embed 数量对得上即可。
incr.bvi.embed_all = lambda texts, label: [[0.0] * incr.bvi.EMBEDDING_DIMENSIONS for _ in texts]
incr.bvi.verify_batch_order = lambda texts: None
incr.bvi.upsert_vectors = lambda index_name, vectors: {"success": True}
incr.bvi.delete_by_ids = lambda index_name, ids: {"success": True}
incr.do_upsert(changed_for_upsert, manifest_cache, "ns", "v2")
check("merge 后 en 的 content_hash 更新为新值",
      written["bilingual-article"]["content_hash"]["en"] == "hash-en-NEW")
check("merge 后 zh 的既有 content_hash 保留不变（回归测试：不能被整条覆盖）",
      written["bilingual-article"]["content_hash"]["zh"] == "hash-zh-1")

# ---- 场景 6：回归测试——同一篇文章在一轮 changed 里有两条记录（新发的双语文章，zh/en
# 都是新的）时，两个语言的 content_hash 都要保留下来，后处理的语言不能把先处理的语言冲掉。----
written2 = {}


def fake_write2(namespace_id, key, value):
    written2[key] = value


mf.write_kv_entry = fake_write2
manifest_cache_new_bilingual = {"new-bilingual": None}  # 全新文章，manifest 里还没有记录
changed_new_bilingual = [
    {"article_id": "new-bilingual", "language": "zh", "text": "t", "title": "t", "tags": [], "url": "/x/", "content_hash": "hash-zh-new"},
    {"article_id": "new-bilingual", "language": "en", "text": "t", "title": "t", "tags": [], "url": "/x/", "content_hash": "hash-en-new"},
]
incr.bvi.embed_all = lambda texts, label: [[0.0] * incr.bvi.EMBEDDING_DIMENSIONS for _ in texts]
incr.bvi.verify_batch_order = lambda texts: None
incr.bvi.upsert_vectors = lambda index_name, vectors: {"success": True}
incr.do_upsert(changed_new_bilingual, manifest_cache_new_bilingual, "ns", "v2")
check("新双语文章：zh 记录没被 en 记录覆盖掉（回归测试）",
      written2["new-bilingual"]["content_hash"].get("zh") == "hash-zh-new")
check("新双语文章：en 记录也在",
      written2["new-bilingual"]["content_hash"].get("en") == "hash-en-new")

# ---- 场景 7：回归测试——security review 发现的 --slug 路径穿越/绝对路径覆盖，load_articles
# 拼路径前必须先拒绝。sys.exit(1) 会抛 SystemExit，不是普通异常，得单独 except 住。----
for bad_slug in ["../../../etc/passwd", "/etc/passwd", "foo/bar", ".."]:
    try:
        incr.load_articles([bad_slug])
        check(f"load_articles 拒绝恶意 slug {bad_slug!r}", False)
    except SystemExit as e:
        check(f"load_articles 拒绝恶意 slug {bad_slug!r}", e.code == 1)

# 正常 slug（含真实文章里出现过的大小写字母，如 macOS/agentOS 风格）应该能通过校验本身
# （不校验文件是否真的存在，只校验字符集不会被 validate_slug 拒绝）
for ok_slug in ["normal-article-slug", "audio8-tts-preview-0.6b-dualAR", "codexbar-macOS-menu-bar-tool"]:
    try:
        incr.validate_slug(ok_slug)
        check(f"validate_slug 接受正常 slug {ok_slug!r}", True)
    except SystemExit:
        check(f"validate_slug 接受正常 slug {ok_slug!r}", False)

# ---- 场景 8：回归测试——review 抓到的真实 bug。upsert_vectors 返回 HTTP 200 +
# success=false（不抛异常）时，do_upsert 必须在写 manifest 之前中止，不能假装成功。----
written3 = {}


def fake_write3(namespace_id, key, value):
    written3[key] = value


mf.write_kv_entry = fake_write3
incr.bvi.embed_all = lambda texts, label: [[0.0] * incr.bvi.EMBEDDING_DIMENSIONS for _ in texts]
incr.bvi.verify_batch_order = lambda texts: None
incr.bvi.upsert_vectors = lambda index_name, vectors: {"success": False, "errors": ["boom"]}
changed_for_failure = [
    {"article_id": "will-fail", "language": "zh", "text": "t", "title": "t", "tags": [], "url": "/x/", "content_hash": "h"},
]
try:
    incr.do_upsert(changed_for_failure, {"will-fail": None}, "ns", "v2")
    check("upsert success=false 时 do_upsert 必须抛异常（回归测试）", False)
except RuntimeError:
    check("upsert success=false 时 do_upsert 必须抛异常（回归测试）", True)
check("upsert success=false 时 manifest 完全不写入（回归测试）", "will-fail" not in written3)

# ---- 场景 9：回归测试——不认识的参数（拼写错误如 --slugs/--sulg）必须报错退出，不能悄悄
# 退化成"没传 --slug"从而跑全库对账。----
import subprocess  # noqa: E402

incr_path = str(Path(__file__).resolve().parent / "incremental-index.py")
r = subprocess.run(["python3", incr_path, "--slugs", "foo"], capture_output=True, text=True)
check("拼写错误的 --slugs 被拒绝而不是静默忽略（回归测试）", r.returncode == 2)

# ---- 场景 10：回归测试——slug 撞 manifest 保留字 _global 必须拒绝，不能读/写坏全局配置记录。----
try:
    incr.load_articles(["_global"])
    check("load_articles 拒绝保留字 _global（回归测试）", False)
except SystemExit as e:
    check("load_articles 拒绝保留字 _global（回归测试）", e.code == 1)

# ---- 场景 11：FU-32 回归测试——文章内容被编辑时，do_upsert 必须删掉旧 content_hash
# 对应的旧 chunk_id，不能任由它在 Vectorize 里变成陈旧孤儿。----
written4 = {}
deleted_calls = []


def fake_write4(namespace_id, key, value):
    written4[key] = value


def fake_delete(index_name, ids):
    deleted_calls.append(list(ids))
    return {"success": True}


mf.write_kv_entry = fake_write4
incr.bvi.embed_all = lambda texts, label: [[0.0] * incr.bvi.EMBEDDING_DIMENSIONS for _ in texts]
incr.bvi.verify_batch_order = lambda texts: None
incr.bvi.upsert_vectors = lambda index_name, vectors: {"success": True}
incr.bvi.delete_by_ids = fake_delete
manifest_cache_edited = {"edited-article": {"content_hash": {"zh": "hash-OLD"}, "chunking_version": "v1", "indexed_at": "old"}}
changed_edited = [
    {"article_id": "edited-article", "language": "zh", "text": "t", "title": "t", "tags": [], "url": "/x/", "content_hash": "hash-NEW"},
]
incr.do_upsert(changed_edited, manifest_cache_edited, "ns", "v2")
expected_old_id = incr.bvi.make_vector_id("edited-article", "zh", "hash-OLD")
check("编辑文章后 delete_by_ids 被调用一次（回归测试，FU-32）", len(deleted_calls) == 1)
check("delete_by_ids 收到的正是旧 content_hash 算出的 chunk_id（回归测试，FU-32）",
      deleted_calls and deleted_calls[0] == [expected_old_id])
check("manifest 仍然正确更新为新 content_hash（回归测试，FU-32）",
      written4["edited-article"]["content_hash"]["zh"] == "hash-NEW")

# ---- 场景 12：FU-32 回归测试——全新文章（manifest_cache 为 None）或新增语言（该语言此前
# 没有 content_hash）没有旧向量可删，delete_by_ids 不应被调用。----
deleted_calls.clear()
written5 = {}
mf.write_kv_entry = lambda namespace_id, key, value: written5.__setitem__(key, value)
manifest_cache_new = {"brand-new-2": None}
changed_new = [
    {"article_id": "brand-new-2", "language": "zh", "text": "t", "title": "t", "tags": [], "url": "/x/", "content_hash": "hash-1"},
]
incr.do_upsert(changed_new, manifest_cache_new, "ns", "v2")
check("全新文章不触发 delete_by_ids（回归测试，FU-32）", len(deleted_calls) == 0)

deleted_calls.clear()
manifest_cache_new_lang = {"bilingual-2": {"content_hash": {"zh": "hash-zh-1"}, "chunking_version": "v1", "indexed_at": "old"}}
changed_new_lang = [
    {"article_id": "bilingual-2", "language": "en", "text": "t", "title": "t", "tags": [], "url": "/x/", "content_hash": "hash-en-1"},
]
incr.do_upsert(changed_new_lang, manifest_cache_new_lang, "ns", "v2")
check("既有文章新增一种语言不触发 delete_by_ids（回归测试，FU-32）", len(deleted_calls) == 0)

# ---- 场景 13：FU-32 回归测试——delete_by_ids 返回 HTTP 200 + success=false 时必须抛异常，
# 且不能写 manifest（跟 upsert_vectors 的 success=false 处理是同一套纪律）。----
written6 = {}
mf.write_kv_entry = lambda namespace_id, key, value: written6.__setitem__(key, value)
incr.bvi.delete_by_ids = lambda index_name, ids: {"success": False, "errors": ["boom"]}
manifest_cache_del_fail = {"del-fail-article": {"content_hash": {"zh": "hash-OLD"}, "chunking_version": "v1", "indexed_at": "old"}}
changed_del_fail = [
    {"article_id": "del-fail-article", "language": "zh", "text": "t", "title": "t", "tags": [], "url": "/x/", "content_hash": "hash-NEW"},
]
try:
    incr.do_upsert(changed_del_fail, manifest_cache_del_fail, "ns", "v2")
    check("delete_by_ids success=false 时 do_upsert 必须抛异常（回归测试，FU-32）", False)
except RuntimeError:
    check("delete_by_ids success=false 时 do_upsert 必须抛异常（回归测试，FU-32）", True)
check("delete_by_ids 失败时 manifest 完全不写入（回归测试，FU-32）", "del-fail-article" not in written6)

# ---- 场景 14：FU-32 回归测试——stale_chunk_ids 数量超过 bvi.BATCH_SIZE（比如 reconcile.py
# 全库对账一次遇到很多篇被编辑的文章）时，delete_by_ids 必须跟 upsert 一样分批调用，不能
# 把几百个 id 塞进一次请求。----
written7 = {}
deleted_batches = []
mf.write_kv_entry = lambda namespace_id, key, value: written7.__setitem__(key, value)
incr.bvi.delete_by_ids = lambda index_name, ids: (deleted_batches.append(list(ids)), {"success": True})[1]
N = incr.bvi.BATCH_SIZE * 2 + 3  # 跨 3 个批次
manifest_cache_many = {f"many-{i}": {"content_hash": {"zh": f"old-{i}"}, "chunking_version": "v1", "indexed_at": "old"} for i in range(N)}
changed_many = [
    {"article_id": f"many-{i}", "language": "zh", "text": "t", "title": "t", "tags": [], "url": "/x/", "content_hash": f"new-{i}"}
    for i in range(N)
]
incr.bvi.embed_all = lambda texts, label: [[0.0] * incr.bvi.EMBEDDING_DIMENSIONS for _ in texts]
incr.bvi.verify_batch_order = lambda texts: None
incr.bvi.upsert_vectors = lambda index_name, vectors: {"success": True}
incr.do_upsert(changed_many, manifest_cache_many, "ns", "v2")
check(f"{N} 个待删 id 被分成 {-(-N // incr.bvi.BATCH_SIZE)} 批而不是一次全塞（回归测试，FU-32）",
      len(deleted_batches) == -(-N // incr.bvi.BATCH_SIZE))
check("每批大小都不超过 BATCH_SIZE（回归测试，FU-32）",
      all(len(b) <= incr.bvi.BATCH_SIZE for b in deleted_batches))
check("分批删除的 id 总数等于待删总数、无遗漏无重复（回归测试，FU-32）",
      sorted(sum(deleted_batches, [])) == sorted({incr.bvi.make_vector_id(f"many-{i}", "zh", f"old-{i}") for i in range(N)}))

print()
if failures:
    print(f"FAILED: {len(failures)} check(s): {failures}")
    sys.exit(1)
print("all checks passed")
