from pathlib import Path
from mempalace.miner import mine
p=Path('/Users/jason/.claude/projects/-Users-jason-Dev-mycelium-blog/memory');slugs=['praxis-1-open-world-action-model-engineering','beeftv-local-creative-workbench-license-guide','notrat_source_availability'];mine(str(p),'/Users/jason/.mempalace/palace',wing_override='blog',agent='codex',respect_gitignore=False,files=[p/('project_'+s+'.md')for s in slugs])
