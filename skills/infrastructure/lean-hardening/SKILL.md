---
name: lean-hardening
description: >-
  Runs token-efficient OS and container hardening reviews for Cursor and
  Codex. Inventories root processes, SSH password auth, sudo NOPASSWD, and
  missing USER in Dockerfiles from local config, then reports compact
  hardening fixes. Use when the user asks for Linux hardening, Windows
  baseline, SSH, sudo, or container user hardening. Do not use for privilege
  escalation exploits or attacking hosts you do not administer.
license: MIT
metadata:
  version: "1.0.0"
---

# Lean Hardening

Defensive baseline on **local Dockerfiles, sshd snippets, and compose** the user maintains.

Let `SKILL_ROOT` be the folder that contains this `SKILL.md`. Prefer `python3`; on Windows use `py -3`.

```text
python3 "$SKILL_ROOT/scripts/lean_hardening.py" baseline .
python3 "$SKILL_ROOT/scripts/lean_hardening.py" trim --chars 2500 path/to/out.txt
```

## Mode

Default `lean`.

| Mode | Budget |
|------|--------|
| `lean` | `baseline` + up to 8 slices; [references/host.md](references/host.md); ≤6 findings |
| `standard` | + [references/container.md](references/container.md); up to 16 slices; ≤10 findings |
| `deep` | needed refs only; ≤16 findings |

## Workflow

1. Run `baseline`. Queue `USER root`, `PermitRootLogin yes`, `NOPASSWD:ALL`, privileged compose.
2. Slice-read. Cap quotes at 12 lines.
3. Report the safer setting. Stop unless asked to patch.

## Hard rules

- Config in this workspace. No live privilege-escalation against a host.
- No kernel exploit recipes.
- Do not dump full sshd_config.

## Report template

```markdown
## Lean-hardening (`<mode>`)

**Target:** <image/host config> | **Budget:** files_read=<n>

| Sev | Location | Issue | Fix |
|-----|----------|-------|-----|
| HIGH | Dockerfile | runs as root | USER nonroot |
```
