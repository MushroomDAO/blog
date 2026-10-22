from pathlib import Path
import re,json
from PIL import Image
b=Path(__file__).resolve().parent;root=b.parents[1];slug='specialized-inference-engines-rise-hardware-specific-llm-optimization';s=(root/'src/content/blog'/f'{slug}.md').read_text();fm=s.split('---',2)[1];parts=s.split('<!--EN-->');checks={}
for k in ['description','descriptionEn']:checks[k]=150<=len(json.loads(re.search('^'+k+': (.+)$',fm,re.M)[1]))<=160
for k,n in [('titleEn',60),('wechatTitle',30),('wechatDigest',54)]:checks[k]=len(json.loads(re.search('^'+k+': (.+)$',fm,re.M)[1]))<=n
checks.update({'bilingual':len(parts)==2,'copyright':s.count('© 2026 Author: Mycelium Protocol.')==2,'faq':all(x.count('### ')>=3 for x in parts),'preservedPubDate':'pubDate: "2026-10-05"'in s,'updatedDate':'updatedDate: "2026-10-22"'in s,'correctsUnverified120':'没有找到“120 tok/s”'in s,'cacheScope':'16 个重放提示全部缓存命中'in s,'noPerformanceRun':'没有下载模型、跑推理'in s,'modelCompatibility':'Flash-Next 暂不支持 MLX checkpoint'in s,'historicalOtherEngines':'其他五个项目'in s,'pinnedSource':'1482f6bbc2abf12375332725302019594150b6cb'in s,'noPlaceholders':'LOCAL_SCOPE_'not in s})
imgs=[]
for name in ['specialized-inference-engines-rise-llm-hardware-optimization-banner.jpg']+[f'splash-1-4-update-fig-{i:02}.png'for i in range(1,4)]:
 p=root/'src/assets/images'/name;im=Image.open(p);size=p.stat().st_size;hero='banner'in name;assert im.size==((1200,630)if hero else(1280,720))and size<(99000 if hero else 90000);imgs.append({'name':name,'dimensions':im.size,'bytes':size});
 if not hero:assert s.count(name)==2
assert all(checks.values()),checks
(b/'seo-geo-check.json').write_text(json.dumps({'slug':slug,'checks':checks,'images':imgs},indent=2));print('SEO metadata,bilingual scope,FAQ,images PASS')
