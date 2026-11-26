from pathlib import Path
import os,json,hashlib,urllib.request,datetime
out=Path(__file__).parent;slugs=json.loads((out/'slugs.json').read_text());ids=[]
for slug,name in zip(slugs,['research']):
 plan=json.loads((out/name/'semantic-plan.json').read_text())['changed'];assert len(plan)==2 and all(x['article_id']==slug for x in plan)
 ids += [hashlib.sha256(f"{r['article_id']}:{r['language']}:{r['content_hash']}".encode()).hexdigest()[:48] for r in plan]
base=f"https://api.cloudflare.com/client/v4/accounts/{os.environ['CLOUDFLARE_ACCOUNT_ID']}/vectorize/v2/indexes/blog-search-v1";headers={'Authorization':'Bearer '+os.environ['CLOUDFLARE_REGISTRAR_TOKEN'],'Content-Type':'application/json'}
def req(u,data,headers=headers):
 return json.load(urllib.request.urlopen(urllib.request.Request(u,data=json.dumps(data).encode(),headers=headers),timeout=45))
r=req(base+'/get_by_ids',{'ids':ids});assert r['success'];rows=[{'id':x['id'],'metadata':x.get('metadata',{})} for x in r['result']];(out/'semantic-readback.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2))
queries=['GPUWorks dGPU 显存配额 NAT Mac 算力池']
reports=[]
for slug,q in (zip(slugs,queries) if len(rows)==2 else []):
 a=req('https://blog.mushroom.cv/api/search',{'query':q},{'Content-Type':'application/json','User-Agent':'Mycelium-Publish-Verification'});reports.append({'slug':slug,'query':q,'found':slug in json.dumps(a),'response':a})
(out/'semantic-search-final.json').write_text(json.dumps(reports,ensure_ascii=False,indent=2));s={'recordsAccepted':2,'readbackVerified':len(rows)==2,'publicSearchVerified':bool(reports) and all(x['found'] for x in reports),'status':'verified' if len(rows)==2 and bool(reports) and all(x['found']for x in reports) else 'propagation-pending','checkedAt':datetime.datetime.now(datetime.timezone.utc).isoformat()};(out/'semantic-status.json').write_text(json.dumps(s,indent=2));print(json.dumps(s))
