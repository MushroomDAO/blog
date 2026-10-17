#!/usr/bin/env python3
"""Build a root-key IndexNow payload offline; performs no network requests."""
import argparse
import json
import re
from pathlib import Path
from urllib.parse import urlsplit


def build_payload(host, key, urls):
    if not re.fullmatch(r'[a-z0-9](?:[a-z0-9.-]*[a-z0-9])?', host):
        raise ValueError('host must be a lowercase hostname without scheme, path or port')
    if any(not label or len(label) > 63 or label.startswith('-') or label.endswith('-')
           for label in host.split('.')) or len(host) > 253:
        raise ValueError('invalid hostname labels')
    if not re.fullmatch(r'[A-Za-z0-9-]{8,128}', key):
        raise ValueError('key must contain 8–128 letters, digits or dashes')
    result = []
    for value in urls:
        if not value or value != value.strip() or any(c.isspace() or ord(c) < 32 for c in value):
            raise ValueError('URLs must be nonempty and have no whitespace or control characters')
        u = urlsplit(value)
        if u.scheme not in ('https', 'http') or u.netloc != host or u.fragment:
            raise ValueError('URLs must use http(s), exactly match host, and have no credentials, port or fragment')
        if value not in result:
            result.append(value)
    if not 1 <= len(result) <= 10000:
        raise ValueError('provide 1–10000 distinct URLs per batch')
    return {'host': host, 'key': key, 'keyLocation': f'https://{host}/{key}.txt', 'urlList': result}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--host', required=True)
    p.add_argument('--key', required=True)
    p.add_argument('--output', type=Path)
    p.add_argument('urls', nargs='+')
    args = p.parse_args()
    try:
        text = json.dumps(build_payload(args.host, args.key, args.urls), ensure_ascii=False, indent=2) + '\n'
    except ValueError as e:
        p.error(str(e))
    if args.output:
        args.output.write_text(text, encoding='utf-8')
    else:
        print(text, end='')


if __name__ == '__main__':
    main()
