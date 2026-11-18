from mempalace.miner import mine
from pathlib import Path
p=Path('/Users/jason/.claude/projects/-Users-jason-Dev-mycelium-blog/memory')
mine(str(p),'/Users/jason/.mempalace/palace',wing_override='blog',agent='codex',respect_gitignore=False,files=[p/'project_univer.md'])
