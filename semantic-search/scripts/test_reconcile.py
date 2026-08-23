#!/usr/bin/env python3
"""T1.4.2 验收测试：孤儿检测 + 删除逻辑。不调用任何网络/Cloudflare API——
manifest.list_manifest_keys/read_kv_entry/delete_kv_entry、build-vectorize-index.py 的
delete_by_ids 在这里全部换成内存假实现。"""

import importlib.util
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import manifest as mf

spec = importlib.util.spec_from_file_location("_reconcile_under_test", Path(__file__).resolve().parent / "reconcile.py")
recon = importlib.util.module_from_spec(spec)
spec.loader.exec_module(recon)

failures = []


def check(name, condition, detail=""):
    status = "PASS" if condition else "FAIL"
    print(f"[{status}] {name}" + (f" — {detail}" if detail and not condition else ""))
    if not condition:
        failures.append(name)


# ---- find_orphans ----
mf.list_manifest_keys = lambda ns: ["alive-1", "alive-2", "gone-1", mf.GLOBAL_KEY]
orphans = recon.find_orphans({"alive-1", "alive-2"}, "ns")
check("孤儿 = manifest 有、本地没有，排除 _global", orphans == ["gone-1"])

mf.list_manifest_keys = lambda ns: ["a", "b", "c"]
orphans = recon.find_orphans({"a", "b", "c"}, "ns")
check("全部都在本地时没有孤儿", orphans == [])

# ---- delete_orphans ----
kv_store = {
    "gone-1": {"content_hash": {"zh": "hash-zh", "en": "hash-en"}, "chunking_version": "v1", "indexed_at": "t"},
    "gone-2": {"content_hash": {"zh": "hash-zh-2"}, "chunking_version": "v1", "indexed_at": "t"},
}
deleted_vector_calls = []
deleted_kv_keys = []


def fake_read(namespace_id, key):
    return kv_store.get(key)


def fake_delete_by_ids(index_name, ids):
    deleted_vector_calls.append(list(ids))
    return {"success": True}


def fake_delete_kv(namespace_id, key):
    deleted_kv_keys.append(key)
    return {"success": True}


mf.read_kv_entry = fake_read
recon.bvi.delete_by_ids = fake_delete_by_ids
mf.delete_kv_entry = fake_delete_kv

n = recon.delete_orphans(["gone-1", "gone-2"], "ns")
check("双语孤儿删了 2 个向量、单语孤儿删了 1 个向量，共 3 个", n == 3)
check("两个孤儿的 manifest key 都被删了", set(deleted_kv_keys) == {"gone-1", "gone-2"})
check("每个孤儿各自一次 delete_by_ids 调用（按文章分批，不是全部混在一起）",
      len(deleted_vector_calls) == 2)

# 回归测试：manifest 记录在 list 和 read 之间消失（理论上不该发生，但不能让整个对账中止）
kv_store_race = {"still-here": {"content_hash": {"zh": "h"}, "chunking_version": "v1", "indexed_at": "t"}}
mf.read_kv_entry = lambda ns, key: kv_store_race.get(key)
deleted_vector_calls.clear()
deleted_kv_keys.clear()
n2 = recon.delete_orphans(["vanished", "still-here"], "ns")
check("消失的孤儿被跳过、不中止后续处理（回归测试）",
      n2 == 1 and deleted_kv_keys == ["still-here"])

# ---- main() 的 argv 校验：不认识的参数必须报错，不能静默忽略 ----
import subprocess  # noqa: E402

recon_path = str(Path(__file__).resolve().parent / "reconcile.py")
r = subprocess.run(["python3", recon_path, "--delete-orphan"], capture_output=True, text=True)
check("拼写错误的 --delete-orphan 被拒绝而不是静默忽略（回归测试）", r.returncode == 2)

