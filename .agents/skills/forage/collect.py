#!/usr/bin/env python3
"""多源采集。每天 21:00 由 cron 调用。

第 2 轮我换协议过滤策略时，只重建了 GitHub 一条线，把小红书 / HF / X /
Trends 全丢了，而且清单里没有任何提示——静默的覆盖率缺失比采不到更糟，
因为它看起来像「今天这些源没东西」。

所以这里每个源都记账，跑完写 coverage.json，某源为 0 会在清单顶部标红。
"""
import json, os, re, subprocess, sys, base64, random, time
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

# 小红书节流。用户明确要求：一轮最多 10 条。
XHS_MAX = 10            # 单轮总上限
PER_CALL = 5            # 单次调用最多取几条
BLOGGERS_PER_RUN = 2    # 每轮只看 2 个博主，按天轮换

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
    """小红书采集 —— 硬上限 10 条，低频、有间隔、撞验证码立即停。

    第一版是爬虫行为，不是刷小红书：6 个博主 × 30 条 + 10 个关键词 × 20 条，
    16 次调用背靠背打完约 380 条，零间隔，还反复跑了几轮。
    结果当天就触发风控，user-posts 返回 Captcha required (type=216)。

    「像真人一样」不只是时长短，更是**量小、次数少、有停顿**：
    真人刷十几分钟大概翻二三十条，一条条滑，中间会停。
    所以这里每轮只打 3 次接口、每次最多取 5 条、总量封顶 10 条，
    调用之间随机停 8-20 秒。博主和关键词按天轮换，覆盖靠天数累积，不靠单轮堆量。
    """
    rows = []
    if "authenticated: true" not in sh(["xhs", "status", "--yaml"]):
        cov["小红书"] = 0
        cov["_xhs_error"] = "cookie 失效，需重新扫码登录（xhs login）"
        return rows

    def take(out, src):
        """解析一次调用的结果。撞验证码就抛出，让整轮立刻停手。"""
        if not out:
            return []
        if "verification_required" in out or "Captcha" in out:
            raise RuntimeError("captcha")
        got = []
        try:
            for n in json.loads(out).get("data", {}).get("notes", [])[:PER_CALL]:
                t = n.get("display_title") or n.get("title") or ""
                if not t:
                    continue
                nid = n.get("note_id") or n.get("id") or ""
                got.append(dict(src=src, title=t, desc="",
                    url=f"https://www.xiaohongshu.com/explore/{nid}" if nid else "", stars=None))
        except (json.JSONDecodeError, AttributeError):
            pass
        return got

    # 按天轮换：今天取这 2 个博主，明天下 2 个。覆盖靠天数累积。
    day = datetime.now(timezone.utc).timetuple().tm_yday
    ids = list(BLOGGERS.items())
    picked = [ids[(day * 2 + i) % len(ids)] for i in range(BLOGGERS_PER_RUN)]
    kw = (CORE_KW + ROTATE_KW)[day % len(CORE_KW + ROTATE_KW)]

    calls = [(["xhs", "user-posts", uid, "--json"], f"小红书@{name}") for uid, name in picked]
    calls.append((["xhs", "search", kw, "--json"], f"小红书·搜索<{kw}>"))

    try:
        for i, (cmd, src) in enumerate(calls):
            if len(rows) >= XHS_MAX:
                break
            if i:                                  # 首次不等，之后每次都停
                time.sleep(random.uniform(8, 20))
            rows.extend(take(sh(cmd), src))
        rows = rows[:XHS_MAX]
    except RuntimeError:
        # 撞验证码：立即停手，并且**明确报出来**。
        # 静默返回 0 会让人以为「今天没内容」，而不是「被风控了」。
        cov["小红书"] = len(rows)
        cov["_xhs_error"] = ("撞到验证码，本轮已停止。需人工过验证："
                             "用 CDP 浏览器打开小红书完成验证后 cookie 会刷新")
        return rows

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
