"""Index the project note with current MemPalace and verify the stored source chunks."""
import os,sys,json,sqlite3
from pathlib import Path
output=os.fdopen(os.dup(1),'w')
from mempalace.miner import mine
p=Path(__file__).parent;file=Path(json.loads((p/'memory-file.json').read_text()))
mine(str(file.parent),str(Path.home()/'.mempalace/palace'),wing_override='blog',agent='codex',respect_gitignore=False,files=[file])
c=sqlite3.connect(f'file:{Path.home()}/.mempalace/palace/chroma.sqlite3?mode=ro',uri=True)
rows=c.execute("SELECT f.c0 FROM embeddings e JOIN embedding_fulltext_search_content f ON f.rowid=e.id JOIN embedding_metadata m ON m.id=e.id WHERE m.key='source_file' AND m.string_value=?",(str(file),)).fetchall()
stored='\n'.join(x[0]for x in rows)
checks={'rows':len(rows),'sourcePresent':'https://github.com/huggingface/paperswithcode'in stored,'slugPresent':'paperswithcode-open-research-catalog-engineering'in stored,'checkScopePresent':'eight cases'in stored}
assert rows and all(checks.values()),checks
(p/'kb-readback.json').write_text(json.dumps(checks,indent=2));print(json.dumps(checks),file=output)
output.flush();sys.stderr.flush();os._exit(0)
