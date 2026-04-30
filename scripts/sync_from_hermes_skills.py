#!/usr/bin/env python3
import argparse
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


def infer_domain(path: Path, source_root: Path) -> str:
    rel = path.relative_to(source_root)
    return rel.parts[0] if len(rel.parts) > 1 else "uncategorized"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--source', required=True, help='Hermes skills dir, e.g. ~/.hermes/skills')
    ap.add_argument('--out', required=True, help='Output index yaml path')
    args = ap.parse_args()

    source = Path(args.source).expanduser().resolve()
    out = Path(args.out).resolve()

    skills = []
    for f in sorted(source.rglob('SKILL.md')):
        txt = f.read_text(encoding='utf-8', errors='ignore')
        meta = parse_frontmatter(txt)
        name = meta.get('name')
        if not name:
            continue
        skills.append({
            'name': name,
            'domain': infer_domain(f, source),
            'status': 'active',
            'version': meta.get('version', '0.0.0'),
            'owner': 'curator',
            'canonical': True,
            'source_path': str(f),
        })

    lines = ['skills:']
    for s in skills:
        lines += [
            f"  - name: {s['name']}",
            f"    domain: {s['domain']}",
            f"    status: {s['status']}",
            f"    version: {s['version']}",
            f"    owner: {s['owner']}",
            f"    canonical: {str(s['canonical']).lower()}",
            f"    source_path: {s['source_path']}",
            ''
        ]

    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text('\n'.join(lines).rstrip() + '\n', encoding='utf-8')
    print(f'synced {len(skills)} skills -> {out}')


if __name__ == '__main__':
    main()
