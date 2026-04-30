#!/usr/bin/env bash
set -euo pipefail

# Usage:
#   ./scripts/apply_branch_protection.sh [owner] [repo] [branch]
# Example:
#   ./scripts/apply_branch_protection.sh Palebluedot-ai skill-asset-governance main

OWNER="${1:-Palebluedot-ai}"
REPO="${2:-skill-asset-governance}"
BRANCH="${3:-main}"

if ! command -v gh >/dev/null 2>&1; then
  echo "gh is required" >&2
  exit 1
fi

if ! gh auth status >/dev/null 2>&1; then
  echo "gh auth is required" >&2
  exit 1
fi

# Note: context name should match GitHub check run name. Current workflow job is 'validate'.
gh api \
  --method PUT \
  -H "Accept: application/vnd.github+json" \
  "/repos/${OWNER}/${REPO}/branches/${BRANCH}/protection" \
  --input .github/branch-protection.sample.json

echo "Applied branch protection to ${OWNER}/${REPO}:${BRANCH}"
