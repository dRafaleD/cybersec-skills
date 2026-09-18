# Android (defensive)

```text
rg -n "android:exported|allowBackup|usesCleartextTraffic|debuggable"
```

| Class | Flag when | Fix |
|-------|-----------|-----|
| Exported | Activity/service/receiver exported without permission | `exported=false` or a signature permission |
| Backup | `allowBackup=true` on an app with secrets | false, or exclude sensitive files |
| Cleartext | `usesCleartextTraffic=true` | HTTPS only |
| Debug | `debuggable=true` in release | false for release |
| Deep link | Intent filter with no auth check in the activity | Auth before navigation |
| WebView | JS enabled + file access | Disable file access; bind only needed JS |

Do not supply an exploit APK. Change the flag.
