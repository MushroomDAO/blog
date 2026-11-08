# Local fixture verification

Source: https://github.com/anthropics/claude-cookbooks
Commit: ce8b2629efe8b24048b127b4c79af1e9cbab93d4

The archived smoke script expects the pinned managed_agents directory at /tmp/anthropic-dreaming-research/managed_agents. Create an isolated Python3.12 virtual environment with anthropic2.x, nbformat and nbclient (resolved versions are in test-requirements.txt), then run dreaming-local-smoke.py. It imports actual upstream helper and nightly modules. NotebookClient is replaced; no notebook code cells are executed, credentials are cleared inside mocked nightly runs, and all filesystem fixtures live in TemporaryDirectory.

Nine grouped checks passed; see JSON and log. Tests establish selected helper and state-transition behavior, not cloud API compatibility, memory factual quality, cost, speed, completeness under concurrent updates or a security audit. In-flight-session loss follows static inspection of the notebook's created_at_gte filter plus status skip and the nightly cursor; it was not tested against a live API.
