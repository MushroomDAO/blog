#!/usr/bin/env python3
"""把 collect.py 的原始采集，去重限量后拉一手信息装库。

cron 环境里能做的都做完：三层去重、配额、协议、README、五原则机械判定。
**做不了的是判断**——「核心增量是什么」「值得从哪几个角度写」需要真读懂内容。
那部分留空标「待判断」，Claude 在会话里补。
"""
import json, os, re, sys, base64, subprocess, hashlib, random
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from store import conn, entities, norm

OUT = "/tmp/forage"
ENV = dict(os.environ); ENV["GH_DEBUG"] = ""
MAX_TOTAL = 10  # 用户明确要求：每天总数不超过 10 条
PER_SOURCE_CAP = 5  # 用户明确要求：任意单一渠道不超过 5 条，防止一个源刷屏
# 按源分配名额，不是先到先得。
# 纯按「一手源优先」排序会让 GitHub+HF 占满全部 10 个名额，
# 小红书采了 171 条却一条进不来——那它就白采了。
# 小红书的定位是线索源：它提供的是「有这么个东西」，
# 值不值得写还得回 GitHub/HF 查一手，但没有它就少了一个发现渠道。
# 下面每个数字都要 <= PER_SOURCE_CAP，改的时候留意别超。
QUOTA = {"GitHub": 4, "HuggingFace": 3, "小红书": 3}
assert all(v <= PER_SOURCE_CAP for v in QUOTA.values()), "某个源的配额超过了 PER_SOURCE_CAP"
def quota_key(src):
    if src.startswith("小红书"): return "小红书"
    if src.startswith("X"): return "X"
    return src

DOMAIN_VETO = [
    (r"meta ads|google ads|facebook ads|广告投放", "广告"),
    (r"\brouter\b|keenetic|openwrt|wi-?fi", "网络设备"),
    (r"app store submit|应用商店上架|testflight", "上架流程"),
    (r"选品|带货|直播话术|copywriter|文案公式", "营销"),
    (r"报税|记账|\berp\b|发票", "财务"),
    (r"简历|resume|面试题", "求职"),
    (r"\bjava\b|jvm|kotlin|scala|spring boot", "JVM系"),
    (r"common lisp|clojure|haskell|erlang|elixir", "小众函数式"),
    (r"\.net\b|c#|asp\.net", ".NET系"),
    (r"\b3d\b|metaverse|元宇宙|unity|unreal", "3D/元宇宙"),
    (r"kubernetes|k8s|集群部署|sso|saml", "企业级"),
    # 内容类型
    (r"融资|轮融资|estimated valuation|行业观察", "纯新闻"),
]


def sh(a, t=25):
    try:
        return subprocess.run(a, capture_output=True, text=True, timeout=t, env=ENV).stdout
    except Exception:
        return ""


def vetoed(text):
    t = norm(text)
    for pat, name in DOMAIN_VETO:
        if re.search(pat, t):
            return name
    return None


def principles(text, lic):
    t = norm(text)
    return {
        "本地优先": bool(re.search(r"local.?first|本地|offline|离线|on-device|self.?host|自托管|ollama|llama\.cpp|mlx|gguf", t)),
        "隐私自主": bool(re.search(r"privacy|隐私|no telemetry|无遥测|never leaves|data stays|离线|self.?host", t)),
        "开源开放": bool(lic and lic not in ("NONE", "", "other")),
        # 判据是「一个人装得起来吗」，不是「有没有依赖」——需要 PostgreSQL 不算违背
        "个人可及": not bool(re.search(r"kubernetes|k8s|集群|cluster|sso|saml|per.?seat|enterprise only", t)),
        "一手可查": True,
    }


