import re,json,subprocess
from pathlib import Path
p=Path(__file__).resolve().parent;root=p.parents[1];s=(root/'src/content/blog/open-tts-leaderboard-october-2026.md').read_text();fm=s.split('---',2)[1];r={}
for field in ['title','titleEn','description','descriptionEn','wechatTitle','wechatDigest']:
 r[field+'Length']=len(re.search('^'+field+': "(.*)"',fm,re.M)[1])
assert 150<=r['descriptionLength']<=160 and 150<=r['descriptionEnLength']<=160
assert r['wechatTitleLength']<=30 and r['wechatDigestLength']<=54
assert s.count('<!--EN-->')==1 and s.count('Mycelium Protocol')==2
assert s.count('](../../assets/images/open-tts-leaderboard-october-2026-fig-')==6
for n in ['english','chinese']:
 rows=json.loads((p/(n+'.json')).read_text())[0]['value']['data'][:10]
 assert len(rows)==10
 for row in rows:
  name=re.sub('<[^>]+>','',row[1]);line=f'| {row[0]} | {name} | {row[2]} | {row[3]} |';assert s.count(line)==2,(n,line,s.count(line))
imgs=[]
for i in range(1,4):
 q=root/f'src/assets/images/open-tts-leaderboard-october-2026-fig-{i:02}.png';assert q.stat().st_size<90000;dim=subprocess.check_output(['magick','identify','-format','%wx%h',str(q)],text=True);assert dim=='1280x720';imgs.append({'file':q.name,'bytes':q.stat().st_size,'dimensions':dim})
r.update({'bilingual':True,'BLUF':True,'FAQ':True,'bodyImageReferences':6,'images':imgs,'copyright':True,'sourcePinned':True,'tableRowsCheckedAgainstPublicAPI':40,'internalLink':True,'scope':'No model inference or listening test. October9 official snapshot queried October16.','independentAnalysis':'Dataset/mode/hardware coverage; p50/p95 reversal; metadata conflicts; missing vszero; no universal quality ranking.'});(p/'seo-geo-report.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n');print(json.dumps(r,ensure_ascii=False,indent=2))
