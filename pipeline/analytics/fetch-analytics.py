#!/usr/bin/env python3
"""
拉取 blog.mushroom.cv 的 Cloudflare Web Analytics（RUM）数据，写成
src/data/blog-analytics.json 供 /analytics 页面在构建时读取。

数据源：Cloudflare GraphQL Analytics API 的 rumPageloadEventsAdaptiveGroups
数据集（账号已对 mushroom.cv 开启 auto-install Web Analytics beacon，
无需改站点代码）。需要 CLOUDFLARE_API_TOKEN（.env）具备该账号的
Web Analytics 读取权限（现有 token 已具备，未额外申请 zone.analytics 权限）。

用法：python3 pipeline/analytics/fetch-analytics.py
被 scripts/update-analytics.sh 调用，定时任务见该脚本注释。
"""
import json
import os
import sys
import urllib.request
from datetime import datetime, timedelta, timezone

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
ENV_FILE = os.path.join(REPO_ROOT, ".env")
OUT_FILE = os.path.join(REPO_ROOT, "src", "data", "blog-analytics.json")

ACCOUNT_TAG = "7bf23342f21baa5ebfc7bc7b74f5a1f2"
SITE_TAG = "d7e4a410d16548ea8e729ced7499afe8"  # mushroom.cv Web Analytics site
DAYS = 30

# ISO 3166-1 alpha-2 -> 中文名（覆盖历史上出现过的国家/地区，未知的直接显示代码）
COUNTRY_NAMES = {
    "SG": "新加坡", "CN": "中国", "TH": "泰国", "US": "美国", "HK": "香港",
    "DE": "德国", "JP": "日本", "TW": "台湾", "MY": "马来西亚", "KR": "韩国",
    "AR": "阿根廷", "CA": "加拿大", "AU": "澳大利亚", "AE": "阿联酋",
    "NL": "荷兰", "VE": "委内瑞拉", "IE": "爱尔兰", "GB": "英国",
    "NZ": "新西兰", "SA": "沙特阿拉伯", "IN": "印度", "FR": "法国",
    "ID": "印度尼西亚", "VN": "越南", "PH": "菲律宾", "BR": "巴西",
    "RU": "俄罗斯", "ES": "西班牙", "IT": "意大利", "CH": "瑞士",
}

# referrer host -> 分类桶
DIRECT = {""}
SEARCH_HOSTS = {"www.google.com", "www.google.com.hk", "www.google.com.tw", "cn.bing.com", "www.bing.com", "www.baidu.com", "duckduckgo.com"}
AI_HOSTS = {"chatgpt.com", "www.perplexity.ai", "ima.qq.com", "claude.ai", "www.bing.com/chat"}
ECOSYSTEM_SUFFIXES = ("mushroom.cv", "mushroom.box", "aastar.io", "aastar.xyz")


def flag_emoji(code):
    if not code or len(code) != 2:
        return "🏳️"
    return "".join(chr(0x1F1E6 + ord(c) - ord("A")) for c in code.upper())


def load_token():
    token = os.environ.get("CLOUDFLARE_API_TOKEN")
    if token:
        return token
    if os.path.exists(ENV_FILE):
        for line in open(ENV_FILE, encoding="utf-8"):
            line = line.strip()
            if line.startswith("CLOUDFLARE_API_TOKEN="):
                return line.split("=", 1)[1].strip().strip('"')
    print("ERROR: CLOUDFLARE_API_TOKEN not found in env or .env", file=sys.stderr)
    sys.exit(1)


