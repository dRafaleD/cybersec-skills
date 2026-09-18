---
name: lean-sec
description: >-
  Runs token-efficient defensive security reviews and hardening for Cursor and
  Codex. Uses local scripts to inventory high-risk files, find likely secrets
  without printing values, and summarize dependency surface, then reports
  compact fix-first findings. Use when the user asks for a security review,
  vulnerability review, OWASP check, secret scan, auth/authz review, IDOR,
  JWT, dependency or supply-chain review, hardening, threat model, or
  cheaper/faster security analysis; also when they mention token budget,
  context bloat, or lean security. Do not use for exploits, exploit PoCs,
  payloads, CTFs, reverse engineering, malware, or unauthorized access.
license: MIT
metadata:
  version: "1.0.0"
---

# Lean Sec

Defensive review with a hard context budget. Scripts summarize; you read only hotspots; you patch only when asked.

Let `SKILL_ROOT` be the folder that contains this `SKILL.md`. Scan target defaults to the current workspace. Prefer `python3`; on Windows use `py -3` if needed.

```text
python3 "$SKILL_ROOT/scripts/lean_sec.py" scope .
python3 "$SKILL_ROOT/scripts/lean_sec.py" secrets .
python3 "$SKILL_ROOT/scripts/lean_sec.py" deps .
```

Do not copy these scripts into the target repo. Do not `cat` lockfiles, SARIF, coverage, or tool logs into the conversation; pipe bulky output through `trim`.

## Mode

Pick one from the user request. Default is `lean`.

| Mode | When | Budget |
|------|------|--------|
| `lean` | default, "quick", "cheap", "token", "hızlı" | scripts + up to 8 file slices; 1 reference; ≤6 findings |
| `standard` | "review this PR", named area, no budget ask | scripts + up to 16 slices; 2 references; ≤10 findings |
| `deep` | user explicitly says audit/thorough/deep/kapsamlı | scripts + more slices; needed references only; ≤16 findings |

Never "go deep" because the repo is large. Large repos make `lean` more important.

## Workflow

1. **Cheap pass (required).** Run `scope`, `secrets`, and `deps`. Read only their stdout. If a command fails, say so and continue with `rg` over auth/crypto/sql/upload/ci paths; still do not dump matches in bulk.
2. **Choose hotspots.** Take the script's ranked paths plus the user's named files. Ignore `node_modules`, `dist`, `build`, `target`, `.git`, lockfile bodies, generated assets.
3. **Load one reference** that matches the hottest class:
   - Web/injection/upload/SSRF → [references/web.md](references/web.md)
   - Session/JWT/RBAC/IDOR → [references/auth.md](references/auth.md)
   - Keys, `.env`, CI secrets → [references/secrets.md](references/secrets.md)
   - Dependencies, CI, containers, IaC → [references/supply-chain.md](references/supply-chain.md)
   - Need stricter budget rules → [references/token-budget.md](references/token-budget.md)
   Load extra references only in `standard`/`deep` when a second class is clearly in play.
4. **Confirm, don't tour.** `rg` first. Read files with line offsets. Stop a file once the issue is confirmed or cleared.
5. **Report** in the template below. Then stop unless the user asked to patch.
6. **Patch (only if asked).** Smallest hardening change. Re-run `secrets` if you touched credentials handling. Do not add scanners, git hooks, or new deps unless asked.

## Hard rules

- **Defense only.** Describe location, impact, and the fix. Do not write exploits, PoCs, payloads, bypasses, or reproduction attack steps. If asked for a fix and an exploit/PoC, ship the fix and refuse the exploit in one sentence.
- **No secret values.** Scripts already redact. If you see a live credential, write `kind @ file:line` and `[REDACTED]`. Tell the user to rotate; do not echo the token.
- **No context stuffing.** Do not paste full files, lockfiles, Dockerfiles, SARIF, `npm ls`, or CVE encyclopedias. Cap any quoted snippet at 12 lines.
- **Authorized scope.** Review code and config the user can already see in this workspace. Do not scan third-party systems, brute-force, or probe live hosts.
- **Do not load** this skill's `README.md` or `LICENSE` while reviewing another repo.

## Report template

```markdown
## Lean-sec (`<lean|standard|deep>`)

**Asset:** <app/lib/ci> | **Stack:** <one line>
**Budget:** scripts=<scope,secrets,deps> files_read=<n> refs=<names>

| Sev | Location | Issue | Fix |
|-----|----------|-------|-----|
| HIGH | file:line | one clause | one concrete patch |

**Also:** <optional 1-line residual risk>
**Not reviewed:** <areas skipped to keep the budget>
```

Severity: `HIGH` exploitable with default access or leaked secret; `MED` needs extra conditions; `LOW` hardening. Sort HIGH first. Skip stylistic nits. If there are no issues, say that in two sentences and list what was covered.

## Threat model (only if asked)

Five bullets: assets, actors, trust boundaries, most likely abuse, cheapest control. No diagrams unless asked. Do not load extra references for this.
