# Web (defensive)

Load for HTTP APIs, browsers, GraphQL, webhooks, uploads, or server-side HTTP clients.

Search, don't dump. Confirm the sink, then state the fix.

```text
rg -n "innerHTML|dangerouslySetInnerHTML|document.write"
rg -n "os.system|subprocess|child_process"
rg -n "axios|httpx|urllib|requests"
rg -n "sendFile|createReadStream|multipart|multer|Busboy"
```

## What to flag and how to fix

| Class | Flag when | Fix |
|-------|-----------|-----|
| XSS | Untrusted strings into HTML/JS | Encode/escape at the sink or use text APIs; CSP as backup |
| SQL/NoSQL | String-built queries or unsanitized operators | Bound parameters / ORM bind; reject unknown keys |
| Command | User input in shell strings | argv arrays, no shell; allowlist verbs |
| Template | User input in template engines / `eval` | Don't evaluate; precompiled templates |
| Path | User path concatenated onto a root | Canonicalize, then prefix-check against the root |
| SSRF | User URL fetched by the server | Allowlist hosts; block link-local/metadata; no protocol switch |
| Upload | Raw user files executed or served as HTML | Allowlist types, random names, separate store, nosniff |
| CSRF | Cookie session mutating GET-less routes without a token/samesite | SameSite + CSRF token or custom header for cookie auth |
| Mass assignment | Request body copied into a model | Explicit allowlist of fields |

## Tests that stay defensive

Assert the safe behavior: parameterized query helper used, allowlist rejects an unknown host, upload handler refuses an executable extension. Do not add exploit payloads or bypass strings.

## Skip

WAF folklore, scanner false-positive debates, and quoting long handler files. One sink + one fix is enough.
