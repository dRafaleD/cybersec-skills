# API (defensive)

Load for JSON APIs, GraphQL, webhooks, and file uploads.

```text
rg -n "cors|graphql|multipart|multer|upload"
rg -n "Authorization|rateLimit|helmet"
```

| Class | Flag when | Fix |
|-------|-----------|-----|
| Authn | Public mutating route | Require a session or bound token |
| Authz | Object id from the client trusted | Authorize with the session subject |
| Mass assignment | Body copied onto a model | Explicit field allowlist |
| Upload | Raw files executed or served as HTML | Type allowlist, random names, nosniff, separate store |
| SSRF | User URL fetched server-side | Host allowlist; block link-local/metadata |
| Cache | `Cache-Control` missing on authenticated JSON | `private, no-store` |
| GraphQL | Introspection + unlimited depth in prod | Disable introspection; query cost/depth limits |
| Webhook | No signature check | HMAC with a server secret; reject stale timestamps |

Do not probe the live API. Review code and config in the workspace only.
