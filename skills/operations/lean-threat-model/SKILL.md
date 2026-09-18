---
name: lean-threat-model
description: >-
  Runs token-efficient threat modeling for Cursor and Codex. Builds a compact
  asset-actor-boundary-abuse-control card from the user's system, without
  diagrams unless asked. Use when the user asks for a threat model, STRIDE,
  attack surface, trust boundaries, or cheapest controls. Do not use for
  exploit design, red-team playbooks, or attacking live systems.
license: MIT
metadata:
  version: "1.0.0"
---

# Lean Threat Model

Five-bullet threat model. Scripts validate the card JSON. No wallpaper diagrams unless asked.

Let `SKILL_ROOT` be the folder that contains this `SKILL.md`. Prefer `python3`; on Windows use `py -3`.

```text
python3 "$SKILL_ROOT/scripts/lean_threat_model.py" template
python3 "$SKILL_ROOT/scripts/lean_threat_model.py" check /path/to/model.json
```

Write the JSON to a temp file, not the user's docs unless they asked.

## Mode

Default `lean`.

| Mode | Budget |
|------|--------|
| `lean` | 1 system card; [references/stride.md](references/stride.md); ≤5 threats |
| `standard` | ≤3 components; ≤10 threats |
| `deep` | still no novel exploits; ≤15 threats |

## Workflow

1. Name assets, actors, trust boundaries from the user's description and a few config files (`lean-net`/`lean-sec` output if already run).
2. For each likely abuse, one **cheapest control**.
3. `check` the JSON. Report the table. Stop.

## Hard rules

- Defense: control, not exploit path.
- No pentest reproduction steps.
- Cap quotes at 12 lines. No architecture novel.

## Report template

```markdown
## Lean-threat-model (`<mode>`)

**System:** <name>

| Asset | Actor | Boundary | Abuse | Cheapest control |
|-------|-------|----------|-------|------------------|
| db | stolen session | app-db | read other rows | authorize by session subject |
```
