---
name: lean-privacy
description: >-
  Runs token-efficient defensive privacy and PII reviews for Cursor and Codex.
  Finds likely emails, phones, and identifier fields in local code and logs
  without printing the values, then reports compact minimization and redaction
  fixes. Use when the user asks for privacy review, PII, GDPR, logging of
  personal data, data minimization, or redaction. Do not use for collecting
  PII on people, doxxing, or building marketing lists.
license: MIT
metadata:
  version: "1.0.0"
---

# Lean Privacy

Defensive PII hygiene in **this workspace**. Scripts report kinds and locations only. Never print the values.

Let `SKILL_ROOT` be the folder that contains this `SKILL.md`. Prefer `python3`; on Windows use `py -3`.

```text
python3 "$SKILL_ROOT/scripts/lean_privacy.py" pii .
python3 "$SKILL_ROOT/scripts/lean_privacy.py" trim --chars 2500 path/to/out.txt
```

## Mode

Default `lean`.

| Mode | Budget |
|------|--------|
| `lean` | `pii` + up to 8 slices; [references/minimize.md](references/minimize.md); ≤6 findings |
| `standard` | + [references/logs.md](references/logs.md); up to 16 slices; ≤10 findings |
| `deep` | needed refs only; ≤16 findings |

## Workflow

1. Run `pii`. Treat hits as locations, not a contact list.
2. Confirm logging, analytics, and error dumps that include user fields.
3. Recommend delete/redact/minimize. Patch only if asked.

## Hard rules

- Never echo a live email, phone, national id, or card number. `[REDACTED]` only.
- Do not build dossiers or export a PII CSV.
- Cap quotes at 12 lines, and strip identifiers from quotes.

## Report template

```markdown
## Lean-privacy (`<mode>`)

**Systems:** <app/logs> | **Budget:** files_read=<n>

| Sev | Location | Kind | Fix |
|-----|----------|------|-----|
| HIGH | file:line | email in logs | drop field; hash if needed for support |
```
