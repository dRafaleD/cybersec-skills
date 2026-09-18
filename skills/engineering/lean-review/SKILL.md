---
name: lean-review
description: >-
  Runs token-efficient code reviews for Cursor and Codex. Uses git diff
  stats instead of dumping the patch, then reports compact correctness,
  test, and regression findings. Use when the user asks for a PR review,
  code review, or a cheap look at local changes. Do not use for style-only
  nits, rewriting the whole tree, or dumping the full diff into chat.
license: MIT
metadata:
  version: "1.0.0"
---

# Lean Review

Review **the change**, not the universe. Script prints diff stats; you read a few hunks; you stop.

Let `SKILL_ROOT` be the folder that contains this `SKILL.md`. Prefer `python3`; on Windows use `py -3`.

```text
python3 "$SKILL_ROOT/scripts/lean_review.py" stats .
python3 "$SKILL_ROOT/scripts/lean_review.py" trim --chars 2500 path/to/out.txt
```

Default to uncommitted+unpushed vs the repo's default branch if git works. If git fails, ask which files.

## Mode

Default `lean`.

| Mode | Budget |
|------|--------|
| `lean` | `stats` + up to 8 file slices; [references/correctness.md](references/correctness.md); ≤6 findings |
| `standard` | up to 16 slices; ≤10 findings |
| `deep` | still no whole-file tours; ≤16 findings |

## Workflow

1. Run `stats`. Rank files by churn. Skip lockfiles, generated, `node_modules`.
2. Slice-read the risky hunks (`git diff -U3 -- path` piped through `trim` if huge).
3. Report correctness, missing tests, regressions. Skip formatting nits unless they hide a bug.
4. Stop unless asked to patch.

## Hard rules

- Do not paste the full diff. Cap quotes at 12 lines.
- No drive-by refactors.
- Security issues: one line + "also run `$lean-sec`" if they are out of scope.

## Report template

```markdown
## Lean-review (`<mode>`)

**Range:** <branch or working tree> | **Files:** <n>

| Sev | Location | Issue | Fix |
|-----|----------|-------|-----|
| HIGH | file:line | nil deref on empty list | guard or test |
```
