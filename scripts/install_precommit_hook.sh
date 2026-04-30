#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
HOOK_DIR="$ROOT_DIR/.git/hooks"
HOOK_FILE="$HOOK_DIR/pre-commit"

mkdir -p "$HOOK_DIR"
cat > "$HOOK_FILE" <<'EOF'
#!/usr/bin/env bash
set -euo pipefail
python3 scripts/scan_secrets.py --root . --staged
EOF
chmod +x "$HOOK_FILE"

echo "Installed pre-commit hook: $HOOK_FILE"
