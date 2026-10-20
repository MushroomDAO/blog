from pathlib import Path
import json,sqlite3
b=Path(__file__).resolve().parent;c=sqlite3.connect('file:/Users/jason/.mempalace/palace/chroma.sqlite3?mode=ro',uri=True);out=[]
for slug in ['ascii-portrait-browser-animation','everything-open-source-app-suite']:
 rows=c.execute('SELECT string_value FROM embedding_fulltext_search WHERE string_value LIKE ?',('%'+slug+'%',)).fetchall();mem=Path('/Users/jason/.claude/projects/-Users-jason-Dev-mycelium-blog/memory')/('project_'+slug+'.md');assert rows and 'Blog published and verified200'in mem.read_text();out.append({'slug':slug,'exactKBMatches':len(rows),'memoryFile':str(mem),'originalBotMaterialReused':True})
(b/'kb-verification.json').write_text(json.dumps(out,indent=2));print(out)
