from pathlib import Path
import json,datetime,re
p=Path(__file__).parent;slug=json.loads((p/'slugs.json').read_text())[0];job=Path('/Users/jason/.heinu1-bot/jobs/f1eb66fd-32b5-4940-b57a-958cb418aa42');job.mkdir(exist_ok=True,parents=True);now=datetime.datetime.now(datetime.timezone.utc).isoformat()
a=json.loads((p/'public-verification.json').read_text());w=json.loads((p/'wechat-verification.json').read_text());s=json.loads((p/'semantic-status.json').read_text());assert a['articles'][0]['slug']==slug and w['drafts'][0]['slug']==slug
r={'slug':slug,'blogUrl':f'https://blog.mushroom.cv/blog/{slug}/','mediaId':w['drafts'][0]['mediaId'],'archivedMediaId':'','wechatStatus':'draft','wechatError':'','semanticStatus':s['status'],'checkedAt':now,'repositoryStatus':'pending-push-and-review'}
for f in [p/'publication-result.json',job/'publication-result.json']:f.write_text(json.dumps(r,ensure_ascii=False,indent=2))
memory=Path('/Users/jason/.claude/projects/-Users-jason-Dev-mycelium-blog/memory')/f'project_{slug}.md';text=memory.read_text();text=text.replace('Blog/WeChat/semantic pending.',f'''Blog: verified {r['blogUrl']}
WeChat: draft {r['mediaId']}; currentfulltext/ordered3images/cover/metadata/source/comments verified at {w['checkedAt']}.
Semantic: {s['status']}
100syntheticCPUfloat32cacheiterations pass directupstreamKVCache(anchor/eviction/storage/RoPE), no modelweights/CUDA/video/audio/throughput/TTFT/peakRAM replication;Torch2.14outsidedeclaredruntime2.6to2.8. Paper32pages methods/results/limitations inspected, notfullmathaudit.
Source: source/20261121-aura. Fullnoncommercialpaper/code/cards archivedprivately; banner8871manualrejectlensgibberish,8872replacement+3LittleMbodyillustrations reviewed.17priorproductionarticlespreserved.
Repository: feature PR pending. Reuse channels on retry; no new Blog/draft/embedding.''');text=re.sub(r'^Semantic:.*$', 'Semantic: '+s['status'], text, flags=re.M);memory.write_text(text)
(p/'.published').write_text(r['blogUrl']+'\n'+now+'\n');(job/'publication-progress.json').write_text(json.dumps({'completed':False,'phase':'finalizing-repository','channelsCompleted':True,'blogVerified':True,'wechatVerified':True,'semanticVerified':s['status']=='verified','kbUpdated':True,'mainMerged':False,'retryScope':'repository bookkeeping only; no new Blog/draft/embedding','updatedAt':now},indent=2));print(json.dumps(r,ensure_ascii=False))
