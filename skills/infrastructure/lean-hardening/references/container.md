# Container (defensive)

```text
rg -n "USER root|privileged: true|--privileged|cap_add"
```

| Class | Flag when | Fix |
|-------|-----------|-----|
| Root process | No `USER` or `USER root` | Numeric non-root USER |
| Privileged | `privileged: true` | Drop; add only needed caps |
| Secrets | ENV with passwords | Runtime secret mount |
| Latest | `FROM foo:latest` | Digest pin |

Pair with `$lean-net` if ports are published.
