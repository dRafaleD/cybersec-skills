# Keys (defensive)

Load for IVs, salts, and key storage.

| Class | Flag when | Fix |
|-------|-----------|-----|
| Static IV | IV/nonce hardcoded | Random IV per encrypt; store beside ciphertext |
| Salt | Same salt for every password | Unique salt, kept with the hash |
| Key in source | PEM or hex key in git | Env or KMS; rotate |
| Compare | `==` on HMAC/password | Constant-time compare |
| Length | AES-128 key truncated from a password | KDF (HKDF/Argon2) into the right size |

Never print key material. Location + kind only.
