from pathlib import Path
import os,json,hashlib,urllib.request,datetime
out=Path(__file__).parent;slugs=['openthai-ocr-markdown-thai-document-engineering','my-office-claude-code-session-dashboard-guide'];plan=json.loads((out/'semantic-plan.json').read_text())['changed'];assert len(plan)==4
ids=[hashlib.sha256(f"{r['article_id']}:{r['language']}:{r['content_hash']}".encode()).hexdigest()[:48]for r in plan]
headers={'Authorization':'Bearer '+os.environ['CLOUDFLARE_REGISTRAR_TOKEN'],'Content-Type':'application/json'};base=f"https://api.cloudflare.com/client/v4/accounts/{os.environ['CLOUDFLARE_ACCOUNT_ID']}/vectorize/v2/indexes/blog-search-v1"
def get(u,data,h=headers):return json.load(urllib.request.urlopen(urllib.request.Request(u,data=json.dumps(data).encode(),headers=h),timeout=45))
r=get(base+'/get_by_ids',{'ids':ids});assert r['success'];rows=[{'id':x['id'],'metadata':x.get('metadata',{})}for x in r['result']];(out/'semantic-readback.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2))
search=[]
for slug,q in zip(slugs,['OpenThai OCR Markdown 泰文 表格 文档 MPS 本地部署','My Office Claude Code 会话 看板 hooks 三维办公室']):
 result=get('https://blog.mushroom.cv/api/search',{'query':q},{'Content-Type':'application/json','User-Agent':'Mycelium-Publish-Verification'});search.append({'slug':slug,'query':q,'found':slug in json.dumps(result),'response':result})
(out/'semantic-search-final.json').write_text(json.dumps(search,ensure_ascii=False,indent=2));verified=len(rows)==4 and all(x['found']for x in search);status={'recordsAccepted':4,'manifestUpdated':True,'readbackVerified':len(rows)==4,'publicSearchVerified':all(x['found']for x in search),'status':'verified'if verified else'propagation-pending','checkedAt':datetime.datetime.now(datetime.timezone.utc).isoformat()};(out/'semantic-status.json').write_text(json.dumps(status,indent=2));print(json.dumps(status))
