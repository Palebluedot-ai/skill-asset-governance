#!/usr/bin/env python3
import argparse
from datetime import date, datetime
from pathlib import Path


def parse_waivers(path: Path):
    if not path.exists():
        return []
    lines = path.read_text(encoding='utf-8', errors='ignore').splitlines()
    items, cur = [], None
    for ln in lines:
        s = ln.strip()
        if s.startswith('- '):
            if cur:
                items.append(cur)
            cur = {}
            s = s[2:]
            if ':' in s:
                k, v = s.split(':', 1)
                cur[k.strip()] = v.strip().strip('"')
        elif cur is not None and ':' in s:
            k, v = s.split(':', 1)
            cur[k.strip()] = v.strip().strip('"')
    if cur:
        items.append(cur)
    return items


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--waivers', default='policies/waivers.yaml')
    ap.add_argument('--warn-days', type=int, default=7)
    ap.add_argument('--fail-on-expired', action='store_true')
    args = ap.parse_args()

    waivers = parse_waivers(Path(args.waivers))
    today = date.today()
    expired, soon = [], []

    for w in waivers:
        exp = w.get('expires_on')
        if not exp:
            continue
        try:
            d = datetime.strptime(exp, '%Y-%m-%d').date()
        except ValueError:
            expired.append((w, f'invalid_date:{exp}'))
            continue
        delta = (d - today).days
        if delta < 0:
            expired.append((w, f'expired {abs(delta)}d ago'))
        elif delta <= args.warn_days:
            soon.append((w, f'expiring in {delta}d'))

    if expired:
        print('FAIL: expired/invalid waivers found')
        for w, msg in expired:
            print(f"- {w.get('id','(no-id)')} target={w.get('target','')} {msg}")
    if soon:
        print('WARN: waivers nearing expiry')
        for w, msg in soon:
            print(f"- {w.get('id','(no-id)')} target={w.get('target','')} {msg}")
    if not expired and not soon:
        print('PASS: waiver expiry check clean')

    if expired and args.fail_on_expired:
        return 2
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
