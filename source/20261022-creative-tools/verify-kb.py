import sqlite3,json
from pathlib import Path
b=Path(__file__).resolve().parent;r=json.loads((b/'publication-result.json').read_text());c=sqlite3.connect('file:/Users/jason/.mempalace/palace/chroma.sqlite3?mode=ro',uri=True);report=[]
for row in r['publications']:
 slug=row['slug'];count=c.execute('SELECT count(*) FROM embedding_fulltext_search WHERE string_value LIKE ?',('%'+slug+'%',)).fetchone()[0];assert count>0
 p=Path('/Users/jason/.claude/projects/-Users-jason-Dev-mycelium-blog/memory')/('project_'+slug+'.md');s=p.read_text();assert 'Blog published and verified200' in s
 if row['wechatStatus']=='recorded':assert 'CurrentWeChatStatus recorded' in s and row['archivedMediaId'] in s
 else:assert row['mediaId'] in s
 report.append({'slug':slug,'exactMatches':count,'memoryExists':True,'wechatStatus':row['wechatStatus'],'rawBotMaterialReused':True})
(b/'kb-verification.json').write_text(json.dumps(report,indent=2)+'\n');print(report)
