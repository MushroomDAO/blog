#!/usr/bin/env python3
"""forage 的持久层：SQLite。

解决三件事：
1. **决定要能被我读到** —— 之前的页面写 localStorage，那是浏览器沙箱里的数据，
   agent 完全读不到，等于白点。现在全部落库，我直接 sqlite3 读。
2. **跨轮次去重** —— seen 表记住每个实体（仓库名/模型名）第一次出现的时间和出处。
   已发过的文章、以前雷达见过的，都不再重复冒出来。
3. **双向打分校准** —— 同一条目存两套 5 维分（我的 + 你的），差值就是校准信号。

用法：
    python3 store.py init          建库 + 用已发布文章播种 seen 表
    python3 store.py sync          重新播种已发布文章 + 把已发布的 write/dig 条目转成 published
    python3 store.py stats         看当前状态

sync 存在的原因：init 只在建库那一刻跑一次，之后每天新发的文章从来没被
重新播种进 seen 表。结果是——同一个仓库如果哪天被自动采集用了另一种措辞
重新命中，decided 标题黑名单（精确字符串匹配）拦不住，会当成新线索再冒出来；
更直接的是，评审台里那些老早就点了「写」、后来也确实发出去了的条目，
会永远停留在「写」桶里，跟真正还没写的混在一起，看起来像是「怎么又出现了」。
sync 就是把这两处状态跟 src/content/blog/ 的真实发布情况对一次账。
应该跟 run-daily.sh 一起每天跑。
"""
import sqlite3, os, re, glob, sys, hashlib, json
from collections import Counter
from datetime import datetime, timezone

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
DB = os.path.join(ROOT, "radar", "forage.db")

# 5 个打分维度。满分各 20，合计 100。
DIMS = [
    ("relevance",  "相关性", "符合本站方向（开源 / 可本地跑 / Agent 生态）"),
    ("primary",    "一手性", "能找到 GitHub 仓库、HF 模型卡或论文原文"),
    ("actionable", "可落地", "有部署路径、硬件要求或成本数字可写"),
    ("novelty",    "新颖度", "本站没写过，且没被搬运烂"),
    ("extensible", "延展性", "能展开成多个角度，不是一次性新闻"),
]

SCHEMA = """
CREATE TABLE IF NOT EXISTS items (
  id          TEXT PRIMARY KEY,
  run_date    TEXT NOT NULL,
  src         TEXT,
  author      TEXT,
  title       TEXT,
  url         TEXT,
  descr       TEXT,
  entity      TEXT,
  auto_score  REAL,
  hits        TEXT,
  research    TEXT,
  ai_relevance INTEGER, ai_primary INTEGER, ai_actionable INTEGER,
  ai_novelty INTEGER, ai_extensible INTEGER, ai_total INTEGER, ai_note TEXT,
  u_relevance INTEGER, u_primary INTEGER, u_actionable INTEGER,
  u_novelty INTEGER, u_extensible INTEGER, u_total INTEGER, u_note TEXT,
  decision    TEXT DEFAULT '',
  created_at  TEXT, updated_at TEXT
);
-- 见过的实体。跨轮次、跨来源去重的唯一依据。
CREATE TABLE IF NOT EXISTS seen (
  entity     TEXT PRIMARY KEY,
  first_seen TEXT,
  origin     TEXT,   -- published | radar
  ref        TEXT
);
CREATE INDEX IF NOT EXISTS idx_items_run  ON items(run_date);
CREATE INDEX IF NOT EXISTS idx_items_dec  ON items(decision);
"""

STOP = {
    "the","and","for","with","how","you","your","are","not","from","open","source",
    "ai","llm","agent","agents","code","coding","skill","skills","mcp","model","models",
    "claude","codex","cursor","gemini","github","tool","tools","new","use","using","本地",
    "开源","模型","工具","项目","这个","一个","可以","支持","实现","如何","什么",
}


def norm(s):
    return re.sub(r"[^a-z0-9一-鿿]+", " ", (s or "").lower()).strip()


