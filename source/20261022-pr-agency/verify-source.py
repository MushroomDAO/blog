"""Read public primary pages and verify specific source statements; no outcome test."""
from pathlib import Path
import json,urllib.request,hashlib
b=Path(__file__).resolve().parent
checks={
 'agency':('https://www.getflack.com/p/should-you-hire-a-pr-agency',['2025-03-14','20-35K','60K-100K','story and strategy','share of voice']),
 'manifesto':('https://www.getflack.com/p/go-direct-the-manifesto',['2024-03-19','doesn’t mean going it alone']),
 'cult':('https://fs.blog/knowledge-project-podcast/lulu-cheng-meservey/',['How To Build A Cult','Members Only','Substack']),
 'measurement':('https://amecorg.com/amecframework/',['outcomes','outputs','benchmarks']),
}
report=[]
for k,(url,needles) in checks.items():
 data=urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0'}),timeout=30).read();s=data.decode();assert all(x in s for x in needles),(k,needles)
 report.append({'url':url,'sha256':hashlib.sha256(data).hexdigest(),'checked':needles})
assert 18000+6000+3000+3000==30000
(b/'source-review.json').write_text(json.dumps({'reviewDate':'2026-10-22','sources':report,'dedup':'Raw KB only for source URL; exact Meservey no publications','scope':'Public article text, manifesto and podcast shownotes; no member transcript/full listening; no SME campaign or market-price survey','historicalFees':'2025 US monthly USD context, not2026Chinaquote','originalApplication':'Fictional18personcompany, worksheets,30K RMBcashcap excludesinternal time,90daypilot; untested recommendations, no ROI or earnedcoverage guarantee','metricDistinction':'Delivery vsunderstandingvsbehaviorvsbusiness contribution; attribution notcausalproof; nozero-denominatorcostclaim','bannerDecision':'Official og video portrait inspected and disqualified; FLUX161 concept cover used','figures':'Research strategy uses3XiaoJ figures; root final review pending','copyright':'Brief attributed synthesis and original SME application, no long direct quotes or full translated reproduction'},ensure_ascii=False,indent=2)+'\n');print('Public source statements and illustrative budget arithmetic PASS')
