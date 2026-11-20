from pathlib import Path
import urllib.request,json,re,datetime,yaml
slugs=["heretic-model-behavior-editing-evaluation-guide","linger-polystrata-local-moe-agent-engineering-guide","organizing-intelligence-ai-jobs-wages-coordination","brief2mp4-agent-motion-graphics-verification-guide","clover-diffusion-llm-sft-engineering-guide","minimind-64m-llm-training-from-scratch-guide",'minimind-o-multimodal-agent-eyes-ears-voice','rumble-2-flash-small-asr-phone-call-benchmarks','cheetah-rust-local-llm-memory-loading-guide','copilotkit-frontend-stack-agents-guide','bifrost-ai-gateway-engineering-guide','univer-ai-native-office-sdk-spreadsheet-agent-headless-teardown','sellbird-ai-sales-agent-self-hosting-guide','amber-heart-memory-ai-companion-gateway-guide','mesh-avatar-studio-live2d-motion-engineering-guide','rust-anything-record-replay-rust-migration-guide'];rows=[]
for slug in slugs:
 u='https://blog.mushroom.cv/blog/'+slug+'/'
 r=urllib.request.urlopen(urllib.request.Request(u,headers={"User-Agent":"Mycelium-Publish-Verification","Cache-Control":"no-cache"}),timeout=45);s=r.read().decode();assert r.status==200
 expected=yaml.safe_load((Path(__file__).resolve().parents[2]/'src/content/blog'/f'{slug}.md').read_text().split('---')[1])['title'];actual=re.search('<title>(.*?)</title>',s)[1];assert actual==expected,(slug,actual,expected)
 rows.append({'slug':slug,'url':u,'status':r.status,'title':re.search('<title>(.*?)</title>',s)[1]})
Path(__file__).with_name('preserved-articles.json').write_text(json.dumps({'checkedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'articles':rows},ensure_ascii=False,indent=2));print(json.dumps(rows,ensure_ascii=False))
