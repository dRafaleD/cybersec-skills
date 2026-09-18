---
name: lean-a11y
description: >-
  Runs token-efficient accessibility reviews for Cursor and Codex.
  Inventories images without alt, click-only divs, and missing labels in
  local UI files, then reports compact accessible-name fixes. Use when the
  user asks for a11y, accessibility, alt text, keyboard, or ARIA review.
  Do not dump large JSX trees or rewrite the whole design system.
license: MIT
metadata:
  version: "1.0.0"
---

# Lean A11y

Accessible name and keyboard first. Scripts list likely gaps; you confirm a few components.

Let `SKILL_ROOT` be the folder that contains this `SKILL.md`. Prefer `python3`; on Windows use `py -3`.

```text
python3 "$SKILL_ROOT/scripts/lean_a11y.py" ui .
python3 "$SKILL_ROOT/scripts/lean_a11y.py" trim --chars 2500 path/to/out.txt
```

## Mode

Default `lean`.

| Mode | Budget |
|------|--------|
| `lean` | `ui` + up to 8 slices; [references/name.md](references/name.md); ≤6 findings |
| `standard` | up to 16 slices; ≤10 findings |
| `deep` | still no full CSS dump; ≤16 findings |

## Workflow

1. Run `ui`. Queue `<img>` without alt, `div onClick`, inputs without label, `target=_blank` without `rel`.
2. Slice-read. Cap quotes at 12 lines.
3. Report the smallest name/keyboard fix. Stop unless asked to patch.

## Hard rules

- Prefer native elements (`button`, `a`) over ARIA theater.
- Do not paste entire components.

## Report template

```markdown
## Lean-a11y (`<mode>`)

**UI:** <app> | **Budget:** files_read=<n>

| Sev | Location | Issue | Fix |
|-----|----------|-------|-----|
| HIGH | file:line | img with no alt | alt text or alt="" if decorative |
```
