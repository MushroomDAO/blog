from pathlib import Path
import json,datetime
s='higgs-audio-v2-engineering-deployment-guide';o=Path(__file__).parent;j=Path('/Users/jason/.heinu1-bot/jobs/c182c0b7-af0b-431e-929d-c5d5ad82b98c')
r=json.loads(Path('pipeline/m2/output',s+'.json').read_text());v=json.loads((o/'wechat-verification.json').read_text());assert v['drafts'][0]['mediaId']==r['mediaId']
assert json.loads((o/'public-verification.json').read_text())['articles'][0]['slug']==s
sem=json.loads((o/'semantic-status.json').read_text())
result={'slug':s,'blogUrl':'https://blog.mushroom.cv/blog/'+s+'/','mediaId':r['mediaId'],'archivedMediaId':'','wechatStatus':'draft','wechatError':''}
for p in [o/'publication-result.json',j/'publication-result.json']:p.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
(o/'.published').write_text(result['blogUrl']+'\n')
(j/'publication-progress.json').write_text(json.dumps({**result,'blogVerified':True,'wechatVerified':True,'semantic':sem,'completed':sem['status']=='verified','updatedAt':datetime.datetime.now(datetime.timezone.utc).isoformat()},indent=2)+'\n')
p=Path('/Users/jason/.claude/projects/-Users-jason-Dev-mycelium-blog/memory')/f'project_{s}.md';t=p.read_text().split('\nFinal channels:')[0].replace('Blog/WeChat: pending.','Channel status below.');p.write_text(t+'\nFinal channels:\nBlog: '+result['blogUrl']+'\nWeChat remote draft verified: '+r['mediaId']+'\nSemantic: '+sem['status']+'\nSix actual upstream pure preprocessing checks passed. Full model/audio/GPU/vLLM/performance not tested. v2 renamed Higgs TTS2, canonical checkpoint bosonai/higgs-tts-2-3b-base revision d80c511612b3040ff2877ce3d408747df1739f11. Deployment uses legacy model10840182ca4ad5d9d9113b60b9bb3c1ef1ba3f84 and tokenizer9d4988fbd4ad07b4cac3a5fa462741a41810dbec to match old package. Code Apache2, weights/tokenizer restricted community license, official24GBrecommendation. NativeDuplex separate. Matching banner and3LittleMimages verified. No masssend.\n')
