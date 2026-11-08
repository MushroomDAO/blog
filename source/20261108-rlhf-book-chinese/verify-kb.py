from pathlib import Path
import json,sqlite3
out=Path(__file__).resolve().parent
result=json.loads((out/'publication-result.json').read_text())
source=Path('/Users/jason/.claude/projects/-Users-jason-Dev-mycelium-blog/memory')/f"project_{result['slug']}.md"
con=sqlite3.connect('file:/Users/jason/.mempalace/palace/chroma.sqlite3?mode=ro',uri=True)
rows=con.execute("SELECT f.c0 FROM embeddings e JOIN embedding_fulltext_search_content f ON f.rowid=e.id JOIN embedding_metadata m ON m.id=e.id WHERE m.key='source_file' AND m.string_value=?",(str(source),)).fetchall()
text='\n'.join(row[0]for row in rows)
checks={'blogUrlPresent':result['blogUrl']in text,'mediaIdPresent':result['mediaId']in text,'semanticStatusPresent':('Semantic: '+json.loads((out/'semantic-status.json').read_text())['status'])in text}
assert all(checks.values()),checks
report={'sourceFile':str(source),'rows':len(rows),**checks}
(out/'kb-readback.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report))
