#!/usr/bin/env python3
"""
Aura AI Static Site Builder
Converts research/local-AI/reports/*.md → dist/ HTML

Usage:
    python3 build.py          # build only
    ./deploy.sh               # build + deploy to Cloudflare Pages (project: auraai)
"""

import markdown
import re
import shutil
from pathlib import Path
from datetime import datetime

# ─────────────────────────────────────────────────────────────────────────────
# Configuration
# ─────────────────────────────────────────────────────────────────────────────

REPORTS_DIR = Path(__file__).parent.parent / "reports"
DIST_DIR = Path(__file__).parent / "dist"
BUILD_DATE = datetime.now().strftime("%Y-%m-%d")

REPORTS = [
    {
        "id": "r01", "slug": "hardware",
        "title": "硬件方案", "title_en": "Hardware",
        "subtitle": "手机 · PC · 社区端 · 极客端",
        "desc": "从手机到工作站，找到最适合你的本地 AI 硬件配置，含中国市场价格与三年成本表。",
        "icon": "🖥️", "color": "#0ea5e9",
        "file": "R01-hardware-china-market.md",
    },
    {
        "id": "r02", "slug": "models",
        "title": "模型匹配", "title_en": "Models",
        "subtitle": "STT · TTS · OCR · 图像 · 代码 · 对话",
        "desc": "10 个 AI 域的最优开源模型推荐，附 VRAM 要求、Ollama 拉取命令与中国访问渠道。",
        "icon": "🤖", "color": "#8b5cf6",
        "file": "R02-models-by-domain.md",
    },
    {
        "id": "r03", "slug": "software",
        "title": "软件工具", "title_en": "Software",
        "subtitle": "程序员 · 设计师 · 运营 · 普通用户",
        "desc": "按岗位角色和使用场景分类的 AI 软件推荐，开源免费优先，含傻瓜级到极客级分层。",
        "icon": "🛠️", "color": "#10b981",
        "file": "R03-software-by-role.md",
    },
    {
        "id": "r04", "slug": "best-practices",
        "title": "最佳实践", "title_en": "Best Practices",
        "subtitle": "中小组织 · 人+AI 角色构建",
        "desc": "如何在组织中引入 AI？从角色分析、技能路径到 Agent 构建与 AI Native 评估标准。",
        "icon": "📋", "color": "#f59e0b",
        "file": "R04-smb-human-ai-roles.md",
    },
]

# Cost calculator data (from R01, 3-year amortized monthly)
COST_DATA = [
    {"name": "手机（已有设备）", "price": 0, "monthly": 0, "models": "1.5B–3B 模型", "note": "利用现有设备，零增量成本"},
    {"name": "Mac Mini M4 16GB", "price": 4499, "monthly": 155, "models": "7B 全量 / 13B Q4", "note": "个人入门首选，静音低功耗"},
    {"name": "Mac Mini M4 24GB", "price": 7499, "monthly": 238, "models": "13B FP16 / 22B Q4", "note": "标准芯片进阶版，性价比高"},
    {"name": "RTX 3060 二手 12GB + PC", "price": 9600, "monthly": 333, "models": "13B Q4", "note": "Windows 生态，显卡可独立升级"},
    {"name": "Mac Mini M4 Pro 24GB", "price": 10999, "monthly": 346, "models": "70B Q4（24GB 勉强）", "note": "团队入门，Pro 芯片带宽更强"},
    {"name": "Mac Mini M4 Pro 48GB", "price": 13499, "monthly": 415, "models": "70B 全量流畅", "note": "5-15 人团队首选，70B 流畅运行"},
    {"name": "RTX 3090 二手 24GB + PC", "price": 13000, "monthly": 461, "models": "70B Q2 / 34B Q4", "note": "Windows 生态，含电费，可微调"},
    {"name": "Mac Studio M4 Max 128GB", "price": 25000, "monthly": 734, "models": "70B 实时推理", "note": "极客/开发者主力机"},
    {"name": "Mac Studio M3 Ultra 256GB", "price": 50000, "monthly": 1469, "models": "超大模型 / 多模型并行", "note": "不受出口管制的终极方案"},
]

