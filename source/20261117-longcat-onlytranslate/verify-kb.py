from pathlib import Path
import sqlite3,json
out=Path(__file__).parent;results=json.loads((out/'publication-result.json').read_text())['articles'];c=sqlite3.connect('file:/Users/jason/.mempalace/palace/chroma.sqlite3?mode=ro',uri=True);reports=[]
for r in results:
 p=Path('/Users/jason/.claude/projects/-Users-jason-Dev-mycelium-blog/memory')/('project_'+r['slug']+'.md');rows=c.execute("SELECT f.c0 FROM embeddings e JOIN embedding_fulltext_search_content f ON f.rowid=e.id JOIN embedding_metadata m ON m.id=e.id WHERE m.key='source_file' AND m.string_value=?",(str(p),)).fetchall();text='\n'.join(x[0]for x in rows);checks={'blogUrlPresent':r['blogUrl']in text,'wechatStatusPresent':'WeChat: draft'in text,'mediaIdPresent':r['mediaId']in text,'semanticPresent':'Semantic: verified'in text};assert rows and all(checks.values());reports.append({'slug':r['slug'],'rows':len(rows),**checks})
(out/'kb-readback.json').write_text(json.dumps(reports,indent=2));print(json.dumps(reports))
