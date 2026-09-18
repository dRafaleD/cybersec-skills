# Actions (defensive)

Load for GitHub Actions / GitLab CI job permissions and triggers.

```text
rg -n "permissions:|write-all|pull_request_target|id-token"
rg -n "secrets.|github.event.issue.title"
```

| Class | Flag when | Fix |
|-------|-----------|-----|
| write-all | Default or explicit `write-all` | Top-level `contents: read`; add writes per job |
| Fork PR | `pull_request_target` with secrets or untrusted checkout | `pull_request` without secrets; or two-job with label gate |
| OIDC | `id-token: write` on a public PR job | Restrict to trusted refs; cloud trust on `sub` |
| Script injection | `run: echo ${{ github.event.issue.title }}` | Env assignment, then quoted `"$TITLE"` |
| Self-hosted | Untrusted PR on a self-hosted runner | Trusted refs only |

Do not demonstrate a working workflow exploit. Show the unsafe line and the safer permissions block.