# ─────────────────────────────────────────────────────────────────────────────
# Markdown helpers
# ─────────────────────────────────────────────────────────────────────────────

md = markdown.Markdown(extensions=["tables", "fenced_code", "toc", "nl2br"])

def render_md(text: str) -> str:
    md.reset()
    return md.convert(text)

def extract_highlights(md_text: str, max_items: int = 5) -> list[str]:
    """Extract bullet points from '关键结论' sections."""
    items = []
    in_section = False
    for line in md_text.splitlines():
        if "关键结论" in line or "关键结论：" in line:
            in_section = True
            continue
        if in_section:
            if line.startswith("##"):
                break
            m = re.match(r"^[-*]\s+(.+)", line)
            if m:
                items.append(m.group(1).strip())
                if len(items) >= max_items:
                    break
    return items

def extract_report_date(md_text: str) -> str:
    m = re.search(r"调研日期[：:]\s*(\d{4}-\d{2}-\d{2})", md_text)
    return m.group(1) if m else BUILD_DATE

# ─────────────────────────────────────────────────────────────────────────────
# CSS
# ─────────────────────────────────────────────────────────────────────────────

CSS = """
:root {
  --bg: #f8fafc;
  --surface: #ffffff;
  --border: #e2e8f0;
  --text: #1e293b;
  --muted: #64748b;
  --radius: 12px;
  --shadow: 0 1px 3px rgba(0,0,0,.08), 0 4px 12px rgba(0,0,0,.04);
}
* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: -apple-system, "PingFang SC", "Microsoft YaHei", sans-serif; background: var(--bg); color: var(--text); line-height: 1.7; font-size: 16px; }
a { color: inherit; text-decoration: none; }
a:hover { opacity: .75; }

/* ── Layout ── */
.container { max-width: 1100px; margin: 0 auto; padding: 0 20px; }

/* ── Header ── */
header { background: #0f172a; color: #e2e8f0; padding: 48px 20px 40px; text-align: center; }
header h1 { font-size: 2rem; font-weight: 700; letter-spacing: -.02em; margin-bottom: 8px; }
header h1 span { color: #38bdf8; }
header p.tagline { font-size: 1.05rem; color: #94a3b8; margin-bottom: 20px; }
.header-links { display: flex; gap: 16px; justify-content: center; flex-wrap: wrap; }
.header-links a { color: #7dd3fc; font-size: .9rem; border: 1px solid #334155; border-radius: 20px; padding: 4px 14px; transition: background .2s; }
.header-links a:hover { background: #1e3a5f; opacity: 1; }

/* ── Section title ── */
.section-title { font-size: 1.4rem; font-weight: 700; margin: 48px 0 20px; color: var(--text); display: flex; align-items: center; gap: 10px; }
.section-title::after { content: ""; flex: 1; height: 1px; background: var(--border); }

/* ── Report cards grid ── */
.cards-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 20px; margin-bottom: 12px; }
@media (max-width: 700px) { .cards-grid { grid-template-columns: 1fr; } }

.card { background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius); padding: 24px; box-shadow: var(--shadow); display: flex; flex-direction: column; transition: transform .15s, box-shadow .15s; }
.card:hover { transform: translateY(-2px); box-shadow: 0 4px 16px rgba(0,0,0,.1); }
.card-header { display: flex; align-items: flex-start; gap: 14px; margin-bottom: 12px; }
.card-icon { font-size: 1.8rem; line-height: 1; }
.card-meta h3 { font-size: 1.1rem; font-weight: 700; margin-bottom: 2px; }
.card-meta .subtitle { font-size: .82rem; color: var(--muted); }
.card-badge { margin-left: auto; font-size: .75rem; padding: 2px 10px; border-radius: 20px; font-weight: 600; white-space: nowrap; }
.badge-live { background: #dcfce7; color: #166534; }
.badge-soon { background: #fef9c3; color: #854d0e; }
.card-desc { font-size: .9rem; color: var(--muted); margin-bottom: 14px; flex: 1; }
.card-highlights { list-style: none; margin-bottom: 16px; }
.card-highlights li { font-size: .85rem; color: var(--text); padding: 3px 0 3px 16px; position: relative; }
.card-highlights li::before { content: "▸"; position: absolute; left: 0; color: #94a3b8; }
.card-footer { display: flex; align-items: center; justify-content: space-between; margin-top: auto; }
.card-date { font-size: .78rem; color: var(--muted); }
.btn { display: inline-block; padding: 8px 18px; border-radius: 8px; font-size: .88rem; font-weight: 600; cursor: pointer; transition: opacity .15s; }
.btn-primary { color: #fff; }
.btn-disabled { background: #f1f5f9; color: #94a3b8; cursor: default; }

/* ── Cost Calculator ── */
.calculator { background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius); padding: 32px; box-shadow: var(--shadow); margin-bottom: 48px; }
.calc-title { font-size: 1.15rem; font-weight: 700; margin-bottom: 6px; }
.calc-sub { font-size: .88rem; color: var(--muted); margin-bottom: 24px; }
.calc-slider-row { display: flex; align-items: center; gap: 16px; margin-bottom: 20px; flex-wrap: wrap; }
.calc-slider-row label { font-size: .95rem; font-weight: 600; white-space: nowrap; }
input[type=range] { flex: 1; min-width: 160px; accent-color: #0ea5e9; height: 4px; }
.budget-display { font-size: 1.1rem; font-weight: 700; color: #0ea5e9; min-width: 80px; text-align: right; }
.calc-result { background: #f0f9ff; border: 1px solid #bae6fd; border-radius: 10px; padding: 20px 24px; }
.result-name { font-size: 1.05rem; font-weight: 700; margin-bottom: 4px; color: #0f172a; }
.result-row { display: flex; gap: 32px; flex-wrap: wrap; margin-top: 10px; }
.result-item { display: flex; flex-direction: column; }
.result-label { font-size: .75rem; color: var(--muted); text-transform: uppercase; letter-spacing: .05em; }
.result-val { font-size: 1.1rem; font-weight: 700; color: #0f172a; }
.result-note { font-size: .85rem; color: var(--muted); margin-top: 8px; }

/* ── Report page ── */
.report-header { background: #0f172a; color: #e2e8f0; padding: 40px 20px 32px; }
.report-header .back { display: inline-flex; align-items: center; gap: 6px; color: #7dd3fc; font-size: .9rem; margin-bottom: 16px; }
.report-header h1 { font-size: 1.8rem; font-weight: 700; margin-bottom: 6px; }
.report-header .meta { font-size: .85rem; color: #94a3b8; }
.report-body { padding: 40px 0 80px; }
.report-body h1 { display: none; }
.report-body h2 { font-size: 1.3rem; font-weight: 700; margin: 36px 0 14px; padding-bottom: 8px; border-bottom: 2px solid var(--border); }
.report-body h3 { font-size: 1.05rem; font-weight: 700; margin: 24px 0 10px; }
.report-body p { margin-bottom: 14px; }
.report-body ul, .report-body ol { padding-left: 24px; margin-bottom: 14px; }
.report-body li { margin-bottom: 4px; }
.report-body table { width: 100%; border-collapse: collapse; margin: 16px 0 24px; font-size: .9rem; overflow-x: auto; display: block; }
.report-body th { background: #f1f5f9; text-align: left; padding: 8px 12px; font-weight: 600; border: 1px solid var(--border); }
.report-body td { padding: 8px 12px; border: 1px solid var(--border); }
.report-body tr:hover td { background: #f8fafc; }
.report-body code { background: #f1f5f9; padding: 1px 6px; border-radius: 4px; font-size: .88em; font-family: "SF Mono", Menlo, monospace; }
.report-body pre { background: #1e293b; color: #e2e8f0; padding: 20px; border-radius: 10px; overflow-x: auto; margin: 16px 0; }
.report-body pre code { background: none; padding: 0; font-size: .88em; }
.report-body blockquote { border-left: 4px solid #0ea5e9; padding-left: 16px; color: var(--muted); font-style: italic; margin: 16px 0; }
.report-body strong { font-weight: 700; }

/* ── Footer ── */
footer { background: #0f172a; color: #475569; text-align: center; padding: 24px 20px; font-size: .85rem; }
footer a { color: #7dd3fc; }
"""

