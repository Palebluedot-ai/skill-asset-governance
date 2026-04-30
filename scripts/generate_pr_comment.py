#!/usr/bin/env python3
import argparse
import json
from pathlib import Path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--lint-json', default='reports/lint-report.json')
    ap.add_argument('--out', default='reports/pr-comment.md')
    args = ap.parse_args()

    p = Path(args.lint_json)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)

    if not p.exists():
        out.write_text('### Skill Governance Report\n\nNo lint report found in this run.\n', encoding='utf-8')
        print(f'wrote {out}')
        return

    data = json.loads(p.read_text(encoding='utf-8'))
    fail = data.get('fail', [])
    warn = data.get('warn', [])
    info = data.get('info', [])
    status = data.get('status', 'UNKNOWN')
    scanned = data.get('skills_scanned', 0)

    lines = []
    lines.append('<!-- skill-governance-report -->')
    lines.append('### Skill Governance Report')
    lines.append('')
    lines.append(f'- Status: **{status}**')
    lines.append(f'- Skills scanned: **{scanned}**')
    lines.append(f'- Fail: **{len(fail)}**, Warn: **{len(warn)}**, Info: **{len(info)}**')
    lines.append('')

    def top(title, arr, cap=10):
        lines.append(f'#### {title}')
        if not arr:
            lines.append('- (none)')
        else:
            for x in arr[:cap]:
                lines.append(f'- {x}')
            if len(arr) > cap:
                lines.append(f'- ... and {len(arr)-cap} more')
        lines.append('')

    top('Top FAIL', fail)
    top('Top WARN', warn)
    top('Top INFO', info)
    lines.append('> Full artifacts are attached in workflow artifacts: `skill-governance-reports`.')

    body = '\n'.join(lines) + '\n'
    out.write_text(body, encoding='utf-8')

    # fingerprint only FAIL/WARN for noise control in CI PR comment updates
    fingerprint = {
        'status': status,
        'fail': fail,
        'warn': warn,
    }
    fp_path = out.with_suffix('.fingerprint.json')
    fp_path.write_text(json.dumps(fingerprint, ensure_ascii=False, sort_keys=True, indent=2), encoding='utf-8')

    print(f'wrote {out}')
    print(f'wrote {fp_path}')


if __name__ == '__main__':
    main()
