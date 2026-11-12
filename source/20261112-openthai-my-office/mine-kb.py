from pathlib import Path
from mempalace.miner import mine
p=Path('/Users/jason/.claude/projects/-Users-jason-Dev-mycelium-blog/memory');slugs=['openthai-ocr-markdown-thai-document-engineering','my-office-claude-code-session-dashboard-guide'];mine(str(p),'/Users/jason/.mempalace/palace',wing_override='blog',agent='codex',respect_gitignore=False,files=[p/('project_'+s+'.md')for s in slugs])