# ─────────────────────────────────────────────────────────────────────────────
# Cost calculator JS
# ─────────────────────────────────────────────────────────────────────────────

CALC_JS = """
const DEVICES = """ + str(COST_DATA).replace("True","true").replace("False","false").replace("'",'"') + """;

function findBest(budget) {
  let best = DEVICES[0];
  for (const d of DEVICES) {
    if (d.price <= budget) best = d;
  }
  return best;
}

function updateCalc() {
  const budget = parseInt(document.getElementById('budget').value);
  document.getElementById('budget-display').textContent = '¥' + budget.toLocaleString();
  const d = findBest(budget);
  document.getElementById('res-name').textContent = d.name;
  document.getElementById('res-price').textContent = d.price === 0 ? '免费' : '¥' + d.price.toLocaleString();
  document.getElementById('res-monthly').textContent = d.monthly === 0 ? '¥0/月' : '¥' + d.monthly + '/月';
  document.getElementById('res-models').textContent = d.models;
  document.getElementById('res-note').textContent = d.note;
}

document.getElementById('budget').addEventListener('input', updateCalc);
updateCalc();
"""

# ─────────────────────────────────────────────────────────────────────────────
# HTML templates
# ─────────────────────────────────────────────────────────────────────────────

def base_html(title: str, body: str, extra_js: str = "") -> str:
    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title>
