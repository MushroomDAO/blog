#!/usr/bin/env python3
"""把插图压到 <90KB，并把稿子里的 <!--FIG:NN--> 占位换成图片。

    python3 .agents/skills/forage/write/insert.py SLUG

没生成出来的那张，占位直接删掉（HTML 注释本身不可见，但留着会让人以为漏了）。
"""
import json, os, re, subprocess, sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
STAGE = os.path.join(ROOT, "radar", "staging")
LIMIT = 92160  # 90KB

s = sys.argv[1]
j = json.load(open(f"{STAGE}/{s}.json", encoding="utf-8"))
md = f"{ROOT}/src/content/blog/{s}.md"
if not os.path.exists(md):
    md = f"{STAGE}/{s}.md"
text = open(md, encoding="utf-8").read()
zh, sep, en = text.partition("<!--EN-->")

for k in sorted(j["figs"]):
    p = f"{ROOT}/src/assets/images/{s}-fig-{k}.png"
    if not os.path.exists(p):
        print(k, "missing")
        continue
    # 手绘线稿颜色少，降色就能大幅瘦身；不够再逐档降分辨率
    subprocess.run(["magick", p, "-strip", "-colors", "64", p], check=True)
    for args in (["-resize", "1280x", "-strip", "-colors", "48"],
                 ["-resize", "1024x", "-strip", "-colors", "32"]):
        if os.path.getsize(p) <= LIMIT:
            break
        subprocess.run(["magick", p, *args, p], check=True)
    print(k, os.path.getsize(p) // 1024, "KB")


def sub(part, lang):
    def rep(m):
        k = m.group(1)
        if not os.path.exists(f"{ROOT}/src/assets/images/{s}-fig-{k}.png"):
            return ""
        if lang == "zh":
            alt = re.split(r"[：:。，,]", j["figs"].get(k, ""))[0][:40] or f"图{int(k)}"
        else:
            alt = f"Figure {int(k)}"
        return f"![{alt}](../../assets/images/{s}-fig-{k}.png)"
    return re.sub(r"<!--FIG:(\d+)-->", rep, part)


open(md, "w", encoding="utf-8").write(sub(zh, "zh") + sep + sub(en, "en"))
print("left placeholders:", len(re.findall(r"<!--FIG:", open(md, encoding="utf-8").read())))
