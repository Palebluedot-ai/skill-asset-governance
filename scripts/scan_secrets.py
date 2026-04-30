#!/usr/bin/env python3
import argparse
import re
import subprocess
from pathlib import Path

PATTERNS = [
    ("openai-ish sk", re.compile(r"\bsk-[A-Za-z0-9]{20,}\b")),
    ("github token", re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}\b")),
    ("aws access key", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("slack token", re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{10,}\b")),
    ("private key header", re.compile(r"-----BEGIN (RSA |OPENSSH |EC |DSA )?PRIVATE KEY-----")),
    ("generic api key assign", re.compile(r"(?i)\b(api[_-]?key|token|secret|password)\b\s*[:=]\s*['\"]?[A-Za-z0-9_\-]{16,}")),
]

IGNORE_DIRS = {".git", "node_modules", ".venv", "venv", "__pycache__"}
IGNORE_SUFFIX = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".pdf", ".zip", ".gz", ".mp3", ".mp4"}


def git_staged_files():
    out = subprocess.check_output(["git", "diff", "--cached", "--name-only"], text=True)
    return [x.strip() for x in out.splitlines() if x.strip()]


def walk_files(root: Path):
    files = []
    for p in root.rglob("*"):
        if p.is_dir():
            continue
        if any(part in IGNORE_DIRS for part in p.parts):
            continue
        if p.suffix.lower() in IGNORE_SUFFIX:
            continue
        files.append(p)
    return files


def scan_file(path: Path):
    hits = []
    try:
        txt = path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return hits
    for i, line in enumerate(txt.splitlines(), start=1):
        for name, pat in PATTERNS:
            if pat.search(line):
                hits.append((i, name, line.strip()[:200]))
    return hits


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".")
    ap.add_argument("--staged", action="store_true")
    args = ap.parse_args()

    root = Path(args.root).resolve()
    targets = []
    if args.staged:
        for rel in git_staged_files():
            p = (root / rel).resolve()
            if p.exists() and p.is_file() and p.suffix.lower() not in IGNORE_SUFFIX and not any(part in IGNORE_DIRS for part in p.parts):
                targets.append(p)
    else:
        targets = walk_files(root)

    findings = []
    for f in targets:
        hits = scan_file(f)
        for ln, kind, sample in hits:
            findings.append((str(f.relative_to(root)), ln, kind, sample))

    if findings:
        print("FAIL: possible secrets detected")
        for fp, ln, kind, sample in findings:
            print(f"- {fp}:{ln} [{kind}] {sample}")
        return 2

    print(f"PASS: no secrets detected in {len(targets)} files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
