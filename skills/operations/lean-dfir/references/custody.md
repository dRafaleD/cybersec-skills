# Custody (authorized)

Load for evidence handling. The job is a defensible note, not a full forensic lab.

## Order of work

1. Write who handed you the files and when (user's words).
2. Hash copies. Do not hash-bomb the original by opening it in an editor that writes.
3. Summarize text logs. Keep a work product separate from evidence.
4. Timeline: time, source, fact, why it matters.

## Collect vs parse

Names of common Windows/Linux artifacts are fine as a **collection checklist** if the user already has admin on that host: Event Logs, syslog, auth.log, browser history exports they made, EDR alerts.

Do not parse raw `$MFT`, registry hives, or memory in this chat. Say: hash the image; use the user's lab (autopsy, plaso, their SIEM) and paste only a trimmed summary.

## Do not

- Alter timestamps, wipe logs, or "clean" a host to hide an incident
- Bypass BitLocker/FileVault or crack password hashes
- Dump SAM/NTDS/LSASS for reuse
- Run exploits "to get a memory image"

If they need containment: isolate the host they own, rotate exposed credentials (`[REDACTED]`), preserve copies.
