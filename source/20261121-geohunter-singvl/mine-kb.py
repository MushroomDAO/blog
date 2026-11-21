from pathlib import Path
import json
from mempalace.miner import mine
p=Path('/Users/jason/.claude/projects/-Users-jason-Dev-mycelium-blog/memory');slugs=json.loads(Path(__file__).with_name('slugs.json').read_text());mine(str(p),'/Users/jason/.mempalace/palace',wing_override='blog',agent='codex',respect_gitignore=False,files=[p/f'project_{s}.md'for s in slugs]+[p/'feedback_publication_three_piece_definition.md'])
