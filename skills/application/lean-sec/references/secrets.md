# Secrets (defensive)

Load for `.env`, keys, CI variables, credential files, or a `secrets` script hit.

## Output rule

Never print a secret. Location + kind + `[REDACTED]` only. HIGH means rotate now, then remove from git history if it was committed.

## What to flag and how to fix

| Class | Flag when | Fix |
|-------|-----------|-----|
| Hardcoded credential | Key/token/password in source | Move to env or a secret manager; rotate the leaked value |
| Private key in repo | PEM / `id_rsa` / cloud key json | Delete from tree, rotate, gitignore, use KMS/agent |
| `.env` committed | Real values in git | Keep `.env.example` with empty placeholders only |
| CI secrets in logs | `echo` of env, debug traces | Mask in the CI system; never print |
| Secret in client bundle | NEXT_PUBLIC_/VITE_ used for private keys | Private keys stay server-side |
| Weak example that is real | "changeme", "password", default cloud keys left in prod config | Fail boot if defaults are used |

## After a HIGH hit

1. Name the kind and `file:line`.
2. Tell the owner to rotate at the provider.
3. Patch so the value cannot return (env, gitignore, example file).
4. Do not run `git log -p` or dump history into context. Mention history scrubbing as a follow-up (`git filter-repo` / provider rotation), without pasting old blobs.

## False positives

`*.md` is skipped by the script. `EXAMPLE` AWS keys and obvious placeholders can be LOW or omitted. When unsure, ask rather than quoting the line.
