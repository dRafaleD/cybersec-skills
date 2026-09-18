# Waste

| Class | Flag when | Fix |
|-------|-----------|-----|
| Size | `t3.2xlarge` / `n1-highmem` with no comment | Smaller type; autoscale |
| Always on | No schedule / no min=0 | Stop nights; scale to zero |
| Image | `:latest` pulling fat images | Slim + digest |
| Artifacts | CI uploads everything | Path allowlist; retention days |
| Logs | Debug in prod | Info; sample traces |
| NAT | NAT gateway per tiny VPC | Shared or none in sandbox |

Agent tokens: keep `$lean-*` skills; do not paste lockfiles. That is a cost control too.
