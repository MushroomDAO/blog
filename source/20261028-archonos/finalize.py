from pathlib import Path
import json,datetime
s='archonos-local-agent-workbench';p=Path(__file__).parent;job=Path('/Users/jason/.heinu1-bot/jobs/142216ae-006f-40cd-abbf-89b1c595c4bf');pub=json.loads((p/'public-verification.json').read_text());assert pub['articles'][0]['HTTP']==200
receipt=Path('pipeline/m2/output/'+s+'.json');log=Path('/tmp/archonos-m2.log').read_text()
if receipt.exists():
 assert (p/'wechat-verification.json').exists();r=json.loads(receipt.read_text());status='draft';mid=r['mediaId'];err=''
else:
 status='failed';mid='';err='公众号草稿创建失败：40164，出口IP223.206.46.98不在公众号白名单；已实际尝试一次，暂停重试。' if '40164'in log else '公众号草稿创建失败，实际错误见wechat-attempt.txt：'+log[-500:]
r={'slug':s,'blogUrl':'https://blog.mushroom.cv/blog/'+s+'/','mediaId':mid,'archivedMediaId':'','wechatStatus':status,'wechatError':err}
for f in [p/'publication-result.json',job/'publication-result.json']:f.write_text(json.dumps(r,ensure_ascii=False,indent=2))
(job/'results.json').write_text(json.dumps({'results':[r]},ensure_ascii=False,indent=2));(p/'.published').write_text(r['blogUrl']+'\n'+datetime.datetime.now(datetime.timezone.utc).isoformat());(p/'.state.json').write_text(json.dumps({'status':'published',**r},ensure_ascii=False,indent=2))
kb={'title':'ArchonOS本地多Agent工作台','summary':'ArchonOS公共版采用MIT许可，整合参谋长任务路由、本地CLI执行、逐席MCP授权、Canvas产物修订和技能改进流程。官方文档要求Node.js20及以上与Python3.10及以上，完整测试另需Bun；克隆后的目录名与文档占位地址需要修正。此次14项模块测试通过，但未验证完整部署、真实模型或工具调用，本地工作台也不等于完全离线推理。','tags':['开源','AI Agent','MCP','本地工具','工作流'],'entities':['ArchonOS','dmquant','Claude Code','Codex','Antigravity'],'content_type':'url','saved_files':[]};(job/'kb-record.json').write_text(json.dumps(kb,ensure_ascii=False,indent=2))
m=Path('/Users/jason/.claude/projects/-Users-jason-Dev-mycelium-blog/memory/project_'+s+'.md');m.write_text('---\nname: ArchonOS local agent workbench\ndescription: Published source review and14 upstream checks\ntype: project\n---\n'+json.dumps(r,ensure_ascii=False,indent=2)+'\nSource https://github.com/dmquant/archonos-pub main a4f4873a9037dc08374232b03a1f458cab3dee45. MIT version0.1.004. Only raw KB previously existed. Node20 Python3.10, full tests alsoBun. Correct clone cd to archonos-pub. Postinstall initializes and discovers configs; not executed.14 module tests passed(ledger10 canvas4), not107 or full deployment. Model CLI can send prompts remotely; optional R2 bridge also sends data, no proven E2EE or autonomous weight improvement. Original raw KB preserved, source has no downloadable bitmap imagery.\n')
print(json.dumps(r,ensure_ascii=False))
