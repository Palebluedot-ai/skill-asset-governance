#!/usr/bin/env python3
import argparse
import json
import re
from pathlib import Path
from difflib import SequenceMatcher
from datetime import date

NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
SEMVER_RE = re.compile(r"^\d+\.\d+\.\d+(?:[-+][0-9A-Za-z.-]+)?$")


def parse_frontmatter(text: str):
    if not text.startswith('---\n'):
        return {}
    end = text.find('\n---\n', 4)
    if end == -1:
        return {}
    d = {}
    for line in text[4:end].strip().splitlines():
        if ':' in line and not line.strip().startswith('#'):
            k, v = line.split(':', 1)
            d[k.strip()] = v.strip().strip('"')
    return d


def parse_simple_waivers(path: Path):
    # minimal parser for policies/waivers.yaml with flat entries
    if not path.exists():
        return []
    lines = path.read_text(encoding='utf-8', errors='ignore').splitlines()
    waivers = []
    cur = None
    for ln in lines:
        s = ln.strip()
        if s.startswith('- '):
            if cur:
                waivers.append(cur)
            cur = {}
            s = s[2:]
            if ':' in s:
                k, v = s.split(':', 1)
                cur[k.strip()] = v.strip().strip('"')
        elif cur is not None and ':' in s:
            k, v = s.split(':', 1)
            cur[k.strip()] = v.strip().strip('"')
    if cur:
        waivers.append(cur)
    return waivers


def waived(kind: str, key: str, waivers):
    today = date.today().isoformat()
    for w in waivers:
        if w.get('type') == kind and w.get('target') == key:
            exp = w.get('expires_on', '9999-12-31')
            if exp >= today:
                return True
    return False


def severity_result(fails, warns, infos):
    if fails:
        return 'FAIL', 2
    if warns:
        return 'WARN', 0
    return 'PASS', 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--source', default='~/.hermes/skills')
    ap.add_argument('--waivers', default='policies/waivers.yaml')
    ap.add_argument('--similarity-threshold', type=float, default=0.90)
    ap.add_argument('--report-json', default='')
    args = ap.parse_args()

    source = Path(args.source).expanduser().resolve()
    waivers = parse_simple_waivers(Path(args.waivers))

    skill_files = list(source.rglob('SKILL.md')) if source.exists() else []
    fails, warns, infos = [], [], []

    if not skill_files:
        fails.append(f'no SKILL.md found under source={source}')
    names = {}
    items = []
    for f in skill_files:
        meta = parse_frontmatter(f.read_text(encoding='utf-8', errors='ignore'))
        name = meta.get('name', '')
        desc = meta.get('description', '')
        ver = meta.get('version', '')
        if not name:
            fails.append(f'{f}: missing frontmatter name')
            continue
        if not NAME_RE.match(name):
            fails.append(f'{f}: invalid name format: {name}')
        if name in names:
            fails.append(f'{f}: duplicate name with {names[name]} -> {name}')
        else:
            names[name] = f
        if not desc:
            warns.append(f'{f}: missing description')
        if ver and not SEMVER_RE.match(ver):
            fails.append(f'{f}: invalid semver version={ver}')
        if not ver:
            warns.append(f'{f}: missing version')
        items.append((name, desc, str(f)))

    # intent similarity risk (name+desc)
    for i in range(len(items)):
        for j in range(i + 1, len(items)):
            a_key = items[i][0]
            b_key = items[j][0]
            a = (items[i][0] + ' ' + items[i][1]).lower()
            b = (items[j][0] + ' ' + items[j][1]).lower()
            score = SequenceMatcher(None, a, b).ratio()
            if score >= args.similarity_threshold:
                key = f'{a_key}::{b_key}'
                msg = f'high-risk intent overlap {key} score={score:.3f}'
                if waived('intent_conflict', key, waivers) or waived('intent_conflict', f'{b_key}::{a_key}', waivers):
                    infos.append('waived: ' + msg)
                else:
                    warns.append(msg)

    status, code = severity_result(fails, warns, infos)
    print(f'{status}: skills_scanned={len(items)} source={source}')
    for x in fails:
        print('FAIL -', x)
    for x in warns:
        print('WARN -', x)
    for x in infos:
        print('INFO -', x)

    if args.report_json:
        payload = {
            'status': status,
            'source': str(source),
            'skills_scanned': len(items),
            'fail': fails,
            'warn': warns,
            'info': infos,
        }
        Path(args.report_json).parent.mkdir(parents=True, exist_ok=True)
        Path(args.report_json).write_text(json.dumps(payload, indent=2), encoding='utf-8')

    return code


if __name__ == '__main__':
    raise SystemExit(main())
