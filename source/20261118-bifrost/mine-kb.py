from pathlib import Path
from mempalace.miner import mine
import json
p=Path('/Users/jason/.claude/projects/-Users-jason-Dev-mycelium-blog/memory');slugs=json.loads(Path(__file__).with_name('slugs.json').read_text());mine(str(p),'/Users/jason/.mempalace/palace',wing_override='blog',agent='codex',respect_gitignore=False,files=[p/('project_'+s+'.md')for s in slugs])
