# Primitives (defensive)

Load for hashes, ciphers, and TLS settings.

```text
rg -n "md5|sha1|DES|ECB|Math.random|InsecureSkipVerify|verify=False"
```

| Class | Flag when | Fix |
|-------|-----------|-----|
| Password hash | MD5, SHA1, unsalted SHA256 | Argon2id or bcrypt with a proper cost |
| Integrity | SHA1 for security (git history is OK) | SHA-256 or BLAKE2 |
| Cipher | DES, 3DES, RC4, AES-ECB | AES-GCM or ChaCha20-Poly1305 |
| RNG | `Math.random` / `random.random` for tokens | `secrets` / `crypto.randomBytes` |
| TLS | `verify=False`, old TLS 1.0 | Verify certs; TLS 1.2+ |
| JWT | `alg: none` or HMAC key as RSA | Allowlist alg; store secret in env |

Do not add a homemade cipher. Replace the call site.
