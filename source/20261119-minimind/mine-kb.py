from pathlib import Path
from mempalace.miner import mine
p=Path('/Users/jason/.claude/projects/-Users-jason-Dev-mycelium-blog/memory')
mine(str(p),'/Users/jason/.mempalace/palace',wing_override='blog',agent='codex',respect_gitignore=False,files=[p/'project_minimind-64m-llm-training-from-scratch-guide.md'])
