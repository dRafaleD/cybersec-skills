---
name: lean-net
description: >-
  Runs token-efficient defensive network and exposure reviews for Cursor and
  Codex. Inventories bind addresses, published ports, security groups, and
  Kubernetes/Docker listeners from local config, then reports compact
  hardening fixes. Use when the user asks for network security, firewall
  review, security groups, open ports, TLS listeners, Docker/K8s exposure,
  or segmentation. Do not use for scanning third-party networks, packet
  crafting, exploits, or unauthorized access.
license: MIT
metadata:
  version: "1.0.0"
---

# Lean Net

Defensive exposure review of **local config**, not of the internet. Scripts list listeners; you confirm a few files; you patch only when asked.

Let `SKILL_ROOT` be the folder that contains this `SKILL.md`. Prefer `python3`; on Windows use `py -3`.

```text
python3 "$SKILL_ROOT/scripts/lean_net.py" expose .
python3 "$SKILL_ROOT/scripts/lean_net.py" trim --chars 2500 path/to/out.txt
```

Do not run nmap, masscan, or cloud APIs against hosts the user did not name as theirs. If they already have a pcap/log, summarize it with `trim`; do not dump packets.

## Mode

Default `lean`. `deep` only if asked.

| Mode | Budget |
|------|--------|
| `lean` | `expose` + up to 8 slices; [references/exposure.md](references/exposure.md); ≤6 findings |
| `standard` | up to 16 slices; ≤10 findings |
| `deep` | needed refs only; ≤16 findings |

## Workflow

1. Run `expose`. Treat `0.0.0.0/0`, `hostNetwork`, Docker `ports:` to all interfaces, and plaintext listeners as the first queue.
2. Slice-read compose, Ingress, Terraform SG, nginx listen lines.
3. Report bind, CIDR, TLS, and egress. Stop unless asked to patch.

## Hard rules

- Config and code in this workspace only. No live port scans of third parties.
- No exploit, spoofing, or packet-injection steps.
- Cap quotes at 12 lines. Never paste a full pcap or flow log.

## Report template

```markdown
## Lean-net (`<mode>`)

**Asset:** <vpc/compose/cluster> | **Budget:** files_read=<n>

| Sev | Location | Issue | Fix |
|-----|----------|-------|-----|
| HIGH | file:line | public bind / open CIDR | tighten CIDR, bind localhost, require TLS |
```
