from pathlib import Path
import json,datetime
root=Path(__file__).resolve().parents[2];src=Path(__file__).resolve().parent;slug='ovisocr3-unified-document-model'
job=Path('/Users/jason/.heinu1-bot/jobs/ab9c3730-8994-44bb-97d6-23558576a777')
public=json.loads((src/'public-verification.json').read_text());article=public['articles'][0];w=json.loads((src/'wechat-verification.json').read_text())['drafts'][0]
assert article['HTTP']==200 and article['carouselRank']==1
assert w['fullTextMatches'] and w['imageIdentitiesMatch'] and w['coverMatches']
r={'slug':slug,'blogUrl':article['url'],'mediaId':w['mediaId'],'archivedMediaId':'','wechatStatus':'draft','wechatError':''}
for p in [src/'publication-result.json',job/'publication-result.json']:p.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n')
(job/'results.json').write_text(json.dumps({'results':[r]},ensure_ascii=False,indent=2)+'\n')
(src/'.published').write_text(article['url']+'\n'+datetime.datetime.now(datetime.timezone.utc).isoformat()+'\n');(src/'.state.json').write_text(json.dumps({'status':'published',**r},indent=2)+'\n')
smoke=json.loads((src/'mac-smoke-final.json').read_text())
mem=Path('/Users/jason/.claude/projects/-Users-jason-Dev-mycelium-blog/memory/project_'+slug+'.md')
mem.write_text('''---
name: OvisOCR3 unified document model
description: Published bilingual source audit, local test evidence and verified WeChat draft
type: project
---
2026-10-27: original raw bot KB existed, no old Blog/M2 receipt/remote draft. Source URLs https://huggingface.co/ATH-MaaS/OvisOCR3 and https://huggingface.co/spaces/ATH-MaaS/OvisOCR3 .
Apache2.0, Qwen3.5-0.8B base, 5 domains and18 task templates. Model4833d5d2afa6e769ee933f024504d67ace80a24c; Space72851f1a4d49e480527a2dc05c920356c9e3d581. Paper2610.33066 submittedOct20. GitHub umbrella README is olderOvis2.5, not completeOCR3 guide.
Official self-reported Omni96.74 is below listed Xiaomi96.83; caption6.93 below Qwen3.8-Max7.30; CrossTab reconstruction89.66 below91.71 despite highest relationF197.07. In-house DocFigCap182pages372targets with Qwen3.8-Max judge; CrossTab890pairs491positive399negative. No benchmark reproduction.
KIE schema is output example template, not formalJSONSchema or constrained decoding. Crosspage Stage1 independent pages, Stage2 recursive adjacent pairs backward with rerender/provenance. Default binding earlierlast/laterfirst table, multiple merges need explicit bindings. Demo Stage1 example can be cached; Stage2 always live. Public uploads are not local/privacy guarantee. vLLM0.22.1 GPU route not native Mac. Weightfile1706030528bytes not RAM minimum.
Five actual released-script synthetic postprocessing checks passed; no visual model inference is established by these checks.
'''+f'Local smoke final evidence: {json.dumps(smoke,ensure_ascii=False)}\nBlog: {article["url"]}\nCurrent WeChat draft/get verified: {w["mediaId"]}\nFull text, three images, metadata, cover, canonical and comment settings match. Primary banner automatic verification and manual illustration review passed.\n')
kb={'title':'OvisOCR3统一五类文档理解任务','summary':'阿里巴巴ATH-MaaS开放OvisOCR3，以0.8B模型统一文档解析、通用OCR、关键信息抽取、文档图片描述和跨页表格重建，采用Apache 2.0许可。官方报告OmniDocBench v1.6为96.74、跨页关系F1为97.07，但不同子指标并非全部领先，且包含内部评测。KIE使用JSON输出模板，跨页重建逐页解析后递归处理相邻两页，业务接入仍需校验结构、来源和识别内容。','tags':['OCR','文档理解','开源模型','KIE','本地AI','表格重建'],'entities':['OvisOCR3','ATH-MaaS','阿里巴巴','Qwen3.5-0.8B','Hugging Face'],'content_type':'url','saved_files':sorted(str(x)for x in Path('/Users/jason/.heinu1-bot/media').glob('ovisocr3-*'))}
(job/'kb-record.json').write_text(json.dumps(kb,ensure_ascii=False,indent=2)+'\n');print(json.dumps(r,ensure_ascii=False))
