# Health

| Class | Flag when | Fix |
|-------|-----------|-----|
| No lockfile | App installs at CI/runtime without a lock | Commit the lock; `npm ci` / equivalent |
| Floating | `*` or `latest` on prod deps | Pin; lockfile |
| Security lib | jwt/auth/crypto/xml parser | Prefer maintained; don't dump CVE lists |
| License | GPL in a proprietary app (if they asked licenses) | Replace or get legal OK |
| Scripts | `postinstall` downloading binaries | Review; ignore-scripts for untrusted |

Do not recommend running random `curl | bash` installers to "fix" a CVE.
