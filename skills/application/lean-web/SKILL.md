---
name: lean-web
description: >-
  Runs token-efficient defensive web application security reviews for Cursor
  and Codex. Inventories cookie, CORS, CSP, CSRF, and proxy config, then
  reports compact header and sink fixes. Use when the user asks for web
  security, OWASP, XSS, CSRF, CORS, CSP, cookie flags, HTTP security headers,
  or browser/API web hardening. Do not use for exploits, payloads, bypasses,
  attacking live sites, or unauthorized scanning.
license: MIT
metadata:
  version: "1.0.0"
---

# Lean Web

Defensive web review with a hard context budget. Scripts inventory config; you confirm a few sinks; you patch only when asked.

Let `SKILL_ROOT` be the folder that contains this `SKILL.md`. Prefer `python3`; on Windows use `py -3`.

```text
python3 "$SKILL_ROOT/scripts/lean_web.py" scope .
python3 "$SKILL_ROOT/scripts/lean_web.py" headers .
```

Do not crawl live sites. Do not paste full nginx/Caddy files or HAR dumps; use `trim` if a tool is noisy.

```text
python3 "$SKILL_ROOT/scripts/lean_web.py" trim --chars 2500 path/to/out.txt
```

## Mode

Default `lean`. `standard` for a named app/route. `deep` only if the user says audit/thorough.

| Mode | Budget |
|------|--------|
| `lean` | scripts + up to 8 slices; load [references/browser.md](references/browser.md); ≤6 findings |
| `standard` | + [references/api.md](references/api.md); up to 16 slices; ≤10 findings |
| `deep` | needed refs only; ≤16 findings |

## Workflow

1. Run `scope` and `headers`. Read stdout only.
2. Hotspots: cookie/session code, CORS, CSP, CSRF, file upload, HTML sinks, reverse-proxy config.
3. `rg` first, then slice-read. Cap quotes at 12 lines.
4. Report, then stop unless asked to patch.

## Hard rules

- Defense only: location, impact, fix. No payloads, bypass strings, or attack reproduction.
- Do not hit third-party URLs, fuzz, or authenticate to systems the user did not open in this workspace.
- No secret values. No full config pastes.

## Report template

```markdown
## Lean-web (`<mode>`)

**App:** <origin or package> | **Budget:** files_read=<n>

| Sev | Location | Issue | Fix |
|-----|----------|-------|-----|
| HIGH | file:line | one clause | one concrete patch |
```
