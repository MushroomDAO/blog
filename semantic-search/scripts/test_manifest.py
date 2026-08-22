#!/usr/bin/env python3
"""T1.3.5 验收测试：manifest 构造逻辑。不调用任何网络/Cloudflare API。"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from manifest import GLOBAL_KEY, build_manifest, validate_key_name

failures = []


def check(name, condition, detail=""):
    status = "PASS" if condition else "FAIL"
    print(f"[{status}] {name}" + (f" — {detail}" if detail and not condition else ""))
    if not condition:
        failures.append(name)


plan = [
    {"metadata": {"article_id": "foo", "language": "zh", "content_hash": "aaa"}},
    {"metadata": {"article_id": "foo", "language": "en", "content_hash": "bbb"}},
    {"metadata": {"article_id": "bar", "language": "zh", "content_hash": "ccc"}},
]
m = build_manifest(plan, "v1", "2026-01-01T00:00:00Z")

check("global entry存在且字段正确",
      m[GLOBAL_KEY]["chunking_version"] == "v1" and m[GLOBAL_KEY]["embedding_dimensions"] == 1024)
check("双语文章 foo 的 zh/en content_hash 都记录了",
      m["foo"]["content_hash"] == {"zh": "aaa", "en": "bbb"})
check("单语文章 bar 只有 zh 记录", m["bar"]["content_hash"] == {"zh": "ccc"})
check("每篇文章一条记录，不是每个 chunk 一条（foo 只有 1 条，不是 2 条）",
      len([k for k in m if k == "foo"]) == 1)
check("总条目数 = 文章数 + 1 个 global", len(m) == 3)

try:
    validate_key_name("../../etc/passwd")
    check("validate_key_name 拒绝路径穿越字符", False)
except ValueError:
    check("validate_key_name 拒绝路径穿越字符", True)

try:
    validate_key_name("normal-article-slug")
    check("validate_key_name 接受正常 slug", True)
except ValueError:
    check("validate_key_name 接受正常 slug", False)

# 回归测试：review 抓到的真实 bug
for bad_key in ["existing-slug?evil=1", "slug#fragment"]:
    try:
        validate_key_name(bad_key)
        check(f"validate_key_name 拒绝 URL 结构字符 {bad_key!r}", False)
    except ValueError:
        check(f"validate_key_name 拒绝 URL 结构字符 {bad_key!r}", True)

try:
    build_manifest(
        [{"metadata": {"article_id": GLOBAL_KEY, "language": "zh", "content_hash": "x"}}],
        "v1", "2026-01-01T00:00:00Z",
    )
    check("build_manifest 拒绝 article_id 撞保留字 _global", False)
except ValueError:
    check("build_manifest 拒绝 article_id 撞保留字 _global", True)

print()
if failures:
    print(f"FAILED: {len(failures)} check(s): {failures}")
    sys.exit(1)
print("all checks passed")
