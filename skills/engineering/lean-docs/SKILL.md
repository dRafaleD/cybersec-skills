---
name: lean-docs
description: >-
  Runs token-efficient documentation gap reviews for Cursor and Codex.
  Checks README for Install, Usage, and License, and flags public APIs
  without a nearby comment, then reports compact doc patches. Use when the
  user asks to update docs, README, API documentation, or fill missing
  usage. Do not dump entire files or rewrite unrelated prose.
license: MIT
metadata:
  version: "1.0.0"
---

# Lean Docs

Find the missing section. Patch the smallest gap. Do not rewrite the novel.

Let `SKILL_ROOT` be the folder that contains this `SKILL.md`. Prefer `python3`; on Windows use `py -3`.

```text
python3 "$SKILL_ROOT/scripts/lean_docs.py" gaps .
python3 "$SKILL_ROOT/scripts/lean_docs.py" trim --chars 2500 path/to/out.txt
```

## Mode

Default `lean`.

| Mode | Budget |
|------|--------|
| `lean` | `gaps` + up to 8 slices; [references/readme.md](references/readme.md); ≤6 findings |
| `standard` | up to 16 slices; ≤10 findings |
| `deep` | still no full-file rewrite; ≤16 findings |

## Workflow

1. Run `gaps`. Queue missing README headings and exported functions with no docstring/comment.
2. Read the surrounding 20 lines. Add the smallest accurate paragraph.
3. Stop unless asked to write more.

## Hard rules

- Do not invent APIs. If you did not see it, do not document it.
- Cap quotes at 12 lines. No README dump.
- License: point at LICENSE; do not paste SPDX essays.

## Report template

```markdown
## Lean-docs (`<mode>`)

**Entry:** README.md

| Sev | Location | Gap | Fix |
|-----|----------|-----|-----|
| MED | README.md | no Install | add clone + one command |
```
