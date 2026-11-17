from pathlib import Path
import json,datetime
s=Path(__file__).parent;root=s.resolve().parents[1];slug='kujira-js-procedural-whale-animation';j=Path('/Users/jason/.heinu1-bot/jobs/638b92f5-3232-4a55-95f4-b2a53f794a41')
rec=json.loads((root/'pipeline/m2/output'/f'{slug}.json').read_text());assert len(json.loads((s/'wechat-verification.json').read_text())['drafts'])==1
assert json.loads((s/'semantic-status.json').read_text())['status']=='verified'
assert json.loads((s/'public-verification.json').read_text())['articles'][0]['slug']==slug
r={'slug':slug,'blogUrl':f'https://blog.mushroom.cv/blog/{slug}/','mediaId':rec['mediaId'],'archivedMediaId':'','wechatStatus':'draft','wechatError':''}
for base in [s,j]:(base/'publication-result.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n')
(j/'publication-progress.json').write_text(json.dumps({**r,'blogVerified':True,'wechatVerified':True,'semanticStatus':'verified','completed':False,'phase':'KB-and-git-finalization','checkedAt':datetime.datetime.now(datetime.timezone.utc).isoformat()},ensure_ascii=False,indent=2))
p=Path('/Users/jason/.claude/projects/-Users-jason-Dev-mycelium-blog/memory/project_'+slug+'.md');t=p.read_text().replace('Status: researching; exact source/entity duplicate check clear.','Status: published; Blog/list/images and complete remote WeChat body/metadata verified.\nBlog: '+r['blogUrl']+'\nWeChat: draft\nMedia ID: '+rec['mediaId']+'\nSemantic: verified\nKB: persisted and indexed after publication.')
t+='\nFinal: exactrepoMITreview, byteidentical1414974Bbuild/gzip295311B usingNode26; realisolatedChrome157Lowcanvas1280x720 visualcheck,frame62/20/62hashrepeat;arrow63/playpause/nativeAudioBuffer5s48kHzstereo240000samples finite/nonzero,observedresourcesempty. Noauditoryquality,actualFPS,power,mobile,encoding,crossGPUtest. SingleHTMLwithvendoredthree notzero-library;repomediaJPGpreviewnotruntimeassets;logical24FPS notachievedrate;hidecontrolsnotMP4export. AuthorMITandadaptedBeyondDev/threecreditsretained. Adoptedofficialrise.jpgbanner91667B and3LittleMconceptfigs; notourscreenshotbanner. BilingualSEO/publictitle/list/images/2semanticvectors/search/currentcompleteWeChattext3orderedimages/metadataverified.\n';p.write_text(t)
(s/'.published').write_text(r['blogUrl']+'\n');print(json.dumps(r,ensure_ascii=False))
