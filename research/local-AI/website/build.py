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

/* ── Evolution diagrams ── */
.evo-section { margin-bottom: 48px; }
.evo-sub { font-size: .85rem; color: var(--muted); margin-bottom: 20px; margin-top: -12px; }

/* Individual path */
.evo-flow { display: flex; align-items: stretch; gap: 0; overflow-x: auto; padding-bottom: 4px; }
.evo-step { flex: 1; min-width: 140px; background: var(--surface); border: 1px solid var(--border); border-radius: 10px; padding: 16px 14px; position: relative; }
.evo-step .step-num { font-size: .72rem; font-weight: 700; text-transform: uppercase; letter-spacing: .08em; color: var(--muted); margin-bottom: 6px; }
.evo-step .step-title { font-size: 1rem; font-weight: 700; margin-bottom: 4px; }
.evo-step .step-time { font-size: .75rem; color: var(--muted); margin-bottom: 10px; }
.evo-step ul { list-style: none; padding: 0; }
.evo-step ul li { font-size: .8rem; color: #475569; padding: 1px 0 1px 14px; position: relative; }
.evo-step ul li::before { content: "·"; position: absolute; left: 4px; color: #94a3b8; }
.evo-arrow { display: flex; align-items: center; padding: 0 6px; color: #94a3b8; font-size: 1.4rem; flex-shrink: 0; align-self: center; }
.evo-step.native { background: #0f172a; border-color: #38bdf8; color: #e2e8f0; }
.evo-step.native .step-num { color: #38bdf8; }
.evo-step.native .step-time { color: #94a3b8; }
.evo-step.native ul li { color: #cbd5e1; }
@media (max-width: 700px) { .evo-flow { flex-direction: column; } .evo-arrow { transform: rotate(90deg); align-self: flex-start; margin-left: 20px; } }

/* Human vs AI two-column */
.human-ai-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-bottom: 16px; }
@media (max-width: 600px) { .human-ai-grid { grid-template-columns: 1fr; } }
.ha-box { background: var(--surface); border: 1px solid var(--border); border-radius: 10px; padding: 20px; }
.ha-box.human { border-top: 3px solid #10b981; }
.ha-box.ai { border-top: 3px solid #8b5cf6; }
.ha-box h4 { font-size: .95rem; font-weight: 700; margin-bottom: 12px; display: flex; align-items: center; gap: 8px; }
.ha-trait { margin-bottom: 10px; }
.ha-trait .trait-name { font-size: .88rem; font-weight: 700; color: var(--text); }
.ha-trait .trait-desc { font-size: .8rem; color: var(--muted); padding-left: 12px; margin-top: 1px; }

/* Collaboration unit formula */
.collab-formula { background: #0f172a; color: #e2e8f0; border-radius: 12px; padding: 24px 28px; font-family: "SF Mono", Menlo, monospace; margin-bottom: 16px; }
.collab-formula .formula-title { font-size: .78rem; color: #38bdf8; text-transform: uppercase; letter-spacing: .1em; margin-bottom: 16px; font-family: inherit; }
.collab-row { display: flex; align-items: center; gap: 12px; flex-wrap: wrap; margin-bottom: 8px; }
.collab-box { background: #1e293b; border: 1px solid #334155; border-radius: 8px; padding: 8px 14px; font-size: .85rem; }
.collab-box.human-box { border-color: #10b981; color: #6ee7b7; }
.collab-box.ai-box { border-color: #8b5cf6; color: #c4b5fd; }
.collab-box.result-box { border-color: #38bdf8; color: #7dd3fc; font-weight: 700; }
.collab-op { color: #f59e0b; font-size: 1.1rem; font-weight: 700; }
.collab-eq { color: #94a3b8; font-size: .85rem; margin: 4px 0 0 0; }
.collab-note { font-size: .78rem; color: #64748b; margin-top: 10px; font-family: -apple-system, "PingFang SC", sans-serif; }

/* Org transformation */
.org-flow { display: grid; grid-template-columns: 1fr auto 1fr auto 1fr; gap: 0; align-items: center; margin-bottom: 16px; }
@media (max-width: 650px) { .org-flow { grid-template-columns: 1fr; gap: 8px; } .org-arrow-v { display: none; } }
.org-stage { background: var(--surface); border: 1px solid var(--border); border-radius: 10px; padding: 18px 16px; }
.org-stage .stage-label { font-size: .72rem; font-weight: 700; text-transform: uppercase; letter-spacing: .08em; margin-bottom: 6px; }
.org-stage h4 { font-size: .95rem; font-weight: 700; margin-bottom: 4px; }
.org-stage .stage-time { font-size: .75rem; color: var(--muted); margin-bottom: 8px; }
.org-stage ul { list-style: none; padding: 0; }
.org-stage ul li { font-size: .8rem; color: #475569; padding: 1px 0 1px 12px; position: relative; }
.org-stage ul li::before { content: "·"; position: absolute; left: 2px; }
.org-stage.s1 .stage-label { color: #0ea5e9; }
.org-stage.s2 .stage-label { color: #8b5cf6; }
.org-stage.s3 { background: #0f172a; border-color: #f59e0b; color: #e2e8f0; }
.org-stage.s3 .stage-label { color: #fbbf24; }
.org-stage.s3 ul li { color: #cbd5e1; }
.org-arrow-v { text-align: center; color: #94a3b8; font-size: 1.4rem; padding: 0 8px; }
.org-insight { background: #fef9c3; border: 1px solid #fde68a; border-radius: 8px; padding: 12px 16px; font-size: .88rem; color: #78350f; }
.org-insight strong { color: #92400e; }

/* ── Footer ── */
footer { background: #0f172a; color: #475569; text-align: center; padding: 24px 20px; font-size: .85rem; }
footer a { color: #7dd3fc; }
"""

# ─────────────────────────────────────────────────────────────────────────────
# Evolution diagrams HTML
# ─────────────────────────────────────────────────────────────────────────────

EVOLUTION_HTML = """
<div class="evo-section">

  <!-- Diagram 1: Individual 4-step path -->
  <div class="section-title">个体演进路径</div>
  <p class="evo-sub">从下载第一个 AI 工具，到工作流完全以 AI 为核心——四个阶段，清晰可操作</p>
  <div class="evo-flow">

    <div class="evo-step">
      <div class="step-num">Step 1</div>
      <div class="step-title">📱 使用应用</div>
      <div class="step-time">0–1 个月</div>
      <ul>
        <li>下载 LM Studio / Jan</li>
        <li>拉取第一个模型</li>
        <li>完成第一个 AI 辅助任务</li>
        <li>感受本地 AI 的边界</li>
      </ul>
    </div>
    <div class="evo-arrow">→</div>

    <div class="evo-step">
      <div class="step-num">Step 2</div>
      <div class="step-title">🔧 技能化</div>
      <div class="step-time">1–3 个月</div>
      <ul>
        <li>精准描述任务（提示词）</li>
        <li>批判性评估 AI 输出</li>
        <li>2–3 工具融入日常流程</li>
        <li>识别哪些任务 AI 不适合</li>
      </ul>
    </div>
    <div class="evo-arrow">→</div>

    <div class="evo-step">
      <div class="step-num">Step 3</div>
      <div class="step-title">🤖 构建 Agent</div>
      <div class="step-time">3–6 个月</div>
      <ul>
        <li>为核心工作流定制 Agent</li>
        <li>搭建私有 RAG 知识库</li>
        <li>提示词工程 / Fine-tune</li>
        <li>Agent 稳定输出可评估</li>
      </ul>
    </div>
    <div class="evo-arrow">→</div>

    <div class="evo-step native">
      <div class="step-num">Step 4</div>
      <div class="step-title">⭐ AI Native</div>
      <div class="step-time">6–18 个月</div>
      <ul>
        <li>工作流以 AI 为中心重设计</li>
        <li>人负责判断、AI 负责执行</li>
        <li>持续更新自己的 Agent</li>
        <li>社会力 × AI 执行力 = 10×</li>
      </ul>
    </div>

  </div><!-- /evo-flow -->

  <!-- Diagram 2: Human irreplaceable vs AI capabilities -->
  <div class="section-title" style="margin-top:40px">人类护城河 vs AI 能力边界</div>
  <p class="evo-sub">理解边界，才能找到正确的协作姿势</p>
  <div class="human-ai-grid">

    <div class="ha-box human">
      <h4>🧠 人类不可替代的三件事</h4>
      <div class="ha-trait">
        <div class="trait-name">① 社会上下文</div>
        <div class="trait-desc">你是谁的朋友、哪所学校的校友、哪个行业的老兵——人类社会数千年积累的社会上下文，个体镶嵌在社会网络中的信用、声誉与社会资本。AI 没有社会网络，无法嵌入真实关系。</div>
      </div>
      <div class="ha-trait">
        <div class="trait-name">② 情感判断</div>
        <div class="trait-desc">好不好、对不对——这些判断没有标准答案。凡需要价值取舍、人际感受、道德边界的地方，人类判断无可替代。</div>
      </div>
      <div class="ha-trait">
        <div class="trait-name">③ 需求提出</div>
        <div class="trait-desc">人类创造了 AI，目的是服务人类。需求的源头永远在人这一侧。能把诉求结构化为 AI 能理解语言的人，价值最高。</div>
      </div>
    </div>

    <div class="ha-box ai">
      <h4>⚡ AI 擅长的四件事</h4>
      <div class="ha-trait">
        <div class="trait-name">① 无限执行力</div>
        <div class="trait-desc">7×24 不疲倦，同时处理多任务，执行标准化工作零差错。</div>
      </div>
      <div class="ha-trait">
        <div class="trait-name">② 知识检索</div>
        <div class="trait-desc">海量信息瞬时调取，跨领域综合，实时跟踪最新数据。</div>
      </div>
      <div class="ha-trait">
        <div class="trait-name">③ 模式识别</div>
        <div class="trait-desc">在数据中发现隐藏规律，超出人类感知速度和范围。</div>
      </div>
      <div class="ha-trait">
        <div class="trait-name">④ 持续迭代</div>
        <div class="trait-desc">每次交互都更新对你的理解，越用越懂你，不断进化。</div>
      </div>
    </div>

  </div><!-- /human-ai-grid -->

  <!-- Diagram 3: Human + AI collaboration formula -->
  <div class="collab-formula">
    <div class="formula-title">// 人 + AI 协作单元公式</div>
    <div class="collab-row">
      <div class="collab-box human-box">社会上下文 + 情感判断 + 需求提出</div>
      <span class="collab-op">×</span>
      <div class="collab-box ai-box">执行力 + 检索 + 模式识别 + 迭代</div>
      <span class="collab-op">=</span>
      <div class="collab-box result-box">人 + AI 协作单元</div>
    </div>
    <div class="collab-eq">// 相乘，不是相加——1人 × AI 倍增器，效能 3–10×</div>
    <div class="collab-note">注：AI 替代的是"生产力"（执行、信息处理、组合创新）；人类转向"社会力"（关系、判断、需求）。这是本质性的分工，不是程度之差。</div>
  </div>

  <!-- Diagram 4: Organization transformation -->
  <div class="section-title" style="margin-top:40px">组织转型三阶段</div>
  <p class="evo-sub">只有能与 AI 协作的个体，才能进入 AI Native 状态的组织</p>
  <div class="org-flow">

    <div class="org-stage s1">
      <div class="stage-label">Phase 1 · Skill</div>
      <h4>全员技能化</h4>
      <div class="stage-time">1–3 个月</div>
      <ul>
        <li>每人掌握 2–3 个 AI 工具</li>
        <li>AI 辅助完成本岗位任务</li>
        <li>建立工具使用规范</li>
        <li>识别高价值 AI 应用场景</li>
      </ul>
    </div>
    <div class="org-arrow-v">→</div>

    <div class="org-stage s2">
      <div class="stage-label">Phase 2 · Agent</div>
      <h4>核心流程 Agent 化</h4>
      <div class="stage-time">3–6 个月</div>
      <ul>
        <li>关键工作流有专属 Agent</li>
        <li>RAG 知识库对接内部文档</li>
        <li>Agent 产出质量可量化</li>
        <li>建立 AI 使用的评估标准</li>
      </ul>
    </div>
    <div class="org-arrow-v">→</div>

    <div class="org-stage s3">
      <div class="stage-label">Phase 3 · Native</div>
      <h4>⭐ 组织 AI Native</h4>
      <div class="stage-time">6–18 个月</div>
      <ul>
        <li>工作流以 AI 为中心重设计</li>
        <li>AI 介入决策与协作层</li>
        <li>人专注判断、关系、创新</li>
        <li>持续自我进化的组织体</li>
      </ul>
    </div>

  </div><!-- /org-flow -->

  <div class="org-insight">
    <strong>核心洞察：</strong>AI 不是来替代你的，但会替代那些不使用 AI 的人。对组织而言，问题不是"要不要引入 AI"——而是"哪些角色怎么引入、边界在哪里"，以及"如何用 AI 乘以人的社会力，而不是用 AI 替换人"。
  </div>

</div><!-- /evo-section -->
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
  {EVOLUTION_HTML}
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
