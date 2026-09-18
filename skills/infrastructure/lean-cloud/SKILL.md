---
name: lean-cloud
description: >-
  Runs token-efficient defensive cloud and IAM reviews for Cursor and Codex.
  Inventories wildcard policies, public buckets, IMDS, and admin roles in local
  Terraform, Bicep, CDK, and cloud JSON, then reports compact hardening fixes.
  Use when the user asks for cloud security, IAM, S3/GCS buckets, security
  groups, IRSA, metadata service, or least privilege. Do not use for attacking
  cloud accounts, stealing keys, or scanning other tenants.
license: MIT
metadata:
  version: "1.0.0"
---

# Lean Cloud

Defensive review of **local cloud config**. Scripts list risky IAM and storage lines; you confirm a few files; you patch only when asked.

Let `SKILL_ROOT` be the folder that contains this `SKILL.md`. Prefer `python3`; on Windows use `py -3`.

```text
python3 "$SKILL_ROOT/scripts/lean_cloud.py" iam .
python3 "$SKILL_ROOT/scripts/lean_cloud.py" trim --chars 2500 path/to/out.txt
```

Do not call cloud APIs against accounts the user did not open in this workspace. Do not dump full IAM JSON.

## Mode

Default `lean`. `deep` only if asked.

| Mode | Budget |
|------|--------|
| `lean` | `iam` + up to 8 slices; [references/iam.md](references/iam.md); ≤6 findings |
| `standard` | + [references/storage.md](references/storage.md); up to 16 slices; ≤10 findings |
| `deep` | needed refs only; ≤16 findings |

## Workflow

1. Run `iam`. Queue wildcards, `Principal "*"`, public ACLs, admin managed policies, IMDS v1, `0.0.0.0/0` on data stores.
2. Slice-read the matching `.tf` / Bicep / SAM / K8s service-account annotations.
3. Report least-privilege fixes. Stop unless asked to patch.

## Hard rules

- Workspace config only. No live `sts`, no enumerating someone else's org.
- No exploit, privilege-escalation recipes, or key theft.
- Cap quotes at 12 lines. Never print secret values.

## Report template

```markdown
## Lean-cloud (`<mode>`)

**Account/stack:** <name or folder> | **Budget:** files_read=<n>

| Sev | Location | Issue | Fix |
|-----|----------|-------|-----|
| HIGH | file:line | wildcard Action/Resource | split by service; constrain Resource |
```
