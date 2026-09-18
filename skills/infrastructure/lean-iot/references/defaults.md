# Defaults (defensive)

```text
rg -n "telnet|mqtt|admin:admin|password=admin|debug uart"
```

| Class | Flag when | Fix |
|-------|-----------|-----|
| Default creds | `admin/admin`, `root/root`, empty password | Unique password or cert auth; fail boot on defaults |
| Telnet | Telnet daemon enabled | Off; SSH or local console only |
| MQTT | Broker with no auth / anonymous | User+TLS or mTLS |
| Debug | UART/ADB/debug HTTP on production image | Compile out; require a physical debug fuse |
| Bind | Management UI on `0.0.0.0` | Localhost or VLAN |
| Update | Unsigned OTA URL | Signed images; HTTPS |

Do not provide a dump of vendor default password lists. Point at the config line.