def gql(token, query):
    req = urllib.request.Request(
        "https://api.cloudflare.com/client/v4/graphql",
        data=json.dumps({"query": query}).encode(),
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        body = json.loads(resp.read())
    if body.get("errors"):
        print("GraphQL errors:", body["errors"], file=sys.stderr)
        sys.exit(1)
    return body["data"]["viewer"]["accounts"][0]


def main():
    token = load_token()
    end = datetime.now(timezone.utc)
    start = end - timedelta(days=DAYS)
    s, e = start.strftime("%Y-%m-%dT%H:%M:%SZ"), end.strftime("%Y-%m-%dT%H:%M:%SZ")
    filt = f'siteTag: "{SITE_TAG}", datetime_geq: "{s}", datetime_leq: "{e}"'

    query = f"""
    query {{
      viewer {{
        accounts(filter: {{accountTag: "{ACCOUNT_TAG}"}}) {{
          daily: rumPageloadEventsAdaptiveGroups(limit: 100, filter: {{{filt}}}, orderBy: [date_ASC]) {{
            count sum {{ visits }} dimensions {{ date }}
          }}
          byCountry: rumPageloadEventsAdaptiveGroups(limit: 25, filter: {{{filt}}}, orderBy: [count_DESC]) {{
            count sum {{ visits }} dimensions {{ countryName }}
          }}
          byPage: rumPageloadEventsAdaptiveGroups(limit: 20, filter: {{{filt}}}, orderBy: [count_DESC]) {{
            count sum {{ visits }} dimensions {{ requestPath }}
          }}
          byReferer: rumPageloadEventsAdaptiveGroups(limit: 25, filter: {{{filt}}}, orderBy: [count_DESC]) {{
            count dimensions {{ refererHost }}
          }}
          byDevice: rumPageloadEventsAdaptiveGroups(limit: 10, filter: {{{filt}}}, orderBy: [count_DESC]) {{
            count dimensions {{ deviceType }}
          }}
          byBrowser: rumPageloadEventsAdaptiveGroups(limit: 10, filter: {{{filt}}}, orderBy: [count_DESC]) {{
            count dimensions {{ userAgentBrowser }}
          }}
          byOS: rumPageloadEventsAdaptiveGroups(limit: 10, filter: {{{filt}}}, orderBy: [count_DESC]) {{
            count dimensions {{ userAgentOS }}
          }}
          byBot: rumPageloadEventsAdaptiveGroups(limit: 5, filter: {{{filt}}}, orderBy: [count_DESC]) {{
            count dimensions {{ bot }}
          }}
        }}
      }}
    }}
    """
    d = gql(token, query)

    daily = sorted(d["daily"], key=lambda x: x["dimensions"]["date"])
    daily_out = [
        {"date": x["dimensions"]["date"][5:], "pv": x["count"], "visits": x["sum"]["visits"]}
        for x in daily
    ]
    total_pv = sum(x["pv"] for x in daily_out)
    total_visits = sum(x["visits"] for x in daily_out)
    bots = next((x["count"] for x in d["byBot"] if x["dimensions"]["bot"] == 1), 0)

    def window(days_ago_start, days_ago_end):
        sl = daily_out[-days_ago_start:-days_ago_end] if days_ago_end else daily_out[-days_ago_start:]
        return {"pv": sum(x["pv"] for x in sl), "visits": sum(x["visits"] for x in sl)}

    last7 = window(7, 0)
    prior7 = window(14, 7)

    countries = []
    for x in sorted(d["byCountry"], key=lambda r: -r["count"])[:12]:
        code = x["dimensions"]["countryName"] or "??"
        countries.append({
            "code": code,
            "flag": flag_emoji(code),
            "name": COUNTRY_NAMES.get(code, code),
            "pv": x["count"],
            "visits": x["sum"]["visits"],
        })
    country_total = sum(x["count"] for x in d["byCountry"])

    ref_buckets = {"direct": 0, "search": 0, "ecosystem": 0, "ai": 0, "other": 0}
    for x in d["byReferer"]:
        host = x["dimensions"]["refererHost"] or ""
        c = x["count"]
        if host in DIRECT:
            ref_buckets["direct"] += c
        elif host in SEARCH_HOSTS or any(s in host for s in ("google.", "bing.", "baidu.", "duckduckgo.")):
            ref_buckets["search"] += c
        elif host in AI_HOSTS or any(a in host for a in ("chatgpt.com", "perplexity.ai", "claude.ai")):
            ref_buckets["ai"] += c
        elif any(host.endswith(suf) for suf in ECOSYSTEM_SUFFIXES):
            ref_buckets["ecosystem"] += c
        else:
            ref_buckets["other"] += c

    def top_dim(key, dim_name):
        return [{"label": x["dimensions"][dim_name], "count": x["count"]} for x in sorted(d[key], key=lambda r: -r["count"])]

    pages = []
    for x in sorted(d["byPage"], key=lambda r: -r["count"])[:15]:
        path = x["dimensions"]["requestPath"]
        slug = path.strip("/")
        if slug.startswith("blog/"):
            slug = slug[len("blog/"):]
        title = "首页"
        if slug:
            md_path = os.path.join(REPO_ROOT, "src", "content", "blog", f"{slug}.md")
            title = slug
            if os.path.exists(md_path):
                for line in open(md_path, encoding="utf-8"):
                    if line.startswith("title:"):
                        title = line.split(":", 1)[1].strip().strip('"')
                        break
        pages.append({"title": title, "path": path, "pv": x["count"], "visits": x["sum"]["visits"]})

    out = {
        "generatedAt": end.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "period": {"start": start.strftime("%Y-%m-%d"), "end": end.strftime("%Y-%m-%d")},
        "totals": {"pageviews": total_pv, "visits": total_visits, "bots": bots},
        "last7": last7,
        "prior7": prior7,
        "daily": daily_out,
        "countries": countries,
        "countryTotal": country_total,
        "referers": ref_buckets,
        "pages": pages,
        "devices": top_dim("byDevice", "deviceType"),
        "os": top_dim("byOS", "userAgentOS"),
        "browsers": top_dim("byBrowser", "userAgentBrowser"),
    }

    os.makedirs(os.path.dirname(OUT_FILE), exist_ok=True)
    with open(OUT_FILE, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print(f"✓ wrote {OUT_FILE} ({total_pv} pageviews, {total_visits} visits, {len(pages)} pages)")


if __name__ == "__main__":
    main()
