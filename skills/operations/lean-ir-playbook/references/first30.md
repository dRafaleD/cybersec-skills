# First 30 minutes (authorized)

Order matters. Do not "clean" a host before copies exist.

1. **Scope** — What host/account/app, who reported, when.
2. **Isolate** — Network off or token revoke on systems they own. Do not scan the internet.
3. **Preserve** — Copy logs/disk to a named folder; hash with `$lean-dfir`. Do not edit originals.
4. **Rotate** — Passwords, API keys, session cookies that may be in play. Values stay `[REDACTED]`.
5. **Communicate** — Who needs to know (security owner, users). Facts only.
6. **Recover** — Rebuild from known-good; do not negotiate with criminals here.

Skip steps that do not apply. Never include "wipe the attacker" or exploit-back.
