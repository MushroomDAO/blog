from pathlib import Path
import importlib.util,json,os,urllib.request,datetime
root=Path(__file__).resolve().parents[2];out=Path(__file__).parent;slug='harnessrouter-uhp-unified-agent-protocol-self-hosted-codex-claude-code'
spec=importlib.util.spec_from_file_location('audit_incremental',root/'semantic-search/scripts/incremental-index.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
records=mod.build_records(mod.load_articles([slug]));ids=[mod.bvi.make_vector_id(x['article_id'],x['language'],x['content_hash'])for x in records]
def req(url,data,headers):return json.load(urllib.request.urlopen(urllib.request.Request(url,data=json.dumps(data).encode(),headers=headers),timeout=45))
a=req(f"https://api.cloudflare.com/client/v4/accounts/{os.environ['CLOUDFLARE_ACCOUNT_ID']}/vectorize/v2/indexes/blog-search-v1/get_by_ids",{'ids':ids},{'Authorization':'Bearer '+os.environ['CLOUDFLARE_REGISTRAR_TOKEN'],'Content-Type':'application/json'});assert a['success']and len(a['result'])==2
q=req('https://blog.mushroom.cv/api/search',{'query':'HarnessRouter UHP 自托管 编码 Agent'},{'Content-Type':'application/json','User-Agent':'Mycelium-Publish-Verification'});assert slug in json.dumps(q)
r={'checkedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'vectorIds':ids,'recordsFound':2,'publicSearchFound':True,'writePerformed':False,'contentUnchanged':True};(out/'semantic-verification.json').write_text(json.dumps(r,indent=2));(out/'semantic-search.json').write_text(json.dumps(q,ensure_ascii=False,indent=2));print(r)
