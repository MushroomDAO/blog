import sqlite3,json
from pathlib import Path
b=Path(__file__).resolve().parent;slug='sac-little-prince-ai-game-workflow'
c=sqlite3.connect('file:/Users/jason/.mempalace/palace/chroma.sqlite3?mode=ro',uri=True)
rows=c.execute('SELECT string_value FROM embedding_fulltext_search WHERE string_value LIKE ?',('%'+slug+'%',)).fetchall();assert rows
mem=Path('/Users/jason/.claude/projects/-Users-jason-Dev-mycelium-blog/memory')/('project_'+slug+'.md');assert mem.exists() and 'Blog published and verified200' in mem.read_text()
(b/'kb-verification.json').write_text(json.dumps({'exactSlugMatches':len(rows),'memoryFile':str(mem),'memoryExists':True,'currentWeChatStatus':'draft','rawBotMaterialReused':True},indent=2));print('exact KB matches',len(rows))
