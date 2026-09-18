# Logs (defensive)

Load for request logs, error trackers, and debug prints.

```text
rg -n "console.log|logger.|print("
rg -n "req.body|request.POST|setUser"
```

| Class | Flag when | Fix |
|-------|-----------|-----|
| Body logging | `log.info(req.body)` | Log route + status only |
| Email in URL | Identifiers in query strings | POST + id that is not an email |
| Error tracker | Sentry/etc sends Authorization or cookies | Deny-list those headers |
| Debug | Verbose PII left on in prod | Guard with env; default off |
| Access logs | Reverse proxy logs `?email=` | Strip query; keep path |

When quoting a log line, replace identifiers with `[REDACTED]` first.
