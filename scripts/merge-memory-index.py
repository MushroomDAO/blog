#!/usr/bin/env python3
"""合并两份 MEMORY.md 索引 —— 取并集，不是「新的赢」。

为什么需要单独处理它：MEMORY.md 是**两台机器都会往里追加**的索引文件。
其余每个 .md 文件各自只有一条记忆、通常只有一台机器在改，用 rsync 的
「修改时间新的赢」是对的；但索引文件两边都在长，整文件覆盖必然丢掉
另一台新加的行。

真出过：Mac mini 的 MEMORY.md 有 4 条 MacBook 上没有的条目
（三件套规则、用户画像、minicpm5 事故复盘、compile-by-training），
如果按整文件覆盖同步，这 4 条会被静默抹掉。

去重键是链接目标（括号里的文件名），不是整行文本 —— 同一条记忆在两台
机器上的钩子描述可能不同，按整行去重会留下两条指向同一个文件的索引。
同一个目标出现在两边时，取来自**修改时间较新**那份文件的写法。

用法：merge-memory-index.py <a.md> <b.md>   # 原地把并集写回两个文件
"""
import os
import re
import sys

LINK = re.compile(r"^\s*-\s*\[[^\]]*\]\(([^)]+)\)")


def parse(path):
    """→ (头部行列表, {链接目标: 整行})，顺序保留。"""
    if not os.path.exists(path):
        return [], {}
    head, entries = [], {}
    seen_entry = False
    for line in open(path, encoding="utf-8").read().splitlines():
        m = LINK.match(line)
        if m:
            seen_entry = True
            entries[m.group(1)] = line.rstrip()
        elif not seen_entry:
            head.append(line.rstrip())
    return head, entries


def main():
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(2)
    a, b = sys.argv[1], sys.argv[2]
    head_a, ent_a = parse(a)
    head_b, ent_b = parse(b)

    # 同一目标两边都有时，用较新那份文件的写法
    a_newer = os.path.getmtime(a) >= os.path.getmtime(b) if (os.path.exists(a) and os.path.exists(b)) else os.path.exists(a)
    older, newer = (ent_b, ent_a) if a_newer else (ent_a, ent_b)
    merged = dict(older)
    merged.update(newer)

    head = head_a if head_a else head_b
    while head and not head[-1].strip():
        head.pop()

    body = "\n".join(head + [""] + list(merged.values())) + "\n"
    for p in (a, b):
        os.makedirs(os.path.dirname(p) or ".", exist_ok=True)
        open(p, "w", encoding="utf-8").write(body)

    only_a = set(ent_a) - set(ent_b)
    only_b = set(ent_b) - set(ent_a)
    print(f"MEMORY.md 并集：{len(merged)} 条"
          f"（{os.path.basename(os.path.dirname(a))} 独有 {len(only_a)}，"
          f"{os.path.basename(os.path.dirname(b))} 独有 {len(only_b)}）")
    for t in sorted(only_a | only_b):
        print(f"   + {t}")


if __name__ == "__main__":
    main()
