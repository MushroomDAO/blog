#!/usr/bin/env python3
"""daily-crawler 解析与卡片生成的测试（不联网）。

    python3 .agents/skills/forage/test_daily_crawler.py

夹具照着真实日报的几种格式写：9/10 起的「S1 —」+ 4 列表头，9/1 的「S1.」+ 没有优先级表。
"""
import os, sys, unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import collect  # noqa: E402
import stage    # noqa: E402

# 9/10 那种：表头只有 Priority/Theme/capability/fit 四列，没有 pain/paid；文末有汇总段
BRIEF_4COL = """# SME AI Daily Brief — 2026-09-10

| Priority | Theme | Product capability to capture | Content fit |
|---|---|---|---|
| **S1** | Messaging-native Business Agent | `messaging-business-capability-kit` | Blog ★★★★★ |
| **S2** | Governed Team Memory | `company-memory-contract` | Blog ★★★★☆ |

## S1 — Messaging-native Business Agent: the front office lives in WhatsApp

### Signal

Meta said on **Sept 9** that business agents can reply inside WhatsApp.

Sources:

- Meta newsroom: <https://about.fb.com/news/2026/09/business-agents/>

### Why it is worth tracking

Customers already live in chat apps.

## S2 — Governed Team Memory: Company Brain is becoming infrastructure

### Signal

TencentDB released an agent memory layer.

- Repo: https://github.com/TencentCloud/TencentDB-Agent-Memory

## Today's source list

- https://example.com/should-not-leak-into-S2
"""

# 9/1 那种：标题用「S1.」和「S2：」，没有优先级表，组件名只在正文反引号里
BRIEF_NO_TABLE = """# SME AI 日报 2026-09-01

## 今日优先级

## S1. PaymentOps Agent：最值得直接做成 Vertical Pack 的场景

### 建议开源组件

`payment-ops-core`：事件状态机、审批、审计。

## S2：Headless Business Capabilities

没有任何链接。
"""


class ParseDailyCrawler(unittest.TestCase):
    def test_columns_mapped_by_header_not_position(self):
        rows = collect.parse_daily_crawler(BRIEF_4COL, "2026-09-10")
        c = rows[0]["crawler"]
        # 4 列表头里第 2 列是 capability：按列序硬取会把它当成 pain
        self.assertEqual(c["component"], "messaging-business-capability-kit")
        self.assertEqual(c["fit"], "Blog ★★★★★")
        self.assertEqual(c["pain"], "")
        self.assertEqual(rows[0]["title"], "[2026-09-10 S1] Messaging-native Business Agent")

    def test_last_section_stops_at_next_h2(self):
        rows = collect.parse_daily_crawler(BRIEF_4COL, "2026-09-10")
        s2 = rows[1]["crawler"]
        self.assertNotIn("https://example.com/should-not-leak-into-S2", s2["links"])
        self.assertIn("https://github.com/TencentCloud/TencentDB-Agent-Memory", s2["links"])
        # GitHub 链接进 repos 候选，不算「原始报道」
        self.assertEqual(s2["sources"], [])

    def test_sources_extracted_from_angle_brackets(self):
        s1 = collect.parse_daily_crawler(BRIEF_4COL, "2026-09-10")[0]["crawler"]
        self.assertEqual(s1["sources"], ["https://about.fb.com/news/2026/09/business-agents/"])
        self.assertIn("Sept 9", s1["signal"])
        self.assertNotIn("**", s1["signal"])

    def test_heading_variants_and_backtick_component_fallback(self):
        rows = collect.parse_daily_crawler(BRIEF_NO_TABLE, "2026-09-01")
        self.assertEqual([r["crawler"]["sid"] for r in rows], ["S1", "S2"])
        self.assertEqual(rows[0]["crawler"]["component"], "payment-ops-core")
        self.assertEqual(rows[1]["crawler"]["heading"], "Headless Business Capabilities")

    def test_non_s_heading_is_not_an_item(self):
        rows = collect.parse_daily_crawler(BRIEF_NO_TABLE, "2026-09-01")
        self.assertNotIn("今日优先级", [r["crawler"]["heading"] for r in rows])


class CrawlerCard(unittest.TestCase):
    P = {"本地优先": False, "隐私自主": False, "开源开放": False, "个人可及": True, "一手可查": True}

    def card(self, **kw):
        cr = dict(sid="S1", heading="h", pain="", component="", paid="", fit="", signal="", why="",
                  sources=[], repos=[], repo_search_failed=False)
        cr.update(kw)
        return stage.crawler_research(cr, self.P)

    def test_gap_tells_what_kind_of_article(self):
        repo = [dict(repo="a/b", stars=500, lic="MIT", pushed="", desc="", via="日报直链")]
        self.assertIn("写之前读 README", self.card(repos=repo, sources=["https://x"])["gap"])
        self.assertIn("项目拆解", self.card(repos=repo)["gap"])
        self.assertIn("行业/产品观察", self.card(sources=["https://x"])["gap"])
        self.assertIn("按规则不写", self.card()["gap"])

    def test_no_evidence_is_not_primary_checkable(self):
        self.assertFalse(self.card()["principles"]["一手可查"])
        self.assertTrue(self.card(sources=["https://x"])["principles"]["一手可查"])

    def test_failed_search_is_not_reported_as_nothing_found(self):
        self.assertIn("未经确认", self.card(sources=["https://x"], repo_search_failed=True)["gap"])
        self.assertNotIn("未经确认", self.card(sources=["https://x"])["gap"])

    def test_card_marks_idea_as_unverified(self):
        self.assertTrue(self.card(heading="Agent Egress Policy")["core"].startswith("【日报构想·待核实】"))


if __name__ == "__main__":
    unittest.main()
