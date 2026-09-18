---
name: lean-phish
description: >-
  Runs token-efficient defensive phishing and email triage for Cursor and
  Codex on messages the user already has. Summarizes headers, flags lookalike
  From/Reply-To mismatch, and hashes attachments without opening them. Use
  when the user asks to triage a suspicious email, .eml, phishing, BEC, or
  lookalike domain. Do not use to write lures, send phishing, spoof mail, or
  execute attachments.
license: MIT
metadata:
  version: "1.0.0"
---

# Lean Phish

Defensive mail triage on **files the user already saved**. Headers, mismatch, hash. Never send mail. Never open attachments.

Let `SKILL_ROOT` be the folder that contains this `SKILL.md`. Prefer `python3`; on Windows use `py -3`.

```text
python3 "$SKILL_ROOT/scripts/lean_phish.py" peek /path/to/message.eml
python3 "$SKILL_ROOT/scripts/lean_phish.py" trim --chars 2500 path/to/out.txt
```

If they pasted a mail into chat, write it to a temp `.eml` and peek that. Do not dump the full body.

## Mode

Default `lean`.

| Mode | Budget |
|------|--------|
| `lean` | `peek`; [references/headers.md](references/headers.md); ≤6 findings |
| `standard` | + extra messages; ≤10 findings |
| `deep` | still no attachment execute; ≤12 findings |

## Workflow

1. Confirm the mail is theirs to review (inbox they own, or a sample they collected).
2. Run `peek`. Read stdout only.
3. Compare From vs Return-Path/Reply-To, auth results if present, attachment names/hashes.
4. Recommend: quarantine, do not click, reset **their** passwords if they already did click (`[REDACTED]`).

## Hard rules

- Do not write phishing copy, landing pages, or spoofing how-to.
- Do not execute or unpack attachments. Hash only.
- Do not log into the sender's provider or "verify" credentials.
- Cap body quotes at 12 lines. Prefer the script summary.

## Report template

```markdown
## Lean-phish (`<mode>`)

**From:** <display> | **Return-Path host:** <host> | **Auth:** <spf/dkim/dmarc or unknown>

| Sev | Signal | Note | Action |
|-----|--------|------|--------|
| HIGH | reply-to mismatch | one clause | quarantine; warn users |
```
