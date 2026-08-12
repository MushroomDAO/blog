#!/usr/bin/env python3
"""多源采集。每天 21:00 由 cron 调用。

第 2 轮我换协议过滤策略时，只重建了 GitHub 一条线，把小红书 / HF / X /
Trends 全丢了，而且清单里没有任何提示——静默的覆盖率缺失比采不到更糟，
因为它看起来像「今天这些源没东西」。

所以这里每个源都记账，跑完写 coverage.json，某源为 0 会在清单顶部标红。
"""
import json, os, re, subprocess, sys, base64, random
from datetime import datetime, timezone, timedelta

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = "/tmp/forage"
os.makedirs(OUT, exist_ok=True)
ENV = dict(os.environ); ENV["GH_DEBUG"] = ""
TWITTER = os.path.expanduser("~/.local/bin/twitter")

BLOGGERS = {
    "5c2824d3000000000600753e": "无糖AI",
    "6720c690000000001c01b883": "小盖",
    "5b208f0511be100f9c278b53": "小天fotos",
    "5c6130b900000000110112e8": "机器之心",
    "5bfbd58b058555000168698b": "碳基智",
    "56da5342aed7585cd6ba2bc5": "持续学习妹妹",
}

# 第一梯队常驻 + 第三梯队轮换（每次随机抽，避免每天搜出同一批）
CORE_KW = ["AI Agent", "Claude Code", "MCP", "Codex", "Skill", "本地部署"]
ROTATE_KW = ["RAG", "强化学习", "多智能体", "多模态", "TTS", "视频生成",
             "AI编程", "工作流", "小模型", "开源模型", "自托管", "MLX"]

GH_QUERIES = ["agent skill", "mcp server local", "local llm inference",
              "self-hosted ai agent", "claude code skill", "local first ai"]

cov = {}


def sh(args, timeout=40):
    try:
        r = subprocess.run(args, capture_output=True, text=True, timeout=timeout, env=ENV)
        return r.stdout
    except Exception as e:
        return ""


def collect_github():
    since = (datetime.now(timezone.utc) - timedelta(days=14)).strftime("%Y-%m-%d")
    merged = {}
    for q in GH_QUERIES:
        # 注意：licenseInfo 不是 search repos 的字段，取了会整条报错。
        # --license 过滤器本身已保证协议，不需要再取字段。
        out = sh(["gh", "search", "repos", q, "--updated", f">{since}",
                  "--license", "mit", "--license", "apache-2.0",
                  "--sort", "stars", "--limit", "12",
                  "--json", "fullName,stargazersCount,description,url"])
        try:
            for r in json.loads(out or "[]"):
                merged[r["fullName"]] = dict(src="GitHub", title=r["fullName"],
                    desc=r.get("description") or "", url=r["url"],
                    stars=r["stargazersCount"])
        except Exception:
            pass
    cov["GitHub"] = len(merged)
    return list(merged.values())


def collect_hf():
    out = sh(["curl", "-s", "--max-time", "25",
              "https://huggingface.co/api/models?sort=trendingScore&direction=-1&limit=40"])
    rows = []
    try:
        for m in json.loads(out or "[]"):
            mid = m.get("modelId", "")
            rows.append(dict(src="HuggingFace", title=mid,
                desc=" ".join(m.get("tags", [])[:10]),
                url=f"https://huggingface.co/{mid}", stars=None,
                downloads=m.get("downloads", 0)))
    except Exception:
        pass
    cov["HuggingFace"] = len(rows)
    return rows


