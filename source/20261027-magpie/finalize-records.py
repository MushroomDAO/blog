from pathlib import Path
import json,datetime
root=Path(__file__).resolve().parents[2];here=Path(__file__).resolve().parent;job=Path('/Users/jason/.heinu1-bot/jobs/6d943056-5f06-4715-b922-5abf575fb4c6')
public=json.loads((here/'public-verification.json').read_text());w=json.loads((here/'wechat-verification.json').read_text())['drafts'][0]
assert w['fullTextMatches'] and w['imageIdentitiesMatch'] and w['coverMatches']
old=json.loads((root/'source/20261027-postiz-update/existing-wechat-status.json').read_text());assert not old['matchingRemoteDrafts'] and old['directError']==40007 and old['publishedError']==48001
results=[]
for a in public['articles']:
 slug=a['slug'];assert a['HTTP']==200 and a['carouselRank']<=8
 if slug.startswith('magpie'):
  archive=here;r={'slug':slug,'blogUrl':a['url'],'mediaId':w['mediaId'],'archivedMediaId':'','wechatStatus':'draft','wechatError':''};note='Fresh bilingual article. MIT yetone/magpie, not Apache project. Primary README and library/session docs reviewed. No installation or live-account integration test. Privacy masking off by default; telemetry configurable. Session visibility is not universal cross-agent state transfer. Library carried backups omit hooks/subagents. Both topic banners locally generated and verified; three body figures per article.'
 else:
  archive=root/'source/20261027-postiz-update';r={'slug':slug,'blogUrl':a['url'],'mediaId':'','archivedMediaId':old['archivedMediaId'],'wechatStatus':'recorded','wechatError':'旧草稿不在远程草稿箱，draft/get 返回40007；已发布列表接口返回48001，无权限核验是否已发布。保留旧凭证，不重复创建。'};note='Updated existing July24 article at same slug; no duplicate article or draft. Official dated Oct26,2024 announcement proves source already public. Employment/CMO role/coordinated-stunt intent not independently confirmed. Corrected old AGPL forbids commercial clones/internal blanket exemption and self-hosting zero-egress claims. Current39,076 stars are attention, not adoption. No deployed installation or social-account test. Three new figures and qualified topic cover.'
 (archive/'publication-result.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n');(archive/'.published').write_text(a['url']+'\n'+datetime.datetime.now(datetime.timezone.utc).isoformat()+'\n');(archive/'.state.json').write_text(json.dumps({'status':'published',**r},ensure_ascii=False,indent=2)+'\n')
 mem=Path('/Users/jason/.claude/projects/-Users-jason-Dev-mycelium-blog/memory')/('project_'+slug+'.md');mem.write_text('---\nname: '+slug+'\ndescription: Published article and current remote publication evidence\ntype: project\n---\n2026-10-28 publication; primary sources retrieved2026-10-27. Task6d943056-5f06-4715-b922-5abf575fb4c6\n'+note+'\n'+json.dumps(r,ensure_ascii=False,indent=2)+'\nEvidence: source/'+archive.name+'/\n');results.append(r)
(job/'results.json').write_text(json.dumps({'results':results},ensure_ascii=False,indent=2)+'\n');(job/'publication-result.json').write_text(json.dumps({'results':results},ensure_ascii=False,indent=2)+'\n')
kb={'title':'Magpie网关与Postiz开源事实核查','summary':'Magpie是yetone开源的多Agent模型网关，统一供应商、账号、路由和技能等配置，隐私脱敏默认关闭，会话管理不等于跨Agent无损交接。Postiz是开源社媒排期工具，2024年官方公告已公开源码，不能把近期传播故事当成首次开源。解雇关系及双方是否联合策划仍未独立核实，自托管也不意味着内容无需发送到外部平台。','tags':['开源','AI Agent','模型网关','社交媒体','事实核查'],'entities':['Magpie','yetone','Postiz','Will','Nevo David'],'content_type':'text'}
(job/'kb-record.json').write_text(json.dumps(kb,ensure_ascii=False,indent=2)+'\n');print(json.dumps(results,ensure_ascii=False))
