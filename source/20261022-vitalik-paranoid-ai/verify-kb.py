import sqlite3,json
from pathlib import Path
b=Path(__file__).resolve().parent;slug='vitalik-paranoid-ai-zkapi-tor'
c=sqlite3.connect('file:/Users/jason/.mempalace/palace/chroma.sqlite3?mode=ro',uri=True)
rows=c.execute('SELECT string_value FROM embedding_fulltext_search WHERE string_value LIKE ?',('%'+slug+'%',)).fetchall();assert rows
mem=Path('/Users/jason/.claude/projects/-Users-jason-Dev-mycelium-blog/memory')/('project_'+slug+'.md');assert mem.exists() and 'Blog published and verified200' in mem.read_text()
pub=json.loads((b/'publication-result.json').read_text()); media_matches=c.execute('SELECT count(*) FROM embedding_fulltext_search WHERE string_value LIKE ?',('%'+pub['mediaId']+'%',)).fetchone()[0];assert media_matches>0
(b/'kb-verification.json').write_text(json.dumps({'exactSlugMatches':len(rows),'currentMediaIdMatches':media_matches,'memoryFile':str(mem),'memoryExists':True,'currentWeChatStatus':'draft','rawBotMaterialReused':True},indent=2));print('exact KB matches',len(rows))
