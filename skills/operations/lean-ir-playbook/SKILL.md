---
name: lean-ir-playbook
description: >-
  Runs token-efficient incident-response playbook drafting for Cursor and
  Codex. Produces a compact first-30-minutes checklist for systems the user
  owns: isolate, preserve, rotate, communicate. Use when the user asks for
  an IR playbook, incident runbook, first response, or containment steps.
  Do not use to attack systems, wipe evidence, or bypass access controls.
license: MIT
metadata:
  version: "1.0.0"
---

# Lean IR Playbook

Authorized first-response notes. Preserve copies. No offense.

Let `SKILL_ROOT` be the folder that contains this `SKILL.md`. Prefer `python3`; on Windows use `py -3`.

```text
python3 "$SKILL_ROOT/scripts/lean_ir_playbook.py" template
python3 "$SKILL_ROOT/scripts/lean_ir_playbook.py" check /path/to/playbook.json
```

If evidence files already exist, prefer `$lean-dfir` for hashing. This skill writes the **human checklist**.

## Mode

Default `lean`.

| Mode | Budget |
|------|--------|
| `lean` | 1 incident type; [references/first30.md](references/first30.md); ≤8 steps |
| `standard` | + comms; ≤12 steps |
| `deep` | still no wipe/exploit; ≤16 steps |

## Workflow

1. Name the incident class (stolen laptop, ransomware note they already have, leaked key, phishing click).
2. Fill isolate → preserve → rotate → communicate → recover.
3. `check` JSON. Do not invent legal advice.

## Hard rules

- Systems the user administers only.
- Do not teach log wiping, anti-forensics, or offensive "to get a dump".
- Credentials: `[REDACTED]`; rotate at the provider.

## Report template

```markdown
## Lean-ir-playbook (`<mode>`)

**Incident class:** <name>

| When | Action | Owner | Done when |
|------|--------|-------|-----------|
| 0-15m | isolate host they own | on-call | NIC down / token revoked |
```