def collect_xhs():
    rows = []
    ok = "authenticated: true" in sh(["xhs", "status", "--yaml"]) or '"authenticated": true' in sh(["xhs", "status", "--json"])
    if not ok:
        cov["小红书"] = 0
        cov["_xhs_error"] = "cookie 失效，需重新扫码登录（xhs login）"
        return rows
    # 关注的博主
    for uid, name in BLOGGERS.items():
        out = sh(["xhs", "user-posts", uid, "--json"])
        try:
            for n in json.loads(out or "{}").get("data", {}).get("notes", []):
                t = n.get("display_title") or n.get("title") or ""
                if not t:
                    continue
                nid = n.get("note_id") or n.get("id") or ""
                rows.append(dict(src=f"小红书@{name}", title=t, desc="",
                    url=f"https://www.xiaohongshu.com/explore/{nid}" if nid else "", stars=None))
        except Exception:
            pass
    # 关键词：常驻 + 随机轮换
    kws = CORE_KW + random.sample(ROTATE_KW, 4)
    for kw in kws:
        out = sh(["xhs", "search", kw, "--json"])
        try:
            for n in json.loads(out or "{}").get("data", {}).get("notes", [])[:20]:
                t = n.get("display_title") or n.get("title") or ""
                if not t:
                    continue
                nid = n.get("note_id") or n.get("id") or ""
                rows.append(dict(src=f"小红书·搜索<{kw}>", title=t, desc="",
                    url=f"https://www.xiaohongshu.com/explore/{nid}" if nid else "", stars=None))
        except Exception:
            pass
    cov["小红书"] = len(rows)
    return rows


def collect_x():
    """可执行文件叫 twitter（不是 twitter-cli），用法 `twitter search "q" -n N`。"""
    rows = []
    for kw in ["claude code skill", "local llm", "open source agent"]:
        out = sh([TWITTER, "search", kw, "-n", "15"], timeout=45)
        if not out.strip():
            continue
        # twitter-cli 目前是坏的（ClientTransaction 初始化失败 → HTTP 404）。
        # 早期版本我把错误输出当内容抓了进来，产生 3 条垃圾「推文」。
        # agent-reach doctor 报它 ok 只验证了二进制存在，不代表能跑。
        if re.search(r"ok:\s*false|error:|HTTP 4\d\d|Failed to init", out):
            cov["_x_error"] = "twitter-cli 调用失败（ClientTransaction/404），需修复后才有数据"
            continue
        try:
            data = json.loads(out)
            items = data if isinstance(data, list) else (
                data.get("data") or data.get("tweets") or data.get("results") or [])
            for t in items[:15]:
                txt = (t.get("text") or t.get("full_text") or "").replace("\n", " ")
                if txt:
                    rows.append(dict(src=f"X·<{kw}>", title=txt[:110], desc="",
                        url=t.get("url") or "", stars=None))
        except json.JSONDecodeError:
            # 非 JSON 输出：按行取有实质内容的
            for line in out.splitlines():
                line = line.strip()
                if len(line) > 30 and not line.startswith(("=", "-", "#")):
                    rows.append(dict(src=f"X·<{kw}>", title=line[:110], desc="",
                                     url="", stars=None))
    cov["X"] = len(rows)
    return rows


def collect_trends():
    """Google Trends 通过 MCP 提供，cron 环境里没有 MCP 客户端。
    这里只标记为「需 Claude 会话内补充」，不假装采到了。"""
    cov["GoogleTrends"] = 0
    cov["_trends_note"] = "需在 Claude 会话内经 MCP 采集，cron 无法直接调用"
    return []


def main():
    rows = []
    rows += collect_github()
    rows += collect_hf()
    rows += collect_xhs()
    rows += collect_x()
    rows += collect_trends()

    json.dump(rows, open(f"{OUT}/raw.json", "w"), ensure_ascii=False)
    cov["_total"] = len(rows)
    cov["_at"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    json.dump(cov, open(f"{OUT}/coverage.json", "w"), ensure_ascii=False, indent=1)

    print(f"采集完成 共 {len(rows)} 条")
    for k, v in cov.items():
        if k.startswith("_"):
            continue
        flag = "  ⚠️ 该源为 0" if v == 0 else ""
        print(f"  {k:<14} {v:>5}{flag}")
    for k in ("_xhs_error", "_trends_note", "_x_error"):
        if cov.get(k):
            print(f"  注意：{cov[k]}")


if __name__ == "__main__":
    main()
