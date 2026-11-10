from pathlib import Path
import json,datetime
slug='openrsi-index-research-agent-benchmark-guide'
o=Path(__file__).parent
job=Path('/Users/jason/.heinu1-bot/jobs/22c882a4-7a52-42f8-84d1-f80407d85c3c')
r=json.loads(Path('pipeline/m2/output',slug+'.json').read_text())
v=json.loads((o/'wechat-verification.json').read_text())
assert v['drafts'][0]['mediaId']==r['mediaId']
assert json.loads((o/'public-verification.json').read_text())['articles'][0]['slug']==slug
sem=json.loads((o/'semantic-status.json').read_text())
result={'slug':slug,'blogUrl':f'https://blog.mushroom.cv/blog/{slug}/','mediaId':r['mediaId'],'archivedMediaId':'','wechatStatus':'draft','wechatError':''}
for p in [o/'publication-result.json',job/'publication-result.json']:p.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
(o/'.published').write_text(result['blogUrl']+'\n')
(job/'publication-progress.json').write_text(json.dumps({**result,'blogVerified':True,'wechatVerified':True,'semantic':sem,'completed':sem['status']=='verified','updatedAt':datetime.datetime.now(datetime.timezone.utc).isoformat()},indent=2)+'\n')
p=Path('/Users/jason/.claude/projects/-Users-jason-Dev-mycelium-blog/memory')/f'project_{slug}.md'
t=p.read_text().split('\nFinal channels:')[0].replace('Blog/WeChat: pending.','Channel status below.')
p.write_text(t+'\nFinal channels:\nBlog: '+result['blogUrl']+'\nWeChat remote draft verified: '+r['mediaId']+'\nSemantic: '+sem['status']+'\nPinned8d170deed4591fc7e4306f2d86ff4d9bcffd1288; Apache2repo, taskdata upstreamterms separate. Four targeted upstream testfiles183checks pass; actual compiler3tasks GEMM1GPU,sparse1GPU,Qwendatawrapper0GPU. Two QwenJSONLs2560each bytes/hash match. NoDocker/firewall/model/GPUtraining/securityaudit/score replication. 26taskmanifests not26portableexperiments. Qwenwrapperdatareward not122Btraining, historical71.7089vs71.9123 recipe mismatch. Marin historicalnonHarborarchive requiresclusterassets. GPIC10Mlogs vs100Mlegacyruntime, screeningFD1286.4504/1043.3926/729.3343 differentcaptionprotocols andnotsealed50kfinal; no agentranking. ExperimentalMaccontrollerCPUlimitednotAppleGPUtraining. FLUX8381cover and3LittleMfigs verified; no masssend.\n')
