# iOS (defensive)

```text
rg -n "NSAllowsArbitraryLoads|CFBundleURLSchemes|UIFileSharingEnabled"
```

| Class | Flag when | Fix |
|-------|-----------|-----|
| ATS | `NSAllowsArbitraryLoads` true | Per-domain exceptions only if required |
| URL scheme | Custom scheme with no auth | Universal links + session check |
| File sharing | `UIFileSharingEnabled` on a data app | Off unless needed |
| Keychain | Data in UserDefaults that belongs in Keychain | Keychain + `WhenUnlockedThisDeviceOnly` |
| ATS leftover | HTTP API in prod | HTTPS |

Do not provide jailbreak or sideload steps.
