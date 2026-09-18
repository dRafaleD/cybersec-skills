---
name: lean-osint
description: >-
  Runs token-efficient authorized OSINT and exposure reviews for Cursor and
  Codex. Builds compact sourced intel cards from public information the user
  is allowed to collect. Use when the user asks for OSINT, own-org attack
  surface, public leak checks, brand impersonation review, or a threat-intel
  summary. Do not use for stalking, doxxing, social engineering, credential
  stuffing, scraping login walls, or accessing non-public systems.
license: MIT
metadata:
  version: "1.0.0"
---

# Lean OSINT

Authorized public-source intel with a hard context budget. Cite, compress, stop.

Let `SKILL_ROOT` be the folder that contains this `SKILL.md`. Prefer `python3`; on Windows use `py -3`.

```text
python3 "$SKILL_ROOT/scripts/lean_osint.py" template
python3 "$SKILL_ROOT/scripts/lean_osint.py" check /path/to/cards.json
python3 "$SKILL_ROOT/scripts/lean_osint.py" trim --chars 2500 path/to/dump.txt
```

Write cards to a temp JSON (not the user's content tree unless they asked). Then `check`. Do not paste SERP dumps, HTML, or people-search exports into chat.

## Mode

Default `lean`.

| Mode | Budget |
|------|--------|
| `lean` | ≤5 sourced cards; [references/intel.md](references/intel.md) |
| `standard` | ≤10 cards |
| `deep` | still public sources only; ≤15 cards |

## Workflow

1. Confirm scope: the user's org, domain, product, or an incident they already own. If the target is a private person, stop and ask.
2. Collect from **public** pages and the user's own workspace files. Prefer official sites, their DNS/certs they already exported, their GitHub org.
3. One claim per card: source URL, date accessed, confidence, next **defensive** action.
4. `check` the JSON. Report the table. Do not keep raw search pages in context.

## Hard rules

- No fake personas, pretexting, or phishing "for OSINT".
- No credentials, session cookies, or bypass of paywalls/auth.
- No dossiers on private individuals (home address, family, phone) unless the user is that person and asked about their own exposure.
- Do not dump WHOIS/full PDFs. Quote ≤12 lines from a source.

## Report template

```markdown
## Lean-osint (`<mode>`)

**Question:** <one line> | **Scope:** <domain/org>

| Conf | Claim | Source | Defensive next step |
|------|-------|--------|---------------------|
| med | one clause | host + date | one action |
```
