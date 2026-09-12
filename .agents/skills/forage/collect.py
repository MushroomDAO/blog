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
    # 2026-09-11 移除「持续学习妹妹」：9/8、9/11 两轮 4 条全是小区/生活内容，已不相关
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


def load_env_file(path):
    """读 KEY=VALUE 格式的 .env，不 source（那个文件不保证是合法 bash）。"""
    out = {}
    try:
        for line in open(path, encoding="utf-8"):
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            k = k.removeprefix("export ").strip()
            out[k] = v.strip().strip('"').strip("'")
    except OSError:
        pass
    return out


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
                # xsec_token 必须在采集这一刻存下来。裸 explore URL 读正文会返回
                # empty noteDetailMap，事后再补要多跑一次 user-posts —— 2026-09-09
                # 的调研就为此白费了 3 次调用。带在 URL 查询串里，后续
                # `xhs read <url> --xsec-token <token>` 直接可用。
                tok = n.get("xsec_token") or ""
                url = f"https://www.xiaohongshu.com/explore/{nid}" if nid else ""
                if url and tok:
                    url += f"?xsec_token={tok}"
                got.append(dict(src=src, title=t, desc="", url=url, stars=None))
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
    """可执行文件叫 twitter（不是 twitter-cli），用法 `twitter search "q" -n N`。

    凭据只走环境变量 TWITTER_AUTH_TOKEN + TWITTER_CT0（放在 ~/Dev/.env）。
    没配就直接跳过，**绝不让 twitter-cli 回退去读浏览器 cookie**——那条路径
    会弹 macOS keychain 授权框，cron 半夜跑起来就卡在弹窗上（2026-09-11）。
    """
    rows = []
    if not os.path.exists(TWITTER):
        cov["X"] = 0
        cov["_x_error"] = "twitter-cli 未安装（pipx install twitter-cli）"
        return rows
    for k, v in load_env_file(os.path.expanduser("~/Dev/.env")).items():
        if k.startswith("TWITTER_") and not ENV.get(k):
            ENV[k] = v
    if not (ENV.get("TWITTER_AUTH_TOKEN") and ENV.get("TWITTER_CT0")):
        cov["X"] = 0
        cov["_x_error"] = ("未配置 TWITTER_AUTH_TOKEN / TWITTER_CT0（写进 ~/Dev/.env）；"
                           "为避免弹 keychain，不从浏览器读 cookie")
        return rows
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
    这里只标记为「需 Claude 会话内补充」，不假装采到了。

    Claude 在会话里手动补采时：只用 mcp__google-trends__related_queries
    配 AI/科技相关关键词（如 "AI agent"、"local llm"、"open source model"），
    不要用 trending_now/每日热搜——那是全品类热搜（明星、食品召回、汇率），
    跟本站选题无关。用户明确要求：Google Trends 只看 AI 和科技。"""
    cov["GoogleTrends"] = 0
    cov["_trends_note"] = "需在 Claude 会话内经 MCP 采集（用 related_queries 配 AI/科技关键词，不要用全品类 trending_now），cron 无法直接调用"
    return []


CRAWLER_REPO = "MushroomDAO/blog"
CRAWLER_STOP = {"sme", "ai", "the", "a", "an", "of", "for", "and", "or", "to", "open", "source",
                "open-source", "kit", "pack", "starter", "template", "v0", "lite", "mini"}


def _crawler_repo_hints(component, links):
    """给一条构想找「可能的一手源」：日报里直接链到的仓库优先，其次按组件名搜 GitHub。

    只是线索，不是结论——搜出来的仓库可能只是同名，写之前要读 README 确认真的在做这件事。
    返回 (hints, search_failed)：搜索本身失败时要如实告诉卡片「没确认」，
    不能和「搜了，确实没有」混成一句「没找到对应开源项目」。
    """
    hints, seen, failed = [], set(), False
    for owner, repo in re.findall(r"github\.com/([\w.-]+)/([\w.-]+)", " ".join(links)):
        full = f"{owner}/{repo}".removesuffix(".git")
        if full.lower() in seen or owner.lower() in ("orgs", "features", "topics"):
            continue
        seen.add(full.lower())
        out = sh(["gh", "api", f"repos/{full}", "--jq",
                  '[.full_name, .stargazers_count, (.license.spdx_id // "未声明"), .pushed_at[:10], (.description // "")] | @tsv'])
        f = out.strip().split("\t")
        if len(f) >= 5 and f[1].isdigit():
            hints.append(dict(repo=f[0], stars=int(f[1]), lic=f[2], pushed=f[3], desc=f[4][:120], via="日报直链"))
        else:
            # 日报直链了仓库却查不到详情（网络/改名/删库）：保留链接，别让它从卡片上消失
            hints.append(dict(repo=full, stars=None, lic="", pushed="", desc="（仓库详情没取到）", via="日报直链"))
    name = re.split(r"[：:，,（(]", component)[0]  # 「sme-local-pool：PAIR profile、节点…」只取名字
    words = [w for w in re.split(r"[\s/_+\-`]+", name.lower()) if w and w not in CRAWLER_STOP]
    if len(words) >= 2 and len(hints) < 3:
        try:
            r = subprocess.run(["gh", "search", "repos", " ".join(words[:4]), "--sort", "stars", "--limit", "3",
                                "--json", "fullName,stargazersCount,pushedAt,description"],
                               capture_output=True, text=True, timeout=40, env=ENV)
            found = json.loads(r.stdout) if r.returncode == 0 else None
        except (OSError, subprocess.TimeoutExpired, ValueError):
            found = None
        if found is None:
            failed = True
        for r in found or []:
            if r["fullName"].lower() in seen or r["stargazersCount"] < 100:
                continue  # 100 星以下多半是同名空仓库，给了也是噪音
            # 搜索是全文模糊匹配：「capacity map」会搜出疫情床位看板。
            # 仓库名+简介里至少命中两个词才算沾边。
            hay = f"{r['fullName']} {r.get('description') or ''}".lower()
            if sum(w in hay for w in words[:4]) < 2:
                continue
            seen.add(r["fullName"].lower())
            hints.append(dict(repo=r["fullName"], stars=r["stargazersCount"], lic="",
                              pushed=(r.get("pushedAt") or "")[:10],
                              desc=(r.get("description") or "")[:120], via=f"搜「{' '.join(words[:4])}」"))
    return hints[:3], failed


def parse_daily_crawler(md, day):
    """纯解析：日报 markdown → 条目列表（不联网，repos 由调用方补）。拆出来是为了能测。"""
    # 优先级表的列每天不一样（都含 Priority 列：9/10 的表头 4 列，9/12 的表头 6 列），
    # 按表头关键词认列，不按列序
    COLS = [("theme", r"theme|topic|主题"), ("pain", r"pain|痛点"),
            ("component", r"component|capability|组件"), ("paid", r"paid|付费"), ("fit", r"content|内容")]
    table, colmap = {}, None
    for line in md.splitlines():
        if re.match(r"\|\s*(Priority|优先级)\s*\|", line):
            heads = [h.strip().lower() for h in line.strip().strip("|").split("|")][1:]
            colmap = {}
            for i, h in enumerate(heads):
                for key, pat in COLS:
                    if key not in colmap and re.search(pat, h):
                        colmap[key] = i
                        break
            continue
        m = re.match(r"\|\s*\*\*(S\d+)\*\*\s*\|(.+)\|\s*$", line)
        if m and colmap is not None:
            cells = [c.strip().strip("*").replace("`", "") for c in m.group(2).split("|")]
            table[m.group(1)] = {k: cells[i] if i < len(cells) else "" for k, i in colmap.items()}

    path = f"daily-crawler/{day}.md"
    rows = []
    # 标题写法也不统一：「## S1 — xx」「## S1. xx」「## S1：xx」
    for sec in re.split(r"(?m)^## (?=S\d+\s*[—\-.:：])", md)[1:]:
        head, _, body = sec.partition("\n")
        m = re.match(r"(S\d+)\s*[—\-.:：]\s*(.+)", head.strip())
        if not m:
            continue
        sid, title = m.group(1), m.group(2).strip()
        # 最后一个 S 段会一路延续到文末的汇总/来源清单，截到下一个二级标题为止，
        # 否则别的主题的链接会串进来
        body = re.split(r"(?m)^## ", body)[0]
        t = table.get(sid, {})
        theme, pain, component, paid, fit = (t.get(k, "") for k in ("theme", "pain", "component", "paid", "fit"))
        if not component:
            # 表里没有组件列的日子，退回正文里第一个反引号包起来的 kebab 名
            cm = re.search(r"`([a-z0-9]+(?:-[a-z0-9]+)+)`", body)
            component = cm.group(1) if cm else ""
        sig = re.search(r"(?s)### Signal\s*(.+?)(?=\n### |\Z)", body)
        signal = re.sub(r"\s+", " ", re.sub(r"(?m)^Sources?:.*$|^- .*$|[*_`>]", "", sig.group(1) if sig else ""))
        why = re.search(r"(?s)### Why it is worth tracking\s*(.+?)(?=\n### |\Z)", body)
        links = sorted(set(u.rstrip(".,)") for u in re.findall(r"https?://[^\s<>)\]]+", body)))
        rows.append(dict(
            src="daily-crawler", title=f"[{day} {sid}] {theme or title}",
            desc=f"{title} — {pain}", stars=None,
            url=f"https://github.com/{CRAWLER_REPO}/blob/main/{path}",
            crawler=dict(sid=sid, heading=title, pain=pain, component=component, paid=paid, fit=fit,
                         signal=signal.strip()[:700],
                         why=re.sub(r"\s+", " ", re.sub(r"[*_`>]", "", why.group(1)))[:400] if why else "",
                         sources=[u for u in links if "github.com" not in u][:6],
                         links=links, repos=[], repo_search_failed=False)))
    return rows


def collect_daily_crawler(day=None):
    """daily-crawler：Codex 每天早上 8-9 点直推 main 的 SME AI 选题日报（S1-S4 构想）。

    它是**建议和信息来源，不是一手源**：条目是产品/内容构想，大多没有对应仓库。
    所以这里除了把构想拆出来，还机械地做两件事，让评审台上直接看到「写的依据」：
      1. 摘出日报引用的原始报道/官方链接；
      2. 找可能已经实现该构想的真实开源项目（日报直链的仓库 + 按组件名搜 GitHub）。
    值不值得写由用户在评审台判；写的时候子 agent 仍须回一手源核实（见 write/WRITE-JOB.md）。

    用 gh api 读 origin/main 上的文件，不碰工作区——这个仓库目录有多个会话共享，
    cron 里 git pull / checkout 会打断别人。
    """
    day = day or datetime.now().strftime("%Y-%m-%d")  # day：补采/测试某一天
    path = f"daily-crawler/{day}.md"
    try:
        r = subprocess.run(["gh", "api", f"repos/{CRAWLER_REPO}/contents/{path}", "--jq", ".content"],
                           capture_output=True, text=True, timeout=40, env=ENV)
        out, err, rc = r.stdout, r.stderr, r.returncode
    except (OSError, subprocess.TimeoutExpired) as e:
        out, err, rc = "", str(e), -1
    # 「日报还没提交」和「读取失败」要分开报：前者早上 8 点前是常态，后者是故障，
    # 混成一句会让采集失败看起来像「今天没东西」
    if rc != 0:
        cov["daily-crawler"] = 0
        cov["_crawler_note"] = (f"{path} 还不存在（日报通常 8-9 点提交）" if "404" in err
                                else f"读取 {path} 失败：{err.strip()[-160:] or f'rc={rc}'}")
        return []
    try:
        md = base64.b64decode(out).decode("utf-8")
    except ValueError as e:
        cov["daily-crawler"] = 0
        cov["_crawler_note"] = f"{path} 内容解码失败：{e}"
        return []

    rows = parse_daily_crawler(md, day)
    for r in rows:
        c = r["crawler"]
        c["repos"], c["repo_search_failed"] = _crawler_repo_hints(c["component"], c.pop("links"))
    # 保留日报自己的 S1→S4 顺序，但既没原始报道也没找到仓库的沉底——按规则写不了，别占名额
    rows.sort(key=lambda r: not (r["crawler"]["repos"] or r["crawler"]["sources"]))
    cov["daily-crawler"] = len(rows)
    if not rows:
        cov["_crawler_note"] = f"{path} 存在但没解析出 S 条目——日报格式可能变了，检查 parse_daily_crawler"
    return rows


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