<meta name="description" content="Aura AI · 让每个人平等拥有 AI · 本地 AI 周报">
<style>{CSS}</style>
</head>
<body>
{body}
<footer>
  <div class="container">
    <p>Aura AI · <a href="https://blog.mushroom.cv" target="_blank">Mycelium Protocol</a> · 开源 · 本地优先 · AI平权</p>
    <p style="margin-top:6px">构建于 {BUILD_DATE} · <a href="https://blog.mushroom.cv/blog/aura-ai-manifesto-153316/" target="_blank">阅读宣言 →</a></p>
  </div>
</footer>
{f'<script>{extra_js}</script>' if extra_js else ''}
</body>
</html>"""


def index_html(reports_data: list[dict]) -> str:
    cards_html = ""
    for r in reports_data:
        report = r["meta"]
        highlights = r.get("highlights", [])
        report_date = r.get("date", "即将发布")
        has_content = r.get("has_content", False)
        badge = '<span class="card-badge badge-live">✅ 已发布</span>' if has_content else '<span class="card-badge badge-soon">🔄 即将发布</span>'
        btn = f'<a class="btn btn-primary" style="background:{report["color"]}" href="{report["slug"]}/">查看报告 →</a>' if has_content else '<span class="btn btn-disabled">即将发布</span>'
        date_str = f'更新：{report_date}' if has_content else "研究进行中"
        hi_items = "".join(f"<li>{h}</li>" for h in highlights[:4]) if highlights else ""
        hi_html = f'<ul class="card-highlights">{hi_items}</ul>' if hi_items else ""

        cards_html += f"""
<div class="card">
  <div class="card-header">
    <div class="card-icon">{report["icon"]}</div>
    <div class="card-meta">
      <h3>{report["title"]}</h3>
      <div class="subtitle">{report["subtitle"]}</div>
    </div>
    {badge}
  </div>
  <p class="card-desc">{report["desc"]}</p>
  {hi_html}
  <div class="card-footer">
    <span class="card-date">{date_str}</span>
    {btn}
  </div>
