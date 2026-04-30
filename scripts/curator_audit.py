#!/usr/bin/env python3
import argparse
import json
from datetime import datetime
from pathlib import Path


def parse_registry(path: Path):
    rows = []
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
    return {r.get('name'): r for r in rows if r.get('name')}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--before', required=True)
    ap.add_argument('--after', required=True)
    ap.add_argument('--out', default='reports/curator-run-latest.md')
    ap.add_argument('--json-out', default='reports/curator-run-latest.json')
    args = ap.parse_args()

    b = parse_registry(Path(args.before))
    a = parse_registry(Path(args.after))

    added = sorted(set(a) - set(b))
    removed = sorted(set(b) - set(a))
    changed = []
    for k in sorted(set(a) & set(b)):
        if a[k] != b[k]:
            changed.append(k)

    md = []
    md.append('# Curator Run Audit')
    md.append('')
    md.append(f'Generated: {datetime.utcnow().isoformat()}Z')
    md.append(f'Before count: {len(b)}')
    md.append(f'After count: {len(a)}')
    md.append('')
    md.append('## Added')
    md += [f'- {x}' for x in added] or ['- (none)']
    md.append('')
    md.append('## Removed')
    md += [f'- {x}' for x in removed] or ['- (none)']
    md.append('')
    md.append('## Changed')
    md += [f'- {x}' for x in changed] or ['- (none)']

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text('\n'.join(md) + '\n', encoding='utf-8')

    j = {
        'added': added,
        'removed': removed,
        'changed': changed,
        'before_count': len(b),
        'after_count': len(a),
    }
    Path(args.json_out).write_text(json.dumps(j, indent=2), encoding='utf-8')
    print(f'wrote {out} and {args.json_out}')


if __name__ == '__main__':
    main()
