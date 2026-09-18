# Host (defensive)

```text
rg -n "PermitRootLogin|PasswordAuthentication|NOPASSWD"
```

| Class | Flag when | Fix |
|-------|-----------|-----|
| Root SSH | `PermitRootLogin yes` | `no` or `prohibit-password` |
| Password SSH | `PasswordAuthentication yes` on internet SSH | keys only |
| Sudo | `NOPASSWD:ALL` | Named commands; require password |
| Shares | World-writable dirs in the image | 0750 + dedicated user |

Do not provide a local-root exploit. Change the setting.