</div>"""

    calc_html = f"""
<div class="calculator">
  <div class="calc-title">💰 三年成本计算器</div>
  <div class="calc-sub">输入你的预算，找到最适合你的本地 AI 硬件方案（三年分摊月均成本）</div>
  <div class="calc-slider-row">
    <label>预算上限</label>
    <input type="range" id="budget" min="0" max="55000" step="1000" value="8000">
    <span class="budget-display" id="budget-display">¥8,000</span>
  </div>
  <div class="calc-result">
    <div class="result-name" id="res-name">—</div>
    <div class="result-row">
      <div class="result-item"><span class="result-label">设备价格</span><span class="result-val" id="res-price">—</span></div>
      <div class="result-item"><span class="result-label">三年月均成本</span><span class="result-val" id="res-monthly">—</span></div>
      <div class="result-item"><span class="result-label">可运行模型</span><span class="result-val" id="res-models">—</span></div>
    </div>
    <div class="result-note" id="res-note"></div>
  </div>
</div>"""

    body = f"""
<header>
  <div class="container">
    <h1>Aura AI · <span>Local AI 周报</span></h1>
    <p class="tagline">让每个人平等、低成本、安全地使用 AI · 每周更新最优本地部署方案</p>
    <div class="header-links">
      <a href="https://blog.mushroom.cv/blog/aura-ai-manifesto-153316/" target="_blank">📖 Aura AI 宣言</a>
      <a href="https://blog.mushroom.cv" target="_blank">🌐 Mycelium Protocol</a>
      <a href="hardware/">💻 硬件方案</a>
      <a href="models/">🤖 模型推荐</a>
    </div>
  </div>
</header>
<main class="container">
  <div class="section-title">四大研究栏目</div>
  <div class="cards-grid">{cards_html}</div>
  <div class="section-title">成本计算器</div>
  {calc_html}
</main>"""

    return base_html("Aura AI · Local AI 周报", body, CALC_JS)


def report_html(report_meta: dict, content_html: str, report_date: str) -> str:
    body = f"""
<div class="report-header">
  <div class="container">
    <a class="back" href="../">← 返回首页</a>
    <h1>{report_meta["icon"]} {report_meta["title"]}</h1>
    <div class="meta">{report_meta["subtitle"]} · 更新：{report_date}</div>
  </div>
</div>
<main class="container">
  <div class="report-body">{content_html}</div>
</main>"""
    return base_html(f"{report_meta['title']} · Aura AI", body)

# ─────────────────────────────────────────────────────────────────────────────
# Build
# ─────────────────────────────────────────────────────────────────────────────

def build():
    # Clean and recreate dist
    if DIST_DIR.exists():
        shutil.rmtree(DIST_DIR)
    DIST_DIR.mkdir(parents=True)

    reports_data = []
    for meta in REPORTS:
        report_path = REPORTS_DIR / meta["file"]
        if not report_path.exists():
            reports_data.append({"meta": meta, "has_content": False})
            continue

        text = report_path.read_text(encoding="utf-8")
        highlights = extract_highlights(text)
        report_date = extract_report_date(text)
        html_content = render_md(text)

        # Write report page
        out_dir = DIST_DIR / meta["slug"]
        out_dir.mkdir()
        (out_dir / "index.html").write_text(
            report_html(meta, html_content, report_date),
            encoding="utf-8"
        )
        reports_data.append({
            "meta": meta,
            "has_content": True,
            "highlights": highlights,
            "date": report_date,
        })
        print(f"  ✅ {meta['slug']}/index.html ({len(text):,} chars)")

    # Write index
    (DIST_DIR / "index.html").write_text(index_html(reports_data), encoding="utf-8")
    print(f"  ✅ index.html")

    print(f"\n🎉 Built to dist/ — {sum(1 for _ in DIST_DIR.rglob('*.html'))} pages")

if __name__ == "__main__":
    print(f"🔨 Building Aura AI site ({BUILD_DATE})...")
    build()
