from pathlib import Path
import json,sqlite3
b=Path(__file__).resolve().parent;pub=json.loads((b/'publication-result.json').read_text());c=sqlite3.connect('file:/Users/jason/.mempalace/palace/chroma.sqlite3?mode=ro',uri=True);rows=c.execute('SELECT string_value FROM embedding_fulltext_search WHERE string_value LIKE ?',('%'+pub['slug']+'%',)).fetchall();matches=[x[0]for x in rows if 'recorded only'in x[0]and pub['archivedMediaId']in x[0]];assert matches
(b/'kb-verification.json').write_text(json.dumps({'exactSlugMatches':len(rows),'currentStatusAndArchivedIdMatches':len(matches),'wechatStatus':'recorded','newDraftCreated':False,'rawBotMaterialReused':True},indent=2));print('KB status and archived ID verified',len(matches))
