---
name: lean-cost
description: >-
  Runs token-efficient cloud and CI cost reviews for Cursor and Codex.
  Inventories always-on compute, unpinned latest images, large artifacts,
  and chatty logging in local IaC and workflows, then reports compact
  spend cuts. Use when the user asks for cloud cost, token waste, CI
  minutes, or cheaper infrastructure. Do not use for attacking billing
  APIs or other accounts.
license: MIT
metadata:
  version: "1.0.0"
---

# Lean Cost

Spend cuts from **local Terraform, compose, and workflows**. No live billing scrape unless the user already exported a CSV.

Let `SKILL_ROOT` be the folder that contains this `SKILL.md`. Prefer `python3`; on Windows use `py -3`.

```text
python3 "$SKILL_ROOT/scripts/lean_cost.py" spend .
python3 "$SKILL_ROOT/scripts/lean_cost.py" trim --chars 2500 path/to/out.txt
```

## Mode

Default `lean`.

| Mode | Budget |
|------|--------|
| `lean` | `spend` + up to 8 slices; [references/waste.md](references/waste.md); ≤6 findings |
| `standard` | up to 16 slices; ≤10 findings |
| `deep` | still no invoice dump; ≤16 findings |

## Workflow

1. Run `spend`. Queue `instance_type` large, `count` high, `latest` images, artifacts always uploaded, debug logging on.
2. Slice-read. Cap quotes at 12 lines.
3. Report smaller size, schedule, or drop. Stop unless asked to patch.

## Hard rules

- This workspace's config. Do not query another tenant's billing.
- If they paste a cost CSV, `trim` it; do not keep the whole file in context.

## Report template

```markdown
## Lean-cost (`<mode>`)

**Stack:** <tf/compose/ci> | **Budget:** files_read=<n>

| Sev | Location | Issue | Fix |
|-----|----------|-------|-----|
| MED | file:line | always-on large instance | smaller type or stop schedule |
```
