from pathlib import Path
import json,re,yaml,hashlib
root=Path(__file__).resolve().parents[2];slugs=['lingbot-open-model-family-repositories-ecosystem-review'];reports=[];hashes={}
for slug in slugs:
 p=root/'src/content/blog'/f'{slug}.md';s=p.read_text();f=yaml.safe_load(s.split('---')[1]);cn,en=s.split('<!--EN-->');figs=sorted((root/'src/assets/images').glob(slug+'-fig-*.png'));hero=root/'src/assets/images'/f'{slug}-banner.jpg'
 c={'fields':all(k in f for k in ['title','titleEn','description','descriptionEn','pubDate','updatedDate','category','tags','heroImage']),'title':len(f['titleEn'])<=60,'description':all(150<=len(f[k])<=160 for k in ['description','descriptionEn']),'wechat':len(f['wechatTitle'])<=30 and len(f['wechatDigest'])<=54,'tags':len(f['tags'])>=3,'bilingual':len(cn)>800 and len(en)>800,'FAQ':'###'in cn and '## FAQ'in en,'sources':'https://github.com/'in cn and 'https://github.com/'in en,'copyright':s.count('© 2026 Author: Mycelium Protocol.')==2,'images':len(figs)==3 and all(x.stat().st_size<90000 and s.count(x.name)==2 for x in figs),'banner':hero.exists()and hero.stat().st_size<99000}
 reports.append({'slug':slug,'checks':c,'passed':all(c.values())})
 for x in [p,hero]+figs:
  if x.exists():hashes[str(x.relative_to(root))]=hashlib.sha256(x.read_bytes()).hexdigest()
Path(__file__).with_name('seo-geo-report.json').write_text(json.dumps(reports,ensure_ascii=False,indent=2));print(json.dumps(reports,ensure_ascii=False));assert all(r['passed']for r in reports);Path(__file__).with_name('frozen-inputs.json').write_text(json.dumps(hashes,indent=2))
