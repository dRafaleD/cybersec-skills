---
name: lean-dfir
description: >-
  Runs token-efficient authorized digital forensics and incident response for
  Cursor and Codex. Hashes evidence, summarizes logs, and keeps chain-of-custody
  notes without dumping images into context. Use when the user asks for DFIR,
  forensics, log timeline, evidence handling, or incident reconstruction on
  data they already have. Do not use to attack systems, bypass encryption,
  alter evidence, recover others' data without authorization, or paste disk
  or memory images into chat.
license: MIT
metadata:
  version: "1.0.0"
---

# Lean DFIR

Authorized forensics on **copies the user already collected**. Hash, summarize, preserve. Do not attack, decrypt-bypass, or dump images.

Let `SKILL_ROOT` be the folder that contains this `SKILL.md`. Prefer `python3`; on Windows use `py -3`.

```text
python3 "$SKILL_ROOT/scripts/lean_dfir.py" hash /path/to/evidence
python3 "$SKILL_ROOT/scripts/lean_dfir.py" logs /path/to/logs-dir
python3 "$SKILL_ROOT/scripts/lean_dfir.py" trim --chars 2500 path/to/tool.txt
```

If the user points at a disk/memory image, hash it and stop. Do not parse `$MFT`, hives, or RAM in this chat.

## Mode

Default `lean`.

| Mode | Budget |
|------|--------|
| `lean` | hash + log summary; [references/custody.md](references/custody.md); ≤8 timeline rows |
| `standard` | + extra log dirs; ≤12 rows |
| `deep` | still no image dumps; ≤16 rows |

## Workflow

1. Confirm authorization and that work is on a **copy**.
2. Hash each evidence file before reading.
3. Summarize text logs (`logs`). Hunt with `rg` on those logs; do not paste full files.
4. Build a short timeline. Recommend containment the user can apply on systems they own.

## Hard rules

- Do not modify evidence. Do not clear logs. Do not teach anti-forensics.
- Do not bypass disk encryption, crack passwords, or dump credential stores for reuse.
- Do not image or scan machines the user does not administer.
- Binary images: hash + size only. Point them at their existing lab tools.

## Report template

```markdown
## Lean-dfir (`<mode>`)

**Incident:** <one line> | **Evidence hashed:** <n files>

| Time | Host/source | What | Why it matters |
|------|-------------|------|----------------|
| ISO-8601 | log:line | one clause | one clause |

**Custody:** copies hashed; originals untouched
**Not done:** memory/disk parse, credential dump
```
