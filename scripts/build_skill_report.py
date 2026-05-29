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


def parse_registry(path: Path):
    """Parse the repo's simple registry/skill-index.yaml without extra deps."""
    if not path.exists():
        return []

    skills = []
    current = None
    for line in path.read_text(encoding='utf-8', errors='ignore').splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith('#') or stripped == 'skills:':
            continue
        if stripped.startswith('- '):
            if current:
                skills.append(current)
            current = {}
            stripped = stripped[2:]
        if current is not None and ':' in stripped:
            key, value = stripped.split(':', 1)
            current[key.strip()] = value.strip().strip('"')
    if current:
        skills.append(current)

    return [skill for skill in skills if skill.get('name')]


def rows_from_registry(root: Path):
    rows = []
    for skill in parse_registry(root / 'registry' / 'skill-index.yaml'):
        rows.append(
            {
                'name': skill.get('name', ''),
                'domain': skill.get('domain', ''),
                'status': skill.get('status', ''),
                'version': skill.get('version', ''),
                'source_path': skill.get('source_path', ''),
            }
        )
    rows.sort(key=lambda x: x['name'])
    return rows


def rows_from_skill_files(root: Path):
    rows = []
    for f in root.rglob('SKILL.md'):
        meta = parse_frontmatter(f.read_text(encoding='utf-8', errors='ignore'))
        if meta.get('name'):
            rows.append(
                {
                    'name': meta.get('name', ''),
                    'domain': '',
                    'status': '',
                    'version': meta.get('version', ''),
                    'source_path': str(f.relative_to(root)),
                }
            )
    rows.sort(key=lambda x: x['name'])
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--root', default='.')
    ap.add_argument('--out', default='reports/skill-report.md')
    args = ap.parse_args()

    root = Path(args.root).resolve()
    out = (root / args.out).resolve()

    source_label = 'registry/skill-index.yaml'
    rows = rows_from_registry(root)
    if not rows:
        source_label = 'local SKILL.md scan'
        rows = rows_from_skill_files(root)

    md = []
    md.append('# Skill Asset Report')
    md.append('')
    md.append(f'Generated: {datetime.utcnow().isoformat()}Z')
    md.append('')
    md.append(f'Source: `{source_label}`')
    md.append('')
    md.append(f'Total skills: {len(rows)}')
    md.append('')
    md.append('| name | domain | status | version | source_path |')
    md.append('|---|---|---|---:|---|')
    for row in rows:
        md.append(
            f"| {row['name']} | {row['domain']} | {row['status']} | {row['version']} | `{row['source_path']}` |"
        )

    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text('\n'.join(md) + '\n', encoding='utf-8')
    print(f'Wrote {out}')


if __name__ == '__main__':
    main()
