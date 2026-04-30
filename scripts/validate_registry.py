#!/usr/bin/env python3
import argparse
import re
from pathlib import Path

STATUSES = {'draft', 'active', 'deprecated', 'archived'}
SEMVER_RE = re.compile(r"^\d+\.\d+\.\d+(?:[-+][0-9A-Za-z.-]+)?$")


def parse_registry(path: Path):
    rows = []
    if not path.exists():
        return rows
    cur = None
    for raw in path.read_text(encoding='utf-8', errors='ignore').splitlines():
        s = raw.strip()
        if s.startswith('- '):
            if cur:
                rows.append(cur)
            cur = {}
            s = s[2:]
            if ':' in s:
                k, v = s.split(':', 1)
                cur[k.strip()] = v.strip()
        elif cur is not None and ':' in s:
            k, v = s.split(':', 1)
            cur[k.strip()] = v.strip()
    if cur:
        rows.append(cur)
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--registry', default='registry/skill-index.yaml')
    args = ap.parse_args()

    rows = parse_registry(Path(args.registry))
    errs = []
    names = {}
    canon = {}
    for r in rows:
        name = r.get('name', '')
        if not name:
            errs.append('entry missing name')
            continue
        if name in names:
            errs.append(f'duplicate name in registry: {name}')
        names[name] = 1
        v = r.get('version', '')
        if not SEMVER_RE.match(v):
            errs.append(f'{name}: invalid semver {v}')
        st = r.get('status', '')
        if st not in STATUSES:
            errs.append(f'{name}: invalid status {st}')
        key = name  # can be expanded to intent_key later
        if r.get('canonical', '').lower() == 'true':
            canon[key] = canon.get(key, 0) + 1

    for k, c in canon.items():
        if c > 1:
            errs.append(f'{k}: canonical appears {c} times')

    if errs:
        print('FAIL: registry schema validation')
        for e in errs:
            print('FAIL -', e)
        return 2
    print(f'PASS: registry valid entries={len(rows)}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