# ---- 回归测试：delete_by_ids 返回 success=false 时，不能删 manifest 记录（跟 T1.4.1 的
# upsert success=false 是同一类 bug，这里更严重——manifest 记录一删，下一轮 find_orphans
# 就再也看不到这个 key，孤儿永久漏网、向量永久留在生产索引里）。----
kv_store3 = {"still-orphan": {"content_hash": {"zh": "h"}, "chunking_version": "v1", "indexed_at": "t"}}
deleted_kv_keys2 = []
mf.read_kv_entry = lambda ns, key: kv_store3.get(key)
mf.delete_kv_entry = lambda ns, key: deleted_kv_keys2.append(key)
recon.bvi.delete_by_ids = lambda index_name, ids: {"success": False, "errors": ["boom"]}
n3 = recon.delete_orphans(["still-orphan"], "ns")
check("delete_by_ids success=false 时不计入删除计数（回归测试）", n3 == 0)
check("delete_by_ids success=false 时不删 manifest 记录，留给下一轮重试（回归测试）",
      deleted_kv_keys2 == [])

# ---- 回归测试：list_local_slugs 必须用原始文件列表，不能用 load_articles 解析成功的子集——
# 一篇 frontmatter 解析失败（缺 title）的文章，文件还在磁盘上，不该被判成孤儿。----
import tempfile  # noqa: E402
import shutil  # noqa: E402

tmp_blog_dir = Path(tempfile.mkdtemp()) / "blog"
tmp_blog_dir.mkdir()
(tmp_blog_dir / "good-article.md").write_text(
    '---\ntitle: "Good"\ndescription: "d"\ntags: [a]\n---\n<!--EN-->\nbody\n', encoding="utf-8"
)
# 没有 title 字段——bvi.parse_frontmatter 能 match 出 frontmatter block，但 field("title")
# 拿到空字符串，incremental-index.py:load_articles 里 `if fm and fm["title"]` 这个条件
# 会把它整篇丢掉,不进 load_articles(None) 的返回值——但文件本身仍然存在于磁盘上。
(tmp_blog_dir / "broken-frontmatter.md").write_text(
    '---\ndescription: "no title field"\n---\nbody\n', encoding="utf-8"
)
# 回归测试：.mdx 是 astro 内容集合真实支持的扩展名（`src/content.config.ts` pattern 是
# `**/*.{md,mdx}`），本仓库确实有一篇发布中的 .mdx 文章——只 glob "*.md" 会让它在
# load_articles(None) 和 list_local_slugs 里都不可见，两边"看不见"程度不一致的话，
# reconcile.py 会把它误判成孤儿删掉。
(tmp_blog_dir / "mdx-article.mdx").write_text(
    '---\ntitle: "MDX"\ndescription: "d"\ntags: [a]\n---\n<!--EN-->\nbody\n', encoding="utf-8"
)
try:
    original_bvi_blog_dir = recon.bvi.BLOG_DIR
    original_incr_blog_dir = recon.incr.BLOG_DIR
    recon.bvi.BLOG_DIR = tmp_blog_dir
    recon.incr.BLOG_DIR = tmp_blog_dir
    parsed = recon.incr.load_articles(None)
    parsed_slugs = {a["slug"] for a in parsed}
    local_slugs = recon.list_local_slugs()
    check("frontmatter 解析失败的文章不在 load_articles(None) 的结果里（确认 bug 场景成立）",
          parsed_slugs == {"good-article", "mdx-article"})
    check("list_local_slugs 用原始文件列表，三篇都在（回归测试：不会把它误判成孤儿）",
          local_slugs == {"good-article", "broken-frontmatter", "mdx-article"})
    check(".mdx 文章能被 load_articles(None) 正常解析出来（回归测试：不再是全库扫描的盲点）",
          "mdx-article" in parsed_slugs)
finally:
    recon.bvi.BLOG_DIR = original_bvi_blog_dir
    recon.incr.BLOG_DIR = original_incr_blog_dir
    shutil.rmtree(tmp_blog_dir.parent)

print()
if failures:
    print(f"FAILED: {len(failures)} check(s): {failures}")
    sys.exit(1)
print("all checks passed")
