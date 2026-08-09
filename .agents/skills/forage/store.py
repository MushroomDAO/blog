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
    python3 store.py stats         看当前状态
"""
import sqlite3, os, re, glob, sys, hashlib, json
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


def entities(text):
    """抽出能当去重键的专有名词：仓库名、模型名、产品名。

    只认「有辨识度」的 token —— 驼峰、含数字版本号、含连字符的复合词。
    通用词（agent/mcp/开源）不是实体，否则所有条目都会互相判重。
    """
    out = set()
    for w in re.findall(r"[A-Za-z][A-Za-z0-9]*(?:[-._][A-Za-z0-9]+)+|[A-Z][a-z]+[A-Z][A-Za-z]*", text or ""):
        wl = w.lower().strip("-._")
        if len(wl) > 3 and wl not in STOP:
            out.add(wl)
    for w in re.findall(r"\b[A-Za-z][A-Za-z0-9]{3,}\b", text or ""):
        wl = w.lower()
        if wl not in STOP and (any(c.isdigit() for c in wl) or w[0].isupper()):
            out.add(wl)
    return out


def conn():
    os.makedirs(os.path.dirname(DB), exist_ok=True)
    c = sqlite3.connect(DB)
    c.row_factory = sqlite3.Row
    return c


def init():
    c = conn()
    c.executescript(SCHEMA)
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    n = 0
    # 用已发布文章播种：这些主题永远不该再被当成新线索
    for f in glob.glob(os.path.join(ROOT, "src", "content", "blog", "*.md")):
        slug = os.path.basename(f)[:-3]
        title = ""
        for line in open(f, encoding="utf-8"):
            if line.startswith("title:"):
                title = line.split(":", 1)[1].strip().strip('"').strip("'"); break
        for e in entities(slug.replace("-", " ")) | entities(title):
            try:
                c.execute("INSERT OR IGNORE INTO seen VALUES (?,?,?,?)", (e, now, "published", slug))
                n += c.total_changes and 1 or 0
            except sqlite3.Error:
                pass
    c.commit()
    cnt = c.execute("SELECT COUNT(*) FROM seen").fetchone()[0]
    print(f"✓ 建库 {DB}")
    print(f"✓ seen 表播种完成：{cnt} 个实体（来自 {len(glob.glob(os.path.join(ROOT,'src','content','blog','*.md')))} 篇已发布文章）")


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
                         AVG(ABS(ai_total-u_total)) d FROM items WHERE u_total IS NOT NULL""").fetchone()
        print(f"  我的均分 {r['a']:.1f} / 你的均分 {r['u']:.1f} / 平均偏差 {r['d']:.1f}")
        print("\n  分歧最大的（这些是校准权重的关键样本）：")
        for x in c.execute("""SELECT title, ai_total, u_total FROM items
                              WHERE u_total IS NOT NULL
                              ORDER BY ABS(ai_total-u_total) DESC LIMIT 5"""):
            print(f"    我{x['ai_total']:>3} vs 你{x['u_total']:>3}  {x['title'][:48]}")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "stats"
    {"init": init, "stats": stats}.get(cmd, stats)()
