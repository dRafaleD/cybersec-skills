# CyberSec Skills

Token-efficient **Agent Skills** for defensive security reviews and everyday engineering checks.

An agent that loads one of these skills runs a small local script first, reads only the hotspots, and returns a short findings table. The design keeps context small on purpose: lockfiles, scanner dumps, and whole-file tours stay out of the conversation.

**22 skills** in four categories. Compatible with the [Agent Skills](https://agentskills.io) format and with Codex (`$skill-name`). Shared install path: `~/.agents/skills/`.

## Why this exists

Security and review prompts often fail in two ways: they spend tokens on noise, or they drift into exploit recipes. lean-sec does the opposite.

- **Cheap pass** — stdlib Python inventories paths, headers, manifests, or hashes. No extra packages.
- **Budgeted read** — a handful of file slices, one reference file, a capped finding list.
- **Fix-first output** — severity, `file:line`, issue, concrete patch.
- **Safe to publish** — defense and containment only. No payloads, no unauthorized scanning, no secret values.

## Quick start

```bash
git clone https://github.com/dRafaleD/cybersec-skills.git
cd cybersec-skills
```

Windows:

```powershell
.\install.ps1
```

macOS / Linux:

```bash
chmod +x install.sh
./install.sh
```

Start a **new** agent session. Ask in domain language (“review this repo for leaked secrets”) or invoke by name (`lean-sec`, `lean-web`, …).

The installer links each skill into `~/.agents/skills/`, `~/.codex/skills/`, and `~/.cursor/skills/` when those directories are used on the machine.

Source: [github.com/dRafaleD/cybersec-skills](https://github.com/dRafaleD/cybersec-skills).

## Skill catalog

Full index with links: **[skills/README.md](skills/README.md)**.

| Category | Skills | Use when |
|----------|--------|----------|
| [Application](skills/application/) | `lean-sec` `lean-web` `lean-crypto` `lean-mobile` `lean-privacy` | App code, web, crypto, mobile, PII |
| [Infrastructure](skills/infrastructure/) | `lean-net` `lean-cloud` `lean-ci` `lean-hardening` `lean-iot` `lean-cost` | Network, IAM, CI, hosts, devices, spend |
| [Operations](skills/operations/) | `lean-phish` `lean-malware` `lean-osint` `lean-dfir` `lean-ir-playbook` `lean-threat-model` | Mail, samples, intel, evidence, IR |
| [Engineering](skills/engineering/) | `lean-review` `lean-deps` `lean-docs` `lean-perf` `lean-a11y` | PR quality, deps, docs, speed, a11y |

Default mode is **`lean`**. Use **`deep`** only when you explicitly want a wider pass.

### What the security skills will not do

Exploits, exploit PoCs, payloads, CTF pwn, malware writing, reverse engineering of samples, hash cracking, phishing lures, stalking, unauthorized network or cloud scans, printing live credentials, or dumping disk/memory images into chat.

## How a run works

1. The skill locates `SKILL.md` and runs its script (`scope`, `secrets`, `peek`, …).
2. It loads **one** file from `references/` that matches the hottest issue class.
3. It confirms a budgeted number of files (`rg`, then a slice). Quotes stay ≤ 12 lines.
4. It reports a table, then stops unless you asked for a patch.

Scripts print **kinds and locations**, never secret or PII values (`[REDACTED]`).

```bash
python3 skills/application/lean-sec/scripts/lean_sec.py self-test
python3 skills/application/lean-sec/scripts/lean_sec.py scope /path/to/repo
```

Windows: `py -3` instead of `python3`. Every skill script has `self-test`.

## Repository layout

```text
cybersec-skills/
  README.md
  CONTRIBUTING.md
  LICENSE
  install.ps1 / install.sh
  skills/
    README.md                 # human catalog
    application/              # app & data
    infrastructure/           # net, cloud, CI, hosts
    operations/               # IR, intel, mail, samples
    engineering/              # review, docs, perf, a11y
```

Each skill directory:

```text
lean-web/
  SKILL.md              # agent instructions (keep this small)
  scripts/              # stdlib inventory; run, do not paste
  references/           # loaded on demand
  agents/openai.yaml    # Codex UI metadata
```

## Requirements

- Python 3 (stdlib only; no `pip` install)
- Git, if you use `lean-review` diff stats

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). One skill or one focused change per pull request. Run `self-test` on any script you touch.

## License

[MIT](LICENSE). Copyright 2026 lean-sec contributors.

---

## Türkçe

CyberSec Skills, ajanlara **az token harcayarak** savunma odaklı güvenlik ve mühendislik incelemesi yaptıran bir skill ailesidir. Ajan önce yerel script ile özetler, birkaç hotspot okur, kısa bir bulgu tablosu verir.

Kurulum: `.\install.ps1` veya `./install.sh`, sonra **yeni sohbet**. Katalog: [skills/README.md](skills/README.md).

**Yapmaz:** exploit, payload, yetkisiz tarama, malware çalıştırma/yazma, reverse engineering, stalking, canlı secret basmak.
