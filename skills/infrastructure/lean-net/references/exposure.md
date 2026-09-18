# Exposure (defensive)

Load when reviewing listeners, security groups, or service mesh binds.

```text
rg -n "0.0.0.0/0|hostNetwork|hostPort"
rg -n "EXPOSE |ports:|listen "
rg -n "aws_security_group|LoadBalancer"
```

| Class | Flag when | Fix |
|-------|-----------|-----|
| Public CIDR | `0.0.0.0/0` or `::/0` on SSH/RDP/DB/admin | Restrict to known egress; private endpoints |
| Bind all | App listens `0.0.0.0` on a sensitive port without a proxy | Bind localhost; put TLS proxy in front |
| Docker publish | `ports: "0.0.0.0:5432:5432"` | Publish only on loopback or drop publish |
| K8s | `hostNetwork`, NodePort/LoadBalancer on admin apps | ClusterIP + ingress with auth |
| TLS | HTTP on the public listener | TLS 1.2+; redirect HTTP |
| Egress | Workloads can reach metadata/IMDS or the whole internet with secrets | IMDS v2/block; egress allowlist |
| DNS | Wildcard `*` ingress with no auth | Auth and exact hosts |

Do not scan the live VPC. Change the config, then the user can verify on their own network.
