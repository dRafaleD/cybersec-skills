# IAM (defensive)

Load for roles, policies, IRSA, and admin bindings.

```text
rg -n "AdministratorAccess|iam:PassRole|public-read|allUsers"
rg -n "169.254.169.254|0.0.0.0/0"
```

| Class | Flag when | Fix |
|-------|-----------|-----|
| Wildcard | `Action: "*"` or `Resource: "*"` on Allow | List services and ARNs; drop `"*"` |
| Admin | `AdministratorAccess`, `Owner`, `roles/owner` | Job-shaped custom role |
| Trust | Trust policy `Principal: "*"` or any federated issuer | Named principals; audience/sub conditions |
| PassRole | Unconstrained `iam:PassRole` | Resource allowlist of roles |
| IRSA/WI | No audience/`sub` condition on the trust | Restrict to the workload SA |
| Long-lived keys | Access keys in repo or user keys for apps | Roles, OIDC, short tokens |

Do not design a privilege-escalation path. State the over-grant and the smaller policy.
