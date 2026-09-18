# STRIDE (cheap)

Use STRIDE only as a prompt, not as a 40-page report.

| Letter | Ask | Typical control |
|--------|-----|-----------------|
| S | Can someone pretend to be this actor? | MFA, bound session, no shared accounts |
| T | Can data be changed in transit or at rest? | TLS, signed tokens, integrity checks |
| R | Can an actor deny an action they did? | Audit log on the server, not the client |
| I | Can they read what they should not? | Authz on every object id |
| D | Can they knock the service over cheaply? | Rate limit, size cap, timeouts |
| E | Can they run code or admin they should not? | Least privilege, no user-controlled exec |

One threat per row. Skip empty letters. Prefer the abuse that is already visible in config (public bind, missing authz).
