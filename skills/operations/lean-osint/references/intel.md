# Intel (authorized)

Load for public-source collection. This is exposure and threat intel for a scope the user owns, not a people-search kit.

## Allowed

- The user's domain, GitHub org, mobile apps, and brand names they named
- Their own exported DNS, cert, and playbook files in the workspace
- Official vendor advisories and public docs

## Not allowed

- Stalking, doxxing, harassment, or mapping a private person's life
- Social-engineering calls, fake accounts, or "pretext interviews"
- Logging into someone else's mail, SaaS, or admin panels
- Credential stuffing, breach-DB password reuse, or buying leak access

## Source quality

| Rank | Kind |
|------|------|
| High | Official site, their DNS/cert export, vendor advisory |
| Med | Reputable news, their public GitHub |
| Low | Unsourced forums, screenshots without a URL |

Mark inference as inference. If a source is a paste of secrets, record `kind=leak` and `[REDACTED]`; tell them to rotate; do not copy the secret.

## Card fields

`claim`, `source_url`, `accessed` (ISO date), `confidence` (`high|med|low`), `next_action` (defensive). Optional `tags`.
