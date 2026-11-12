from pathlib import Path
import sqlite3,json
out=Path(__file__).parent;r=json.loads((out/'publication-result.json').read_text());p=Path('/Users/jason/.claude/projects/-Users-jason-Dev-mycelium-blog/memory')/('project_'+r['slug']+'.md')
c=sqlite3.connect('file:/Users/jason/.mempalace/palace/chroma.sqlite3?mode=ro',uri=True);rows=c.execute("SELECT f.c0 FROM embeddings e JOIN embedding_fulltext_search_content f ON f.rowid=e.id JOIN embedding_metadata m ON m.id=e.id WHERE m.key='source_file' AND m.string_value=?",(str(p),)).fetchall();text='\n'.join(x[0] for x in rows)
checks={'blogUrlPresent':r['blogUrl'] in text,'wechatStatusPresent':('WeChat: '+r['wechatStatus']) in text,'semanticStatusPresent':('Semantic: '+json.loads((out/'semantic-status.json').read_text())['status']) in text}
if r['mediaId']:checks['mediaIdPresent']=r['mediaId'] in text
else:checks['wechatErrorPresent']=r['wechatError'] in text and bool(r['wechatError'])
assert rows and all(checks.values()),checks
report={'sourceFile':str(p),'rows':len(rows),**checks};(out/'kb-readback.json').write_text(json.dumps(report,indent=2));print(json.dumps(report))
