# Pins (defensive)

Load for action versions, images, and install scripts.

```text
rg -n "uses: .*@(v[0-9]+|main|master|latest)"
rg -n "npm ci|pip install|curl .*bash"
```

| Class | Flag when | Fix |
|-------|-----------|-----|
| Floating tag | `uses: org/action@v4` or `@main` | Pin the full commit SHA; comment the tag |
| Latest image | `image: foo:latest` | Digest pin |
| Curl-pipe | `curl ... \| bash` in CI | Vendor the script; hash-pin |
| No lockfile | App install without a committed lockfile | Commit the lockfile; `npm ci` |
| Mutable cache | Cache key includes untrusted PR files plus write credentials | Split cache; no secrets in cache |

If `lean-sec` `deps` was already run, do not re-dump the manifest list. Reuse it.
