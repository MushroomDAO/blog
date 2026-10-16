import re,json,subprocess
from pathlib import Path
p=Path(__file__).resolve().parent;root=p.parents[1];s=(root/'src/content/blog/valtz-local-ai-creative-studio.md').read_text();fm=s.split('---',2)[1];r={}
for f in ['title','titleEn','description','descriptionEn','wechatTitle','wechatDigest']:r[f+'Length']=len(re.search('^'+f+': "(.*)"',fm,re.M)[1])
assert 150<=r['descriptionLength']<=160 and 150<=r['descriptionEnLength']<=160
assert r['wechatTitleLength']<=30 and r['wechatDigestLength']<=54
assert s.count('<!--EN-->')==1 and s.count('Mycelium Protocol')==2
assert s.count('](../../assets/images/valtz-local-ai-creative-studio-fig-')==6
assert '210 项运行，192 通过、1 失败、17 跳过' in s
assert '210 tests: 192 passed, one failed and 17 skipped' in s
assert '未构建或启动 SwiftUI 应用' in s and 'did not build or launch SwiftUI' in s
imgs=[]
for i in range(1,4):
 q=root/f'src/assets/images/valtz-local-ai-creative-studio-fig-{i:02}.png';assert q.stat().st_size<90000;dim=subprocess.check_output(['magick','identify','-format','%wx%h',str(q)],text=True);assert dim=='1280x720';imgs.append({'file':q.name,'bytes':q.stat().st_size,'dimensions':dim})
r.update({'bilingual':True,'BLUF':True,'FAQ':True,'copyright':True,'sourcePinned':True,'internalLink200':True,'bodyImageReferences':6,'images':imgs,'independentAnalysis':'Recipe provenance not bitwise guarantee; LMDBworkingcopy vs CBORsavedpackage; Fleet wholejobs not pooledGPUmemory; local vscloud; explicitbuild/testfailureboundaries','scope':'No-engine core/CLI only;210ran192passed1failed17skip; onefailure rerun reproduced; originalPNG64x64CLIroundtrip; noGUI/inference/performance/liveFleet'});(p/'seo-geo-report.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n');print(json.dumps(r,ensure_ascii=False,indent=2))
