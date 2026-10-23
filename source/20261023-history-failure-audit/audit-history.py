from pathlib import Path
import sqlite3,json,concurrent.futures,urllib.request,urllib.error
b=Path(__file__).resolve().parent;root=b.parents[1];jobs=Path('/Users/jason/.heinu1-bot/jobs');c=sqlite3.connect('file:/Users/jason/.heinu1-bot/sessions.db?mode=ro',uri=True);c.row_factory=sqlite3.Row
states=[dict(x)for x in c.execute("SELECT id,status,attempts,error,kb_confirmed FROM workflow_jobs WHERE workspace='blog' ORDER BY created_at")];records={}
def add(value,job):
 if isinstance(value,list):
  for x in value:add(x,job)
 elif isinstance(value,dict):
  slug=value.get('slug')
  if slug and value.get('blogUrl')=='https://blog.mushroom.cv/blog/'+slug+'/':
   entry=records.setdefault(slug,{'slug':slug,'url':value['blogUrl'],'jobs':[],'receiptIds':[]});entry['jobs'].append(job)
   for k in ['mediaId','archivedMediaId']:
    if value.get(k)and value[k]not in entry['receiptIds']:entry['receiptIds'].append(value[k])
  else:
   for v in value.values():
    if isinstance(v,(list,dict)):add(v,job)
for p in jobs.glob('*/publication-result.json'):
 try:add(json.loads(p.read_text()),p.parent.name)
 except(json.JSONDecodeError,OSError):pass
def check(entry):
 entry['jobs']=sorted(set(entry['jobs']));slug=entry['slug'];md=root/'src/content/blog'/f'{slug}.md';entry['localArticleExists']=md.exists();receipt=root/'pipeline/m2/output'/f'{slug}.json';entry['localReceiptExists']=receipt.exists()
 if receipt.exists():
  d=json.loads(receipt.read_text());entry['localReceiptId']=d.get('mediaId')or d.get('media_id');entry['receiptMatchesRecorded']=entry['localReceiptId']in entry['receiptIds']
 try:
  res=urllib.request.urlopen(urllib.request.Request(entry['url'],headers={'User-Agent':'Mycelium-Recovery-Audit'}),timeout=25);entry['blogHTTP']=res.status;res.close()
 except urllib.error.HTTPError as e:entry['blogHTTP']=e.code
 except Exception as e:entry['blogHTTP']=None;entry['blogError']=type(e).__name__
 return entry
with concurrent.futures.ThreadPoolExecutor(max_workers=6)as pool:articles=list(pool.map(check,records.values()))
summary={'workspaceJobs':len(states),'jobStatusCounts':{k:sum(x['status']==k for x in states)for k in sorted({x['status']for x in states})},'articles':len(articles),'online200':sum(x['blogHTTP']==200 for x in articles),'localReceiptMatches':sum(x.get('receiptMatchesRecorded',False)for x in articles),'unresolvedJobs':[x for x in states if x['status']not in ['complete','running']]};out={'summary':summary,'articles':articles};(b/'history-audit.json').write_text(json.dumps(out,ensure_ascii=False,indent=2));print(json.dumps(summary,ensure_ascii=False));print('articleExceptions',[x['slug']for x in articles if x['blogHTTP']!=200 or not x.get('receiptMatchesRecorded')])
