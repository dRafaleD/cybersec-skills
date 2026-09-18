---
name: lean-deps
description: >-
  Runs token-efficient dependency and license reviews for Cursor and Codex.
  Summarizes direct packages from manifests without dumping lockfiles, and
  flags abandoned or high-churn security-sensitive libraries. Use when the
  user asks for dependency review, outdated packages, license scan, or
  lockfile health. Do not use for exploiting package managers or
  publishing malware to registries.
license: MIT
metadata:
  version: "1.0.0"
---

# Lean Deps

Manifest summary only. Do not `cat` lockfiles. Do not paste CVE encyclopedias.

Let `SKILL_ROOT` be the folder that contains this `SKILL.md`. Prefer `python3`; on Windows use `py -3`.

```text
python3 "$SKILL_ROOT/scripts/lean_deps.py" summary .
python3 "$SKILL_ROOT/scripts/lean_deps.py" trim --chars 2500 path/to/out.txt
```

If `$lean-sec` `deps` already ran, reuse that stdout instead of scanning twice.

## Mode

Default `lean`.

| Mode | Budget |
|------|--------|
| `lean` | `summary` + up to 8 slices; [references/health.md](references/health.md); ≤6 findings |
| `standard` | up to 16 slices; ≤10 findings |
| `deep` | still no lockfile dump; ≤16 findings |

## Workflow

1. Run `summary`. Note missing lockfiles, `latest` ranges, security-surface packages.
2. Open only the manifest, not the lockfile body.
3. Report pin/lockfile/replace. Stop unless asked to patch.

## Hard rules

- Never paste lockfiles, `npm ls`, or full audit JSON. `trim` if a scanner already ran.
- No malicious package publishing.
- Cap quotes at 12 lines.

## Report template

```markdown
## Lean-deps (`<mode>`)

**Ecosystems:** <npm/py/go> | **Direct:** <n>

| Sev | Location | Issue | Fix |
|-----|----------|-------|-----|
| MED | package.json | no lockfile | commit package-lock; npm ci |
```
