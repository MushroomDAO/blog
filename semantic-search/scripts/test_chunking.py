#!/usr/bin/env python3
"""
T1.3.2 验收测试：对真实文章跑分片，断言 chunk 数与 language 分布符合预期。
不调用任何网络/Cloudflare API，纯本地跑。

用法：python3 semantic-search/scripts/test_chunking.py
"""

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from chunking import (
    approx_token_count,
    chunk_article,
    detect_language,
    group_blocks_into_chunks,
    is_heading_block,
    make_chunk_id,
    split_into_blocks,
    strip_code_fences,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
BLOG_DIR = REPO_ROOT / "src" / "content" / "blog"

failures = []


def check(name, condition, detail=""):
    status = "PASS" if condition else "FAIL"
    print(f"[{status}] {name}" + (f" — {detail}" if detail and not condition else ""))
    if not condition:
        failures.append(name)


def read_body(slug):
    text = (BLOG_DIR / f"{slug}.md").read_text(encoding="utf-8")
    m = re.match(r"^---\n.*?\n---\n(.*)$", text, re.DOTALL)
    return m.group(1)


# --- 单元级测试：不依赖真实文章内容 ---

check(
    "strip_code_fences 剔除围栏代码块",
    "def foo" not in strip_code_fences("正文\n```python\ndef foo(): pass\n```\n后续正文"),
)

check(
    "detect_language 中文样本判定为 zh",
    detect_language("这是一段完全的中文测试文本，用来验证语言判定逻辑是否正确工作。") == "zh",
)

check(
    "detect_language 英文样本判定为 en",
    detect_language("This is a plain English sentence used to test language detection.") == "en",
)

check(
    "make_chunk_id 长度恒定且不含冒号（Vectorize id 安全字符集）",
    len(make_chunk_id("a" * 100, "zh", "paragraph", "0123456789abcdef")) == 48
    and ":" not in make_chunk_id("a" * 100, "zh", "paragraph", "0123456789abcdef"),
)

check(
    "make_chunk_id 幂等：同输入产出同 id",
    make_chunk_id("slug", "zh", "paragraph", "abc") == make_chunk_id("slug", "zh", "paragraph", "abc"),
)

check(
    "make_chunk_id chunk_type 影响 id（article 级和 paragraph 级不会撞车）",
    make_chunk_id("slug", "zh", "article", "abc") != make_chunk_id("slug", "zh", "paragraph", "abc"),
)

# 极端输入：单篇超长文章不应产出超过硬上限的片数
huge_blocks = [f"段落 {i}：" + ("很长的正文内容 " * 200) for i in range(50)]
huge_chunks = group_blocks_into_chunks(huge_blocks)
check(
    "超长文章分片数不超过硬上限 16",
    len(huge_chunks) <= 16,
    f"实际 {len(huge_chunks)} 片",
)

# 极短输入：内容不足一个 chunk 时不应该产出 0 片或报错
tiny_chunks = group_blocks_into_chunks(["一小段文字。"])
check("极短文章仍能产出至少 1 个 chunk", len(tiny_chunks) == 1)

empty_chunks = group_blocks_into_chunks([])
check("空输入不报错、返回空列表", empty_chunks == [])


# --- 真实文章测试（验收命令要求的场景）---

BILINGUAL_SLUG = "adapta-self-hosted-local-knowledge-base-guide"
bilingual_path = BLOG_DIR / f"{BILINGUAL_SLUG}.md"
if bilingual_path.exists():
    body = read_body(BILINGUAL_SLUG)
    check(f"{BILINGUAL_SLUG} 确实包含 <!--EN--> 分隔符（测试样本有效性前提）", "<!--EN-->" in body)

    chunks = chunk_article(BILINGUAL_SLUG, body)
    langs = [c["language"] for c in chunks]
    zh_count = langs.count("zh")
    en_count = langs.count("en")

    check("双语文章产出的 chunk 里同时有 zh 和 en", zh_count > 0 and en_count > 0,
          f"zh={zh_count} en={en_count}")
    check("双语文章总 chunk 数在 [2, 32] 合理区间内（每种语言各自 ≤16）",
          2 <= len(chunks) <= 32, f"实际 {len(chunks)} 片")
    check("所有 chunk 只有 zh/en 两种取值，没有 bilingual",
          set(langs) <= {"zh", "en"})

    ids = [c["chunk_id"] for c in chunks]
    check("同一篇文章内 chunk_id 全部唯一（无碰撞）", len(ids) == len(set(ids)))

    for c in chunks:
        tc = approx_token_count(c["text"])
        check(f"chunk（{c['language']}, hash={c['content_hash'][:8]}）token 数在合理范围内（<=900，留有余量）",
              tc <= 900, f"实际约 {tc} tokens")
else:
    print(f"[SKIP] 测试样本文章 {BILINGUAL_SLUG}.md 不存在，跳过真实文章分片测试")

# 单语英文文章：验证语言判定不会被 titleEn 之类的 frontmatter 字段误导
# （T1.3.1 已经踩过这个坑：没有 <!--EN--> 分隔符时不能假设是中文）
MONOLINGUAL_EN_SLUG = "codexbar-macOS-menu-bar-tool"
mono_path = BLOG_DIR / f"{MONOLINGUAL_EN_SLUG}.md"
if mono_path.exists():
    body = read_body(MONOLINGUAL_EN_SLUG)
    check(f"{MONOLINGUAL_EN_SLUG} 确实不含 <!--EN--> 分隔符（单语样本有效性前提）",
          "<!--EN-->" not in body)
    chunks = chunk_article(MONOLINGUAL_EN_SLUG, body)
    langs = set(c["language"] for c in chunks)
    check("单语英文文章的 chunk 全部判定为 en（不是想当然的 zh）",
          langs == {"en"}, f"实际 {langs}")
else:
    print(f"[SKIP] 测试样本文章 {MONOLINGUAL_EN_SLUG}.md 不存在，跳过单语判定测试")

# 回归测试：正文里内联提及 "<!--EN-->" 字面量（比如用反引号引用它来说明博客的双语约定）
# 不能触发误判——真正的分隔符必须独占一行。这是对抗式 review 抓到的真实 bug：
# 之前用子串匹配，这两篇文章的大段中文内容曾被错误标成 language=en。
INLINE_MENTION_SLUGS = [
    "seo-geo-skill-ai-citation-optimization",
    "geo-generative-engine-optimization-guide",
]
for slug in INLINE_MENTION_SLUGS:
    p = BLOG_DIR / f"{slug}.md"
    if not p.exists():
        print(f"[SKIP] 测试样本文章 {slug}.md 不存在，跳过内联提及回归测试")
        continue
    body = read_body(slug)
    chunks = chunk_article(slug, body)
    CJK_ONLY_RE = re.compile(r"[一-鿿㐀-䶿]")
    mislabeled = [c for c in chunks if c["language"] == "en" and len(CJK_ONLY_RE.findall(c["text"])) > 30]
    check(f"{slug}：内联提及 <!--EN--> 不会把大段中文错误标成 en",
          len(mislabeled) == 0,
          f"发现 {len(mislabeled)} 个 en chunk 里有 >30 个中文字符")

# 回归测试：标题不能单独成一个 chunk（会在下一个 chunk 里重复出现，浪费一个几乎无用的
# 向量位）。对抗式 review 在真实文章里找到了这个案例。
HEADING_ORPHAN_SLUG = "agent-customer-service-architecture-teardown-review"
p = BLOG_DIR / f"{HEADING_ORPHAN_SLUG}.md"
if p.exists():
    body = read_body(HEADING_ORPHAN_SLUG)
    chunks = chunk_article(HEADING_ORPHAN_SLUG, body)
    orphans = [c for c in chunks if is_heading_block(c["text"].strip()) and "\n" not in c["text"].strip()]
    check(f"{HEADING_ORPHAN_SLUG}：没有只含标题、没有正文的孤儿 chunk",
          len(orphans) == 0, f"发现 {len(orphans)} 个孤儿 chunk：{[o['text'] for o in orphans]}")
else:
    print(f"[SKIP] 测试样本文章 {HEADING_ORPHAN_SLUG}.md 不存在，跳过标题孤儿回归测试")


print()
if failures:
    print(f"FAILED: {len(failures)} check(s) failed: {failures}")
    sys.exit(1)
print("all checks passed")
