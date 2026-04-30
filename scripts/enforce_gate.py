#!/usr/bin/env python3
import argparse
import json
from pathlib import Path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--lint-json', default='reports/lint-report.json')
    ap.add_argument('--fail-on-warn', action='store_true')
    args = ap.parse_args()

    p = Path(args.lint_json)
    if not p.exists():
        print('INFO: lint report missing; gate skipped')
        return 0

    data = json.loads(p.read_text(encoding='utf-8'))
    status = data.get('status', 'UNKNOWN')
    fail = data.get('fail', [])
    warn = data.get('warn', [])

    print(f'gate-check: status={status} fail={len(fail)} warn={len(warn)}')
    if fail:
        print('BLOCK: FAIL items present')
        return 2
    if args.fail_on_warn and warn:
        print('BLOCK: WARN items present and fail-on-warn enabled')
        return 3
    print('PASS: gate passed')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
