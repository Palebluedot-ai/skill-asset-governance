#!/usr/bin/env python3
import argparse
import re
from pathlib import Path

NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def parse_frontmatter(text: str):
    if not text.startswith('---\n'):
        return {}
    end = text.find('\n---\n', 4)
    if end == -1:
        return {}
    fm = text[4:end].strip().splitlines()
    d = {}
    for line in fm:
        if ':' in line and not line.strip().startswith('#'):
            k, v = line.split(':', 1)
            d[k.strip()] = v.strip().strip('"')
    return d


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--root', default='.')
    args = ap.parse_args()
    root = Path(args.root).resolve()

    skill_files = list(root.rglob('SKILL.md'))
    if not skill_files:
        print('WARN: no SKILL.md found')
        return 0

    names = {}
    errors = []

    for f in skill_files:
        txt = f.read_text(encoding='utf-8', errors='ignore')
        meta = parse_frontmatter(txt)
        name = meta.get('name')
        desc = meta.get('description')
        ver = meta.get('version')

        if not name:
            errors.append(f'{f}: missing frontmatter name')
            continue
        if not NAME_RE.match(name):
            errors.append(f'{f}: invalid name format: {name}')
        if name in names:
            errors.append(f'{f}: duplicate name with {names[name]} -> {name}')
        else:
            names[name] = f
        if not desc:
            errors.append(f'{f}: missing description')
        if not ver:
            errors.append(f'{f}: missing version')

    if errors:
        print('FAIL')
        for e in errors:
            print('-', e)
        return 2

    print(f'OK: scanned {len(skill_files)} skills, no blocking conflicts')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
