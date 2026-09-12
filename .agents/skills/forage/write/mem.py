#!/usr/bin/env python3
"""发布后入账：从交接 JSON 生成 project memory 文件，追加 MEMORY.md 索引，并挖进 MemPalace。

    python3 .agents/skills/forage/write/mem.py SLUG "一行描述（含日期和一句话结论）" "索引标题"

MemPalace 是跨机器查重的唯一账本（blog-publisher 规则 12），只挖这一个新文件，
不要对整个 memory 目录重跑 mine —— 那会把老条目重排一遍，账本不收敛。
"""
import json, os, re, shutil, subprocess, sys, tempfile
from datetime import date

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
STAGE = os.path.join(ROOT, "radar", "staging")
MEM = os.path.expanduser("~/.claude/projects/-Users-jason-Dev-mycelium-blog/memory")

slug, desc = sys.argv[1], sys.argv[2]
title = sys.argv[3] if len(sys.argv) > 3 else slug
j = json.load(open(f"{STAGE}/{slug}.json", encoding="utf-8"))
name = re.sub(r"[^a-z0-9]+", "-", slug.lower())[:48].strip("-")
fn = f"project_{name.replace('-', '_')}.md"

body = f"""---
name: {name}
description: {desc}
metadata:
  type: project
---

**slug**：`{slug}`
{j['memory'].strip()}
**发布状态**：{date.today().isoformat()} blog 200 + 公众号草稿 + commit/push 完成。来源 forage 评审台「开始写」任务。

[[forage-review-publish-workflow]]
"""
path = os.path.join(MEM, fn)
existed = os.path.exists(path)
open(path, "w", encoding="utf-8").write(body)
if not existed:
    with open(os.path.join(MEM, "MEMORY.md"), "a", encoding="utf-8") as f:
        f.write(f"- [{title}]({fn}) — {desc}\n")
print("memory:", fn)

if shutil.which("mempalace"):
    with tempfile.TemporaryDirectory() as d:
        shutil.copy(path, d)
        r = subprocess.run(["mempalace", "mine", d, "--wing", "blog"],
                           capture_output=True, text=True)
        print("mempalace:", "ok" if r.returncode == 0 else f"失败（不阻塞）：{r.stderr[-200:]}")
