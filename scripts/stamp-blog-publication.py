"""Record precise publication order without changing the original calendar dates."""
from datetime import datetime, timezone
from pathlib import Path
import re
import sys


def stamp_publication(text: str, at: datetime) -> str:
    if not text.startswith('---\n') or '\n---\n' not in text[4:]:
        raise ValueError('Expected YAML frontmatter')
    frontmatter, body = text[4:].split('\n---\n', 1)
    timestamp = at.astimezone(timezone.utc).isoformat(timespec='seconds').replace('+00:00', 'Z')
    line = f'lastPublishedAt: "{timestamp}"'
    if re.search(r'^lastPublishedAt:', frontmatter, re.MULTILINE):
        frontmatter = re.sub(r'^lastPublishedAt:.*$', line, frontmatter, flags=re.MULTILINE)
    else:
        frontmatter += '\n' + line
    return '---\n' + frontmatter + '\n---\n' + body


if __name__ == '__main__':
    path = Path(sys.argv[1])
    path.write_text(stamp_publication(path.read_text(), datetime.now(timezone.utc)))
