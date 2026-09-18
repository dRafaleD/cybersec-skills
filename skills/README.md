# Skills catalog

Each skill is a folder with `SKILL.md`, optional `scripts/`, `references/`, and `agents/openai.yaml`.
Installers look for `SKILL.md` anywhere under this directory and expose the **skill folder name** (for example `lean-web`), not the category.

| Category | What it covers |
|----------|----------------|
| [application](application/) | App code, web, crypto, mobile, privacy |
| [infrastructure](infrastructure/) | Network, cloud/IAM, CI, host hardening, IoT, cost |
| [operations](operations/) | Phishing, malware triage, OSINT, DFIR, IR, threat modeling |
| [engineering](engineering/) | PR review, dependencies, docs, performance, accessibility |

How a run works: a stdlib Python script summarizes the tree, the agent reads a small number of hotspots, then it returns a compact table. Default mode is `lean`.

---

## application/

| Skill | When to use it |
|-------|----------------|
| [lean-sec](application/lean-sec/) | Security review of application code, secrets, authz, and dependencies |
| [lean-web](application/lean-web/) | Cookies, CORS, CSP, CSRF, XSS sinks, API headers |
| [lean-crypto](application/lean-crypto/) | Weak hashes, ECB, poor RNGs, TLS verification off |
| [lean-mobile](application/lean-mobile/) | Android/iOS manifests: exported components, backup, ATS |
| [lean-privacy](application/lean-privacy/) | PII in code and logs (values are redacted) |

## infrastructure/

| Skill | When to use it |
|-------|----------------|
| [lean-net](infrastructure/lean-net/) | Bind addresses, published ports, open CIDRs |
| [lean-cloud](infrastructure/lean-cloud/) | IAM wildcards, public buckets, IMDS |
| [lean-ci](infrastructure/lean-ci/) | Workflow permissions, unpinned actions, fork PRs |
| [lean-hardening](infrastructure/lean-hardening/) | SSH, sudo, container `USER`, privileged flags |
| [lean-iot](infrastructure/lean-iot/) | Default passwords, telnet, open MQTT |
| [lean-cost](infrastructure/lean-cost/) | Always-on compute, `:latest` images, heavy CI artifacts |

## operations/

| Skill | When to use it |
|-------|----------------|
| [lean-phish](operations/lean-phish/) | Triage a saved `.eml` (headers and attachment hashes) |
| [lean-malware](operations/lean-malware/) | Hash and peek a sample you already have; do not run it |
| [lean-osint](operations/lean-osint/) | Authorized public-source intel cards |
| [lean-dfir](operations/lean-dfir/) | Hash evidence copies and summarize logs |
| [lean-ir-playbook](operations/lean-ir-playbook/) | First 30 minutes: isolate, preserve, rotate, communicate |
| [lean-threat-model](operations/lean-threat-model/) | Compact asset / actor / control cards |

## engineering/

| Skill | When to use it |
|-------|----------------|
| [lean-review](engineering/lean-review/) | PR review from git diff stats, not a full patch dump |
| [lean-deps](engineering/lean-deps/) | Direct dependencies, missing lockfiles, floating `latest` |
| [lean-docs](engineering/lean-docs/) | README gaps and undocumented public APIs |
| [lean-perf](engineering/lean-perf/) | N+1 queries, `SELECT *`, unbounded reads |
| [lean-a11y](engineering/lean-a11y/) | Missing alt text, click-only divs, unlabeled inputs |

Invoke a skill by name (`lean-web`) or by asking for that domain. See the root [README](../README.md) for install and policy.
