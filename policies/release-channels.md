# Release Channels Policy

## Channels

- `staging/`: draft skills and experimental curation output
- `main`: only active-ready governed assets

## Promotion rule

1. Curator operates in staging first.
2. Run lint + registry validation + conflict report.
3. Only PASS + accepted WARNs can be promoted to main.

## Blocking conditions

- duplicate skill name
- invalid semantic version
- invalid status value
- unwaived high-risk intent conflict

## Rollback

If promotion causes issues, use `scripts/rollback_registry.py --to <commit_sha>` and open a recovery PR.
