from pathlib import Path
import json,re
from PIL import Image
b=Path(__file__).resolve().parent;root=b.parents[1];reports=[]
for slug in ['abot-recon-streaming-3d-reconstruction','openui-1-generative-ui-engineering']:
 s=(root/'src/content/blog'/f'{slug}.md').read_text();fm=s.split('---',2)[1];parts=s.split('<!--EN-->');fields={}
 for k in ['description','descriptionEn','titleEn','wechatTitle','wechatDigest']:fields[k]=json.loads(re.search('^'+k+r': (.+)$',fm,re.M)[1])
 checks={'descriptions':all(150<=len(fields[k])<=160 for k in ['description','descriptionEn']),'titleEn':len(fields['titleEn'])<=60,'wechatTitle':len(fields['wechatTitle'])<=30,'wechatDigest':len(fields['wechatDigest'])<=54,'bilingual':len(parts)==2,'copyright':s.count('© 2026 Author: Mycelium Protocol.')==2,'faq':all(x.count('### ')>=3 for x in parts),'questionHeadings':len(re.findall(r'^## .*?[？?]',s,re.M))>=2,'date':'pubDate: "2026-10-20"'in fm,'category':'category: "Tech-News"'in fm,'tags':len(json.loads(re.search(r'^tags: (.+)$',fm,re.M)[1]))>=3,'figuresBothLanguages':all(s.count(f'{slug}-fig-{i:02}.png')==2 for i in range(1,4)),'primarySources':'https://github.com/'in s,'internalLink':'https://blog.mushroom.cv/blog/'in s,'scope':('未下载模型权重' in s if slug.startswith('abot') else '没有调用大模型' in s)}
 assets=[]
 for suffix in ['-banner.jpg']+[f'-fig-{i:02}.png'for i in range(1,4)]:
  p=root/'src/assets/images'/(slug+suffix);im=Image.open(p);n=p.stat().st_size;assert im.size==((1200,630)if'banner'in suffix else(1280,720));assert n<(99000 if'banner'in suffix else 90000);assets.append({'path':str(p.relative_to(root)),'dimensions':im.size,'bytes':n})
 assert all(checks.values()),checks
 reports.append({'slug':slug,'checks':checks,'assets':assets});print(slug,'PASS')
(b/'seo-geo-check.json').write_text(json.dumps(reports,ensure_ascii=False,indent=2))
