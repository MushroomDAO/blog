from pathlib import Path
import json,re
from PIL import Image
base=Path('source/20261017-d2r-kinex-glimpse');reports=[]
for topic in json.loads((base/'topics.json').read_text()):
 slug=topic['slug'];s=Path('src/content/blog',slug+'.md').read_text();fm=s.split('---',2)[1];parts=s.split('<!--EN-->');r={'slug':slug,'checks':{},'images':[]}
 for k in ['description','descriptionEn']:
  v=json.loads(re.search('^'+k+r': (.+)$',fm,re.M)[1]);r['checks'][k]=150<=len(v)<=160
 for k,n in [('titleEn',60),('wechatTitle',30),('wechatDigest',54)]:r['checks'][k]=len(json.loads(re.search('^'+k+r': (.+)$',fm,re.M)[1]))<=n
 r['checks'].update({'bilingual':len(parts)==2,'copyright':s.count('© 2026 Author: Mycelium Protocol.')==2,'faq':all(x.count('### ')>=3 for x in parts),'question_heading':bool(re.search(r'^## .*?[？?]',s,re.M)),'source': 'https://github.com/' in s,'date':'pubDate: "2026-10-17"' in s,'category':'category: "Tech-News"' in s,'figures_twice':all(s.count(slug+f'-fig-{i:02}.png')==2 for i in range(1,4)),'no_placeholder':'PLACEHOLDER' not in s})
 for suffix in ['-banner.jpg']+[f'-fig-{i:02}.png' for i in range(1,4)]:
  q=Path('src/assets/images')/(slug+suffix);im=Image.open(q);size=q.stat().st_size;r['images'].append({'path':str(q),'dimensions':im.size,'bytes':size});assert im.size==((1200,630) if 'banner' in suffix else (1280,720));assert size<(99000 if 'banner' in suffix else 90000)
 assert all(r['checks'].values()),r
 reports.append(r);print(slug,'PASS')
base.joinpath('seo-geo-check.json').write_text(json.dumps(reports,ensure_ascii=False,indent=2))