def entities(text, strict=False):
    """抽出能当去重键的专有名词：仓库名、模型名、产品名。

    只认「有辨识度」的 token —— 驼峰、含数字版本号、含连字符的复合词。
    通用词（agent/mcp/开源）不是实体，否则所有条目都会互相判重。

    strict=True 时额外禁用「首字母大写 = 专有名词」这条启发式。它对散文式的
    描述文本管用（desc 里的 "Ollama" 确实是产品名），但对**文章标题**是灾难：
    英文标题走 Title Case，"Local First Server" 里三个词全大写开头，抽出来的
    local / first / server 根本不是实体。播种 seen 表时必须 strict，否则
    557 篇文章的标题会把一堆通用词灌进去，之后任何项目描述沾上一个就被判重。
    """
    out = set()
    for w in re.findall(r"[A-Za-z][A-Za-z0-9]*(?:[-._][A-Za-z0-9]+)+|[A-Z][a-z]+[A-Z][A-Za-z]*", text or ""):
        wl = w.lower().strip("-._")
        if len(wl) > 3 and wl not in STOP:
            out.add(wl)
    for w in re.findall(r"\b[A-Za-z][A-Za-z0-9]{3,}\b", text or ""):
        wl = w.lower()
        if wl in STOP:
            continue
        if any(c.isdigit() for c in wl) or (w[0].isupper() and not strict):
            out.add(wl)
    return out


def repo_fragment(title):
    """从条目标题里取最有辨识度的那一段，用于子串匹配。

    "u14app/neo-chat" → "neo-chat"；"markhuangai/dense-mem" → "dense-mem"；
    没有斜杠的（HF 模型名常见）就用整个标题。这是因为本站发文的 slug 惯例
    是「项目名-描述性词语」，项目名原样嵌在 slug 里
    （neo-chat-local-first-encrypted-sync-mcp-rag-workspace 里有 "neo-chat"）。
    entities() 那套词袋匹配对这种复合项目名并不可靠——连字符一拆，
    "neo-chat" 就找不回来了，只能退化成 "neo"（3 个字符，太短不算实体）
    或 "chat"（太通用）。子串匹配直接、可解释，比词袋更适合这个场景。
    """
    frag = title.rsplit("/", 1)[-1] if "/" in title else title
    frag = re.sub(r"[^a-z0-9-]+", "-", frag.lower()).strip("-")
    return frag


def published_match(title, by_slug):
    """标题的 repo_fragment 是不是某篇已发布文章 slug 里的一个完整词。命中返回 slug，否则 None。

    真出过事：getomnico/omni 的 frag 是 "omni"，只有 4 个字符，被旧版"长度>=5"
    的门槛拦住了，导致这篇明明 8/18 就发过的文章没被识别成已发布，一路混进了
    「写」的队列，用户差点让我把它重新写一遍。
    教训是：光靠拉长最小长度换不来安全，真正该做的是**按连字符分词边界比对**——
    "omni" 必须是 slug 里独立的一段（"omni-open-source-..." 的开头，或者被
    "-" 夹在中间/结尾），不能是任意子串（比如不能让 "omni" 命中
    "insomnia-something" 这种把 "omni" 吞在词中间的假阳性）。
    边界匹配比"子串+长度门槛"精确得多，长度门槛可以放宽到 4。

    但边界匹配本身也翻过车：getomnico/omni 的 frag "omni" 用边界匹配对上了
    两篇完全不相关的文章（企业 agent「Omni」 vs 多模态模型「MiniCPM-o」，
    slug 里都有独立的 "omni" 词段），自动挑了第一个命中的，挑错了。
    "omni"/"all"/"core" 这类通用英文词短到 4 个字符时，边界匹配也救不回来。
    所以命中多篇的情况不自动下结论——返回 None，交给人工核对哪篇才是真的，
    比自动选一个（很可能选错）安全。

    还有一种漏网的：agentskills/agentskills（一个词，没连字符）实际发过了，
    slug 是 agent-skills-open-standard-...——写文章时把它按人类习惯拆成了
    "Agent Skills"两个词，slug 化后中间多了个连字符。边界匹配找“agentskills”
    这个完整词根本找不到，因为 slug 里从来没有连着不带连字符的"agentskills"。
    补一层：把 slug 按"-"拆词后，相邻 2/3 个词**贴在一起（不加连字符）**
    再跟 frag 比对——"agent"+"skills" 贴成"agentskills"就对上了。
    这一层要求整词相等，不是子串，所以不会重新引入子串误判的老问题。
    """
    frag = repo_fragment(title)
    if len(frag) < 4:
        return None
    hits = set()
    for slug in by_slug:
        if slug == frag or slug.startswith(frag + "-") or slug.endswith("-" + frag) or f"-{frag}-" in slug:
            hits.add(slug)
            continue
        words = slug.split("-")
        for n in (2, 3):
            for i in range(len(words) - n + 1):
                if "".join(words[i:i + n]) == frag:
                    hits.add(slug)
    return next(iter(hits)) if len(hits) == 1 else None


