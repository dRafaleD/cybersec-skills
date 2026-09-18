# Minimize (defensive)

Load for collection and storage of personal data.

| Class | Flag when | Fix |
|-------|-----------|-----|
| Extra fields | App stores unused birthday, location, contacts | Delete column; stop collecting |
| Secrets + PII | Same table as passwords and government ids | Split; encrypt ids; strict ACL |
| Client dump | Analytics SDK sends full form bodies | Allowlist event properties |
| Support export | Admin CSV of all users with emails | Role gate; time-limited; audit |
| Retention | Logs keep PII forever | TTL; drop identifiers after N days |

Do not copy sample rows into chat. Point at the field name and the file.
