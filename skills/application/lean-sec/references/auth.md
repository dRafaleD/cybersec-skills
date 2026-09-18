# Auth (defensive)

Load for login, sessions, JWT, OAuth/OIDC, RBAC, API keys, or IDOR.

```text
rg -n "jwt|jsonwebtoken|jose|passport|session|Set-Cookie|Authorization"
rg -n "findById|authorize|req.user|req.params"
```

## What to flag and how to fix

| Class | Flag when | Fix |
|-------|-----------|-----|
| IDOR / missing authz | Object id from the client is trusted | Authorize with the session subject on every object access |
| JWT in source / weak JWT | Secret hardcoded; `alg` trusted from header; no `exp` | Env-stored secret, allowlist alg, short TTL, rotate |
| Session cookie | Missing `HttpOnly`, `Secure`, `SameSite` | Set all three; regenerate session id at login |
| Password storage | Plaintext, reversible crypto, fast hashes | Argon2id or bcrypt with a proper cost; never log passwords |
| Reset / invite tokens | Guessable or reusable tokens | High-entropy, single-use, short TTL, hashed at rest |
| OAuth redirect | Open redirect_uri | Exact allowlist of redirect URIs |
| CSRF on cookie auth | State-changing cookie requests with no CSRF control | SameSite=Lax/Strict plus CSRF token or custom header |
| Privilege | Role from the client body | Role only from the server-side account record |

## JWT notes (cheap)

Treat JWT as a bearer token. Flag tokens in `localStorage` for XSS-heavy apps; prefer httpOnly cookies when the client is a first-party browser. Do not design novel crypto.

## Tests that stay defensive

Assert 401/403 on missing/foreign object ids, cookie flags, and that role cannot be set from the request body. Do not include token-forging or session-fixation attack recipes.