def conn():
    os.makedirs(os.path.dirname(DB), exist_ok=True)
    c = sqlite3.connect(DB)
    c.row_factory = sqlite3.Row
    return c


# 一个词出现在多少篇已发布文章里，就不再算「有辨识度的专有名词」。
# 真出过事（2026-09-05）：seen 表播种时把标题里所有首字母大写的英文词都当了
# 实体，557 篇文章攒出 local / server / docker / google / harness / browser /
# first / search / apache / three 这一堆通用词。结果当晚 GitHub 采到的 70 条
# 里 63 条被判「已见过」——只要项目描述里出现 "local" 或 "server" 就出局，
# 整个 GitHub 源一条都进不了库，雷达空转。
# 手工维护停用词表治标不治本（通用词是无限的），用文档频次数据驱动：
# 专有名词天然只出现在讲它的那一两篇里，通用词才会横跨很多篇。
DF_CAP = 3


def blog_entities():
    """扫 src/content/blog/ 抽每篇的实体，返回 {slug: {entities}}。不写库。"""
    by_slug = {}
    for f in glob.glob(os.path.join(ROOT, "src", "content", "blog", "*.md")):
        slug = os.path.basename(f)[:-3]
        title = ""
        for line in open(f, encoding="utf-8"):
            if line.startswith("title:"):
                title = line.split(":", 1)[1].strip().strip('"').strip("'"); break
        # slug 原样也要抽一遍：把连字符替换成空格会拆碎复合项目名
        # （"neo-chat-local-first..." → "neo chat local first..."，
        # "neo-chat" 这个真正的实体名就再也拼不出来了），
        # 只留 replace(" ") 版本是为了拆出独立词，两种都要，不能互相替代。
        by_slug[slug] = (entities(slug, strict=True) | entities(slug.replace("-", " "), strict=True)
                         | entities(title, strict=True))
    return by_slug


def seed_from_blog(c):
    """扫 src/content/blog/ 播种 seen 表。幂等，可重复跑（INSERT OR IGNORE）。

    跨 DF_CAP 篇以上的高频词不入 seen——它们是通用词不是实体，当去重键会误杀。
    但仍然留在返回的 by_slug 里：published_match / sync 那边是拿整个 slug 做
    边界匹配，不受高频词影响，删了反而会漏掉真重复。

    返回 {slug: {entities}}，供 sync() 复用，不用再扫一次文件系统。
    """
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    by_slug = blog_entities()
    df = Counter(e for ents in by_slug.values() for e in ents)
    # 先清空再重播，而不是纯 INSERT OR IGNORE 往上叠：抽取规则一旦收紧
    # （比如 strict / DF_CAP），旧规则灌进去的脏实体不会自己消失，
    # 修了代码也照样误杀。播种本来就该是「按当前规则重建」而不是「累加」。
    c.execute("DELETE FROM seen WHERE origin='published'")
    for slug, ents in by_slug.items():
        for e in ents:
            if df[e] >= DF_CAP:
                continue
            try:
                c.execute("INSERT OR IGNORE INTO seen VALUES (?,?,?,?)", (e, now, "published", slug))
            except sqlite3.Error:
                pass
    # 历史遗留：DF_CAP 上线前播种的高频词还躺在库里，必须清掉，
    # 否则修了播种逻辑也照样误杀（seen 是 INSERT OR IGNORE，不会自愈）。
    # radar 侧（雷达自己播的）没有重播机制，只能按同样的高频规则清一遍
    stale = [e for e, n in df.items() if n >= DF_CAP]
    if stale:
        c.executemany("DELETE FROM seen WHERE entity=? AND origin='radar'", [(e,) for e in stale])
    c.commit()
    return by_slug