def main():
    rows = json.load(open(f"{OUT}/raw.json"))
    cov = json.load(open(f"{OUT}/coverage.json"))
    c = conn()
    seen = {r["entity"] for r in c.execute("SELECT entity FROM seen")}
    # 已经做过决定的条目，标题直接进黑名单：重采到也不再入库。
    # 之前用 INSERT OR REPLACE 会把整行覆盖，连同用户的决定一起抹掉——
    # aegra 被用户标了「写」，第二天重新采到就被清成未决定了。
    decided = {r["title"] for r in c.execute("SELECT title FROM items WHERE decision!=''")}

    # 一手源优先：GitHub > HF > 小红书 / X
    rank = lambda s: 3 if s == "GitHub" else 2 if s == "HuggingFace" else 1
    rows.sort(key=lambda r: -rank(r["src"]))

    kept, per_src, run_ents = [], {}, set()
    drop = {"veto": 0, "seen": 0, "decided": 0, "cross": 0, "src_cap": 0, "total_cap": 0}

    for r in rows:
        txt = f"{r['title']} {r.get('desc','')}"
        if vetoed(txt):
            drop["veto"] += 1; continue
        ents = {e for e in entities(txt) if len(e) > 4}
        if any(e in seen for e in ents):
            drop["seen"] += 1; continue
        if r["title"] in decided:
            drop["decided"] += 1; continue
        if any(e in run_ents for e in ents):
            drop["cross"] += 1; continue
        src = quota_key(r["src"])
        if per_src.get(src, 0) >= QUOTA.get(src, 2):
            drop["src_cap"] += 1; continue
        if len(kept) >= MAX_TOTAL:
            drop["total_cap"] += 1; continue
        per_src[src] = per_src.get(src, 0) + 1
        run_ents |= ents
        kept.append(r)

    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    run = datetime.now(timezone.utc).strftime("%Y%m%d")
    # 清掉所有未决定的（不只是更早日期的）。同一天重复跑会堆积——
    # 今天测试跑了 3 次，条目从 9 涨到 28。已决定的不动。
    c.execute("DELETE FROM items WHERE decision=''")

    for r in kept:
        lic, readme = "NONE", ""
        if r["src"] == "GitHub":
            lic = (sh(["gh", "api", f"repos/{r['title']}", "--jq", '.license.spdx_id // "NONE"']) or "NONE").strip()
            rd = sh(["gh", "api", f"repos/{r['title']}/readme", "--jq", ".content"]).strip()
            if rd:
                try: readme = base64.b64decode(rd).decode("utf-8", "ignore")[:2400]
                except Exception: pass
        P = principles(f"{r['title']} {r.get('desc','')} {readme}", lic)
        R = dict(stars=r.get("stars"), lic=lic if lic != "NONE" else "未声明",
                 lang="", pushed="", core="", angles=[], gap="",
                 principles=P, readme_head=readme[:900], staged=True)
        iid = hashlib.sha1(f"{r['src']}|{r['title']}".encode()).hexdigest()[:16]
        c.execute("""INSERT OR IGNORE INTO items
            (id,run_date,src,author,title,url,descr,entity,auto_score,hits,research,ai_note,created_at,updated_at)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (iid, run, r["src"], r["src"], r["title"], r.get("url", ""), r.get("desc", ""),
             ",".join(sorted(entities(r["title"]))[:5]), 0, "[]",
             json.dumps(R, ensure_ascii=False), "", now, now))
        for e in list(entities(r["title"]))[:5]:
            c.execute("INSERT OR IGNORE INTO seen VALUES (?,?,?,?)", (e, now, "radar", r["title"][:60]))
    c.execute("INSERT OR REPLACE INTO seen VALUES (?,?,?,?)",
              ("__coverage__", now, "meta", json.dumps(cov, ensure_ascii=False)))
    c.commit()

    print(f"采集 {len(rows)} → 入库 {len(kept)}")
    for k, v in drop.items():
        print(f"  丢弃·{k}: {v}")
    print("各源入库:", dict(per_src))
    zero = [k for k, v in cov.items() if not k.startswith("_") and v == 0]
    if zero:
        print(f"⚠️ 本轮为 0 的源: {', '.join(zero)}")
    print("→ 条目已标 staged，核心增量待 Claude 在会话内补充")


if __name__ == "__main__":
    main()
