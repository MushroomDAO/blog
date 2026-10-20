from pathlib import Path
import sqlite3,json
b=Path(__file__).resolve().parent;db=sqlite3.connect('file:/Users/jason/.mempalace/palace/chroma.sqlite3?mode=ro',uri=True);reports=[]
for slug in ['abot-recon-streaming-3d-reconstruction','openui-1-generative-ui-engineering']:
 rows=db.execute('SELECT string_value FROM embedding_fulltext_search WHERE string_value LIKE ?',('%'+slug+'%',)).fetchall();f=Path('/Users/jason/.claude/projects/-Users-jason-Dev-mycelium-blog/memory')/('project_'+slug+'.md');assert rows and 'Blog published and verified200' in f.read_text();reports.append({'slug':slug,'exactSlugMatches':len(rows),'projectMemoryExists':f.exists(),'rawBotMaterialReused':True,'currentWeChatStatus':'draft'})
(b/'kb-verification.json').write_text(json.dumps(reports,indent=2));print(reports)
