from pathlib import Path
import os,json,hashlib,urllib.request,datetime
slug="anthropic-dreaming-dynamic-workflow-memory-review"
out=Path(__file__).parent
plan=json.loads(out.joinpath("semantic-plan.json").read_text())["changed"]
assert len(plan)==2 and all(r["article_id"]==slug for r in plan)
ids=[hashlib.sha256(f"{r['article_id']}:{r['language']}:{r['content_hash']}".encode()).hexdigest()[:48] for r in plan]
base=f"https://api.cloudflare.com/client/v4/accounts/{os.environ['CLOUDFLARE_ACCOUNT_ID']}/vectorize/v2/indexes/blog-search-v1"
headers={"Authorization":"Bearer "+os.environ["CLOUDFLARE_REGISTRAR_TOKEN"],"Content-Type":"application/json"}
def get(url,data=None,headers=headers):
 req=urllib.request.Request(url,data=None if data is None else json.dumps(data).encode(),headers=headers)
 return json.load(urllib.request.urlopen(req,timeout=45))
r=get(base+"/get_by_ids",{"ids":ids});assert r["success"]
rows=[{"id":v["id"],"metadata":v.get("metadata",{})} for v in r["result"]]
out.joinpath("semantic-readback.json").write_text(json.dumps(rows,ensure_ascii=False,indent=2))
info=get(base+"/info");out.joinpath("semantic-index-info.json").write_text(json.dumps(info,indent=2))
search=get("https://blog.mushroom.cv/api/search",{"query":"Anthropic dreaming dynamic workflow transcript memory analyzer organizer"},{"Content-Type":"application/json","User-Agent":"Mycelium-Publish-Verification"})
out.joinpath("semantic-search-final.json").write_text(json.dumps(search,ensure_ascii=False,indent=2))
hit=slug in json.dumps(search)
status={"recordsAccepted":2,"manifestUpdated":True,"readbackVerified":len(rows)==2,"publicSearchVerified":hit,"status":"verified" if len(rows)==2 and hit else "propagation-pending","checkedAt":datetime.datetime.now(datetime.timezone.utc).isoformat()}
out.joinpath("semantic-status.json").write_text(json.dumps(status,indent=2));print(json.dumps(status))
