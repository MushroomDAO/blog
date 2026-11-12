from pathlib import Path
from datetime import datetime,timezone
import sqlite3,json,urllib.request,re,os
b=Path(__file__).resolve().parent;data=Path('/Users/jason/.heinu1-bot');job='676b2b45-71fd-4e24-80c0-1c103e618b15';url='https://blog.mushroom.cv/'
response=urllib.request.urlopen(urllib.request.Request(url,headers={'Cache-Control':'no-cache','User-Agent':'Mycelium-Recovery-Audit'}),timeout=20);html=response.read().decode();a=html.index('id="carouselContainer"');first=re.search(r'href="(/blog/[^" ]+)"',html[a:])[1];assert response.status==200 and first=='/blog/specialized-inference-engines-rise-hardware-specific-llm-optimization/'
assert json.loads((data/'jobs'/job/'maintenance-result.json').read_text())['deployed']is True
now=datetime.now(timezone.utc).isoformat(timespec='seconds');backup=data/'backups'/('sessions-before-maintenance-reconcile-'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')+'.db');source=sqlite3.connect('file:'+str(data/'sessions.db')+'?mode=ro',uri=True);target=sqlite3.connect(backup);source.backup(target);target.close();source.close();os.chmod(backup,0o600)
proof={'kind':'maintenance','homepage':url,'verifiedAt':now,'firstSlide':first,'deployed':True,'newArticleCreated':False,'wechatAction':'none','reconciledFrom':'publication-result falsely required for maintenance','evidence':'source/20261022-home-carousel-fix/'}
c=sqlite3.connect(data/'sessions.db',timeout=10);c.execute('BEGIN IMMEDIATE');row=c.execute('SELECT status,error,attempts FROM workflow_jobs WHERE id=?',(job,)).fetchone();assert row is not None
if row[0]=='complete':changes=0
else:
 assert row[0]=='failed'and row[1]=='缺少可核验的三件套发布结果',row
 changes=c.execute("UPDATE workflow_jobs SET status='complete',error='',next_retry=0,result_json=? WHERE id=? AND status='failed' AND error=?",(json.dumps(proof,ensure_ascii=False),job,row[1])).rowcount;assert changes==1
c.commit();statuses=dict(c.execute("SELECT status,count(*) FROM workflow_jobs WHERE workspace='blog' GROUP BY status").fetchall());c.close();out={'job':job,'previous':{'status':row[0],'error':row[1],'attempts':row[2]},'changedRows':changes,'statusAfter':'complete','backupCreated':True,'backupFile':str(backup),'verifiedHomepageHTTP':200,'newArticleCreated':False,'newDraftCreated':False,'jobStatusCountsAfter':statuses};(b/'reconciliation.json').write_text(json.dumps(out,ensure_ascii=False,indent=2));print(out)
