# Browser (defensive)

Load for cookies, CSP, CORS, CSRF, and HTML sinks.

```text
rg -n "Set-Cookie|sameSite|httpOnly|secure"
rg -n "Access-Control-Allow-Origin|cors("
rg -n "Content-Security-Policy|contentSecurityPolicy|helmet"
rg -n "innerHTML|dangerouslySetInnerHTML|document.write"
```

| Class | Flag when | Fix |
|-------|-----------|-----|
| Cookie | Session cookie missing `HttpOnly`, `Secure`, or `SameSite` | Set all three; prefer `SameSite=Lax` or `Strict` |
| CSRF | Cookie-auth mutating routes with no CSRF token/custom header | Token or custom header; do not CSRF-exempt JSON blindly |
| CORS | `*` with credentials, or reflecting any Origin | Explicit origin allowlist; never `*` + `Allow-Credentials` |
| CSP | Missing CSP, or `unsafe-inline`/`unsafe-eval` as the only control | Default-src/script-src without unsafe-inline; nonces if needed |
| XSS | Untrusted data into HTML/JS | Encode at the sink or use text APIs |
| Clickjacking | Missing `frame-ancestors` / `X-Frame-Options` | `frame-ancestors 'none'` or allowlist |
| Mixed content | HTTPS page loading HTTP scripts | HTTPS-only; HSTS on the apex |

Do not add exploit payloads to tests. Assert cookie flags, origin allowlist rejects, and encoding helpers.
