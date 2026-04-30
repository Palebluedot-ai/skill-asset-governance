#!/usr/bin/env python3
import argparse
import subprocess
from pathlib import Path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--to', required=True, help='commit sha to restore registry from')
    ap.add_argument('--path', default='registry/skill-index.yaml')
    args = ap.parse_args()

    target = args.path
    content = subprocess.check_output(['git', 'show', f'{args.to}:{target}'], text=True)
    p = Path(target)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding='utf-8')
    print(f'restored {target} from {args.to}')


if __name__ == '__main__':
    main()
