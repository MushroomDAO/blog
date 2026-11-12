from pathlib import Path
import json,sqlite3
out=Path(__file__).parent;rs=json.loads((out/'publication-results.json').read_text());c=sqlite3.connect('file:/Users/jason/.mempalace/palace/chroma.sqlite3?mode=ro',uri=True);reports=[]
for r in rs:
 p=Path('/Users/jason/.claude/projects/-Users-jason-Dev-mycelium-blog/memory')/('project_'+r['slug']+'.md');rows=c.execute("SELECT f.c0 FROM embeddings e JOIN embedding_fulltext_search_content f ON f.rowid=e.id JOIN embedding_metadata m ON m.id=e.id WHERE m.key='source_file' AND m.string_value=?",(str(p),)).fetchall();text='\n'.join(x[0]for x in rows);checks={'url':r['blogUrl']in text,'wechatStatus':('WeChat: '+r['wechatStatus'])in text,'semantic':('Semantic: '+json.loads((out/'semantic-status.json').read_text())['status'])in text}
 if r['mediaId']:checks['mediaId']=r['mediaId']in text
 else:checks['error']=bool(r['wechatError'])and r['wechatError']in text
 assert rows and all(checks.values()),checks
 reports.append({'slug':r['slug'],'rows':len(rows),'checks':checks})
p=Path('/Users/jason/.claude/projects/-Users-jason-Dev-mycelium-blog/memory/project_notrat_source_availability.md');rows=c.execute("SELECT f.c0 FROM embeddings e JOIN embedding_fulltext_search_content f ON f.rowid=e.id JOIN embedding_metadata m ON m.id=e.id WHERE m.key='source_file' AND m.string_value=?",(str(p),)).fetchall();text='\n'.join(x[0] for x in rows);assert rows and 'https://notra.cn/docs' in text and 'closed' in text.lower();reports.append({'project':'Notrat','rows':len(rows),'closedSourceDecisionVerified':True})
(out/'kb-readback.json').write_text(json.dumps(reports,indent=2));print(json.dumps(reports))
