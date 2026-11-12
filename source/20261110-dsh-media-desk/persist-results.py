from pathlib import Path
import json,datetime
slug='dsh-media-desk-creator-workbench-guide'
o=Path(__file__).parent
job=Path('/Users/jason/.heinu1-bot/jobs/a954f8d2-847e-4a2e-bec3-bde814f22c60')
r=json.loads(Path('pipeline/m2/output',slug+'.json').read_text())
v=json.loads((o/'wechat-verification.json').read_text())
assert v['drafts'][0]['mediaId']==r['mediaId']
assert json.loads((o/'public-verification.json').read_text())['articles'][0]['slug']==slug
sem=json.loads((o/'semantic-status.json').read_text())
result={'slug':slug,'blogUrl':f'https://blog.mushroom.cv/blog/{slug}/','mediaId':r['mediaId'],'archivedMediaId':'','wechatStatus':'draft','wechatError':''}
for p in [o/'publication-result.json',job/'publication-result.json']:p.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
(o/'.published').write_text(result['blogUrl']+'\n')
(job/'publication-progress.json').write_text(json.dumps({**result,'blogVerified':True,'wechatVerified':True,'semantic':sem,'completed':sem['status']=='verified' and (o/'kb-readback.json').exists(),'updatedAt':datetime.datetime.now(datetime.timezone.utc).isoformat()},indent=2)+'\n')
p=Path('/Users/jason/.claude/projects/-Users-jason-Dev-mycelium-blog/memory')/f'project_{slug}.md'
t=p.read_text().split('\nFinal channels:')[0].replace('Blog/WeChat: pending.','Channel status below.')
p.write_text(t+'\nFinal channels:\nBlog: '+result['blogUrl']+'\nWeChat remote draft verified: '+r['mediaId']+'\nSemantic: '+sem['status']+'\nPinnedfc237f3388d048f51c3145cfd411dbb80ba2b388 andnpm2.6.2 MITcommunityDSHplugin notofficialDeepSeek. RequiresDSH>=0.2.1rc5<0.3,authorhosttest0.2.2rc1notours. Build andall6Nodeunitfiles87pass0fail0skip, isolatedDSH_HOME andTZAsiaShanghai. No realhost/UI/paidmodel/image/Monid/nativeplugininstall/performance/growth test. HostJS+Reactclientlazybundle/Cordispatch,JSONstate files, mtime+perprocessqueue notmultiuserDBtransactions. Default1cover+2fig+6shots=9images/concurrency3not3xspeedclaim. StructuredfallbacknotfullAIoutput; pageclosevsHostrestart interruptedstates. HTTPimagevsDSHsubscriptionroottools/executor/publicdirectory/accountfallback distinct; registeredtoolsnotaccountquotaoridentityproof. CodeModePTCunsupported, noautoHTTPfallback/toolretry. Monidownpublicaccountoptional3rdparty, engagementnotviews, unsupportedYouTube/WeChatimports despiteplatformdraft/schedule support. No directpublishing orvideoediting. Reviewrulesconfirm/prompt/Skill notweighttraining orcausalgrowthproof. Localsettings0600notencrypted,no modelkey inpublicresponse; dataexport/backup considerations stated. FLUX8391rejectedpseudoletters,final8392blankcardscover and3LittleMfigs verified. No masssend.\n')
