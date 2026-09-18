---
name: lean-iot
description: >-
  Runs token-efficient defensive IoT and firmware-config reviews for Cursor
  and Codex. Inventories default passwords, telnet, open MQTT, and debug
  listeners in local device config, then reports compact hardening fixes.
  Use when the user asks for IoT security, firmware config, MQTT, default
  credentials, or embedded debug ports. Do not use for device exploits,
  UART attacks, or unauthorized firmware dumps.
license: MIT
metadata:
  version: "1.0.0"
---

# Lean IoT

Defensive review of **device config the user already has**. Scripts list default secrets and debug listeners; you do not flash or attack devices.

Let `SKILL_ROOT` be the folder that contains this `SKILL.md`. Prefer `python3`; on Windows use `py -3`.

```text
python3 "$SKILL_ROOT/scripts/lean_iot.py" device .
python3 "$SKILL_ROOT/scripts/lean_iot.py" trim --chars 2500 path/to/out.txt
```

## Mode

Default `lean`.

| Mode | Budget |
|------|--------|
| `lean` | `device` + up to 8 slices; [references/defaults.md](references/defaults.md); ≤6 findings |
| `standard` | up to 16 slices; ≤10 findings |
| `deep` | needed refs only; ≤16 findings |

## Workflow

1. Run `device`. Queue `admin/admin`, telnet, MQTT without auth, serial debug, `0.0.0.0` management ports.
2. Slice-read the matching conf. Cap quotes at 12 lines.
3. Report disable-debug / unique password / TLS MQTT. Stop unless asked to patch.

## Hard rules

- Config in this workspace only. No scanning random cameras or shodan.
- No UART/JTAG attack steps, no firmware unpack recipes.
- Default passwords: report the **kind**, not a live unique password if present (`[REDACTED]`).

## Report template

```markdown
## Lean-iot (`<mode>`)

**Device/tree:** <folder> | **Budget:** files_read=<n>

| Sev | Location | Issue | Fix |
|-----|----------|-------|-----|
| HIGH | file:line | telnet enabled | disable; SSH with keys |
```
