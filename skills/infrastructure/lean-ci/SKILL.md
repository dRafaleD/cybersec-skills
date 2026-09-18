---
name: lean-ci
description: >-
  Runs token-efficient defensive CI and supply-chain reviews for Cursor and
  Codex. Inventories GitHub Actions and GitLab CI for write-all permissions,
  unpinned actions, pull_request_target, and secret echoes, then reports
  compact pipeline hardening. Use when the user asks for CI security, GitHub
  Actions review, supply chain, unpinned actions, or workflow permissions.
  Do not use for exploiting CI, stealing secrets from other repos, or
  poisoning registries.
license: MIT
metadata:
  version: "1.0.0"
---

# Lean CI

Defensive pipeline review of **workflow files in this workspace**. Scripts list risky jobs; you patch only when asked.

Let `SKILL_ROOT` be the folder that contains this `SKILL.md`. Prefer `python3`; on Windows use `py -3`.

```text
python3 "$SKILL_ROOT/scripts/lean_ci.py" workflows .
python3 "$SKILL_ROOT/scripts/lean_ci.py" trim --chars 2500 path/to/out.txt
```

Do not dump `npm audit` JSON or lockfiles. Do not attack GitHub/GitLab.

## Mode

Default `lean`.

| Mode | Budget |
|------|--------|
| `lean` | `workflows` + up to 8 slices; [references/actions.md](references/actions.md); ≤6 findings |
| `standard` | + [references/pins.md](references/pins.md); up to 16 slices; ≤10 findings |
| `deep` | needed refs only; ≤16 findings |

## Workflow

1. Run `workflows`. Queue `write-all`, `pull_request_target`, unpinned `uses:`, `echo` of secrets, checkout of untrusted PRs with secrets.
2. Slice-read the workflow YAML.
3. Report least privilege, pin-to-SHA, and fork isolation. Stop unless asked to patch.

## Hard rules

- This repo's pipelines only. No abusing `pull_request_target` as an attack demo.
- No payload in `run:` blocks. Describe the unsafe pattern and the safer YAML.
- Cap quotes at 12 lines.

## Report template

```markdown
## Lean-ci (`<mode>`)

**System:** GitHub Actions / GitLab CI | **Budget:** files_read=<n>

| Sev | Location | Issue | Fix |
|-----|----------|-------|-----|
| HIGH | file:line | pull_request_target + secrets | split jobs; do not share secrets with fork PRs |
```