def init():
    c = conn()
    c.executescript(SCHEMA)
    seed_from_blog(c)
    cnt = c.execute("SELECT COUNT(*) FROM seen").fetchone()[0]
    print(f"✓ 建库 {DB}")
    print(f"✓ seen 表播种完成：{cnt} 个实体（来自 {len(glob.glob(os.path.join(ROOT,'src','content','blog','*.md')))} 篇已发布文章）")


def sync():
    c = conn()
    by_slug = seed_from_blog(c)

    # 未决定 / 已选写 / 已选再挖 —— 只要不是用户主动定过性的终态（存档/不要），
    # 都要核对一遍是不是其实已经发过了。未决定的也要查：这才是真正防止
    # 「同一个东西又被判一遍要不要写」的地方，不能等用户自己点了「写」才补救。
    moved = []
    rows = c.execute("SELECT id, title, descr, decision, u_note FROM items WHERE decision IN ('', 'write', 'dig')").fetchall()
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    for r in rows:
        # 只用子串匹配（repo_fragment 是不是嵌在某篇已发布文章的 slug 里）。
        # 试过叠加 entities() 词袋重叠当兜底，结果"flash"/"spark"/"nvidia"/
        # "agent-network"里的"network"这类高频词把三条完全不相关的条目
        # 误判成了"已发布"（GLM-DGX-Spark 部署实录被"flash"配对到一篇
        # 完全不相关的 DeepSeek 文章上）。词袋匹配对这个场景就是不可靠，
        # 子串匹配虽然会漏掉一些真实重复，但不会瞎认——宁可漏检，不能错杀。
        slug = published_match(r["title"], by_slug)
        if not slug:
            continue
        note = (r["u_note"] or "").strip()
        tag = f"[已确认发布于 {slug}]"
        note = f"{note} {tag}".strip() if tag not in note else note
        c.execute("UPDATE items SET decision='published', u_note=?, updated_at=? WHERE id=?",
                  (note, now, r["id"]))
        moved.append((r["title"], slug))
    c.commit()
    print(f"✓ seen 重新播种完成（{sum(len(v) for v in by_slug.values())} 个实体，{len(by_slug)} 篇文章）")
    if moved:
        print(f"✓ {len(moved)} 条转为 已发布：")
        for title, slug in moved:
            print(f"    {title}  →  {slug}")
    else:
        print("  没有需要转移的条目")


def stats():
    c = conn()
    try:
        seen = c.execute("SELECT COUNT(*) FROM seen").fetchone()[0]
        tot = c.execute("SELECT COUNT(*) FROM items").fetchone()[0]
    except sqlite3.OperationalError:
        print("库还没建，先跑 init"); return
    print(f"seen 实体: {seen}")
    print(f"条目总数: {tot}")
    for row in c.execute("SELECT decision, COUNT(*) n FROM items GROUP BY decision"):
        print(f"  {row['decision'] or '(未决定)'}: {row['n']}")
    rated = c.execute("SELECT COUNT(*) FROM items WHERE u_total IS NOT NULL").fetchone()[0]
    print(f"你已打分: {rated}")
    if rated:
        r = c.execute("""SELECT AVG(ai_total) a, AVG(u_total) u,
                         AVG(ABS(ai_total-u_total)) d FROM items
                         WHERE u_total IS NOT NULL AND ai_total IS NOT NULL""").fetchone()
        fmt = lambda v: f"{v:.1f}" if v is not None else "—（ai_total 还没打分）"
        print(f"  我的均分 {fmt(r['a'])} / 你的均分 {fmt(r['u'])} / 平均偏差 {fmt(r['d'])}")
        rows = list(c.execute("""SELECT title, ai_total, u_total FROM items
                              WHERE u_total IS NOT NULL AND ai_total IS NOT NULL
                              ORDER BY ABS(ai_total-u_total) DESC LIMIT 5"""))
        if rows:
            print("\n  分歧最大的（这些是校准权重的关键样本）：")
            for x in rows:
                print(f"    我{x['ai_total']:>3} vs 你{x['u_total']:>3}  {x['title'][:48]}")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "stats"
    {"init": init, "sync": sync, "stats": stats}.get(cmd, stats)()
