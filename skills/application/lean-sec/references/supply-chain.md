# Supply chain (defensive)

Load for dependencies, CI, containers, or IaC.

The `deps` script already summarized direct dependencies. Do not `cat` lockfiles. Do not paste CVE databases. If a scanner JSON appears, `trim` it and keep only package + severity + whether it is direct.

## What to flag and how to fix

| Class | Flag when | Fix |
|-------|-----------|-----|
| Unpinned install | Floating `latest`, unpinned Actions (`@master`) | Pin versions; pin Actions to a SHA |
| CI permissions | `write-all`, pull_request running on secrets | Least privilege; do not expose secrets to fork PRs |
| Script injection | User-controlled input in `run:` or shell | Env vars quoted; no interpolation of untrusted titles |
| Container | Process as root, secrets in layers, `:latest` | Non-root user, runtime secrets, digest pins |
| IaC public | S3/GCS public, `0.0.0.0/0` SSH, metadata exposed | Private by default, tight CIDR, no public buckets |
| Dangerous parsers | `pickle`, `yaml.load` without `SafeLoader`, XML external entities | Safe loaders; disable DTD/XXE |
| Scope | `npm` lifecycle scripts from unknown packages | Ignore scripts when installing untrusted trees; lockfile committed |

## Cheap checks

```text
rg -n "uses: .*@master|uses: .*@main" .github/workflows
rg -n "pickle.load|yaml.load|image: .*:latest" --glob "!node_modules"
```

If no lockfile exists for an app that installs at runtime, that is a MED finding: add and commit one.

Do not recommend running exploit PoCs against registries or pulling unknown malware samples.
