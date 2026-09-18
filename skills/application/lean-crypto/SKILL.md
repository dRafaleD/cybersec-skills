---
name: lean-crypto
description: >-
  Runs token-efficient defensive cryptography reviews for Cursor and Codex.
  Inventories weak hashes, ECB mode, Math.random tokens, and hardcoded IVs
  in local code, then reports compact algorithm and key-handling fixes. Use
  when the user asks for crypto review, TLS, hashing, JWT signing, RNG, or
  password storage. Do not use for cracking hashes, forging tokens, or
  designing novel ciphers.
license: MIT
metadata:
  version: "1.0.0"
---

# Lean Crypto

Defensive crypto hygiene in **this workspace**. Scripts list weak primitives; you confirm a few files; you patch only when asked.

Let `SKILL_ROOT` be the folder that contains this `SKILL.md`. Prefer `python3`; on Windows use `py -3`.

```text
python3 "$SKILL_ROOT/scripts/lean_crypto.py" weak .
python3 "$SKILL_ROOT/scripts/lean_crypto.py" trim --chars 2500 path/to/out.txt
```

## Mode

Default `lean`. `deep` only if asked.

| Mode | Budget |
|------|--------|
| `lean` | `weak` + up to 8 slices; [references/primitives.md](references/primitives.md); ≤6 findings |
| `standard` | + [references/keys.md](references/keys.md); up to 16 slices; ≤10 findings |
| `deep` | needed refs only; ≤16 findings |

## Workflow

1. Run `weak`. Queue MD5/SHA1 for security, DES/ECB, `Math.random` for tokens, static IVs, `verify=False`.
2. Slice-read the matching file. Cap quotes at 12 lines.
3. Report the safer primitive. Stop unless asked to patch.

## Hard rules

- No hash cracking, rainbow tables, or token-forging steps.
- No secret values. `[REDACTED]` for keys.
- Do not invent custom crypto. Prefer platform libraries.

## Report template

```markdown
## Lean-crypto (`<mode>`)

**Scope:** <app> | **Budget:** files_read=<n>

| Sev | Location | Issue | Fix |
|-----|----------|-------|-----|
| HIGH | file:line | MD5 for passwords | Argon2id or bcrypt |
```
