from pathlib import Path
import os,json,hashlib,urllib.request,datetime
out=Path(__file__).parent;slugs=['praxis-1-open-world-action-model-engineering','beeftv-local-creative-workbench-license-guide'];plan=json.loads((out/'semantic-plan.json').read_text())['changed'];assert len(plan)==4
ids=[hashlib.sha256(f"{r['article_id']}:{r['language']}:{r['content_hash']}".encode()).hexdigest()[:48]for r in plan]
headers={'Authorization':'Bearer '+os.environ['CLOUDFLARE_REGISTRAR_TOKEN'],'Content-Type':'application/json'};base=f"https://api.cloudflare.com/client/v4/accounts/{os.environ['CLOUDFLARE_ACCOUNT_ID']}/vectorize/v2/indexes/blog-search-v1"
def get(u,data,h=headers):return json.load(urllib.request.urlopen(urllib.request.Request(u,data=json.dumps(data).encode(),headers=h),timeout=45))
r=get(base+'/get_by_ids',{'ids':ids});assert r['success'];rows=[{'id':x['id'],'metadata':x.get('metadata',{})}for x in r['result']];(out/'semantic-readback.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2))
search=[]
for slug,q in zip(slugs,['Praxis-1 开放权重 视频动作联合训练 SM120 机器人设备适配','BeefTV 创意工作台 历史MIT 新增代码许可 持久任务恢复']):
 result=get('https://blog.mushroom.cv/api/search',{'query':q},{'Content-Type':'application/json','User-Agent':'Mycelium-Publish-Verification'});search.append({'slug':slug,'query':q,'found':slug in json.dumps(result),'response':result})
(out/'semantic-search-final.json').write_text(json.dumps(search,ensure_ascii=False,indent=2));verified=len(rows)==4 and all(x['found']for x in search);status={'recordsAccepted':4,'manifestUpdated':True,'readbackVerified':len(rows)==4,'publicSearchVerified':all(x['found']for x in search),'status':'verified'if verified else'propagation-pending','checkedAt':datetime.datetime.now(datetime.timezone.utc).isoformat()};(out/'semantic-status.json').write_text(json.dumps(status,indent=2));print(json.dumps(status))
