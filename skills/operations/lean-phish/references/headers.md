# Headers (defensive)

Load when triaging a saved email. You are classifying risk, not building a lure.

## Signals

| Signal | Why it matters | Action |
|--------|----------------|--------|
| From display ≠ Return-Path / Reply-To host | Lookalike or relay | Treat as untrusted; do not use Reply |
| No SPF/DKIM/DMARC pass (if Authentication-Results present) | Weak auth | Higher suspicion; still not proof |
| Unexpected attachment (`.html`, `.iso`, `.js`, `.exe`, `.lnk`, macro Office) | Payload path | Do not open; hash; org sandbox if they have one |
| Link host ≠ claimed brand | Lookalike | Block domain at mail/DNS; do not visit |
| Urgency + gift card / wire / MFA code | BEC pattern | Out-of-band verify with a known number |

## Do not

- Visit the lure URL "to see"
- Send a test phish
- Open the attachment to "confirm"
- Paste the full raw message into extra tools that store it

Body: one-line gist max. Attachments: name + sha256 only.
