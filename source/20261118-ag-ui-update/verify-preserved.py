from pathlib import Path
import urllib.request,json,re,datetime
slugs=['bifrost-ai-gateway-engineering-guide','univer-ai-native-office-sdk-spreadsheet-agent-headless-teardown','sellbird-ai-sales-agent-self-hosting-guide','amber-heart-memory-ai-companion-gateway-guide','mesh-avatar-studio-live2d-motion-engineering-guide','rust-anything-record-replay-rust-migration-guide'];rows=[]
for slug in slugs:
 u='https://blog.mushroom.cv/blog/'+slug+'/'
 r=urllib.request.urlopen(urllib.request.Request(u,headers={"User-Agent":"Mycelium-Publish-Verification","Cache-Control":"no-cache"}),timeout=45);s=r.read().decode();assert r.status==200
 rows.append({'slug':slug,'url':u,'status':r.status,'title':re.search('<title>(.*?)</title>',s)[1]})
Path(__file__).with_name('preserved-articles.json').write_text(json.dumps({'checkedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'articles':rows},ensure_ascii=False,indent=2));print(json.dumps(rows,ensure_ascii=False))
