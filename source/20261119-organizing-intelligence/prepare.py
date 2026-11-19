from pathlib import Path
import json,sqlite3,datetime,hashlib
p=Path(__file__).parent;slug='organizing-intelligence-ai-jobs-wages-coordination';job='4124913f-d640-4580-9065-ef75c531f32e';old=p.parent/'20261119-brief2mp4';oldslug='brief2mp4-agent-motion-graphics-verification-guide'
(p/'slugs.json').write_text(json.dumps([slug]))
for name in ['check.py','verify-public.py','verify-preserved.py','verify-wechat.cjs','wechat-content-canonical.py','remote-preflight.cjs','check-semantic.py','mine-kb.py','verify-kb.py','compress-figures.py']:
 s=(old/name).read_text().replace(oldslug,slug).replace('cb9807fa-444c-4ea6-bb71-6e756882fa97',job)
 if name=='check.py':s=s.replace("'https://github.com/'in cn and 'https://github.com/'in en","'https://arxiv.org/'in cn and 'https://arxiv.org/'in en")
 if name=='verify-preserved.py':s=s.replace('slugs=[','slugs=[\"'+oldslug+'\",')
 if name=='remote-preflight.cjs':
  a=s.index('const matches=');b=s.index('const{data:p}',a);s=s[:a]+f'const matches=items.filter(x=>/Organizing\\s*Intelligence|2611\\.05417|economics-of-intelligence|{slug}/i.test(JSON.stringify(x)));'+s[b:]
 if name=='check-semantic.py':s=s.replace('brief2mp4 MIT animation brief SPEC REPORT delivery checks','Organizing Intelligence Imas Koh Legg 工资 协调 组织重构')
 (p/name).write_text(s)
c=sqlite3.connect('file:/Users/jason/.mempalace/palace/chroma.sqlite3?mode=ro',uri=True)
rows=c.execute("SELECT c0 FROM embedding_fulltext_search_content WHERE lower(c0) LIKE '%organizing intelligence%' OR c0 LIKE '%2611.05417%' OR c0 LIKE '%economics-of-intelligence%' ").fetchall()
(p/'exact-kb-dedup.json').write_text(json.dumps({'checkedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'matches':[{'heading':x[0].splitlines()[0],'rawMaterialOnly':True}for x in rows]},ensure_ascii=False,indent=2))
mem=Path('/Users/jason/.claude/projects/-Users-jason-Dev-mycelium-blog/memory');f=mem/f'project_{slug}.md'
f.write_text(f'''---
name: Organizing Intelligence wages and coordination analysis
description: Imas Koh Legg paper2611.05417v1; conditional labor outcomes, coordination rents and empirical limits.
type: project
---
# Organizing Intelligence
Paper: https://arxiv.org/abs/2611.05417v1
Companion: https://institute.deepmind.com/essays/the-economics-of-intelligence/
Authors: Alex Imas and Andrew Koh equal lead contribution, Shane Legg. Paper dated2026-10-31; DMIessaypublished2026-10-29, metadataupdatedNov19, not newlypublishedtoday.108page theoreticalworkingpaper, CC BY4.0. Views ofauthors notGooglecorporateforecast.
Slug: {slug}
Dedup: exactprimaryURL noledgerhits; exacttitle onlyincomingrawKB. Generic intelligence/organizing token hits unrelated; no prior article/localM2receipt/remotedraft; publishedAPI48001 unavailable.
Competence changes productivitylevels, coordination changes scaling. Complementary humanmosaics canoutperformAIthatbeatsaverageindividual. ReplicableAI/fixedhuman supply changes scarcitywages. Model explicitly allows gradual/sudden fullunemployment underconditions; no guarantee jobsneverzero. MinimalAGI toy14humans remainemployed yetspecialistwages4.15to2.90 andcoordinators2.41to1.30. Figure22coordinatorssurvivewhilepayfalls. Figure25reorganizationcanraise thenlowercoordinationwages; D.7finite-menuchecks notglobalpathcertificate. ASI nichehumanemployment nearthreshold inpaper differsfromstrongeressaylanguage; relationalemployment/highrealwages essaypossibility notformalcalibratedforecast. AssumptionssingleAItypeunlimitedcopiesconstant rental/fixedhumancapabilities/reservationwages/competitivezero-profit; concentrationnotproofmonopolyrents.
Blog pending. WeChat pending. Semantic pending.
Source: source/20261119-organizing-intelligence. Fullpaper andarticleprivatearchive; originalarticlewithsourceattribution and3LittleJillustrations.
''')
i=mem/'MEMORY.md';s=i.read_text()
if f.name not in s:i.write_text(s+f'\n- [Organizing Intelligence]({f.name}) — conditional jobs/wages, coordination and reorganization boundaries.\n')
print(json.dumps({'slug':slug,'exactKBMatches':len(rows),'memory':str(f)}))
