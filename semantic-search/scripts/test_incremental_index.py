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
# do_upsert 会调用 bvi.verify_batch_order/embed_all/upsert_vectors——这里只想测
# manifest 合并这一段，所以把网络相关函数换成假的，只保留 embed 数量对得上即可。
incr.bvi.embed_all = lambda texts, label: [[0.0] * incr.bvi.EMBEDDING_DIMENSIONS for _ in texts]
incr.bvi.verify_batch_order = lambda texts: None
incr.bvi.upsert_vectors = lambda index_name, vectors: {"success": True}
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

print()
if failures:
    print(f"FAILED: {len(failures)} check(s): {failures}")
    sys.exit(1)
print("all checks passed")
