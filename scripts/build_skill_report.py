#!/usr/bin/env python3
import argparse
from datetime import datetime
from pathlib import Path


def parse_frontmatter(text: str):
    if not text.startswith('---\n'):
        return {}
    end = text.find('\n---\n', 4)
    if end == -1:
        return {}
    lines = text[4:end].strip().splitlines()
    d = {}
    for line in lines:
        if ':' in line and not line.strip().startswith('#'):
            k, v = line.split(':', 1)
            d[k.strip()] = v.strip().strip('"')
    return d


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--root', default='.')
    ap.add_argument('--out', default='reports/skill-report.md')
    args = ap.parse_args()

    root = Path(args.root).resolve()
    out = (root / args.out).resolve()

    rows = []
    for f in root.rglob('SKILL.md'):
        meta = parse_frontmatter(f.read_text(encoding='utf-8', errors='ignore'))
        if meta.get('name'):
            rows.append((meta.get('name', ''), meta.get('version', ''), str(f.relative_to(root))))

    rows.sort(key=lambda x: x[0])

    md = []
    md.append('# Skill Asset Report')
    md.append('')
    md.append(f'Generated: {datetime.utcnow().isoformat()}Z')
    md.append('')
    md.append(f'Total skills: {len(rows)}')
    md.append('')
    md.append('| name | version | path |')
    md.append('|---|---:|---|')
    for n, v, p in rows:
        md.append(f'| {n} | {v} | `{p}` |')

    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text('\n'.join(md) + '\n', encoding='utf-8')
    print(f'Wrote {out}')


if __name__ == '__main__':
    main()
