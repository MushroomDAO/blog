"""Recompute the pinned official directory inventory; does not execute skills."""
import json
from pathlib import Path
root = Path(__file__).resolve().parent
skills = json.loads((root / 'skills.json').read_text())
agents = json.loads((root / 'agents.json').read_text())
playbooks = json.loads((root / 'skills-poteto-mode-playbooks.json').read_text())
manifest = json.loads((root / 'upstream-plugin.json').read_text())
names = {entry['name'] for entry in skills if entry['type'] == 'dir'}
report = {
    'version': manifest['version'],
    'revision': json.loads((root / 'revision.json').read_text())['revision'],
    'skills': len(names),
    'principles': sum(name.startswith('principle-') for name in names),
    'otherSkills': sum(not name.startswith('principle-') for name in names),
    'subagents': sum(entry['name'].endswith('.md') for entry in agents),
    'playbooks': sum(entry['name'].endswith('.md') for entry in playbooks),
    'catchupExists': 'catchup' in names,
    'ketchupExists': 'ketchup' in names,
    'scope': 'Static pinned repository inventory, not agent execution benchmark',
}
assert report['skills'] == 58 and report['principles'] == 24
assert report['subagents'] == 2 and report['playbooks'] == 23
assert not report['catchupExists'] and report['ketchupExists']
(root / 'inventory-verification.json').write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps(report))
