from pathlib import Path
import json,re,datetime
root=Path(__file__).resolve().parents[2]
slug='halcyon-without-language-pretraining'
p=root/'src/content/blog'/f'{slug}.md';s=p.read_text()
keys=['title','titleEn','description','descriptionEn','wechatTitle','wechatDigest','pubDate','updatedDate','category','tags','heroImage']
m={k:json.loads(re.search('^'+k+': (.*)',s,re.M)[1]) for k in keys}
cn,en=s.split('<!--EN-->')
checks={'titleLimits':len(m['title'])<=60 and len(m['titleEn'])<=60,'descriptions':all(150<=len(m[k])<=160 for k in ['description','descriptionEn']), 'wechat':len(m['wechatTitle'])<=30 and len(m['wechatDigest'])<=54,'tags':len(m['tags'])>=3,'dates':all(re.fullmatch(r'\d{4}-\d{2}-\d{2}',m[k]) for k in ['pubDate','updatedDate']),'category':m['category']=='Tech-News','bilingual':len(cn)>3000 and len(en)>3000,'copyright':s.count('© 2026 Author: Mycelium Protocol.')==2,'questions':cn.count('？')>=3 and en.count('?')>=3,'FAQ':'## 常见问题' in cn and '## FAQ' in en,'sources':all(u in s for u in ['https://arxiv.org/abs/2610.26863','https://github.com/keshik6/halcyon','https://huggingface.co/collections/radicalnumerics/halcyon']),'computeBoundary':'274.63' in s and '历史' in cn,'runtimeLimits':'没有跑图像生成' in cn and 'No generated images' in en,'accessLimits':'401' in cn and 'gated' in en,'sourcePin':'52931e3a2d34207f5f54da64a7d71c3e582ea966' in s,'internalLinks':'https://blog.mushroom.cv/blog/corespeed-tie-mac-studio-guide/' in s}
figs=list(root.glob('src/assets/images/'+slug+'-fig-*.png'))
checks['figures']=len(figs)==3 and all(p.stat().st_size<92160 for p in figs) and all(s.count(p.name)==2 for p in figs)
checks['hero']=(root/'src/assets/images'/f'{slug}-banner.jpg').stat().st_size<99000
out={'checkedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'passed':all(checks.values()),'checks':checks,'lengths':{k:len(m[k]) for k in ['title','titleEn','description','descriptionEn','wechatTitle','wechatDigest']},'manualReview':['BLUF in both languages; external URLs remain plain text','Claims distinguish author results, source audits and no local inference','Official promotional artwork identified; not a locally tested sample','Training stack not claimed public; code MIT not extrapolated to weight terms','Existing Astro metadata/heading anchors reused; no new structured-data implementation']}
Path(__file__).with_name('seo-geo-report.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print(json.dumps(out,ensure_ascii=False));assert out['passed']
