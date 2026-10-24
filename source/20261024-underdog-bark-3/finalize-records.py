"""Finish publication records only after public and current remote-draft verification."""
from pathlib import Path
import json,datetime,shutil
s=Path(__file__).resolve().parent;slug='underdog-bark-3-local-asr'
p=json.loads((s/'public-verification.json').read_text())['articles'][0]
w=json.loads((s/'wechat-verification.json').read_text())['drafts'][0]
assert p['HTTP']==200 and p['carouselRank']==1 and w['fullTextMatches'] and w['coverMatches']
r={'slug':slug,'blogUrl':'https://blog.mushroom.cv/blog/'+slug+'/','mediaId':w['mediaId'],'wechatStatus':'draft','wechatError':''}
(s/'publication-result.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n')
j=Path('/Users/jason/.heinu1-bot/jobs/9b3755d4-af7b-40ae-aed1-8d29a0b97303');j.mkdir(exist_ok=True,parents=True);(j/'publication-result.json').write_text(json.dumps({**r,'results':[r]},ensure_ascii=False,indent=2)+'\n')
(s/'.published').write_text('2026-10-24\n'+r['blogUrl']+'\n');(s/'.state.json').write_text(json.dumps({'status':'published','verifiedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),**r},ensure_ascii=False,indent=2)+'\n')
m=Path('/Users/jason/.claude/projects/-Users-jason-Dev-mycelium-blog/memory/project_'+slug+'.md');t=m.read_text().replace('Blog pending; WeChat pending. OriginalrawKBbot saved.','Blog '+r['blogUrl']+' HTTP200, list/hero/images verified. Current remote WeChatdraft '+r['mediaId']+' fulltext, orderedimages, metadata, cover and comments verified. OriginalrawKBreused. AppleM4/16GB realFP16MLXshortsyntheticEnglishASRpassed, notspeed/meeting/Cleanbenchmark. Official app0.5sec/5min versus publicMLX1.5sec/min remain distinct.')
m.write_text(t);shutil.copy(m,Path('/tmp/bark-memory-only')/m.name)
f=Path('.agents/skills/forage/FEEDBACK.md');entry='\n\n## 2026-10-24 — Underdog Bark 3.0 source check and local smoke\n\n- '+r['blogUrl']+' Standard163MB/Clean180MBbasedonPlus separated;EnglishWERnotCER; AMI7.82 versus seven-set4.94 maker-run, not submittedleaderboard.4.937/4.941 Parakeetmean almosttie. OfficialM5Maxapp595x versusstockM2MLX41x not samebenchmark; no ownspeedtest. ExactstandardHFpin85db2ad18ab41e534a222ee253c29191d77ed919, publicFP16MLX real3.24sec AppleSamantha synthetic English -> expected wordsequence, casing/punctuation omitted. OfflineHubmode, model163398645bytes versus~1.26GBexpandedweightdiskfile, notpeakRAM. NoClean/meeting/longaudioeval. Topiccover+3XiaoM, bilingualSEO, publicassets/list/carousel,currentdraft fulltext/images/cover/comments and semanticKBverified. Task9b3755d4-af7b-40ae-aed1-8d29a0b97303.\n'
if r['blogUrl']not in f.read_text():f.write_text(f.read_text().rstrip()+entry)
print(json.dumps(r))
