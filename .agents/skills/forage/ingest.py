#!/usr/bin/env python3
"""把采集结果去重、打分、限量后写入库。

三层去重（按顺序）：
  1. vs 已发布文章 —— seen 表里 origin='published' 的实体
  2. vs 历史雷达   —— seen 表里 origin='radar' 的实体，上轮见过的不再冒出来
  3. 同轮内跨来源 —— 几个博主同时聊一个仓库/模型，只保留信息最全的那条
     （优先级：GitHub > HuggingFace > 小红书；同级取分高的）

两条限量（你明确要求的）：
  - 单个博主每轮最多 5 条 —— 防止把某个号一次挖几十条，那是采集内容不是采集偏好
  - 每轮总量最多 30 条 —— 目标是筛出符合偏好的，不是产出量

五维打分（各 20 分，合计 100）：见 store.py 的 DIMS。
"""
import json, os, sys, hashlib, re, glob
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from store import conn, entities, norm, DIMS

MAX_PER_AUTHOR = 5
MAX_TOTAL = 30
RUN = datetime.now(timezone.utc).strftime("%Y%m%d")

SRC_RANK = {"GitHub": 3, "HuggingFace": 2}   # 越大越优先保留


def src_rank(src):
    return SRC_RANK.get(src, 1)


def dims_from(row, research):
    """把关键词分和调研结果折成 5 个维度。

    这不是随便拆的——每一维对应一类可独立判断的问题，
    这样你我打分不一致时，能定位到是哪一维的判断不同。
    """
    hits = row.get("hits") or []
    txt = norm(f"{row['title']} {row.get('desc','')}")
    src = row["src"]
    has_repo = src in ("GitHub", "HuggingFace")

    # 相关性：主题命中的密度
    topical = sum(1 for h in hits if "(" in h and not h.startswith(("逆热度", "已烂大街", "HF一手")))
    relevance = min(20, round(topical * 3.2))

    # 一手性：能不能直接拿到原始仓库/模型卡
    primary = 18 if src == "GitHub" else 16 if src == "HuggingFace" else 5
    if research.get("lic") and "未声明" in str(research.get("lic")):
        primary -= 4          # 没协议 = 一手源不完整，影响能不能依赖
    primary = max(0, primary)

    # 可落地：有没有部署路径 / 硬件 / 成本
    act = 0
    for pat, w in [(r"部署|deploy|install|安装|上手|教程", 7),
                   (r"成本|cost|显存|vram|价格", 7),
                   (r"本地|local|离线|on-device", 4),
                   (r"mac|apple silicon|mlx", 2)]:
        if re.search(pat, txt): act += w
    actionable = min(20, act)

    # 新颖度：本站没写过 + 没被搬烂
    nov = 12
    stars = row.get("stars")
    if stars is not None:
        if stars < 50: nov += 6
        elif stars < 500: nov += 3
        elif stars > 5000: nov -= 6
    if row.get("bridge"): nov += 4      # 桥接探测命中 = 打到了空白方向
    novelty = max(0, min(20, nov))

    # 延展性：能不能展开成多个角度
    ext = min(20, len(research.get("angles", [])) * 5) if research.get("angles") else (
        12 if has_repo else 6)
    extensible = ext

    vals = dict(relevance=relevance, primary=primary, actionable=actionable,
                novelty=novelty, extensible=extensible)
    vals["total"] = sum(vals.values())
    return vals


def main():
    scored = json.load(open("/tmp/forage/scored.json"))
    research = json.load(open("/tmp/forage/research.json")) if os.path.exists("/tmp/forage/research.json") else {}

    c = conn()
    seen = {r["entity"]: r["origin"] for r in c.execute("SELECT entity, origin FROM seen")}

    rows = [r for r in scored if not r.get("veto")]
    kept, dropped = [], {"published": 0, "radar": 0, "cross": 0, "author_cap": 0, "total_cap": 0}
    run_entities = {}

    # 按「信息量优先」排序：GitHub/HF 在前，同级按分
    rows.sort(key=lambda r: (-src_rank(r["src"]), -r["score"]))

    per_author = {}
    for r in rows:
        ents = entities(f"{r['title']} {r.get('desc','')}")
        strong = {e for e in ents if len(e) > 4}

        # 层 1+2：撞上已发布或历史雷达
        hit = next((e for e in strong if e in seen), None)
        if hit:
            dropped["published" if seen[hit] == "published" else "radar"] += 1
            continue

        # 层 3：同轮内跨来源重复
        dupe = next((e for e in strong if e in run_entities), None)
        if dupe:
            dropped["cross"] += 1
            continue

        author = r["src"]
        if per_author.get(author, 0) >= MAX_PER_AUTHOR:
            dropped["author_cap"] += 1
            continue

        if len(kept) >= MAX_TOTAL:
            dropped["total_cap"] += 1
            continue

        per_author[author] = per_author.get(author, 0) + 1
        for e in strong: run_entities[e] = True
        kept.append(r)

    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    for r in kept:
        R = research.get(r["title"], {})
        d = dims_from(r, R)
        iid = hashlib.sha1(f"{r['src']}|{r['title']}".encode()).hexdigest()[:16]
        author = r["src"].split("@")[-1] if "@" in r["src"] else r["src"]
        c.execute("""INSERT OR REPLACE INTO items
            (id,run_date,src,author,title,url,descr,entity,auto_score,hits,research,
             ai_relevance,ai_primary,ai_actionable,ai_novelty,ai_extensible,ai_total,ai_note,
             created_at,updated_at)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (iid, RUN, r["src"], author, r["title"], r.get("url",""), r.get("desc",""),
             ",".join(sorted(entities(r["title"]))[:5]), r["score"],
             json.dumps(r.get("hits",[]), ensure_ascii=False),
             json.dumps(R, ensure_ascii=False),
             d["relevance"], d["primary"], d["actionable"], d["novelty"], d["extensible"],
             d["total"], R.get("why",""), now, now))
        # 记进 seen，下轮不再重复出现
        for e in list(entities(r["title"]))[:5]:
            c.execute("INSERT OR IGNORE INTO seen VALUES (?,?,?,?)", (e, now, "radar", r["title"][:60]))
    c.commit()

    print(f"采集 {len(scored)} → 入库 {len(kept)}")
    print(f"  去重·已发布过   {dropped['published']}")
    print(f"  去重·历史雷达   {dropped['radar']}")
    print(f"  去重·同轮跨来源 {dropped['cross']}")
    print(f"  超单号 5 条上限  {dropped['author_cap']}")
    print(f"  超总量 30 上限   {dropped['total_cap']}")
    print("\n各来源入库数：")
    for a, n in sorted(per_author.items(), key=lambda x: -x[1]):
        print(f"  {a}: {n}")


if __name__ == "__main__":
    main()
